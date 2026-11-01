"""
课程模块的路由配置。

通过 DRF DefaultRouter 注册 CourseViewSet，自动生成列表、详情以及
review/submit/offline/upload 等自定义 action 路由；由 config/urls.py
以 /api/courses/ 为前缀挂载。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

# DefaultRouter 会扫描视图集中的 @action 方法，自动补充对应的 URL
router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')

# 本模块对外暴露的全部路由均来自上面的 router
urlpatterns = [
    path('', include(router.urls)),
]
