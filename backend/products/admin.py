# products 应用的 Django 后台管理配置。
# 在 Django Admin 中注册作品与库存流水两个模型，并定制列表展示字段、
# 过滤条件与搜索字段，方便管理员在后台直接维护数据。

from django.contrib import admin
from .models import Product, ProductStockRecord


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """作品的后台管理类：配置列表展示列、筛选条件、搜索字段与排序方式。"""

    # 列表页展示列：包含价格、成本、库存与预警值，便于后台快速核对经营数据
    list_display = ('id', 'name', 'craft', 'status', 'saleable', 'price', 'cost_price', 'stock', 'alert_threshold', 'owner')
    # 右侧筛选器：按审核状态、技艺和是否可售过滤
    list_filter = ('status', 'craft', 'saleable')
    # 顶部搜索框：按作品名和技艺模糊搜索
    search_fields = ('name', 'craft')
    ordering = ('-id',)


@admin.register(ProductStockRecord)
class ProductStockRecordAdmin(admin.ModelAdmin):
    """库存流水的后台管理类：配置流水列表展示列、筛选条件、搜索字段与排序方式。"""

    # 列表页展示列：作品名、流水类型、数量、操作人与时间，方便逐条对账
    list_display = ('id', 'product_name', 'type', 'qty', 'operator', 'time')
    # 右侧筛选器：按流水类型（入库/出库/销售/损耗）过滤
    list_filter = ('type',)
    # 顶部搜索框：按作品名和操作人搜索
    search_fields = ('product_name', 'operator')
    ordering = ('-id',)
