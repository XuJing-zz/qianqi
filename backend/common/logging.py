# common/logging.py —— 操作日志的公共工具
# 提供获取客户端 IP、解析操作人、写入操作日志三个函数，以及可复用的日志混入类，
# 供各业务模块统一记录后台操作，避免每处重复写日志逻辑。

from django.utils import timezone


def client_ip(request):
    """获取请求来源 IP，优先取代理转发头，取不到再退回直连地址。

    参数：request 为 Django 的 HttpRequest 对象。
    返回：str，形如 '1.2.3.4'；无法获取时返回空字符串。
    """
    # 经过 Nginx 等反向代理时，真实 IP 放在 X-Forwarded-For 的第一个位置
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        first = xff.split(',')[0].strip()
        if first:
            return first
    # 无代理场景直接使用 TCP 连接的对端地址
    return request.META.get('REMOTE_ADDR') or ''


def actor_name(request_or_user):
    """取得操作人的展示名称。

    参数：request_or_user 既可以是请求对象，也可以直接是用户对象。
    返回：str，优先返回用户的中文名 name，没有则退回 username，都没有返回空串。
    """
    # 传请求时取 request.user，传用户对象时原样使用
    u = getattr(request_or_user, 'user', request_or_user)
    return (getattr(u, 'name', '') or '') or (getattr(u, 'username', '') or '')


def write_log(request, log_type, action, detail='', operator=None):
    """写一条操作日志，失败不影响主业务流程。

    参数：request 当前请求；log_type 日志类型（对应 OperationLog.TYPE_CHOICES）；
         action 操作摘要；detail 详细内容；operator 操作人，未传则自动从请求解析。
    返回：无。内部异常被吞掉，保证日志写入不阻断业务请求。
    """
    try:
        # 延迟导入，避免 common 与 system 模块在启动阶段相互引用
        from system.models import OperationLog
        if operator is None:
            operator = actor_name(request)
        OperationLog.objects.create(
            type=log_type,
            operator=operator or '系统',
            action=action,
            detail=detail or '',
            ip=client_ip(request),
            time=timezone.now().strftime('%Y-%m-%d %H:%M'),
        )
    except Exception:
        # 日志不是核心链路，写入失败时静默跳过，避免影响接口正常返回
        pass


class AutoLogMixin:
    """自动记日志混入类：配合 DRF 的 ModelViewSet 使用，在增删改时自动写操作日志。

    调用方只需继承本类并设置 auto_log_name（如「商品」「留言」），
    即可自动记录「新增/修改/删除 + 名称」格式的日志。
    """

    # 业务对象名称，子类覆盖后日志文案会自动带上该名称
    auto_log_name = '数据'

    def _log_obj(self, request, log_type, verb, obj):
        """根据对象生成并写入一条日志。

        参数：request 当前请求；log_type 日志类型；verb 动作词（新增/修改等）；
             obj 被操作的数据对象，用于取名称。
        返回：无。
        """
        label = self.auto_log_name
        # 依次尝试 name、item_name，都没有则退化为 '#主键'，保证日志可读
        name = getattr(obj, 'name', '') or getattr(obj, 'item_name', '') or f'#{getattr(obj, "pk", "")}'
        write_log(request, log_type, f'{verb}{label}', f'{verb}{label}「{name}」')

    def perform_create(self, serializer):
        """新增成功后写一条 create 类型日志；参数 serializer 为 DRF 序列化器。"""
        # 先执行父类的新增逻辑，确保 serializer.instance 已生成
        super().perform_create(serializer)
        self._log_obj(self.request, 'create', '新增', serializer.instance)

    def perform_update(self, serializer):
        """修改成功后写一条 update 类型日志；参数 serializer 为 DRF 序列化器。"""
        super().perform_update(serializer)
        self._log_obj(self.request, 'update', '修改', serializer.instance)

    def perform_destroy(self, instance):
        """删除前先取名称，删除成功后写 delete 类型日志。

        参数：instance 为待删除的数据对象；返回：无。
        """
        # 删除后对象属性可能不可用，需提前保存主键和名称
        pk = instance.pk
        name = getattr(instance, 'name', '') or getattr(instance, 'item_name', '') or f'#{pk}'
        super().perform_destroy(instance)
        write_log(self.request, 'delete', f'删除{self.auto_log_name}', f'删除{self.auto_log_name}「{name}」')
