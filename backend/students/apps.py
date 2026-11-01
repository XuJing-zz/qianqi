"""students 应用的 AppConfig 配置。

向 Django 声明应用名称，Django 启动时据此加载该应用的模型、
信号与后台注册等模块。
"""
from django.apps import AppConfig


class StudentsConfig(AppConfig):
    """students 应用配置类。

    name 必须与应用的 Python 包名一致，Django 通过它定位应用目录并注册
    模型命名空间；数据库表名等细节在 models.py 的 Meta 中指定。
    """

    name = 'students'
