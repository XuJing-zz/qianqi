# products 应用的路由配置。
# 使用 DRF 的 DefaultRouter 根据 ViewSet 自动生成列表、详情与 @action 自定义动作的 URL，
# 再由 config/urls.py 统一挂载到 /api/products/ 前缀下，供前端调用。

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, FavoriteViewSet, ProductStockRecordViewSet

router = DefaultRouter()
# 作品路由：/api/products/products/，并自动生成 filters、review、submit、stock_in_out 等子路径
router.register('products', ProductViewSet, basename='product')
# 收藏路由：/api/products/favorites/，含 remove 与 check 两个自定义动作
router.register('favorites', FavoriteViewSet, basename='favorite')
# 库存流水路由：/api/products/stock-records/，只读接口，由 ViewSet 自动生成
router.register('stock-records', ProductStockRecordViewSet, basename='product-stock-record')

urlpatterns = [
    # 把 Router 生成的 URL 列表并入本应用，交给上级路由按 /api/products/ 前缀分发
    path('', include(router.urls)),
]
