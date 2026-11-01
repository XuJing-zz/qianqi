"""技艺档案路由模块。

用 DRF 的 DefaultRouter 把 SkillViewSet 注册为 skills 资源，自动生成列表、详情
以及 filters/upload/review 等自定义动作的路由，最终由 config/urls.py 以
/api/skills/ 前缀挂载，形成 /api/skills/skills/... 形式的接口地址。
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SkillViewSet

# 注册资源名 skills：Router 会为视图集生成标准 CRUD 路由与 @action 附加路由
router = DefaultRouter()
# basename 用于生成 URL 反向解析名（如 skill-list、skill-detail）
router.register('skills', SkillViewSet, basename='skill')

# 空路径 include 路由表，实际前缀由父级 urls.py 决定
urlpatterns = [
    path('', include(router.urls)),
]
