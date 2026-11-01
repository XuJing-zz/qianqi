"""账号相关接口：登录注册、个人资料，以及管理员对账号的后台管理。

AuthViewSet 负责注册、登录、退出、当前登录人与资料修改，路由前缀 /api/accounts/auth/；
AccountManageViewSet 负责账号的查询、新增、编辑、启停、重置密码与删除，路由前缀 /api/accounts/admin/。
两个视图集都基于 DRF 的 ViewSet，用 @action 把方法映射成具体接口。
"""
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from common.logging import write_log
from common.pagination import OptInPagination
from .models import User, Admin, Inheritor
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer, UpdateProfileSerializer,
    CreateInheritorSerializer, AdminCreateAccountSerializer, AdminUpdateAccountSerializer,
    account_serializer_data, role_of_account,
)

# 前端传来的身份标识 -> 具体账号模型，账号管理接口靠它定位到要操作的表
MODEL_MAP = {
    'user': User,
    'admin': Admin,
    'heritage': Inheritor,
}


def _truthy(v):
    """把前端传来的确认标记转成布尔值。

    参数：
        v: 原始值，可能是 1、'true'、'on' 等。
    返回：
        命中常见真值写法时为 True，其余（含 None）为 False。
    """
    return str(v).lower() in ('1', 'true', 'yes', 'on')


def issue_token(account):
    """为登录成功的账号签发 JWT，并把身份信息写进 Token 载荷。

    参数：
        account: 已通过账号密码校验的 User / Admin / Inheritor 实例。
    返回：
        (refresh, access) 二元组，两个 Token 对象都可直接 str() 成字符串返回前端。
    """
    role = role_of_account(account)
    refresh = RefreshToken()
    # 自定义载荷：user_id 用于认证时回查账号，role 决定查哪张表
    refresh['user_id'] = account.pk
    refresh['username'] = account.username
    refresh['name'] = account.name or ''
    refresh['role'] = role
    refresh['role_label'] = {'user': '学员', 'admin': '管理员', 'heritage': '传承人'}[role]
    refresh['status'] = account.status
    refresh['is_superuser'] = getattr(account, 'is_superuser', False)

    # access 由 refresh 派生，同样补齐自定义字段，供前端直接读取
    access = refresh.access_token
    access['user_id'] = account.pk
    access['username'] = account.username
    access['name'] = account.name or ''
    access['role'] = role
    access['role_label'] = {'user': '学员', 'admin': '管理员', 'heritage': '传承人'}[role]
    access['status'] = account.status
    return refresh, access


class AuthViewSet(viewsets.ViewSet):
    """认证相关接口集合，路由前缀 /api/accounts/auth/。

    登录、注册对游客开放；退出、获取当前用户、修改资料都要求携带有效 Token。
    """

    def get_permissions(self):
        """按当前 action 动态返回权限类。

        返回：
            权限类实例列表；login、register 为 AllowAny，其余为 IsAuthenticated。
        """
        # 登录与注册必须允许匿名访问，其他接口统一要求已登录
        if self.action in ('login', 'register'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """注册学员账号。

        接口：POST /api/accounts/auth/register/
        权限：AllowAny，游客可调用。
        参数：请求体交给 RegisterSerializer 校验（username、password、nick、phone、email 等）。
        返回：201 + {msg, user}，user 为新建学员的序列化数据。
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'msg': '注册成功',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """账号登录，校验通过后签发双 Token。

        接口：POST /api/accounts/auth/login/
        权限：AllowAny，游客可调用。
        参数：username、password，由 LoginSerializer 在三个账号表中逐一核对。
        返回：{refresh, access, user}，其中 user 为当前账号的序列化数据。
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data['account']
        role = role_of_account(account)
        name = (account.name or '').strip() or account.username
        # 登录行为写入操作日志，便于后台审计
        write_log(
            request, 'login', '登录系统',
            f'{role}账号「{account.username}」登录',
            operator=name,
        )
        refresh, access = issue_token(account)
        return Response({
            'refresh': str(refresh),
            'access': str(access),
            'user': account_serializer_data(account),
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """退出登录，把 refresh Token 加入黑名单使其立即失效。

        接口：POST /api/accounts/auth/logout/
        权限：IsAuthenticated，需登录后调用。
        参数：请求体中的 refresh 字段（可选）。
        返回：{msg} 提示已退出；Token 缺失或已失效也按成功处理，保证退出幂等。
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # 拉黑后该 refresh Token 无法再换取新的 access Token
                RefreshToken(refresh_token).blacklist()
        except Exception:
            # Token 非法或已过期时忽略异常，前端照常清除本地登录态
            pass
        return Response({'msg': '已退出登录'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前登录账号的资料。

        接口：GET /api/accounts/auth/me/
        权限：IsAuthenticated，需登录后调用。
        返回：账号统一序列化数据（含 role、role_label、status 等）。
        """
        user = request.user
        return Response(account_serializer_data(user))

    @action(detail=False, methods=['post'])
    def update_profile(self, request):
        """修改当前登录账号的个人资料。

        接口：POST /api/accounts/auth/update-profile/
        权限：IsAuthenticated，只能改自己的资料。
        参数：UpdateProfileSerializer 中的任意可选字段（昵称、头像、简介等）。
        返回：{msg, user}，user 为更新后的账号数据。
        """
        account = request.user
        serializer = UpdateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 只把请求中出现的字段覆盖到当前账号，未传的字段保持原值
        account = serializer.update(account, serializer.validated_data)
        return Response({
            'msg': '资料已更新',
            'user': account_serializer_data(account),
        })


class AccountManageViewSet(viewsets.ViewSet):
    """账号后台管理接口集合，路由前缀 /api/accounts/admin/。

    全部接口都要求登录，且由 _require_admin 再校验一次管理员身份，
    因此学员与传承人即使拿到 Token 也无法调用。
    """

    permission_classes = [IsAuthenticated]

    def _require_admin(self, request):
        """管理员身份校验的公共入口。

        参数：
            request: 当前请求，取 request.user 判断身份。
        返回：
            非管理员时返回 403 的 Response 由调用方直接返回；
            管理员时返回 None，表示继续执行后续逻辑。
        """
        if role_of_account(request.user) != 'admin':
            return Response({'msg': '无权限，仅管理员可操作'}, status=status.HTTP_403_FORBIDDEN)
        return None

    @action(detail=False, methods=['get'])
    def list_accounts(self, request):
        """分页查询三类账号的合并列表。

        接口：GET /api/accounts/admin/list/
        权限：IsAuthenticated + 管理员。
        参数：role（user/admin/heritage/all，默认 all）、keyword（账号/姓名/手机号模糊搜索）、
              status（按状态过滤）、page 与 page_size（可选，传了才分页）。
        返回：未传分页参数时返回数组；传了则返回含 count/page/page_size/results 的分页结构。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        role = request.query_params.get('role', 'all')
        # 只接受已知角色，避免把任意参数拼进模型映射
        if role not in MODEL_MAP and role != 'all':
            return Response({'msg': '未知角色'}, status=status.HTTP_400_BAD_REQUEST)
        roles = ('user', 'admin', 'heritage') if role == 'all' else (role,)
        kw = (request.query_params.get('keyword') or '').strip()
        status_q = request.query_params.get('status')

        rows = []
        for r in roles:
            Model = MODEL_MAP[r]
            qs = Model.objects.all()
            if status_q:
                qs = qs.filter(status=status_q)
            if kw:
                # 关键字在账号、姓名、手机号三个字段上做“包含”匹配
                qs = qs.filter(
                    Q(username__icontains=kw) | Q(name__icontains=kw) | Q(phone__icontains=kw)
                )
            # 三张表分别查询后统一转成字典再合并，最后按 id 倒序展示
            rows.extend(account_serializer_data(o) for o in qs.order_by('-id'))

        # OptInPagination 只在请求带 page/page_size 时生效，否则返回 None
        paginator = OptInPagination()
        page = paginator.paginate_queryset(rows, request, view=self)
        if page is None:
            return Response(rows)
        return paginator.get_paginated_response(page)

    @action(detail=False, methods=['post'])
    def create_account(self, request):
        """新增一个指定身份的账号。

        接口：POST /api/accounts/admin/create/
        权限：IsAuthenticated + 管理员。
        参数：role（user/admin/heritage）、username，以及可选的 password、name、phone、email。
        返回：201 + 新账号序列化数据；角色未知或管理员重复时返回 400。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        serializer = AdminCreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        role = d['role']
        Model = MODEL_MAP.get(role)
        if not Model:
            return Response({'msg': '未知角色'}, status=status.HTTP_400_BAD_REQUEST)
        # 业务约束：系统只允许存在一个管理员账号
        if role == 'admin' and Admin.objects.exists():
            return Response({'msg': '系统只允许存在一个管理员账号'}, status=status.HTTP_400_BAD_REQUEST)
        # create_user 内部会做密码哈希，未填密码时用默认密码 123456
        account = Model.objects.create_user(
            username=d['username'],
            password=d.get('password', '123456'),
            name=d.get('name', ''),
            phone=d.get('phone', ''),
            email=d.get('email', ''),
            status='active',
        )
        write_log(request, 'create', '新增账号',
                  f'新增{account.role}账号「{account.username}」')
        return Response(account_serializer_data(account), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def issue_inheritor(self, request):
        """给传承人发放登录账号（自动落在传承人表）。

        接口：POST /api/accounts/admin/issue-inheritor/
        权限：IsAuthenticated + 管理员。
        参数：username 必填，password/name/phone/email 可选，密码缺省为 123456。
        返回：201 + 新建传承人账号的序列化数据。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        serializer = CreateInheritorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inheritor = serializer.save()
        write_log(request, 'create', '发放传承人账号',
                  f'发放传承人账号「{inheritor.username}」')
        return Response(account_serializer_data(inheritor), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def toggle_status(self, request):
        """启用 / 停用指定账号。

        接口：POST /api/accounts/admin/toggle-status/
        权限：IsAuthenticated + 管理员。
        参数：role、id（账号主键）。
        返回：更新后的账号数据；参数错误 400、账号不存在 404、要停用唯一管理员时 400。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        role = request.data.get('role', 'user')
        account_id = request.data.get('id')
        Model = MODEL_MAP.get(role)
        if not Model or account_id is None:
            return Response({'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        account = Model.objects.filter(pk=account_id).first()
        if not account:
            return Response({'msg': '账号不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 保护性判断：不能让系统里最后一个可用管理员被停用，否则后台无人可管
        if role == 'admin' and account.status == 'active' and Admin.objects.filter(status='active').count() <= 1:
            return Response({'msg': '不能停用唯一的管理员账号'}, status=status.HTTP_400_BAD_REQUEST)
        # 状态在两值之间翻转：正常 <-> 禁用
        account.status = 'disabled' if account.status == 'active' else 'active'
        account.save()
        write_log(request, 'update', '账号状态变更',
                  f'{account.role}账号「{account.username}」已{account.get_status_display()}')
        return Response(account_serializer_data(account))

    @action(detail=False, methods=['post'])
    def update_account(self, request):
        """编辑账号的账号名、姓名、手机号与邮箱。

        接口：POST /api/accounts/admin/update-account/
        权限：IsAuthenticated + 管理员。
        参数：role、id，以及可选的 username、name、phone、email。
        返回：更新后的账号数据；用户名重复时返回 400。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        role = request.data.get('role', 'user')
        account_id = request.data.get('id')
        Model = MODEL_MAP.get(role)
        if not Model or account_id is None:
            return Response({'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        account = Model.objects.filter(pk=account_id).first()
        if not account:
            return Response({'msg': '账号不存在'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUpdateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        username = d.get('username')
        # 用户名在三张账号表中共用一个命名空间，改名时需排除自己后再查重
        if username and username != account.username:
            for M in (User, Admin, Inheritor):
                if M.objects.exclude(pk=account.pk).filter(username=username).exists():
                    return Response({'msg': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
        # 只允许修改这几个基础字段，其余字段（如密码、状态）走各自专用接口
        for f in ('username', 'name', 'phone', 'email'):
            if f in d:
                setattr(account, f, d[f])
        account.save()
        write_log(request, 'update', '编辑账号', f'编辑{account.role}账号「{account.username}」资料')
        return Response(account_serializer_data(account))

    def _account_impact(self, role, account):
        """统计账号名下关联的数据量，供删除前风险提示使用。

        参数：
            role: 账号身份（user / heritage）。
            account: 待删除的账号实例。
        返回：
            [(中文名称, 条数)] 列表，只保留条数大于 0 的项；管理员返回空列表。
        """
        # 延迟导入：避免应用启动阶段 accounts 与业务应用相互导入
        from orders.models import Order
        from products.models import Favorite, Product
        from courses.models import Course
        from skills.models import Skill
        from heritage.models import HeritageProfile
        from students.models import Student

        if role == 'user':
            items = (
                ('报名记录', Student.objects.filter(user=account).count()),
                ('订单', Order.objects.filter(buyer_user=account).count()),
                ('收藏', Favorite.objects.filter(user=account).count()),
            )
        elif role == 'heritage':
            items = (
                ('传承人档案', HeritageProfile.objects.filter(account=account).count()),
                ('技艺档案', Skill.objects.filter(owner=account).count()),
                ('课程', Course.objects.filter(owner=account).count()),
                ('作品', Product.objects.filter(owner=account).count()),
            )
        else:
            # 管理员账号没有业务归属数据，无需提示
            items = ()
        return [(label, n) for label, n in items if n]

    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """删除账号；若名下有业务数据则先提示影响范围再确认删除。

        接口：POST /api/accounts/admin/delete-account/
        权限：IsAuthenticated + 管理员。
        参数：role、id，以及可选的 confirm（确认标记）。
        返回：首次命中关联数据时返回 409 + need_confirm 与 impact 清单；
              带 confirm 再次提交或本无关联数据时真正删除并返回 {msg, impact}。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        role = request.data.get('role', 'user')
        account_id = request.data.get('id')
        Model = MODEL_MAP.get(role)
        if not Model or account_id is None:
            return Response({'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        account = Model.objects.filter(pk=account_id).first()
        if not account:
            return Response({'msg': '账号不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 禁止删除当前正在操作的账号，避免管理员把自己删掉后无法登录
        if role == role_of_account(request.user) and account.pk == request.user.pk:
            return Response({'msg': '不能删除当前登录的账号'}, status=status.HTTP_400_BAD_REQUEST)
        # 系统至少保留一个管理员账号
        if role == 'admin' and Admin.objects.count() <= 1:
            return Response({'msg': '系统至少保留一个管理员账号'}, status=status.HTTP_400_BAD_REQUEST)

        # 先算清名下关联数据；有数据时必须带 confirm 再次提交
        impact = self._account_impact(role, account)
        if impact and not _truthy(request.data.get('confirm')):
            detail = '、'.join(f'{label} {n} 条' for label, n in impact)
            return Response({
                'msg': f'该账号名下还有 {detail}。删除后这些记录会失去归属（档案/课程/作品本身保留，但不再关联该账号），确认删除请再次提交。',
                'need_confirm': True,
                'impact': [{'label': label, 'count': n} for label, n in impact],
            }, status=status.HTTP_409_CONFLICT)

        # 删除后日志里仍要展示原账号名，所以先暂存再删除
        username, name = account.username, account.name
        account.delete()
        write_log(request, 'delete', '删除账号', f'删除{role}账号「{username}」')
        return Response({'msg': f'已删除账号「{name or username}」', 'impact': [{'label': l, 'count': n} for l, n in impact]})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """管理员把账号密码重置为初始密码 123456。

        接口：POST /api/accounts/admin/reset-password/
        权限：IsAuthenticated + 管理员。
        参数：role、id（账号主键）。
        返回：{msg} 提示；参数错误 400、账号不存在 404。
        """
        denied = self._require_admin(request)
        if denied:
            return denied
        role = request.data.get('role', 'user')
        account_id = request.data.get('id')
        Model = MODEL_MAP.get(role)
        if not Model or account_id is None:
            return Response({'msg': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        account = Model.objects.filter(pk=account_id).first()
        if not account:
            return Response({'msg': '账号不存在'}, status=status.HTTP_404_NOT_FOUND)
        # set_password 负责重新哈希，保存后旧密码立即失效
        account.set_password('123456')
        account.save()
        write_log(request, 'update', '重置账号密码',
                  f'重置{account.role}账号「{account.username}」的密码')
        return Response({'msg': f'已重置 {account.name or account.username} 的密码为 123456'})
