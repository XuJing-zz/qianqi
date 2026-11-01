# system/admin.py —— 系统管理模块的 Django 后台注册
# 把操作日志和系统配置注册到 admin 后台，并配置列表列、筛选、搜索和排序方式。
# 留言数据通过自定义接口管理，因此这里未注册 FeedbackMessage。

from django.contrib import admin
from .models import OperationLog, SystemConfig


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志后台管理：以表格形式浏览日志，支持按类型筛选和按人/操作搜索。"""

    # 列表页展示的列，控制信息密度，详情内容不在此展示
    list_display = ('id', 'type', 'operator', 'action', 'time')

    # 右侧按日志类型筛选，方便只看登录、删除等某类操作
    list_filter = ('type',)

    # 顶部搜索框匹配操作人和操作描述
    search_fields = ('operator', 'action')

    # 新增的在最前，便于查看最近操作
    ordering = ('-id',)


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """系统配置后台管理：查看和直接编辑 JSON 配置内容。"""

    list_display = ('key', 'updated_at')

    # 按配置键字母序排，配置项较少时定位更直观
    ordering = ('key',)
