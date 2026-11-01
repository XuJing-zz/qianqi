# heritage/views.py —— 传承人档案的接口层（DRF ViewSet）
# 提供档案的增删改查、在职状态切换、传承人「我的主页」和证书上传接口，
# 路由注册见 heritage/urls.py，由 config/urls.py 挂载在 /api/heritage/ 下，
# 权限按角色分级：游客只读、传承人维护本人档案、管理员负责录入与删除。

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.permissions import IsStaffRole
from common.logging import write_log
from common.pagination import OptInPagination
from common.uploads import save_upload_file
from .models import HeritageProfile
from .serializers import HeritageProfileSerializer


class IsAdmin(IsAuthenticated):
    """管理员专用权限类：在登录校验之上要求当前账号角色为 admin。

    用于 toggle_status 这类只允许管理员调用的动作。
    """

    def has_permission(self, request, view):
        """判断当前请求是否来自已登录的管理员。

        参数：request 为 DRF 请求对象（含 user）；view 为当前视图实例。
        返回：bool，True 放行；False 由 DRF 转成 401/403。
        """
        # 先做登录校验，未登录直接拒绝，避免匿名用户走到角色判断
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'admin'


class HeritageProfileViewSet(viewsets.ModelViewSet):
    """传承人档案视图集，路由前缀 /api/heritage/profiles/。

    标准动作：GET 列表、GET 详情（游客可访问）；POST 新增（仅管理员）；
    PUT/PATCH 修改（档案对应的传承人本人或管理员）；DELETE 删除（仅管理员）。
    额外动作：POST {id}/toggle_status/ 切换在职状态、GET my/ 查看本人档案、
    POST upload_cert/ 上传荣誉证书。
    queryset 用 select_related 预取关联账号，避免列表页逐条回查账号表。
    """

    queryset = HeritageProfile.objects.select_related('account').all()
    serializer_class = HeritageProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_permissions(self):
        """按动作动态决定权限：查询类动作公开，其余沿用动作上声明的权限类。

        返回值：权限类实例列表，交给 DRF 逐个校验。
        """
        # 列表与详情是公开主页内容，允许游客浏览；离岗档案已在 get_queryset 中被过滤
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        # 其余动作读取 @action(permission_classes=...) 的声明，未声明则要求登录
        handler = getattr(self, self.action, None)
        declared = (getattr(handler, 'kwargs', None) or {}).get('permission_classes')
        if declared:
            return [p() for p in declared]
        return [IsAuthenticated()]

    def get_queryset(self):
        """在基础查询集上叠加可见性过滤和列表筛选条件。

        查询参数：level（传承等级）、status（在职状态）、keyword（模糊关键词）。
        返回值：过滤后的 QuerySet，供列表和详情动作共用。
        """
        qs = super().get_queryset()
        user = getattr(self.request, 'user', None)
        # 可见性控制：非管理员看不到离岗档案，前台展示的都是在职传承人
        if getattr(user, 'role', None) != 'admin':
            qs = qs.exclude(status='leave')
        level = self.request.query_params.get('level')
        status_q = self.request.query_params.get('status')
        # 等级与状态为精确匹配，参数为空时忽略该条件
        if level:
            qs = qs.filter(level=level)
        if status_q:
            qs = qs.filter(status=status_q)
        kw = (self.request.query_params.get('keyword') or '').strip()
        # 关键词在姓名、电话、技艺、师承、简介中任一命中即返回（Q 对象用 | 组合成 OR）
        if kw:
            qs = qs.filter(
                Q(name__icontains=kw) | Q(phone__icontains=kw)
                | Q(craft__icontains=kw) | Q(mentor__icontains=kw)
                | Q(intro__icontains=kw)
            )
        return qs

    def update(self, request, *args, **kwargs):
        """编辑档案，PUT 与 PATCH 共用这一入口。

        URL：/api/heritage/profiles/{id}/；请求方法：PUT 或 PATCH；
        权限：传承人本人（heritage 角色且档案 account 是自己）或管理员。
        返回：200 + 更新后的档案数据；角色不符或越权时返回 403 及提示信息。
        """
        # 角色门槛：学员等其他角色一律不允许改动档案
        role = request.user.role
        if role not in ('heritage', 'admin'):
            return Response({'msg': '仅传承人本人或管理员可编辑档案'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        # 传承人只能改自己的档案：直接比较外键值 account_id，省去一次账号查询
        if role == 'heritage' and obj.account_id != request.user.id:
            return Response(
                {'msg': '只能编辑自己的档案'},
                status=status.HTTP_403_FORBIDDEN,
            )
        resp = super().update(request, *args, **kwargs)
        # 写操作成功后记一条审计日志，便于后台追溯
        write_log(request, 'update', '编辑传承人档案', f'编辑传承人「{obj.name}」档案')
        return resp

    def partial_update(self, request, *args, **kwargs):
        """PATCH 局部更新，复用 update 的权限判断与日志逻辑。

        参数：request 为 DRF 请求；kwargs 含路由中的 pk。
        返回值：与 update 相同。
        """
        # 交给 update 统一处理，用 partial 标记让序列化器只校验传入的字段
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """录入新的传承人档案。

        URL：/api/heritage/profiles/；请求方法：POST；权限：仅管理员。
        请求体可附带 account_id 直接绑定已有登录账号。
        返回：201 + 新建档案数据；账号不存在或该账号已绑定档案时返回 400，
        并且会先删除刚创建的记录，避免留下脏数据。
        """
        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可录入传承人档案'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # 账号绑定单独处理：account 不在序列化器的可写字段里，属于可选的后置关联
        link = request.data.get('account_id')
        if link:
            from accounts.models import Inheritor
            acc = Inheritor.objects.filter(pk=link).first()
            # 目标账号不存在：回滚刚建好的档案再返回错误
            if not acc:
                instance.delete()
                return Response({'msg': '要关联的传承人账号不存在'}, status=status.HTTP_400_BAD_REQUEST)
            # 一对一约束：该账号已有档案时拒绝重复发放
            if HeritageProfile.objects.filter(account=acc).exists():
                instance.delete()
                return Response({'msg': '该传承人账号已有关联档案，无需重复发放'}, status=status.HTTP_400_BAD_REQUEST)
            instance.account = acc
            # 只更新 account 一列，缩小写库范围
            instance.save(update_fields=['account'])
        write_log(request, 'create', '录入传承人档案', f'录入传承人「{instance.name}」档案')
        headers = self.get_success_headers(serializer.data)
        # 重新序列化 instance，保证响应里带上刚补绑的账号信息
        return Response(HeritageProfileSerializer(instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """删除档案。

        URL：/api/heritage/profiles/{id}/；请求方法：DELETE；权限：仅管理员。
        返回：204 无内容；非管理员返回 403。
        """
        if request.user.role != 'admin':
            return Response({'msg': '无权删除'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        # 先取出姓名：对象删除后就无法再读取属性，而日志需要记录被删的是谁
        name = obj.name
        resp = super().destroy(request, *args, **kwargs)
        write_log(request, 'delete', '删除传承人档案', f'删除传承人「{name}」档案')
        return resp

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_status(self, request, pk=None):
        """切换传承人的在职 / 离岗状态。

        URL：/api/heritage/profiles/{id}/toggle_status/；请求方法：POST；
        权限：仅管理员（本动作的 permission_classes 声明为 IsAdmin）。
        参数：pk 为档案主键。返回：200 + 更新后的档案数据。
        """
        obj = self.get_object()
        # 状态是二值互斥的，取反后再保存即可完成流转
        obj.status = 'leave' if obj.status == 'active' else 'active'
        obj.save()
        # 日志用 get_status_display() 输出中文状态名，而不是数据库里的英文取值
        write_log(
            request, 'update', '传承人在职状态',
            f'传承人「{obj.name}」调整为{obj.get_status_display()}',
        )
        return Response(HeritageProfileSerializer(obj).data)

    @action(detail=False, methods=['get'])
    def my(self, request):
        """查询当前传承人自己的公开档案。

        URL：/api/heritage/profiles/my/；请求方法：GET；权限：登录且角色为 heritage。
        返回：200 + 档案数据；角色不符返回 403；尚未建档返回 404。
        """
        # 该接口只服务于传承人本人的「我的主页」，其他角色一律拒绝
        if request.user.role != 'heritage':
            return Response({'msg': '仅传承人可访问自己的主页'}, status=status.HTTP_403_FORBIDDEN)
        # account 是一对一关系，最多命中一条；查不到说明管理员还没为其建档
        profile = HeritageProfile.objects.filter(account=request.user).first()
        if not profile:
            return Response({'msg': '尚未开通公开主页'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HeritageProfileSerializer(profile).data)

    @action(detail=False, methods=['post'], permission_classes=[IsStaffRole])
    def upload_cert(self, request):
        """上传荣誉证书附件，返回文件信息供前端写入 cert_files 字段。

        URL：/api/heritage/profiles/upload_cert/；请求方法：POST（multipart，字段名 file）；
        权限：管理员或传承人（IsStaffRole）。
        上传校验：只允许图片与文档类扩展名，单文件不超过 20MB，且受「系统配置」里的总开关约束；
        校验失败时由 save_upload_file 抛出 400 校验错误。
        返回：200 + {'url', 'name', 'size', 'ext'}。
        """
        # 传参说明：folder 指定媒体目录下的子目录，allow 限定文件类别，max_mb 为大小上限
        return Response(save_upload_file(request, folder='heritage_certs', allow=('image', 'doc'), max_mb=20))
