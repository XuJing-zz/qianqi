"""账号模块路由表，整体挂载在 /api/accounts/ 前缀下。

把 URL 映射到 ViewSet 的具体 action；as_view 字典的键是 HTTP 方法，
值是对应的方法名，因此同一个 ViewSet 可以按需暴露不同方法。
"""
from django.urls import path
from .views import AuthViewSet, AccountManageViewSet

urlpatterns = [

    # 登录 / 注册 / 退出 / 当前用户 / 资料修改 -> AuthViewSet
    path('auth/', AuthViewSet.as_view({'post': 'login', 'get': 'me'}), name='auth'),
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/me/', AuthViewSet.as_view({'get': 'me'}), name='auth-me'),
    path('auth/update-profile/', AuthViewSet.as_view({'post': 'update_profile'}), name='auth-update-profile'),


    # 账号后台管理 -> AccountManageViewSet，均要求管理员身份
    path('admin/list/', AccountManageViewSet.as_view({'get': 'list_accounts'}), name='account-list'),
    path('admin/create/', AccountManageViewSet.as_view({'post': 'create_account'}), name='account-create'),
    path('admin/issue-inheritor/', AccountManageViewSet.as_view({'post': 'issue_inheritor'}), name='account-issue-inheritor'),
    path('admin/update-account/', AccountManageViewSet.as_view({'post': 'update_account'}), name='account-update'),
    path('admin/toggle-status/', AccountManageViewSet.as_view({'post': 'toggle_status'}), name='account-toggle-status'),
    path('admin/reset-password/', AccountManageViewSet.as_view({'post': 'reset_password'}), name='account-reset-password'),
    path('admin/delete-account/', AccountManageViewSet.as_view({'post': 'delete_account'}), name='account-delete'),
]
