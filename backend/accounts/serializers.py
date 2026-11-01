"""账号序列化与字段校验。

集中提供账号数据的输出结构（account_serializer_data）、身份判断（role_of_account），
以及注册、登录、资料修改、管理员建号等场景的入参校验器；
三张账号表的字段基本一致，因此通用校验函数被多个序列化器复用。
"""
import re

from rest_framework import serializers
from .models import User, Admin, Inheritor

# 账号允许的字符集；手机号严格规则；宽松规则的手机号允许 - 与 * 做脱敏展示
_USERNAME_RE = re.compile(r'^[\w.@+-]+$')
_MOBILE_RE = re.compile(r'^1\d{10}$')
_LOOSE_PHONE_RE = re.compile(r'^[0-9\-\*]{7,20}$')


def _reject(msg):
    """统一抛出 DRF 校验错误，让错误信息以 400 返回前端。

    参数：
        msg: 提示给用户的中文错误文案。
    """
    raise serializers.ValidationError(msg)


def clean_username(value):
    """校验并清理登录账号。

    参数：
        value: 原始账号字符串，可能带首尾空格。
    返回：
        去掉首尾空格后的账号。
    异常：
        长度不在 3~30 位或含非法字符时抛 ValidationError。
    """
    v = (value or '').strip()
    if not (3 <= len(v) <= 30):
        _reject('账号长度需在 3~30 位之间')
    if not _USERNAME_RE.fullmatch(v):
        _reject('账号仅可包含字母、数字、下划线、中划线、点与中文，且不能包含空格')
    return v


def check_username_unique(value):
    """在清理账号格式的基础上，再校验全局唯一。

    参数：
        value: 原始账号字符串。
    返回：
        格式合法且未被占用的账号。
    """
    v = clean_username(value)
    # 三张账号表共用一个登录入口，所以用户名必须在三张表里都没被占用
    if any(M.objects.filter(username=v).exists() for M in (User, Admin, Inheritor)):
        _reject('用户名已存在')
    return v


def clean_password(value, label='密码'):
    """校验密码强度与格式。

    参数：
        value: 原始密码，非字符串按空处理。
        label: 错误提示中使用的字段名，默认“密码”。
    返回：
        校验通过的密码原文。
    """
    v = value if isinstance(value, str) else ''
    if not v:
        _reject(f'请输入{label}')
    if len(v) < 6:
        _reject(f'{label}至少 6 位')
    if len(v) > 32:
        _reject(f'{label}不能超过 32 位')
    if v != v.strip():
        _reject(f'{label}不能以空格开头或结尾')
    return v


def clean_nick(value, required=False, max_len=20):
    """校验昵称，可配置是否必填与最大长度。

    参数：
        value: 原始昵称。
        required: 为 True 时昵称不能为空。
        max_len: 允许的最大字符数。
    返回：
        去空格后的昵称；非必填且为空时返回空字符串。
    """
    v = (value or '').strip()
    if not v:
        if required:
            _reject('请输入昵称')
        return ''
    if len(v) > max_len:
        _reject(f'昵称不能超过 {max_len} 个字符')
    return v


def clean_phone(value, required=False, strict=False):
    """校验手机号，区分严格模式与脱敏模式。

    参数：
        value: 原始手机号。
        required: 为 True 时手机号不能为空。
        strict: 为 True 时必须是 11 位手机号（注册场景）；
                为 False 时允许 - 与 * 等脱敏字符（资料展示场景）。
    返回：
        去空格后的手机号；非必填且为空时返回空字符串。
    """
    v = (value or '').strip()
    if not v:
        if required:
            _reject('请输入手机号')
        return ''
    if strict:
        if not _MOBILE_RE.fullmatch(v):
            _reject('请输入正确的 11 位手机号')
    elif not _LOOSE_PHONE_RE.fullmatch(v):
        _reject('手机号格式不正确（仅支持数字，可用 - 或 * 脱敏）')
    return v


def clean_text(value, label='内容', max_len=50):
    """通用文本字段校验：去空格 + 限长。

    参数：
        value: 原始文本。
        label: 错误提示中使用的字段名。
        max_len: 允许的最大字符数。
    返回：
        清理后的文本；为空时返回空字符串。
    """
    v = (value or '').strip()
    if not v:
        return ''
    if len(v) > max_len:
        _reject(f'{label}不能超过 {max_len} 个字符')
    return v


def role_of_account(obj):
    """判断账号所属身份。

    参数：
        obj: User / Admin / Inheritor 之一。
    返回：
        'admin'、'heritage' 或 'user'；无法识别时按学员处理。
    """
    # 三张表之间没有继承关系，只能按实例所属模型区分身份
    if isinstance(obj, Admin):
        return 'admin'
    if isinstance(obj, Inheritor):
        return 'heritage'
    return 'user'


def account_serializer_data(obj):
    """把任意身份账号转成前端统一的字典结构。

    三张表字段相同、身份不同，统一成一份结构后前端可用一套逻辑渲染。

    参数：
        obj: 任意账号实例。
    返回：
        dict，含 id、username、role、role_label、status_label 等展示字段；
        表里没有的字段用 getattr 兜底为空值。
    """
    return {
        'id': obj.pk,
        'username': obj.username,
        'name': obj.name or '',
        'first_name': getattr(obj, 'first_name', '') or '',
        'last_name': getattr(obj, 'last_name', '') or '',
        'nick': obj.nick or '',
        'gender': obj.gender or '',
        'region': obj.region or '',
        'bio': obj.bio or '',
        'avatar': obj.avatar or '',
        'role': role_of_account(obj),
        'role_label': {'admin': '管理员', 'heritage': '传承人', 'user': '学员'}[role_of_account(obj)],
        'phone': obj.phone or '',
        'email': obj.email or '',
        'level': getattr(obj, 'level', '') or '',
        'craft': getattr(obj, 'craft', '') or '',
        'years': getattr(obj, 'years', None),
        'intro': getattr(obj, 'intro', '') or '',
        'honor': getattr(obj, 'honor', '') or '',
        'status': obj.status,
        # 状态码转中文，前端直接展示而不用自己映射
        'status_label': '正常' if obj.status == 'active' else '禁用',
        'created_at': getattr(obj, 'created_at', None),
    }


class UserSerializer(serializers.ModelSerializer):
    """学员账号的输出序列化器，用于注册成功后回显新建账号。

    只读字段，不做写入校验；role_label 与 status_label 为计算字段。
    """

    role_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        """指定序列化所用的模型、输出字段与只读字段。"""

        model = User
        fields = ['id', 'username', 'name', 'nick', 'gender', 'region', 'bio', 'avatar',
                  'role_label', 'phone', 'email', 'first_name', 'last_name', 'status', 'status_label', 'created_at']
        read_only_fields = ['created_at']

    def get_role_label(self, obj):
        """返回身份的中文名称；该序列化器只服务学员，故固定为“学员”。"""
        return '学员'

    def get_status_label(self, obj):
        """把 status 字段转成中文展示文案。"""
        return '正常' if obj.status == 'active' else '禁用'


class RegisterSerializer(serializers.Serializer):
    """学员注册的入参校验器，校验通过后创建 User 记录。"""

    username = serializers.CharField(error_messages={'required': '请输入账号', 'blank': '请输入账号'})
    password = serializers.CharField(write_only=True, error_messages={'required': '请输入密码', 'blank': '请输入密码'})
    nick = serializers.CharField(error_messages={'required': '请输入昵称', 'blank': '请输入昵称'})
    name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(error_messages={'required': '请输入手机号', 'blank': '请输入手机号'})
    email = serializers.CharField(error_messages={'required': '请输入邮箱', 'blank': '请输入邮箱'})


    def validate_username(self, value):
        """校验账号格式并在三张表中查重。"""
        return check_username_unique(value)

    def validate_password(self, value):
        """校验密码长度与首尾空格。"""
        return clean_password(value)

    def validate_nick(self, value):
        """昵称必填，且不超过默认长度。"""
        return clean_nick(value, required=True)

    def validate_phone(self, value):
        """注册场景使用严格模式，必须是 11 位手机号。"""
        return clean_phone(value, required=True, strict=True)

    def validate_email(self, value):
        """做最简邮箱校验：恰好一个 @ 且不在首尾。"""
        v = (value or '').strip()
        if '@' not in v or v.count('@') != 1 or v.startswith('@') or v.endswith('@'):
            _reject('请输入正确的邮箱地址')
        return v

    def create(self, validated_data):
        """创建学员账号。

        参数：
            validated_data: 已通过上述校验的字段字典。
        返回：
            新建并已加密密码的 User 实例。
        """
        ln = (validated_data.get('last_name') or '').strip()
        fn = (validated_data.get('first_name') or '').strip()
        name = validated_data.get('name', '')
        # 未单独填写姓名时，用“姓 + 名”拼出展示名
        if not name and (ln or fn):
            name = ln + fn
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            nick=validated_data.get('nick', ''),
            name=name,
            first_name=fn,
            last_name=ln,
            phone=validated_data.get('phone', ''),
            email=validated_data.get('email', ''),
            status='active',
        )


class UpdateProfileSerializer(serializers.Serializer):
    """个人资料修改的入参校验器，所有字段可选，只更新传了的字段。"""

    nick = serializers.CharField(max_length=50, required=False, allow_blank=True)
    name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)
    region = serializers.CharField(max_length=50, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    avatar = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=50, required=False, allow_blank=True)
    level = serializers.CharField(max_length=20, required=False, allow_blank=True)
    craft = serializers.CharField(max_length=200, required=False, allow_blank=True)
    years = serializers.IntegerField(required=False, allow_null=True)
    intro = serializers.CharField(max_length=100, required=False, allow_blank=True)
    honor = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_avatar(self, value):
        """头像上传校验：限制 data URI 的近似体积，避免超大图片入库。

        参数：
            value: 头像字段，可能是 data:image/...;base64,xxx，也可能是纯 base64。
        返回：
            原样返回头像字符串。
        """
        if not value:
            return value
        from common.uploads import effective_max_mb
        cap = effective_max_mb(5)
        # 去掉 data URI 前缀只留 base64 正文，再按 3/4 估算原始字节数
        b64 = value.split(',', 1)[1] if value.startswith('data:') and ',' in value else value
        approx_mb = len(b64) * 3 / 4 / 1024 / 1024
        if approx_mb > cap:
            raise serializers.ValidationError(f'图片不能超过 {cap}MB')
        return value

    def validate_nick(self, value):
        """昵称可留空，非空时限制长度。"""
        return clean_nick(value)

    def validate_phone(self, value):
        """资料里的手机号用宽松模式，允许脱敏字符。"""
        return clean_phone(value, strict=False)

    def validate_name(self, value):
        """姓名去空格并限制在 50 字以内。"""
        return clean_text(value, '姓名', 50)

    def validate_bio(self, value):
        """个人简介去空格并限制在 500 字以内。"""
        return clean_text(value, '个人简介', 500)

    def validate_honor(self, value):
        """荣誉去空格并限制在 200 字以内。"""
        return clean_text(value, '荣誉', 200)

    def validate_intro(self, value):
        """一句话签名去空格并限制在 100 字以内。"""
        return clean_text(value, '一句话签名', 100)

    def validate_craft(self, value):
        """技艺方向去空格并限制在 200 字以内。"""
        return clean_text(value, '技艺方向', 200)

    def update(self, account, validated_data):
        """把校验后的字段写回账号并保存。

        参数：
            account: 当前登录的账号实例。
            validated_data: 本次请求中出现的字段。
        返回：
            保存后的账号实例。
        """
        # 白名单式更新：只遍历允许修改的字段，未传入的保持原值
        for field in ['nick', 'name', 'first_name', 'last_name', 'gender', 'region', 'bio', 'avatar', 'phone', 'email',
                      'level', 'craft', 'years', 'intro', 'honor']:
            if field in validated_data:
                setattr(account, field, validated_data[field])
        account.save()
        return account


class LoginSerializer(serializers.Serializer):
    """登录入参校验器，负责在三个账号表中核对账号密码并检查账号状态。"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """跨字段校验：依次在三张账号表中比对账号与密码。

        参数：
            attrs: 已通过字段级校验的 username、password。
        返回：
            补充了 account 字段的 attrs，供视图直接取用。
        """
        username = attrs['username']
        password = attrs['password']

        # 三张表结构独立，无法用一条查询完成，逐个表尝试匹配
        account = None
        for Model in (User, Admin, Inheritor):
            try:
                cand = Model.objects.get(username=username)
            except Model.DoesNotExist:
                continue
            if cand.check_password(password):
                account = cand
                break

        if account is None:
            # 不区分“账号不存在”和“密码错误”，避免暴露账号是否存在
            raise serializers.ValidationError('用户名或密码错误')
        if not getattr(account, 'is_active', True):
            raise serializers.ValidationError('账号不可用')
        # 业务状态被管理员置为 disabled 时也不允许登录
        if account.status == 'disabled':
            raise serializers.ValidationError('账号已被禁用，请联系管理员')

        attrs['account'] = account
        return attrs


class CreateInheritorSerializer(serializers.Serializer):
    """发放传承人账号的入参校验器，校验通过后创建 Inheritor 记录。"""

    username = serializers.CharField(error_messages={'required': '请输入用户名', 'blank': '请输入用户名'})
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, default='123456')
    name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        """校验账号格式并在三张表中查重。"""
        return check_username_unique(value)

    def validate_password(self, value):
        """密码可留空，空值回落到默认密码 123456。"""
        if value in (None, ''):
            return '123456'
        return clean_password(value)

    def validate_phone(self, value):
        """手机号沿用宽松模式，允许留空。"""
        return clean_phone(value, strict=False)

    def validate_email(self, value):
        """邮箱可留空；非空时要求恰好一个 @。"""
        v = (value or '').strip()
        if not v:
            return ''
        if '@' not in v or v.count('@') != 1:
            _reject('请输入正确的邮箱地址')
        return v

    def create(self, validated_data):
        """创建传承人账号（密码经 create_user 加密）。

        参数：
            validated_data: 已通过校验的字段字典。
        返回：
            新建的 Inheritor 实例。
        """
        return Inheritor.objects.create_user(
            username=validated_data['username'],
            password=validated_data.get('password', '123456'),
            name=validated_data.get('name', ''),
            phone=validated_data.get('phone', ''),
            email=validated_data.get('email', ''),
            status='active',
        )


class AdminCreateAccountSerializer(serializers.Serializer):
    """管理员新增账号的入参校验器。

    role 决定新建账号落在哪张表，因此用 ChoiceField 只放行三种已知身份。
    """

    role = serializers.ChoiceField(choices=['user', 'admin', 'heritage'],
                                   error_messages={'required': '请选择身份', 'invalid_choice': '未知身份'})
    username = serializers.CharField(error_messages={'required': '请输入用户名', 'blank': '请输入用户名'})
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, default='123456')
    name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        """校验账号格式并在三张表中查重。"""
        return check_username_unique(value)

    def validate_password(self, value):
        """密码可留空，空值回落到默认密码 123456。"""
        if value in (None, ''):
            return '123456'
        return clean_password(value)

    def validate_phone(self, value):
        """手机号沿用宽松模式，允许留空。"""
        return clean_phone(value, strict=False)

    def validate_email(self, value):
        """邮箱可留空；非空时要求恰好一个 @。"""
        v = (value or '').strip()
        if not v:
            return ''
        if '@' not in v or v.count('@') != 1:
            _reject('请输入正确的邮箱地址')
        return v



class AdminUpdateAccountSerializer(serializers.Serializer):
    """管理员编辑账号的入参校验器，只允许改账号名、姓名、手机号与邮箱。"""

    username = serializers.CharField(required=False, allow_blank=False)
    name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        """只校验账号格式；改名时的全局查重放在视图里排除自身后处理。"""
        return clean_username(value)

    def validate_phone(self, value):
        """手机号沿用宽松模式，允许留空。"""
        return clean_phone(value, strict=False)

    def validate_email(self, value):
        """邮箱可留空；非空时要求恰好一个 @。"""
        v = (value or '').strip()
        if not v:
            return ''
        if '@' not in v or v.count('@') != 1:
            _reject('请输入正确的邮箱地址')
        return v
