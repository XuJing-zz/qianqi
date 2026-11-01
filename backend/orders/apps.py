# 订单模块 —— 应用配置
# 声明 orders 这个 Django 应用的注册信息，供 INSTALLED_APPS 加载应用及其模型。

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """orders 应用的配置类：指定应用的点路径名，Django 据此加载本应用的模型。"""

    # 应用的点路径名，必须与目录名一致
    name = 'orders'
