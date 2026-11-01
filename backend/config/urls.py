"""
项目根路由模块：把前端请求按前缀分发到各业务应用的子路由。

同时注册 Django 后台入口、JWT 刷新接口，并在开发模式下提供媒体文件的访问路由。
新增业务模块时，需在此补充一行 include 前缀。
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

# 路由表：先由 Django 后台与各应用前缀匹配，未命中时再交给 JWT 刷新接口
urlpatterns = [
    # Django 自带后台管理站，供管理员维护数据
    path('admin/', admin.site.urls),

    # 各业务模块的子路由，统一以 /api/ 开头，具体路径由各应用内的 urls.py 决定
    path('api/accounts/', include('accounts.urls')),
    path('api/heritage/', include('heritage.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/students/', include('students.urls')),
    path('api/skills/', include('skills.urls')),
    path('api/products/', include('products.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/system/', include('system.urls')),

    # 用刷新令牌换取新的访问令牌，供前端在访问令牌过期后自动续期
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# 仅在调试模式下由 Django 直接托管上传文件；生产环境应交给 Nginx 等静态服务器处理
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
