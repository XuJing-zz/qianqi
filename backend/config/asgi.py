
"""
ASGI 部署入口模块：为异步 ASGI 服务器（如 Daphne、Uvicorn）提供应用对象。

在支持 WebSocket、长连接等异步特性的部署方式下使用，与 wsgi.py 作用对应。
"""

import os

from django.core.asgi import get_asgi_application

# 指定默认的配置模块；使用 setdefault 是为了让部署环境已设置的环境变量优先生效
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 依据上述配置完成 Django 初始化，生成供 ASGI 服务器调用的应用入口
application = get_asgi_application()
