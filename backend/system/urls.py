# system/urls.py —— 系统管理模块的路由配置
# 用 DRF 的 DefaultRouter 把三个 ViewSet 自动注册成资源路由，
# 最终挂载到 config/urls.py 的 /api/system/ 前缀下。

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationLogViewSet, SystemConfigViewSet, FeedbackMessageViewSet

# 路由器会自动生成列表、详情路由，并注册各 ViewSet 中 @action 声明的自定义接口
router = DefaultRouter()
# basename 用于反向解析路由名，如 log-list、log-export
router.register('logs', OperationLogViewSet, basename='log')
router.register('config', SystemConfigViewSet, basename='config')
router.register('messages', FeedbackMessageViewSet, basename='message')

# 把路由器生成的全部子路由统一交给上级 urls.py 的 include 处理
urlpatterns = [
    path('', include(router.urls)),
]
