"""skills 应用配置模块。

声明技艺档案应用的 AppConfig 子类，供 Django 在 INSTALLED_APPS 中加载该应用
并识别其模型、迁移与后台注册。
"""
from django.apps import AppConfig


class SkillsConfig(AppConfig):
    """「技艺档案」应用的配置类。

    属性：
        name: 应用的 Python 包路径，Django 据此定位 models、views 等模块。
    """

    name = 'skills'
