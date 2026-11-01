# heritage/apps.py —— 传承人档案应用的配置类
# Django 启动时通过本文件加载 heritage 应用，声明应用名，
# 供 settings.INSTALLED_APPS 中的 'heritage' 条目定位到具体模块。

from django.apps import AppConfig


class HeritageConfig(AppConfig):
    """heritage 应用的配置类。

    只声明应用名，不额外注册信号或做启动初始化；后台名称与模型名称统一在 models.py 中定义。
    """

    name = 'heritage'
