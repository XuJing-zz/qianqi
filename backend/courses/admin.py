"""
课程模块的后台管理配置。

把 Course 模型注册到 Django Admin，并配置列表展示字段、筛选项与搜索字段，
便于管理员在后台查看和维护申报课程数据。
"""

from django.contrib import admin
from .models import Course


# 装饰器完成模型注册，等价于 admin.site.register(Course, CourseAdmin)
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    课程后台管理类，控制课程列表页的展示列、筛选器与搜索方式。
    """

    list_display = ('id', 'name', 'craft', 'status', 'enrolled', 'owner', 'submit_time')
    list_filter = ('status', 'craft')
    search_fields = ('name', 'craft')
    ordering = ('-id',)
