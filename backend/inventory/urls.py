"""inventory 应用的路由配置：用 DefaultRouter 生成 RESTful 路由。

最终挂载在 /api/inventory/ 下，提供 materials、stock-records、shipments
三组资源的列表/详情接口，以及 ViewSet 中声明的自定义动作路由。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, StockRecordViewSet, ShipmentViewSet

router = DefaultRouter()
# 注册三个 ViewSet，自动生成列表、详情以及 stock_in_out、ship、sign 动作的 URL
router.register('materials', MaterialViewSet, basename='material')
router.register('stock-records', StockRecordViewSet, basename='stock-record')
router.register('shipments', ShipmentViewSet, basename='shipment')

urlpatterns = [
    path('', include(router.urls)),
]
