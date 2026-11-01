"""inventory 应用的 Django Admin 配置：注册物料、流水、邮寄单三个模型。

为每个模型设置后台列表展示字段、过滤器与搜索字段，
方便管理员直接维护库存数据，作为接口之外的后台管理入口。
"""
from django.contrib import admin
from .models import Material, StockRecord, Shipment


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """物料后台管理：列表展示名称、类型、库存与告警阈值，可按类型筛选。"""

    list_display = ('id', 'name', 'type', 'stock', 'alert_threshold', 'linked_course_name')
    # 按物料类型过滤，便于区分基础材料与工具
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    """出入库流水后台管理：只读维护流水，可按类型筛选、按物料名搜索。"""

    list_display = ('id', 'material_name', 'type', 'qty', 'operator', 'time')
    # 按入库/领用出库/损耗过滤流水
    list_filter = ('type',)
    search_fields = ('material_name',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """材料邮寄单后台管理：展示学员、课程、状态与快递信息，可按状态筛选。"""

    list_display = ('id', 'student_name', 'course_name', 'status', 'company', 'tracking_no')
    # 按待寄/已寄/已签收过滤邮寄单
    list_filter = ('status',)
    search_fields = ('student_name', 'course_name')
