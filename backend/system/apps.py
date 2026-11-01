# system/apps.py —— system 应用的配置入口
# Django 启动时加载该配置，用于标识应用名称及后续可扩展的启动钩子。
# 目前保持最小配置，具体业务逻辑分散在 models、views、serializers 中。

from django.apps import AppConfig


class SystemConfig(AppConfig):
    """system 应用的配置类：声明应用名，供 Django 在 INSTALLED_APPS 中识别。"""

    # 应用的点路径，对应 system/ 目录，需与 INSTALLED_APPS 中的 'system' 一致
    name = 'system'

