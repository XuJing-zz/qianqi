"""inventory 应用的接口视图：物料、出入库流水与材料邮寄单的 REST API。

MaterialViewSet 提供物料增删改查与出入库动作；StockRecordViewSet 只读查询流水；
ShipmentViewSet 负责邮寄单管理以及发货、签收两个状态流转动作。
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from accounts.permissions import IsAdminRole, IsStaffRole
from common.logging import AutoLogMixin, write_log
from common.pagination import OptInPagination
from .models import Material, StockRecord, Shipment
from .serializers import (
    MaterialSerializer, StockRecordSerializer, ShipmentSerializer,
    StockInOutSerializer, ShipOutSerializer,
)


def _now():
    """返回本地时区的当前时间，格式为 YYYY-MM-DD HH:MM。

    无参数；返回 str，用于流水与邮寄单中展示用的时间字段。
    """
    from django.utils import timezone
    return timezone.localtime().strftime('%Y-%m-%d %H:%M')


class MaterialViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """物料接口：/api/inventory/materials/ 下的增删改查与出入库动作。

    GET 列表/详情登录即可访问；POST/PUT/PATCH/DELETE 仅管理员可用。
    自定义动作 POST /api/inventory/materials/{id}/stock_in_out/ 仅管理员，
    列表支持 course_id、type、keyword 过滤，带 page 或 page_size 参数时分页。
    """

    auto_log_name = '物料'
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_permissions(self):
        """按当前 action 动态选择权限类。

        写操作（create/update/partial_update/destroy）要求管理员角色，
        其余动作仅要求登录；返回权限类实例列表。
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """返回物料查询集，并按请求参数逐项过滤。

        支持 course_id（关联课程）、type（物料类型）、keyword（模糊匹配
        名称/规格/关联课程名）；返回过滤后的 QuerySet。
        """
        qs = super().get_queryset()
        # 按关联课程精确过滤
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(linked_course_id=course_id)
        # 按物料类型（基础材料/工具）精确过滤
        type_q = self.request.query_params.get('type')
        if type_q:
            qs = qs.filter(type=type_q)
        # 关键字在名称、规格、关联课程名中做不区分大小写的模糊匹配
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(name__icontains=kw) | Q(spec__icontains=kw) | Q(linked_course_name__icontains=kw)
            )
        return qs

    @action(detail=True, methods=['post'])
    def stock_in_out(self, request, pk=None):
        """物料出入库：POST /api/inventory/materials/{id}/stock_in_out/。

        仅管理员可操作；请求体包含 type（in/out/loss）、qty、note。
        先校验库存是否充足，再更新物料库存并写入流水与操作日志，
        返回更新后的物料数据。
        """
        # 权限：自定义动作不走 get_permissions，这里二次校验角色
        if request.user.role != 'admin':
            return Response({'msg': '无权操作库存'}, status=status.HTTP_403_FORBIDDEN)
        material = self.get_object()
        s = StockInOutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        typ = s.validated_data['type']
        qty = s.validated_data['qty']
        note = s.validated_data.get('note', '')

        # 出库和损耗都会减少库存，数量不足时直接返回 400
        if typ in ('out', 'loss') and material.stock < qty:
            return Response({'msg': f'库存不足（当前 {material.stock}）'}, status=status.HTTP_400_BAD_REQUEST)

        # 入库记正数，出库/损耗记负数
        delta = qty if typ == 'in' else -qty
        material.stock += delta
        material.save()
        # 流水冗余保存物料名与操作人，避免列表查询时再关联物料表
        StockRecord.objects.create(
            material=material, material_name=material.name, type=typ, qty=qty,
            note=note, operator=request.user.name or request.user.username, time=_now(),
        )
        write_log(request, 'update', '物料出入库',
                  f'{s.validated_data.get("type")}物料「{material.name}」{qty}，当前库存 {material.stock}')
        return Response(MaterialSerializer(material).data)


class StockRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """出入库流水接口：/api/inventory/stock-records/ 的只读查询。

    仅提供 GET 列表/详情，登录即可访问；支持 material_id、type、keyword
    过滤，带 page 或 page_size 参数时启用分页。
    """

    queryset = StockRecord.objects.all()
    serializer_class = StockRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_queryset(self):
        """返回流水查询集，并按请求参数过滤。

        支持 material_id（关联物料）、type（流水类型）、keyword（模糊匹配
        物料名/操作人/备注）；返回过滤后的 QuerySet。
        """
        qs = super().get_queryset()
        # 按关联物料 ID 过滤某物料的流水
        material_id = self.request.query_params.get('material_id')
        if material_id:
            qs = qs.filter(material_id=material_id)
        # 按流水类型（入库/领用出库/损耗）精确过滤
        type_q = self.request.query_params.get('type')
        if type_q:
            qs = qs.filter(type=type_q)
        # 关键字在物料名、操作人、备注中模糊匹配
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(material_name__icontains=kw) | Q(operator__icontains=kw) | Q(note__icontains=kw)
            )
        return qs


class ShipmentViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """材料邮寄单接口：/api/inventory/shipments/ 的管理与状态流转。

    GET 列表/详情登录即可访问；写操作以及 ship、sign 动作要求管理员或
    传承人角色。列表支持 status、keyword 过滤，带 page 或 page_size 参数时分页。
    """

    auto_log_name = '材料邮寄单'
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_permissions(self):
        """按当前 action 动态选择权限类。

        新增、修改、删除以及 ship/sign 动作要求管理员或传承人，
        其余动作仅要求登录；返回权限类实例列表。
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'ship', 'sign'):
            return [IsStaffRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """返回邮寄单查询集，并按请求参数过滤。

        支持 status（邮寄状态）、keyword（模糊匹配学员名/课程名/快递公司/
        快递单号）；返回过滤后的 QuerySet。
        """
        qs = super().get_queryset()
        # 按邮寄状态过滤：待寄/已寄/已签收
        status_q = self.request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        # 关键字在学员、课程、快递公司、快递单号中模糊匹配
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(student_name__icontains=kw) | Q(course_name__icontains=kw)
                | Q(company__icontains=kw) | Q(tracking_no__icontains=kw)
            )
        return qs

    # 库存扣减与单据状态更新必须同时成功，因此放在同一事务中
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货：POST /api/inventory/shipments/{id}/ship/。

        要求管理员或传承人角色；请求体包含 company（快递公司）、
        tracking_no（快递单号）。仅“待寄”状态可发货：事务内先整体校验
        物料库存，再扣减库存并更新为“已寄”，返回更新后的邮寄单。
        """
        shipment = self.get_object()
        # 状态校验：只有待寄的单据才能发货，避免重复扣减库存
        if shipment.status != 'pending':
            return Response({'msg': '当前状态不可发货'}, status=status.HTTP_400_BAD_REQUEST)
        s = ShipOutSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        # 第一轮只校验库存，保证所有物料都充足后再统一扣减
        for it in shipment.items or []:
            mat = Material.objects.filter(id=it.get('materialId')).first()
            if not mat or mat.stock < it.get('qty', 1):
                return Response(
                    {'msg': f'库存不足：{it.get("materialName", "物料")}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # 第二轮执行扣减：数量缺省为 1，物料已删除时跳过
        for it in shipment.items or []:
            mat = Material.objects.filter(id=it.get('materialId')).first()
            if mat:
                mat.stock -= it.get('qty', 1)
                mat.save()

        # 记录快递信息并推进状态：待寄 → 已寄
        shipment.company = s.validated_data['company']
        shipment.tracking_no = s.validated_data['tracking_no']
        shipment.status = 'shipped'
        shipment.ship_time = _now()
        shipment.save()
        write_log(request, 'ship', '材料包邮寄',
                  f'学员「{shipment.student_name}」材料包已寄出（{shipment.company} {shipment.tracking_no}）')
        return Response(ShipmentSerializer(shipment).data)

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """签收：POST /api/inventory/shipments/{id}/sign/。

        要求管理员或传承人角色；无请求体，直接把邮寄单状态置为“已签收”
        并写入操作日志，返回更新后的邮寄单。
        """
        shipment = self.get_object()
        # 更新状态为已签收并保存（代码未校验前置状态）
        shipment.status = 'signed'
        shipment.save()
        write_log(request, 'update', '材料包签收', f'学员「{shipment.student_name}」材料包已签收')
        return Response(ShipmentSerializer(shipment).data)
