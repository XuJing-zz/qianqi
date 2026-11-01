"""Django 后台管理配置：把三张账号表注册进 admin 后台。

列表页、筛选项、搜索字段和表单分组统一放在 BaseAccountAdmin 中，
三个子类只负责注册，避免重复配置。
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Admin, Inheritor


class BaseAccountAdmin(UserAdmin):
    """账号后台管理基类，统一列表展示、筛选、搜索与表单字段分组。

    继承 Django 自带的 UserAdmin，保留分组、权限、密码修改等内置能力，
    子类只换模型即可复用。
    """

    # 列表页展示的列
    list_display = ('username', 'name', 'phone', 'email', 'status', 'created_at')
    # 右侧筛选器，按账号状态过滤
    list_filter = ('status',)
    # 顶部搜索框支持模糊匹配的字段
    search_fields = ('username', 'name', 'phone', 'email')
    # 默认排序：新注册的账号排在前面
    ordering = ('-created_at',)

    # 编辑页的字段分组；未列出的字段不会出现在表单中
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('基本信息', {'fields': ('name', 'phone', 'email')}),
        ('状态', {'fields': ('status', 'is_active')}),
        ('权限', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    # 新增页的字段分组，含两次密码确认
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'name', 'phone', 'email', 'status', 'is_staff'),
        }),
    )


@admin.register(User)
class UserAdmin(BaseAccountAdmin):
    """学员账号的后台管理入口，后台菜单名取自模型的 verbose_name。"""

    pass


@admin.register(Admin)
class AdminAdmin(BaseAccountAdmin):
    """管理员账号的后台管理入口。"""

    pass


@admin.register(Inheritor)
class InheritorAdmin(BaseAccountAdmin):
    """传承人账号的后台管理入口。"""

    pass
