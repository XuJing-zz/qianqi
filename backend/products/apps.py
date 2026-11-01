# products 应用的 AppConfig 配置。
# 用于向 Django 注册本应用并声明应用的点路径，
# 使作品、收藏、库存流水等模型能够被框架正确加载和识别。

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """products 应用的配置类：声明应用的点路径，供 Django 在启动时加载本应用。"""

    # 应用的点路径，必须与目录名一致，Django 据此定位 models、views 等模块
    name = 'products'
