# common/uploads.py —— 文件上传的公共校验与保存逻辑
# 定义允许上传的图片/文档/视频扩展名，读取后台配置的上传上限，
# 并统一完成「取文件 → 校验类型与大小 → 存储 → 返回访问地址」这一流程。

import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

# 允许的图片扩展名（统一小写，比较前会把文件名后缀转小写）
IMAGE_EXT = ('jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp')
# 允许的文档扩展名
DOC_EXT = (
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'md', 'csv', 'zip', 'rar',
)
# 允许的视频扩展名
VIDEO_EXT = ('mp4', 'webm', 'mov', 'm4v')
# 全部允许的扩展名，对外展示时使用
ALL_EXT = IMAGE_EXT + DOC_EXT + VIDEO_EXT

# 业务类别到扩展名白名单的映射，save_upload_file 的 allow 参数按此展开
_KIND_EXT = {'image': IMAGE_EXT, 'doc': DOC_EXT, 'video': VIDEO_EXT}

# 校验失败时给用户看的格式提示文案，按类别拼接
_EXT_LABEL = {
    'image': '/'.join(IMAGE_EXT),
    'doc': '/'.join(DOC_EXT),
    'video': '视频(' + '/'.join(VIDEO_EXT) + ')',
}

# 后台未配置时的默认单文件大小上限（MB）
DEFAULT_MAX_MB = 50


def _as_flag(v, default=True):
    """把配置里的开关值解析成布尔值。

    参数：v 原始配置值（可能是 bool、None、'1'、'true' 等）；default 缺省值。
    返回：bool。None 时返回 default，字符串按 1/true/yes/on 判定为真。
    """
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    # 兼容前端传字符串的开关值，其余一律视为关闭
    return str(v).strip().lower() in ('1', 'true', 'yes', 'on')


def get_upload_limits():
    """读取后台「系统配置」中的上传限制。

    返回：dict，包含 max_mb 单文件上限（MB）、max_count 单次数量上限、
         allow_video 是否允许视频、allow_doc 是否允许文档；未配置项为 None 或默认开关。
    """
    # 延迟导入，避免模块加载时就和 system 应用产生循环依赖
    from system.models import SystemConfig
    try:
        obj = SystemConfig.objects.filter(key='system').first()
    except Exception:
        # 数据库尚未迁移或配置表缺失时不阻塞上传，按默认规则处理
        obj = None
    v = dict((obj.value if obj else None) or {})

    def _int(key):
        """把配置值转成正整数，非法值或非正数返回 None（表示未设置）。"""
        try:
            n = int(float(v.get(key)))
            return n if n > 0 else None
        except (TypeError, ValueError):
            return None

    return {
        'max_mb': _int('uploadMaxSize'),
        'max_count': _int('uploadMaxCount'),
        'allow_video': _as_flag(v.get('allowVideo'), True),
        'allow_doc': _as_flag(v.get('allowDoc'), True),
    }


def effective_max_mb(default_mb=None):
    """计算实际生效的单文件大小上限。

    参数：default_mb 调用方期望的默认上限（MB），可为空。
    返回：int，优先级为后台配置 > 调用方传入 > DEFAULT_MAX_MB。
    """
    return get_upload_limits()['max_mb'] or default_mb or DEFAULT_MAX_MB


def save_upload_file(request, folder='files', allow=('image', 'doc'), max_mb=None):
    """校验并保存上传文件，返回可直接访问的文件信息。

    参数：request 当前请求（文件取自表单字段 file）；folder 存储子目录；
         allow 允许的类别元组，可含 image/doc/video；max_mb 本次允许的最大体积。
    返回：dict，包含 url 绝对访问地址、name 原始文件名、size 字节数、ext 小写扩展名。
    异常：未选文件、格式不在白名单、后台关闭该类上传、超出大小限制时抛出 ValidationError。
    """
    file = request.FILES.get('file')
    if file is None:
        raise ValidationError('未选择文件')
    # 只取最后一个点之后的后缀并转小写，避免 'A.JPG' 这类大小写绕过
    ext = (file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else '')
    allowed_exts = [e for k in allow for e in _KIND_EXT.get(k, ())]
    # 上传校验第一层：扩展名必须在本次允许的类别白名单内
    if ext not in allowed_exts:
        labels = ' / '.join(_EXT_LABEL[k] for k in allow if k in _EXT_LABEL)
        raise ValidationError(f'仅支持{labels}格式')

    limits = get_upload_limits()
    # 上传校验第二层：后台可能已按业务需要关闭视频或文档上传
    if ext in VIDEO_EXT and not limits['allow_video']:
        raise ValidationError('管理员已在「系统配置」中关闭视频上传')
    if ext in DOC_EXT and not limits['allow_doc']:
        raise ValidationError('管理员已在「系统配置」中关闭文档上传')

    # 上传校验第三层：体积上限取后台配置，其次调用方参数，最后默认值
    cap = limits['max_mb'] or max_mb or DEFAULT_MAX_MB
    if file.size > cap * 1024 * 1024:
        raise ValidationError(f'文件不能超过 {cap}MB')

    # 用 uuid 重命名，避免同名覆盖和中文文件名在 URL 中的编码问题
    name = f'{folder}/{uuid.uuid4().hex}.{ext}'
    saved = default_storage.save(name, file)
    # 拼成带域名和协议的绝对地址，前端可直接用于图片/附件展示
    media_url = settings.MEDIA_URL.rstrip('/')
    url = request.build_absolute_uri(f'{media_url}/{saved}')
    return {'url': url, 'name': file.name, 'size': file.size, 'ext': ext}
