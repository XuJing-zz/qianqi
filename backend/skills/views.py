"""技艺档案接口模块（ViewSet）。

集中提供技艺档案的增删改查、组合筛选、图片/文档上传、审核、提交审核与上下架接口，
统一由 SkillViewSet 通过 DRF Router 暴露，实际地址前缀为 /api/skills/skills/。
"""
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.permissions import IsHeritageRole, IsStaffRole, OwnerOrAdminWrite
from common.logging import AutoLogMixin, write_log
from common.pagination import OptInPagination
from common.uploads import save_upload_file
from django.db.models import Q

from .models import Skill
from .serializers import SkillSerializer, SkillReviewSerializer


def _now_str():
    """生成写入 submit_time 字段的时间字符串。

    参数：无。
    返回：str，本地当前时间，格式为 'YYYY-MM-DD HH:MM'。
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M')


class SkillViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """技艺档案视图集：一个类管理该资源的全部接口。

    路由前缀：/api/skills/skills/（config/urls.py 的 api/skills/ 前缀 + router 注册的 skills 资源），
    支持 GET 列表/详情、POST 新增、PUT/PATCH 修改、DELETE 删除，以及 filters、upload、
    upload_doc、categories、review、submit、toggle_offline 等自定义动作。
    权限：列表/详情对游客开放；新增仅传承人；改删限本人或管理员；上传限管理员与传承人；
    其余动作需登录，其中审核仅管理员可做。
    审计：继承 AutoLogMixin，新增/修改/删除会自动写入操作日志。
    """

    auto_log_name = '技艺档案'
    # 列表查询预取所属传承人，避免逐条查库产生 N+1；默认按模型 Meta 的 -id 排序
    queryset = Skill.objects.select_related('owner').all()
    serializer_class = SkillSerializer
    # 分页只在请求带 page/page_size 参数时启用，前端可选择一次性取全量
    pagination_class = OptInPagination

    def get_permissions(self):
        """按当前 action 动态分配权限类，实现同一资源不同接口的差异化鉴权。

        参数：无，内部读取 self.action（Router 解析出的动作名）。
        返回：list，DRF 权限类实例列表；任一权限不通过即返回 403。
        """
        # 列表与详情对游客开放，未登录也能浏览已通过的档案
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        # 新增只允许传承人为自己建档
        if self.action == 'create':
            return [IsHeritageRole()]
        # 修改/删除先要求非学员身份，再做对象级归属校验（本人或管理员）
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsStaffRole(), OwnerOrAdminWrite()]
        # 文件上传只对管理员与传承人开放
        if self.action in ('upload', 'upload_doc'):
            return [IsStaffRole()]
        # 其余动作（filters、categories、review、submit、toggle_offline）至少要求登录
        return [IsAuthenticated()]

    def get_queryset(self):
        """构造列表/详情使用的查询集：先按角色收窄可见范围，再叠加查询参数筛选。

        参数：无，内部读取 self.request.user 与 query_params。
        返回：QuerySet[Skill]，已应用行级权限与可选筛选项。
        """
        qs = super().get_queryset()
        user = self.request.user
        # 行级权限：传承人只看自己的档案，游客与学员只看已通过，管理员看全部
        if user.is_authenticated and user.role == 'heritage':
            qs = qs.filter(owner=user)
        elif not user.is_authenticated or user.role != 'admin':
            qs = qs.filter(status='approved')
        # 状态精确筛选仅对管理员与传承人开放，防止越权查看他人的草稿或待审档案
        status_q = self.request.query_params.get('status')
        if status_q and user.is_authenticated and user.role in ('admin', 'heritage'):
            qs = qs.filter(status=status_q)
        # 以下为列表页的可选筛选项，参数缺失或为空白时忽略
        params = self.request.query_params
        level_q = (params.get('level') or '').strip()
        if level_q:
            qs = qs.filter(level=level_q)
        category_q = (params.get('category') or '').strip()
        if category_q:
            qs = qs.filter(category=category_q)
        difficulty_q = (params.get('difficulty') or '').strip()
        if difficulty_q:
            qs = qs.filter(difficulty=difficulty_q)
        school_q = (params.get('school') or '').strip()
        if school_q:
            qs = qs.filter(school=school_q)
        region_q = (params.get('region') or '').strip()
        if region_q:
            qs = qs.filter(region=region_q)
        # 关键字模糊搜索：命中名称、概述、简介、分类、流派、地区、材料、工具与传承人姓名
        kw = (params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(name__icontains=kw) | Q(abstract__icontains=kw) | Q(desc__icontains=kw)
                | Q(category__icontains=kw) | Q(school__icontains=kw) | Q(region__icontains=kw)
                | Q(raw_materials__icontains=kw) | Q(tools__icontains=kw)
                | Q(owner__name__icontains=kw)
            )
        return qs

    def perform_create(self, serializer):
        """保存新建档案时自动把归属绑定为当前登录用户，并记录操作日志。

        参数：serializer 为已校验通过的 SkillSerializer。
        返回：None。
        """
        # owner 由服务端强制指定，避免前端伪造归属到其他传承人名下
        serializer.save(owner=self.request.user)
        self._log_obj(self.request, 'create', '新增', serializer.instance)

    @action(detail=False, methods=['get'])
    def filters(self, request):
        """返回筛选下拉框的候选值。

        接口：GET /api/skills/skills/filters/；权限：需登录
        （未在 get_permissions 中单列，落到默认的 IsAuthenticated）。
        按当前用户可见范围统计各维度去重值，供前端渲染下拉选项。
        参数：request 为当前请求。
        返回：Response，形如 {'category': [...], 'difficulty': [...], 'region': [...],
        'level': [...], 'school': [...]}。
        """
        user = request.user
        base = Skill.objects.all()
        # 与列表口径保持一致：传承人看自己的，其余非管理员看已通过
        if user.is_authenticated and user.role == 'heritage':
            base = base.filter(owner=user)
        elif not user.is_authenticated or user.role != 'admin':
            base = base.filter(status='approved')

        def distinct(field):
            """取某字段的非空去重值并排序。

            参数：field 为模型字段名（如 'category'）。
            返回：list[str]，已去掉首尾空格并按字典序升序排列。
            """
            # 用集合去重，同时过滤空值，保证返回内容可直接作为下拉项
            vals = base.values_list(field, flat=True)
            return sorted({(v or '').strip() for v in vals if (v or '').strip()})
        return Response({
            'category': distinct('category'),
            'difficulty': distinct('difficulty'),
            'region': distinct('region'),
            'level': distinct('level'),
            'school': distinct('school'),
        })

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """上传技艺图片。

        接口：POST /api/skills/skills/upload/；权限：IsStaffRole（管理员或传承人）。
        表单字段 file 为待上传图片，仅接受图片格式。
        参数：request 携带 FILES['file']。
        返回：Response，含 url/name/size/ext；类型或大小不合规时由公共上传模块抛 ValidationError。
        """
        # max_mb 为默认上限 15MB，系统配置中若设置了更小的全局上限会以配置为准
        return Response(save_upload_file(request, folder='skill_images', allow=('image',), max_mb=15))

    @action(detail=False, methods=['post'])
    def upload_doc(self, request):
        """上传技艺附件文档（也允许顺带传图片）。

        接口：POST /api/skills/skills/upload_doc/；权限：IsStaffRole（管理员或传承人）。
        表单字段 file 为待上传文件，允许图片与 pdf/doc/xls/ppt/txt/压缩包等文档格式。
        参数：request 携带 FILES['file']。
        返回：Response，含 url/name/size/ext；格式或大小不合规时抛 ValidationError。
        """
        # 附件默认上限 20MB，同样受「系统配置」中的全局上传限制约束
        return Response(save_upload_file(request, folder='skill_files', allow=('image', 'doc'), max_mb=20))

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """返回可用技艺分类列表，用于分类导航或筛选。

        接口：GET /api/skills/skills/categories/；权限：需登录（落到默认 IsAuthenticated）。
        数据来源为已通过档案的分类，传承人额外并入自己档案中出现过的分类。
        参数：request 为当前请求。
        返回：Response，str 列表，已去空、去重并升序排列。
        """
        user = request.user
        cats = set(Skill.objects.filter(status='approved').values_list('category', flat=True))
        # 传承人还要看到自己未审核档案里的分类，便于继续维护同分类内容
        if user.is_authenticated and user.role == 'heritage':
            cats.update(Skill.objects.filter(owner=user).values_list('category', flat=True))
        ordered = sorted({c.strip() for c in cats if c and c.strip()})
        return Response(ordered)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """审核单条技艺档案，通过或驳回。

        接口：POST /api/skills/skills/{id}/review/；权限：仅管理员
        （先校验 role，非管理员返回 403）。
        参数：pk 为档案 id；请求体 action 取 approve/reject，review_comment 为审核意见
        （驳回时必填）。
        返回：Response，审核后的档案数据；无权限 403，驳回未填原因 400。
        """
        # 角色先行校验，非管理员直接拒绝，不再查询对象
        if request.user.role != 'admin':
            return Response({'msg': '无权审核'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        s = SkillReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        action = s.validated_data['action']
        comment = (s.validated_data.get('review_comment') or '').strip()
        # 驳回必须说明原因，方便传承人按意见修改后重新提交
        if action == 'reject' and not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        # 状态流转：通过则清空历史审核意见；驳回则保留本次原因
        if action == 'approve':
            obj.status = 'approved'
            obj.review_comment = ''
        else:
            obj.status = 'rejected'
            obj.review_comment = comment
        obj.save()
        # 审核结果写入操作日志，形成可追溯的审核记录
        write_log(
            request, 'review', '技艺档案审核',
            f'{"通过" if action == "approve" else "驳回"}技艺档案「{obj.name}」'
            + (f'，原因：{comment}' if comment else ''),
        )
        return Response(SkillSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """把技艺档案提交审核，状态置为待审核。

        接口：POST /api/skills/skills/{id}/submit/；权限：需登录，
        且仅档案所属传承人本人或管理员可操作。
        参数：pk 为档案 id。
        返回：Response，提交后的档案数据；非本人提交 403。
        """
        obj = self.get_object()
        # 归属校验：只能提交自己名下的技艺，管理员不受限
        if obj.owner_id != request.user.id and request.user.role != 'admin':
            return Response({'msg': '只能提交自己的技艺'}, status=status.HTTP_403_FORBIDDEN)
        # 状态流转：草稿/已驳回/已下架都会回到待审核，并记录本次提交时间
        obj.status = 'pending'
        obj.submit_time = _now_str()
        obj.save()
        write_log(request, 'review', '提交技艺档案审核', f'提交技艺档案「{obj.name}」待审核')
        return Response(SkillSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def toggle_offline(self, request, pk=None):
        """切换技艺档案的上下架状态。

        接口：POST /api/skills/skills/{id}/toggle_offline/；权限：需登录，
        仅档案所属传承人本人或管理员可操作。
        参数：pk 为档案 id。
        返回：Response，切换后的档案数据；当前状态不允许上下架时返回 400。
        """
        obj = self.get_object()
        # 归属校验：只能操作自己名下的技艺，管理员不受限
        if obj.owner_id != request.user.id and request.user.role != 'admin':
            return Response({'msg': '只能操作自己的技艺'}, status=status.HTTP_403_FORBIDDEN)
        # 仅「已通过」与「已下架」之间允许互切，草稿/待审/已驳回没有上架概念
        if obj.status == 'approved':
            obj.status = 'offline'
        elif obj.status == 'offline':
            obj.status = 'approved'
        else:
            return Response({'msg': '当前状态不可上下架'}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        # 记录上下架动作，便于后台追溯档案的可见性变化
        write_log(
            request, 'update', '技艺档案上下架',
            f'{"下架" if obj.status == "offline" else "上架"}技艺档案「{obj.name}」',
        )
        return Response(SkillSerializer(obj).data)
