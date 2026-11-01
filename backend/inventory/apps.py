"""inventory 应用配置：向 Django 声明库存应用及其注册名称。

Django 启动时会加载本配置，INSTALLED_APPS 中的 'inventory' 对应此类。
"""
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """库存应用配置类，指定应用在项目中的注册名。"""

    # 应用名必须与 INSTALLED_APPS 中的条目、包目录名一致
    name = 'inventory'
