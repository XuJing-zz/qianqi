"""accounts 应用配置模块。

把账号模块注册为 Django 应用，供 settings.INSTALLED_APPS 引用，
同时作为 accounts 下模型、视图等代码的加载入口。
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """accounts 应用的配置类，Django 启动时据此加载本应用。"""

    # 应用的点路径，用于定位模块并生成默认 app_label
    name = 'accounts'

