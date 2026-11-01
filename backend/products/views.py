# products 应用的视图层（基于 DRF ViewSet）。
# 负责文创作品的增删改查、审核与提交、作品出入库、库存流水查询以及学员收藏接口，
# 同时在这里完成数据隔离（普通用户只看已通过作品）和角色权限控制。
# 所有路由由 products/urls.py 中的 DefaultRouter 自动生成，统一挂在 /api/products/ 下。

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction
from accounts.permissions import IsHeritageRole, IsStaffRole, OwnerOrAdminWrite
from common.logging import AutoLogMixin, write_log
from common.pagination import OptInPagination
from .models import Product, Favorite, ProductStockRecord
from .serializers import (
    ProductSerializer, ProductReviewSerializer, FavoriteSerializer,
    ProductStockRecordSerializer, ProductStockInOutSerializer,
)


def _now():
    """返回当前服务器本地时间的“年-月-日 时:分”字符串，用于写入库存流水的时间字段。"""
    from django.utils import timezone
    return timezone.localtime().strftime('%Y-%m-%d %H:%M')


class ProductViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """
    文创作品主接口，路由前缀 /api/products/products/。

    提供标准 CRUD（GET/POST/PUT/PATCH/DELETE），并额外提供：
    - GET  /api/products/products/filters/          作品筛选项（分类/技艺/传承人）
    - POST /api/products/products/{id}/review/      管理员审核作品
    - POST /api/products/products/{id}/submit/      提交作品进入待审核
    - POST /api/products/products/{id}/stock_in_out/ 作品入库/出库
    权限随 action 变化（见 get_permissions）；分页为按需分页（OptInPagination）。
    """

    auto_log_name = '作品'
    queryset = Product.objects.select_related('owner').all()
    serializer_class = ProductSerializer
    pagination_class = OptInPagination

    def get_permissions(self):
        """
        按当前 action 动态分配权限类，返回权限实例列表（DRF 会在请求前逐个校验）。

        列表/详情对匿名用户开放（AllowAny），新增要求员工角色，改删要求“员工+本人或管理员”，
        其余动作（审核、提交、出入库、筛选项）至少要求登录。
        """
        # 公开读：作品列表与详情允许匿名访问，便于未登录用户浏览
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        # 新增作品只允许管理员/员工角色
        if self.action == 'create':
            return [IsStaffRole()]
        # 修改与删除：先校验角色，再校验“本人或管理员”，防止越权改他人作品
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsStaffRole(), OwnerOrAdminWrite()]
        # 其余自定义动作（review/submit/stock_in_out/filters）默认要求登录
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        返回当前用户可见的作品查询集，并叠加 URL 查询参数过滤条件。

        数据隔离规则：传承人只能看到自己的作品；未登录用户与非管理员只能看到“已通过”的作品；
        管理员可看到全部。查询参数支持 status/craft/category/inheritor/price_min/price_max/
        stock_status/low_stock/saleable/keyword，返回过滤后的 QuerySet。
        """
        qs = super().get_queryset()
        user = self.request.user
        # 角色隔离：传承人只看自己的作品
        if user.is_authenticated and user.role == 'heritage':
            qs = qs.filter(owner=user)
        # 匿名用户或普通学员只返回已审核通过的作品
        elif not user.is_authenticated or user.role != 'admin':
            qs = qs.filter(status='approved')
        # 状态筛选仅对管理员和传承人开放，避免普通用户探测草稿/驳回数据
        status_q = self.request.query_params.get('status')
        if status_q and user.is_authenticated and user.role in ('admin', 'heritage'):
            qs = qs.filter(status=status_q)
        params = self.request.query_params
        # 下面三个为精确匹配的文本筛选（技艺/分类/传承人），空字符串视为不筛选
        craft_q = (params.get('craft') or '').strip()
        if craft_q:
            qs = qs.filter(craft=craft_q)
        category_q = (params.get('category') or '').strip()
        if category_q:
            qs = qs.filter(category=category_q)
        inheritor_q = (params.get('inheritor') or '').strip()
        if inheritor_q:
            qs = qs.filter(inheritor=inheritor_q)
        # 价格区间筛选：参数为非法数字时捕获异常并跳过，避免接口直接报 500
        price_min = (params.get('price_min') or '').strip()
        price_max = (params.get('price_max') or '').strip()
        try:
            if price_min:
                qs = qs.filter(price__gte=price_min)
            if price_max:
                qs = qs.filter(price__lte=price_max)
        except (ValueError, TypeError):
            pass
        # 库存状态筛选：in=有货、out=缺货、low=低于预警值（用 F 表达式在数据库侧比较字段）
        stock_q = (params.get('stock_status') or '').strip()
        from django.db.models import F, Q
        if stock_q == 'in':
            qs = qs.filter(stock__gt=0)
        elif stock_q == 'out':
            qs = qs.filter(stock=0)
        elif stock_q == 'low':
            qs = qs.filter(stock__lte=F('alert_threshold'))
        # low_stock=1 是给管理端用的库存预警快捷开关，同样只对管理员/传承人生效
        low = params.get('low_stock')
        if low in ('1', 'true', 'True') and user.is_authenticated and user.role in ('admin', 'heritage'):
            qs = qs.filter(stock__lte=F('alert_threshold'))
        # 是否可售筛选：'1'→可售，'0'→不可售
        saleable_q = (params.get('saleable') or '').strip()
        if saleable_q in ('0', '1'):
            qs = qs.filter(saleable=(saleable_q == '1'))
        # 关键词模糊搜索：同时匹配名称、传承人、技艺、分类、材质，用 OR 组合
        kw = (params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(name__icontains=kw) | Q(inheritor__icontains=kw) | Q(craft__icontains=kw)
                | Q(category__icontains=kw) | Q(material__icontains=kw)
            )
        return qs

    @action(detail=False, methods=['get'])
    def filters(self, request):
        """
        作品筛选项接口：GET /api/products/products/filters/。

        与列表接口保持同样的数据隔离逻辑（传承人只看自己、普通用户只看已通过、管理员看全部），
        返回 {'category': [...], 'craft': [...], 'inheritor': [...]} 三个去重排序后的候选项，
        供前端筛选下拉框使用。
        """
        base = Product.objects.all()
        user = request.user
        # 复用与 get_queryset 一致的数据隔离规则，保证筛选项不会泄露不可见作品的信息
        if user.is_authenticated and getattr(user, 'role', None) == 'heritage':
            base = base.filter(owner=user)
        elif not user.is_authenticated or getattr(user, 'role', None) != 'admin':
            base = base.filter(status='approved')

        def distinct(field):
            """取出某字段的去重非空值（去首尾空格）并排序，返回字符串列表。"""
            vals = base.values_list(field, flat=True)
            return sorted({(v or '').strip() for v in vals if (v or '').strip()})
        return Response({
            'category': distinct('category'),
            'craft': distinct('craft'),
            'inheritor': distinct('inheritor'),
        })

    def _resolve_owner(self):
        """
        计算新作品的归属账号。

        管理员代建作品时按请求体中的 inheritor（传承人姓名）反查其账号，查不到返回 None；
        非管理员（传承人本人）直接返回当前登录用户。
        """
        user = self.request.user
        if getattr(user, 'role', None) != 'admin':
            return user
        profile = self._profile_by_name(self.request.data.get('inheritor'))
        return profile.account if (profile and profile.account_id) else None

    def _profile_by_name(self, name):
        """
        按传承人姓名查找唯一的传承人档案。

        参数 name：姓名，允许为空或带空格。返回匹配的 HeritageProfile 实例；
        为空、无匹配或重名（命中多条）时返回 None，避免把作品挂到错误的人名下。
        """
        from heritage.models import HeritageProfile
        name = (name or '').strip()
        if not name:
            return None
        hits = list(HeritageProfile.objects.select_related('account').filter(name=name))
        return hits[0] if len(hits) == 1 else None

    def _default_author(self, owner):
        """推断作品作者名：优先取归属账号的姓名，其次是传承人本人的姓名/用户名，返回字符串。"""
        name = (getattr(owner, 'name', '') or '').strip()
        if name:
            return name
        user = self.request.user
        if getattr(user, 'role', None) == 'heritage':
            return (getattr(user, 'name', '') or getattr(user, 'username', '') or '').strip()
        return ''

    def _default_level(self, author, owner):
        """推断传承等级：优先取该传承人档案中的 level，其次取归属账号的 level，返回字符串。"""
        profile = self._profile_by_name(author)
        if profile and profile.level:
            return profile.level
        return (getattr(owner, 'level', '') or '').strip()

    def perform_create(self, serializer):
        """
        新增作品时的补充逻辑（POST /api/products/products/）。

        在保存前确定归属账号，并用“请求字段 → 默认推断”的顺序补全作者与传承等级，
        保存成功后写入一条新增操作日志。参数 serializer 为已完成校验的序列化器。
        """
        owner = self._resolve_owner()
        data = self.request.data
        author = (data.get('inheritor') or '').strip() or self._default_author(owner)
        level = (data.get('level') or '').strip() or self._default_level(author, owner)
        # owner/inheritor/level 由后端计算后写入，前端传的值会被这里的默认值兜底
        serializer.save(owner=owner, inheritor=author, level=level)
        self._log_obj(self.request, 'create', '新增', serializer.instance)

    def perform_update(self, serializer):
        """
        修改作品时的补充逻辑（PUT/PATCH /api/products/products/{id}/）。

        若前端显式把 inheritor 置空，则回退为原作者名或归属账号姓名，避免作者字段丢失，
        保存成功后写入一条修改操作日志。
        """
        data = self.request.data
        # 显式提交空作者时才回填，防止误清空；未提交该字段则按原样保存
        if 'inheritor' in data and not (data.get('inheritor') or '').strip():
            inst = serializer.instance
            fallback = (inst.inheritor or '').strip() or self._default_author(inst.owner)
            serializer.save(inheritor=fallback)
        else:
            serializer.save()
        self._log_obj(self.request, 'update', '修改', serializer.instance)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        作品审核接口：POST /api/products/products/{id}/review/。

        仅管理员可调用。请求体经 ProductReviewSerializer 校验，action 取 approve/reject；
        通过则状态置为 approved 并清空审核意见，驳回则置为 rejected 并必须填写原因。
        返回审核后的作品数据。
        """
        # 权限二次校验：非管理员直接 403（get_permissions 只保证已登录）
        if request.user.role != 'admin':
            return Response({'msg': '无权审核'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        s = ProductReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        action = s.validated_data['action']
        comment = (s.validated_data.get('review_comment') or '').strip()
        # 驳回必须说明原因，方便传承人修改后重新提交
        if action == 'reject' and not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        # 审核状态流转：approve → 已通过并清空意见；reject → 已驳回并记录原因
        if action == 'approve':
            obj.status = 'approved'
            obj.review_comment = ''
        else:
            obj.status = 'rejected'
            obj.review_comment = comment
        obj.save()
        write_log(
            request, 'review', '作品审核',
            f'{"通过" if action == "approve" else "驳回"}作品「{obj.name}」'
            + (f'，原因：{comment}' if comment else ''),
        )
        return Response(ProductSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交审核接口：POST /api/products/products/{id}/submit/。

        要求登录；仅作品归属人本人或管理员可提交。把作品状态统一改为 pending（待审核），
        写入操作日志并返回更新后的作品数据。
        """
        obj = self.get_object()
        # 归属校验：非本人且非管理员不允许提交他人作品
        if obj.owner_id != request.user.id and request.user.role != 'admin':
            return Response({'msg': '只能提交自己的作品'}, status=status.HTTP_403_FORBIDDEN)
        # 状态流转：任意状态提交后统一进入待审核队列，由管理员在 review 接口处理
        obj.status = 'pending'
        obj.save()
        write_log(request, 'review', '提交作品审核', f'提交作品「{obj.name}」待审核')
        return Response(ProductSerializer(obj).data)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def stock_in_out(self, request, pk=None):
        """
        作品出入库接口：POST /api/products/products/{id}/stock_in_out/。

        仅管理员与传承人可操作。请求体经 ProductStockInOutSerializer 校验，
        type 取 in/out/order/loss，qty 为正整数；会校验出库库存是否充足，
        然后更新作品库存并新增一条库存流水，返回更新后的作品数据。
        整个过程包在事务中，保证“改库存”和“写流水”同时成功或同时回滚。
        """
        # 角色校验：学员账号无权改动库存
        if request.user.role not in ('admin', 'heritage'):
            return Response({'msg': '无权操作作品库存'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object()
        s = ProductStockInOutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        typ = s.validated_data['type']
        qty = s.validated_data['qty']
        note = s.validated_data.get('note', '')

        # 出库类操作（手工出库/销售/损耗）先校验库存，库存不足直接拒绝，避免出现负库存
        if typ in ('out', 'order', 'loss') and product.stock < qty:
            return Response(
                {'msg': f'库存不足（当前 {product.stock}）'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 方向换算：入库加数量，其余类型减数量
        delta = qty if typ == 'in' else -qty
        product.stock += delta
        product.save(update_fields=['stock'])
        # 记录流水：冗余保存作品名与操作人，便于后续按流水对账和追溯
        ProductStockRecord.objects.create(
            product=product, product_name=product.name, type=typ, qty=qty,
            note=note, operator=request.user.name or request.user.username, time=_now(),
        )
        write_log(
            request, 'update', '作品出入库',
            f'{s.validated_data.get("type")}作品「{product.name}」{qty} 件，当前库存 {product.stock}',
        )
        return Response(ProductSerializer(product).data)


class ProductStockRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    库存流水只读接口，路由前缀 /api/products/stock-records/。

    仅支持 GET（列表/详情），要求登录。传承人只能看到自己作品的流水，
    并支持通过查询参数 product_id 按作品过滤；分页为按需分页。
    """

    queryset = ProductStockRecord.objects.all()
    serializer_class = ProductStockRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_queryset(self):
        """
        返回当前用户可查看的库存流水，并支持按 product_id 过滤。

        传承人仅能查看自己名下作品的流水；管理员与普通学员不受此限制。
        返回过滤后的 QuerySet。
        """
        qs = super().get_queryset()
        user = self.request.user
        # 数据隔离：按流水的 product 反查作品归属，限制传承人只能看自己的
        if user.is_authenticated and user.role == 'heritage':
            qs = qs.filter(product__owner=user)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    学员收藏接口，路由前缀 /api/products/favorites/。

    要求登录，且仅 role 为 user（学员）的账号可收藏。提供：
    - GET  /api/products/favorites/                  我的收藏列表
    - POST /api/products/favorites/                  添加收藏（幂等）
    - DELETE /api/products/favorites/{id}/           删除收藏
    - DELETE /api/products/favorites/remove/?product_id=  按作品取消收藏
    - GET  /api/products/favorites/check/?product_id=     查询是否已收藏
    为避免越权，查询集始终限定为当前登录学员自己的收藏。
    """

    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def _favorite_owner(self):
        """
        判断当前登录账号是否为可收藏的学员账号。

        是学员返回当前用户对象，否则（管理员/传承人等）返回 None，
        各动作据此统一拒绝非学员的收藏请求。
        """
        user = self.request.user
        if getattr(user, 'role', None) != 'user':
            return None
        return user

    def get_queryset(self):
        """返回当前登录学员自己的收藏列表（预取作品信息）；非学员返回空查询集。"""
        owner = self._favorite_owner()
        if owner is None:
            return Favorite.objects.none()
        return Favorite.objects.select_related('product').filter(user=owner)

    def create(self, request, *args, **kwargs):
        """
        添加收藏：POST /api/products/favorites/。

        请求体需带 product_id；作品不存在返回 404。使用 get_or_create 实现幂等，
        重复收藏不会报错，统一返回 201 与收藏数据。
        """
        if self._favorite_owner() is None:
            return Response({'msg': '仅学员账号可收藏'}, status=status.HTTP_403_FORBIDDEN)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'msg': '缺少 product_id'}, status=status.HTTP_400_BAD_REQUEST)
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'msg': '作品不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 幂等写入：已收藏则直接返回原记录，created 未被使用但保留元组解包
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        return Response(FavoriteSerializer(fav).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """
        取消收藏：DELETE /api/products/favorites/remove/?product_id=xxx。

        仅学员可调用；product_id 可放在查询参数或请求体中。删除后返回 {'msg': '已取消收藏'}，
        未收藏时同样返回成功，保证前端调用幂等。
        """
        owner = self._favorite_owner()
        if owner is None:
            return Response({'msg': '仅学员账号可收藏'}, status=status.HTTP_403_FORBIDDEN)
        # 兼容两种传参位置：查询参数优先，其次请求体
        product_id = request.query_params.get('product_id') or request.data.get('product_id')
        if not product_id:
            return Response({'msg': '缺少 product_id'}, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=owner, product_id=product_id).delete()
        return Response({'msg': '已取消收藏'})

    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        收藏状态查询：GET /api/products/favorites/check/?product_id=xxx。

        返回 {'favorited': true/false} 供前端显示收藏按钮状态；
        非学员账号直接返回 false，缺少 product_id 返回 400。
        """
        owner = self._favorite_owner()
        if owner is None:
            return Response({'favorited': False})
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'msg': '缺少 product_id'}, status=status.HTTP_400_BAD_REQUEST)
        # 只判断存在性，用 exists() 避免取出整行数据
        exists = Favorite.objects.filter(user=owner, product_id=product_id).exists()
        return Response({'favorited': exists})
