# 订单模块 —— 接口视图层
# 负责订单与收货地址的 REST 接口：下单购买、模拟支付、审核、发货、确认收货、取消，
# 以及按角色做数据隔离和权限校验，并在关键节点写入库存流水与操作日志。

from django.db import transaction
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.models import Product, ProductStockRecord
from common.logging import write_log
from common.pagination import OptInPagination
from .models import Order, Address
from .serializers import (
    OrderSerializer, OrderShipSerializer, OrderBuyProductSerializer, OrderPaySerializer,
    AddressSerializer, OrderAuditSerializer, OrderManualSerializer, OrderStatusSetSerializer,
)


def _now():
    """获取当前本地时间，格式化为 'yyyy-mm-dd HH:MM' 的字符串。

    返回：用于写入订单各时间字段的字符串。
    """
    from django.utils import timezone
    return timezone.localtime().strftime('%Y-%m-%d %H:%M')


def _who(request):
    """从请求中取当前操作人名称，供订单状态日志与操作日志记录。

    参数:
        request: 当前请求对象。
    返回:
        优先取用户姓名，其次取用户名，都为空时返回“系统”。
    """
    u = getattr(request, 'user', None)
    return (getattr(u, 'name', '') or '') or (getattr(u, 'username', '') or '') or '系统'


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集：订单的查询、创建以及支付、审核、发货、完成、取消、改状态等业务接口。

    路由前缀为 /api/orders/，全部接口要求登录；接口内部的角色权限见各方法说明。
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # 仅在请求携带 page/page_size 参数时分页，避免前端下拉框等场景被分页截断
    pagination_class = OptInPagination
    # 只开放查询与 POST 业务动作，订单数据不允许通过 PUT/PATCH/DELETE 直接改删
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """按角色做数据隔离，并叠加类型、状态、关键字等筛选条件。

        返回:
            过滤后的订单查询集。学员（role=user）仅见自己的订单，
            传承人（role=heritage）仅见自己作为卖家的订单，管理员可见全部。
        """
        qs = super().get_queryset()
        user = self.request.user
        # 数据隔离：不同角色只能看到与自己相关的订单
        if user.role == 'heritage':
            qs = qs.filter(seller=user)
        else:
            if user.role == 'user':
                qs = qs.filter(buyer_user=user)
        type_q = self.request.query_params.get('type')
        status_q = self.request.query_params.get('status')
        if type_q:
            qs = qs.filter(type=type_q)
        if status_q:
            qs = qs.filter(status=status_q)
        # 关键字模糊匹配订单号、商品名、买家、电话、收件人、物流单号
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            q = (Q(order_no__icontains=kw) | Q(item_name__icontains=kw) | Q(buyer__icontains=kw)
                 | Q(buyer_phone__icontains=kw) | Q(receiver__icontains=kw)
                 | Q(phone__icontains=kw) | Q(tracking_no__icontains=kw))
            # 关键字为纯数字时额外按订单主键精确匹配，方便直接搜 ID
            if kw.isdigit():
                q = q | Q(id=int(kw))
            qs = qs.filter(q)
        order_no_q = (self.request.query_params.get('order_no') or '').strip()
        if order_no_q:
            qs = qs.filter(order_no__icontains=order_no_q)
        return qs

    def perform_create(self, serializer):
        """创建订单时的统一兜底：来源固定为自动下单、初始状态待付款，学员创建时绑定买家账号。"""
        data = {'source': 'auto', 'status': 'pending'}
        if self.request.user.role == 'user':
            data['buyer_user'] = self.request.user
        serializer.save(**data)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def buy_product(self, request):
        """学员购买作品下单。

        URL: POST /api/orders/buy_product/
        权限: 仅普通用户（role=user）可调用。
        参数: product_id、qty、pay_method、receiver、phone、address、remark。
        返回: 201 及新建订单数据；作品不存在返回 404，不可售/库存不足返回 400。
        """
        # 角色校验：传承人与管理员不能走学员下单入口
        if request.user.role != 'user':
            return Response({'msg': '仅普通用户账号可购买作品'}, status=status.HTTP_403_FORBIDDEN)
        s = OrderBuyProductSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        # 行级锁锁住作品记录，防止并发下单造成超卖
        product = Product.objects.select_for_update().filter(id=d['product_id']).first()
        if not product:
            return Response({'msg': '作品不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 只有审核通过且开启售卖的作品才允许购买
        if product.status != 'approved' or not product.saleable:
            return Response({'msg': '该作品当前不可购买'}, status=status.HTTP_400_BAD_REQUEST)
        qty = d['qty']
        if product.stock < qty:
            return Response({'msg': f'库存不足（剩余 {product.stock} 件）'}, status=status.HTTP_400_BAD_REQUEST)

        now = _now()
        user = request.user
        # 下单时只生成待付款订单，库存留到支付成功时再扣减
        order = Order.objects.create(
            type='product',
            item_name=product.name,
            glyph=product.glyph or '盏',
            buyer_user=user,
            buyer=user.name or user.username,
            buyer_phone=user.phone or '',
            seller=product.owner,
            price=product.price * qty,
            status='pending',
            source='auto',
            product_id=product.id,
            qty=qty,
            pay_method=d.get('pay_method') or '',
            order_time=now,
            receiver=d.get('receiver', ''),
            address=d.get('address', ''),
            phone=d.get('phone', ''),
            remark=d.get('remark', ''),
        )
        # 记录初始状态日志与操作日志，操作人取当前登录账号
        order.log_status('pending', operator=_who(request), note='用户提交订单', from_status='')
        write_log(request, 'order', '提交订单',
                  f'订单 {order.order_no}「{order.item_name}」×{qty} 已生成，待付款')
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """模拟支付订单：扣减作品库存并流转为“待发货”。

        URL: POST /api/orders/{id}/pay/
        权限: 仅普通用户（role=user），且只能支付自己名下的待付款订单。
        返回: 支付后的订单数据；状态不符或作品不可售时返回 400。
        """
        if request.user.role != 'user':
            return Response({'msg': '仅普通用户账号可执行支付'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        # 只有待付款状态允许支付，避免重复扣库存
        if obj.status != 'pending':
            return Response({'msg': '仅待付款订单可支付'}, status=status.HTTP_400_BAD_REQUEST)
        s = OrderPaySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        pm = (s.validated_data.get('pay_method') or '').strip()

        # 作品订单需在支付成功时真正出库：加行级锁后校验并扣减库存
        if obj.type == 'product' and obj.product_id and obj.qty:
            product = Product.objects.select_for_update().filter(id=obj.product_id).first()
            if product is None:
                return Response({'msg': '关联作品已不存在，无法完成支付'}, status=status.HTTP_400_BAD_REQUEST)
            if product.status != 'approved' or not product.saleable:
                return Response({'msg': '该作品当前不可售，无法完成支付'}, status=status.HTTP_400_BAD_REQUEST)
            if product.stock < obj.qty:
                return Response(
                    {'msg': f'库存不足（当前仅剩 {product.stock} 件），无法完成支付'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            product.stock -= obj.qty
            product.save(update_fields=['stock'])
            # 写入库存出库流水，留在库存管理中可查
            ProductStockRecord.objects.create(
                product=product, product_name=product.name, type='order', qty=obj.qty,
                note='在线支付成功销售出库', operator=request.user.name or request.user.username, time=_now(),
            )
        prev = obj.status
        obj.status = 'paid'
        obj.pay_time = _now()
        if pm:
            obj.pay_method = pm
        obj.review_comment = ''
        obj.save()
        obj.log_status('paid', operator=_who(request), note=f'模拟支付（{obj.pay_method or "未填支付方式"}）', from_status=prev)
        write_log(request, 'order', '订单支付', f'订单 {obj.order_no}「{obj.item_name}」支付成功，待发货')
        return Response(OrderSerializer(obj).data)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        """审核待审核订单：通过则扣库存转“待发货”，驳回则转“已驳回”并记录原因。

        URL: POST /api/orders/{id}/audit/
        权限: 仅管理员（role=admin）可调用。
        参数: action 取 approve/reject，驳回时 review_comment 必填。
        返回: 审核后的订单数据。
        """
        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可审核订单'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        if obj.status != 'review':
            return Response({'msg': '仅待审核订单可执行审核'}, status=status.HTTP_400_BAD_REQUEST)
        s = OrderAuditSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        action = s.validated_data['action']
        comment = (s.validated_data.get('review_comment') or '').strip()
        # 驳回必须说明原因，方便学员看到驳回理由
        if action == 'reject' and not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        prev = obj.status

        if action == 'approve':
            # 审核通过才真正占用库存，因此必须先校验库存是否充足
            if obj.type == 'product' and obj.product_id and obj.qty:
                product = Product.objects.select_for_update().filter(id=obj.product_id).first()
                if product is None:
                    return Response({'msg': '关联作品已不存在，无法通过审核'}, status=status.HTTP_400_BAD_REQUEST)
                if product.stock < obj.qty:
                    return Response(
                        {'msg': f'库存不足（当前 {product.stock} 件），请先补货再通过审核'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                product.stock -= obj.qty
                product.save(update_fields=['stock'])
                ProductStockRecord.objects.create(
                    product=product, product_name=product.name, type='order', qty=obj.qty,
                    note='订单审核通过销售出库', operator=request.user.name or request.user.username, time=_now(),
                )
            obj.status = 'paid'
            if not obj.pay_time:
                obj.pay_time = _now()
            obj.review_comment = ''
        else:
            obj.status = 'rejected'
            obj.review_comment = comment or '订单信息不完整，予以驳回'
        obj.save()
        obj.log_status(obj.status, operator=_who(request),
                       note=('审核通过，待发货' if action == 'approve' else f'审核驳回：{obj.review_comment}'),
                       from_status=prev)
        write_log(request, 'review', '订单审核',
                  f'{"通过" if action == "approve" else "驳回"}订单 {obj.order_no}'
                  + (f'，原因：{comment}' if action == 'reject' else ''))
        return Response(OrderSerializer(obj).data)

    @action(detail=False, methods=['post'])
    def manual_create(self, request):
        """管理员手动录入订单，录入后状态为“待审核”，需再走审核流程。

        URL: POST /api/orders/manual_create/
        权限: 仅管理员（role=admin）可调用。
        参数: 可选 product_id 关联作品，或直接填写 item_name、price 等线下订单信息。
        返回: 201 及新建订单数据。
        """
        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可手动录入订单'}, status=status.HTTP_403_FORBIDDEN)
        s = OrderManualSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        now = _now()
        # 两种录入方式：关联作品时商品信息与卖家由作品带出；否则按纯文本录入
        if d.get('product_id'):
            product = Product.objects.filter(id=d['product_id']).first()
            if product is None or not product.saleable:
                return Response({'msg': '所选作品不存在或不可售'}, status=status.HTTP_400_BAD_REQUEST)
            qty = d.get('qty') or 1
            item_name = product.name
            glyph = product.glyph or '盏'
            price = product.price * qty
            seller = product.owner
            product_id = product.id
            typ = 'product'
        else:
            item_name = d.get('item_name') or ''
            if not item_name.strip():
                return Response({'msg': '请选择订购作品或填写商品名称'}, status=status.HTTP_400_BAD_REQUEST)
            qty = d.get('qty') or 1
            glyph = (d.get('type') == 'course') and '课' or '盏'
            price = d.get('price') or 0
            seller = None
            product_id = 0
            typ = d.get('type') or 'product'

        # 手动录入订单一律以 review 起步，由审核环节决定通过或驳回
        order = Order.objects.create(
            type=typ, item_name=item_name, glyph=glyph,
            buyer=d.get('buyer', ''), buyer_phone=d.get('buyer_phone', ''),
            seller=seller, price=price,
            status='review',
            source='manual',
            product_id=product_id, qty=qty,
            pay_method=d.get('pay_method') or '',
            order_time=now,
            receiver=d.get('receiver', ''), address=d.get('address', ''),
            phone=d.get('phone', ''), remark=d.get('remark', ''),
        )
        order.log_status('review', operator=_who(request), note='管理员手动录入，待审核', from_status='')
        write_log(request, 'create', '手动录入订单',
                  f'订单 {order.order_no}「{order.item_name}」×{qty} 已录入，待审核')
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """订单发货：写入物流公司与单号，状态由“待发货”流转为“已发货”。

        URL: POST /api/orders/{id}/ship/
        权限: 管理员或传承人（role=admin/heritage）可调用。
        参数: company、tracking_no，均不允许为空。
        返回: 发货后的订单数据；课程订单或状态不符时返回 400。
        """
        obj = self.get_object()
        # 角色校验：学员不能自行发货
        if request.user.role not in ('admin', 'heritage'):
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        # 课程订单无实物，不需要物流发货
        if obj.type != 'product':
            return Response({'msg': '课程订单无需物流发货'}, status=status.HTTP_400_BAD_REQUEST)
        if obj.status != 'paid':
            return Response({'msg': '当前状态不可发货'}, status=status.HTTP_400_BAD_REQUEST)
        s = OrderShipSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj.status = 'shipped'
        obj.company = s.validated_data['company']
        obj.tracking_no = s.validated_data['tracking_no']
        obj.ship_time = _now()
        obj.save()
        obj.log_status('shipped', operator=_who(request),
                       note=f'发货：{obj.company} {obj.tracking_no}')
        write_log(request, 'ship', '订单发货',
                  f'订单 {obj.order_no} 已发货（{obj.company} {obj.tracking_no}）')
        return Response(OrderSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """确认收货：将已发货订单标记为“已完成”。

        URL: POST /api/orders/{id}/complete/
        权限: 学员只能确认自己名下的订单，管理员与传承人可代为标记。
        返回: 完成后的订单数据。
        """
        obj = self.get_object()
        if obj.status != 'shipped':
            return Response({'msg': '当前状态不可标记完成'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        # 学员只能确认收货自己的订单；其他角色中仅管理员、传承人可操作
        if user.role == 'user':
            if obj.buyer_user_id != user.id:
                return Response({'msg': '只能确认收货自己的订单'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role not in ('admin', 'heritage'):
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        obj.status = 'done'
        obj.save()
        obj.log_status('done', operator=_who(request),
                       note='用户确认收货' if user.role == 'user' else '管理员/传承人标记完成')
        write_log(request, 'order', '订单完成', f'订单 {obj.order_no}「{obj.item_name}」已完成')
        return Response(OrderSerializer(obj).data)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单：已支付的作品订单会把库存退回。

        URL: POST /api/orders/{id}/cancel/
        权限: 学员仅能取消本人订单，管理员可取消任意订单；传承人无权取消。
        返回: 取消后的订单数据；已发货/已完成等状态不可取消。
        """
        obj = self.get_object()
        # 只有未发货前的订单可取消，已发货、已完成、已驳回等状态不再允许
        if obj.status not in ('review', 'pending', 'paid'):
            return Response({'msg': '当前状态不可取消'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        # 权限校验：学员限本人订单，管理员不限，其他角色拒绝
        if user.role == 'user':
            if obj.buyer_user_id != user.id:
                return Response({'msg': '只能取消自己的订单'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role != 'admin':
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        # 已支付订单取消时需要回滚库存：加锁后加回数量并写入入库流水
        if obj.status == 'paid' and obj.type == 'product' and obj.product_id and obj.qty:
            product = Product.objects.select_for_update().filter(id=obj.product_id).first()
            if product:
                product.stock += obj.qty
                product.save(update_fields=['stock'])
                ProductStockRecord.objects.create(
                    product=product, product_name=product.name, type='in', qty=obj.qty,
                    note='订单取消，已支付库存退回', operator=user.name or user.username, time=_now(),
                )
        prev = obj.status
        obj.status = 'cancelled'
        obj.review_comment = '订单已取消' if not obj.review_comment else obj.review_comment
        obj.save()
        obj.log_status('cancelled', operator=_who(request),
                       note='用户取消订单' if user.role == 'user' else '管理员取消订单', from_status=prev)
        write_log(request, 'order', '取消订单', f'订单 {obj.order_no}「{obj.item_name}」已取消')
        return Response(OrderSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """管理员手动切换订单状态，并按目标状态自动调整库存。

        URL: POST /api/orders/{id}/set_status/
        权限: 仅管理员（role=admin）可调用。
        参数: status 目标状态码，note 可选备注。
        返回: 调整后的订单数据；目标状态与当前相同或库存不足时返回 400。
        """
        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可手动切换订单状态'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        s = OrderStatusSetSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        target = s.validated_data['status']
        note = (s.validated_data.get('note') or '').strip()
        prev = obj.status
        if target == prev:
            return Response({'msg': '订单已处于该状态'}, status=status.HTTP_400_BAD_REQUEST)

        # 库存是否已被该订单占用：paid/shipped/done 视为已占库存，其余状态视为未占库存。
        # 仅当“原状态占用情况”与“目标状态占用情况”不同时，才需要扣减或退回库存。
        stock_held = prev in ('paid', 'shipped', 'done')
        stock_wanted = target in ('paid', 'shipped', 'done')
        if obj.type == 'product' and obj.product_id and obj.qty and stock_held != stock_wanted:
            product = Product.objects.select_for_update().filter(id=obj.product_id).first()
            if product is not None:
                if stock_wanted:
                    # 从未占用变为占用：先校验库存再扣减
                    if product.stock < obj.qty:
                        return Response(
                            {'msg': f'库存不足（当前 {product.stock} 件），无法切换到该状态'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    product.stock -= obj.qty
                    note_flow = '订单状态变更，扣减库存'
                    rec_type = 'order'
                else:
                    # 从占用变为不占用（如退回待付款/取消）：库存加回
                    product.stock += obj.qty
                    note_flow = '订单状态变更，退回库存'
                    rec_type = 'in'
                product.save(update_fields=['stock'])
                ProductStockRecord.objects.create(
                    product=product, product_name=product.name, type=rec_type, qty=obj.qty,
                    note=note_flow, operator=_who(request), time=_now(),
                )
        obj.status = target
        obj.save(update_fields=['status'])
        obj.log_status(target, operator=_who(request), note=note or '管理员手动调整状态', from_status=prev)
        # 日志中用中文状态名展示，比原始状态码更易读
        labels = dict(Order.STATUS_CHOICES)
        write_log(request, 'order', '订单状态调整',
                  f'订单 {obj.order_no} 由「{labels.get(prev, prev)}」改为「{labels.get(target, target)}」'
                  + (f'，备注：{note}' if note else ''))
        return Response(OrderSerializer(obj).data)


class AddressViewSet(viewsets.ModelViewSet):
    """收货地址视图集：普通用户对自己地址的增删改查，并自动维护唯一默认地址。

    路由前缀为 /api/orders/addresses/，全部接口要求登录且仅限普通用户（role=user）。
    """

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def _check_user(self, request):
        """内部权限校验：非普通用户直接抛出 403，防止越权维护地址。

        参数:
            request: 当前请求对象。
        """
        if getattr(request.user, 'role', None) != 'user':
            raise PermissionDenied('仅普通用户可管理收货地址')

    def get_queryset(self):
        """只返回当前登录用户自己的地址；其他角色返回空集，看不到任何地址数据。"""
        if getattr(self.request.user, 'role', None) != 'user':
            return Address.objects.none()
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """新增地址：归属强制绑定当前用户，并保证同一用户默认地址唯一。

        参数:
            serializer: 已校验的地址序列化器。
        """
        self._check_user(self.request)
        user = self.request.user
        addr = serializer.save(user=user)
        # 新增地址被设为默认时，取消其他地址的默认标记
        if addr.is_default:
            Address.objects.filter(user=user).exclude(pk=addr.pk).update(is_default=False)
        # 用户还没有任何默认地址时，把这条自动设为默认
        elif not Address.objects.filter(user=user, is_default=True).exclude(pk=addr.pk).exists():
            addr.is_default = True
            addr.save(update_fields=['is_default'])

    def perform_update(self, serializer):
        """修改地址：同样维护默认地址唯一性，且只允许操作自己的地址。

        参数:
            serializer: 已校验的地址序列化器。
        """
        self._check_user(self.request)
        user = self.request.user
        addr = serializer.save()
        # 设为默认时清除其他地址的默认标记
        if addr.is_default:
            Address.objects.filter(user=user).exclude(pk=addr.pk).update(is_default=False)
        # 更新后若该用户已无默认地址，则将当前地址补为默认
        elif not Address.objects.filter(user=user, is_default=True).exists():
            addr.is_default = True
            addr.save(update_fields=['is_default'])

    def perform_destroy(self, instance):
        """删除地址：若删除的是默认地址，则自动把剩余最新的一条设为默认。

        参数:
            instance: 待删除的地址对象。
        """
        self._check_user(self.request)
        user = instance.user
        was_default = instance.is_default
        super().perform_destroy(instance)
        # 删除默认地址后需要重新指定一条默认地址，避免下单时取不到默认收货信息
        if was_default:
            first = Address.objects.filter(user=user).order_by('-id').first()
            if first:
                first.is_default = True
                first.save(update_fields=['is_default'])
