# heritage/urls.py —— 传承人档案模块的路由配置
# 用 DRF 的 DefaultRouter 把 HeritageProfileViewSet 注册成 profiles 资源，
# 由 config/urls.py 以 /api/heritage/ 前缀引入，最终地址形如 /api/heritage/profiles/。
# 本文件只做路由声明，不包含业务逻辑。

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HeritageProfileViewSet

# 路由器会根据视图集自动生成列表 / 详情路由，以及 @action 声明的自定义动作路由
router = DefaultRouter()
# 资源名 profiles 决定 URL 片段，basename 作为反向解析时的路由名前缀
router.register('profiles', HeritageProfileViewSet, basename='profile')

urlpatterns = [
    # 把路由器生成的全部路由并入本模块的 urlpatterns
    path('', include(router.urls)),
]
