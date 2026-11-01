"""
courses 应用的配置。

声明课程应用的名称，供 Django 启动时识别并加载该应用，
同时作为迁移与后台显示名的基础配置。
"""

from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """
    课程应用配置类，指定应用名为 courses，使 Django 能定位该应用模块。
    """

    name = 'courses'
