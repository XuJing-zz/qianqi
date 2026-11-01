"""
students 应用的路由配置。

用 DRF 的 DefaultRouter 注册学员与培训记录两个视图集，自动生成列表、
详情以及 mark_done/approve/reject/export 等自定义 action 的 URL，
再由 config/urls.py 挂载到 /api/students/ 前缀下。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, TrainingRecordViewSet

router = DefaultRouter()
# basename 用于生成 URL 名称，前端可通过路由名反向解析具体接口
router.register('students', StudentViewSet, basename='student')
router.register('training-records', TrainingRecordViewSet, basename='training-record')

urlpatterns = [
    # 把路由表生成的 URL 挂到 students 应用的根路径，全部由 config/urls.py 统一转发
    path('', include(router.urls)),
]
