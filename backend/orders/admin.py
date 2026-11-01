# 订单模块 —— Django 后台管理配置
# 负责在 /admin 后台中注册订单模型，并配置列表展示字段、筛选器与搜索条件。

from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """订单后台管理：展示订单核心信息，支持按类型/状态筛选和商品名、买家搜索。"""

    # 列表页展示的列，可直观看到订单状态与物流信息
    list_display = ('id', 'type', 'item_name', 'buyer', 'price', 'status', 'company', 'tracking_no', 'order_time')
    # 右侧筛选器：按订单类型与状态快速过滤
    list_filter = ('type', 'status')
    # 顶部搜索框支持的模糊搜索字段
    search_fields = ('item_name', 'buyer')
    # 默认按主键倒序，新订单排在最前面
    ordering = ('-id',)
