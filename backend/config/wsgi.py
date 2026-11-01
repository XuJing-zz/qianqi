
"""
WSGI 部署入口模块：为同步 WSGI 服务器（如 Gunicorn、uWSGI）提供应用对象。

服务器启动时导入本模块，即可拿到处理 HTTP 请求的 application 可调用对象。
"""

import os

from django.core.wsgi import get_wsgi_application

# 指定默认的配置模块；使用 setdefault 是为了让部署环境已设置的环境变量优先生效
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 依据上述配置完成 Django 初始化，生成供 WSGI 服务器调用的应用入口
application = get_wsgi_application()
