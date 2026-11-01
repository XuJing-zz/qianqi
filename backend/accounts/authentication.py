"""JWT 认证模块：让三张账号表共用同一套 Token 校验逻辑。

项目里学员、管理员、传承人各占一张表，没有统一的用户表；本模块按 Token 里的
role 字段找到对应模型，再取出当前登录账号交给 DRF 作为 request.user。
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, Admin, Inheritor

# 身份标识 -> 账号模型，与 accounts.views 中的 MODEL_MAP 保持一致
ROLE_MODEL = {
    'user': User,
    'admin': Admin,
    'heritage': Inheritor,
}


class MultiTableJWTAuthentication(JWTAuthentication):
    """多表 JWT 认证类，用来替换 DRF 默认的 JWTAuthentication。

    签名、过期时间等校验仍由父类完成，这里只重写“根据 Token 取用户”这一步。
    """

    def get_user(self, validated_token):
        """按 Token 中的 user_id 与 role 到对应账号表取当前用户。

        参数：
            validated_token: 已通过签名与有效期校验的 JWT 载荷。
        返回：
            匹配到的账号实例；Token 缺字段、账号不存在或已被停用时返回 None。
        """
        try:
            user_id = validated_token['user_id']
            # 兼容早期未写入 role 的旧 Token，缺省按学员处理
            role = validated_token.get('role', 'user')
        except KeyError:
            return None

        Model = ROLE_MODEL.get(role, User)
        try:
            # is_active=True 让后台停用的账号在认证阶段就直接失效
            user = Model.objects.get(pk=user_id, is_active=True)
        except Model.DoesNotExist:
            return None
        return user
