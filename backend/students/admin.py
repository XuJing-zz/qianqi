"""students 应用的 Django 后台管理配置。

把学员报名与培训记录注册到 admin 后台，并配置列表展示列、
筛选条件、搜索字段与默认排序，方便管理员直接维护数据。
"""
from django.contrib import admin
from .models import Student, TrainingRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """学员报名后台管理：列表展示报名核心信息，支持按状态筛选和关键字搜索。"""

    list_display = ('id', 'name', 'course_name', 'teacher', 'status', 'progress', 'enroll_time')
    list_filter = ('status',)
    search_fields = ('name', 'course_name', 'teacher')
    # 与模型 Meta.ordering 保持一致：新报名记录排在最前
    ordering = ('-id',)


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    """培训记录后台管理：列表展示课程、授课人、时间与内容，可按授课人筛选。"""

    list_display = ('id', 'course_name', 'teacher', 'record_time', 'content')
    list_filter = ('teacher',)
    search_fields = ('course_name', 'teacher', 'content')
    # 最新的培训记录优先展示
    ordering = ('-id',)
