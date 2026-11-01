"""技艺档案后台管理模块。

在 Django Admin 中注册 Skill 模型并配置列表展示、筛选、搜索与排序，
让管理员无需前端页面即可在后台维护技艺档案数据。
"""
from django.contrib import admin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """技艺档案的后台管理配置类。

    列表页展示编号、名称、级别、分类、状态、传承人与提交时间，
    便于快速定位档案并查看审核进度；默认新档案在前。
    """

    # 列表页展示的列，覆盖识别档案与查看审核进度所需的最小信息
    list_display = ('id', 'name', 'level', 'category', 'status', 'owner', 'submit_time')
    # 右侧筛选器：按审核状态与技艺级别收窄列表
    list_filter = ('status', 'level')
    # 顶部搜索框：支持技艺名称与分类的模糊搜索
    search_fields = ('name', 'category')
    # 默认排序：-id 表示最近创建的档案排在最前
    ordering = ('-id',)
