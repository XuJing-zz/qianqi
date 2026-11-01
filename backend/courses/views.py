"""
课程模块的接口视图。

基于 DRF ModelViewSet 提供课程的增删改查、提交审核、审核与下架，
以及封面/教学视频上传和课时视频审核；同时按用户角色过滤可见数据。
"""

import re
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.permissions import IsHeritageRole, IsStaffRole, OwnerOrAdminWrite
from common.logging import AutoLogMixin, write_log
from common.uploads import save_upload_file, get_upload_limits
from students.models import Student
from common.pagination import OptInPagination
from .models import Course
from .serializers import CourseSerializer, CourseReviewSerializer, VideoReviewSerializer


def _les(les, camel, default=''):
    """
    读取课时字典中的字段，兼容驼峰与下划线两种键名。

    :param les: 单个课时的字典，非字典时直接返回 default
    :param camel: 驼峰风格键名，如 videoStatus
    :param default: 两种键名都不存在时的默认返回值
    :return: 字段值，缺失时返回 default
    """
    if not isinstance(les, dict):
        return default
    if camel in les:
        return les[camel]
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()
    return les.get(snake, default)


class CourseViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """
    课程资源视图集，提供课程列表、详情、创建、修改及审核类自定义动作。

    接口前缀为 /api/courses/，主要端点：
    GET    /api/courses/                    课程列表（匿名可访问，默认只见已通过课程）
    POST   /api/courses/                    创建课程（仅传承人）
    GET    /api/courses/{id}/               课程详情（匿名可访问）
    PATCH  /api/courses/{id}/               修改课程（本人或管理员）
    POST   /api/courses/{id}/review/        课程审核（仅管理员）
    POST   /api/courses/{id}/submit/        提交审核（本人或管理员）
    POST   /api/courses/{id}/offline/       课程下架（本人或管理员）
    POST   /api/courses/upload/             上传教学视频（传承人/管理员）
    POST   /api/courses/cover/              上传封面图（传承人/管理员）
    GET    /api/courses/video_reviews/      课时视频审核列表（仅管理员）
    POST   /api/courses/{id}/review_video/  课时视频审核（仅管理员）

    具体权限由 get_permissions 依据 self.action 动态分配。
    """

    auto_log_name = '课程'
    queryset = Course.objects.select_related('owner').all()
    serializer_class = CourseSerializer
    pagination_class = OptInPagination
    # 不开放 PUT/DELETE：课程只做局部更新，下架通过 offline 动作完成
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        """
        按当前 action 返回接口权限。

        list/retrieve 允许匿名访问；create 仅传承人；update/partial_update/destroy
        需管理员或传承人并通过对象级归属校验；offline/upload/cover 仅管理员与传承人。

        :return: 权限实例列表
        """
        # 课程列表与详情对前台公开，无需登录
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        # 只有传承人才能申报课程
        if self.action == 'create':
            return [IsHeritageRole()]
        # 先校验角色，再由 OwnerOrAdminWrite 判断是否为本人课程
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsStaffRole(), OwnerOrAdminWrite()]
        if self.action in ('offline', 'upload', 'cover'):
            return [IsStaffRole()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        """
        在序列化上下文中补充当前用户角色与已报名课程 ID 集合。

        CourseSerializer 依据这些信息决定是否返回课时视频等受限字段。

        :return: 序列化上下文字典
        """
        ctx = super().get_serializer_context()
        user = getattr(self.request, 'user', None)
        role = getattr(user, 'role', None) if user is not None and user.is_authenticated else None
        ctx['role'] = role
        enrolled_ids = set()
        # 只有学员需要「已报名课程」集合，用于放行已报名课程的完整课时信息
        if role == 'user':
            enrolled_ids = set(Student.objects.filter(user=user).values_list('course_id', flat=True))
        ctx['enrolled_ids'] = enrolled_ids
        return ctx

    def get_queryset(self):
        """
        按当前用户角色过滤可见课程，并支持按状态筛选。

        :return: 过滤后的 Course 查询集
        """
        qs = super().get_queryset()
        user = self.request.user
        # 传承人只能看到自己申报的课程（含草稿与被驳回的）
        if user.is_authenticated and user.role == 'heritage':
            qs = qs.filter(owner=user)
        # 未登录用户与其他角色只能看到审核通过的课程
        elif not user.is_authenticated or user.role != 'admin':
            qs = qs.filter(status='approved')
        status_q = self.request.query_params.get('status')
        # status 参数只对管理员与传承人生效，避免前台越权查看草稿
        if status_q and user.is_authenticated and user.role in ('admin', 'heritage'):
            qs = qs.filter(status=status_q)
        return qs

    def perform_create(self, serializer):
        """
        保存新课程并把当前用户设为所属传承人，随后记录操作日志。

        :param serializer: 已通过校验的 CourseSerializer
        """
        serializer.save(owner=self.request.user)
        self._log_obj(self.request, 'create', '新增', serializer.instance)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        管理员审核课程，通过或驳回。

        URL: POST /api/courses/{id}/review/
        权限: 仅 admin 角色（方法内二次校验）。

        :param request: 含 action(approve/reject) 与 review_comment 的请求
        :param pk: 课程主键
        :return: 审核后的课程序列化数据
        """
        if request.user.role != 'admin':
            return Response({'msg': '无权审核'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        s = CourseReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        action = s.validated_data['action']
        comment = (s.validated_data.get('review_comment') or '').strip()
        # 驳回必须写明原因，方便传承人按意见修改后重新提交
        if action == 'reject' and not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        # 写回审核结果：通过时清空上一次的驳回意见
        obj.status = 'approved' if action == 'approve' else 'rejected'
        obj.review_comment = '' if action == 'approve' else comment
        obj.save()
        write_log(
            request, 'review', '课程审核',
            f'{"通过" if action == "approve" else "驳回"}课程「{obj.name}」'
            + (f'，原因：{comment}' if comment else ''),
        )
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        把课程提交为待审核状态。

        URL: POST /api/courses/{id}/submit/
        权限: 课程所属传承人本人或管理员。

        :param request: 当前请求
        :param pk: 课程主键
        :return: 提交后的课程序列化数据
        """
        obj = self.get_object()
        # 归属校验：既不是本人课程也不是管理员时拒绝
        if obj.owner_id != request.user.id and request.user.role != 'admin':
            return Response({'msg': '只能提交自己的课程'}, status=status.HTTP_403_FORBIDDEN)
        obj.status = 'pending'
        obj.save()
        write_log(request, 'review', '提交课程审核', f'提交课程「{obj.name}」待审核')
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def offline(self, request, pk=None):
        """
        下架一门已通过审核的课程。

        URL: POST /api/courses/{id}/offline/
        权限: 管理员或课程所属传承人本人；仅 approved 状态可下架。

        :param request: 当前请求
        :param pk: 课程主键
        :return: 下架后的课程序列化数据
        """
        obj = self.get_object()
        # 归属校验：非本人课程且非管理员时拒绝
        if request.user.role != 'admin' and obj.owner_id != request.user.id:
            return Response({'msg': '只能下架自己的课程'}, status=status.HTTP_403_FORBIDDEN)
        # 状态流转限制：仅已上架课程允许下架
        if obj.status != 'approved':
            return Response({'msg': '仅已上架课程可下架'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = 'offline'
        # 只更新状态字段，避免覆盖其他并发修改
        obj.save(update_fields=['status'])
        write_log(request, 'update', '课程下架', f'下架课程「{obj.name}」')
        return Response(self.get_serializer(obj).data)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        上传课程教学视频并返回可访问地址。

        URL: POST /api/courses/upload/（multipart，文件字段名 file）
        权限: 管理员或传承人（IsStaffRole）。

        :param request: 含上传文件的请求
        :return: {url, name, video_status}，新上传视频的审核状态固定为 pending
        """
        file = request.FILES.get('file')
        if file is None:
            return Response({'msg': '未选择文件'}, status=status.HTTP_400_BAD_REQUEST)
        # 先读系统配置：管理员可在「系统配置」中整体关闭视频上传
        limits = get_upload_limits()
        if not limits['allow_video']:
            return Response({'msg': '管理员已在「系统配置」中关闭视频上传'}, status=status.HTTP_400_BAD_REQUEST)
        # 扩展名白名单校验（取最后一段后缀并转小写）
        ext = (file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else '')
        if ext not in ('mp4', 'webm', 'mov', 'm4v'):
            return Response({'msg': '仅支持 mp4/webm/mov/m4v 格式的视频'}, status=status.HTTP_400_BAD_REQUEST)
        # 大小上限优先取系统配置，未配置时回退到 settings 默认值
        cap = limits['max_mb'] or settings.MAX_VIDEO_MB
        if file.size > cap * 1024 * 1024:
            return Response({'msg': f'视频不能超过 {cap}MB'}, status=status.HTTP_400_BAD_REQUEST)
        # 用 uuid 重命名，避免同名覆盖和中文文件名兼容问题
        name = f'course_videos/{uuid.uuid4().hex}.{ext}'
        saved = default_storage.save(name, file)
        media_url = settings.MEDIA_URL.rstrip('/')
        url = request.build_absolute_uri(f'{media_url}/{saved}')
        return Response({'url': url, 'name': file.name, 'video_status': 'pending'})

    @action(detail=False, methods=['post'])
    def cover(self, request):
        """
        上传课程封面图。

        URL: POST /api/courses/cover/（multipart，文件字段名 file）
        权限: 管理员或传承人（IsStaffRole）。

        :param request: 含图片文件的请求
        :return: 公共上传工具返回的 {url, name, size, ext}；格式或大小不合法时返回 400
        """
        # 复用公共上传工具：只允许图片类型且不超过 5MB
        res = save_upload_file(request, folder='course_covers', allow=('image',), max_mb=5)
        return Response(res)

    @action(detail=False, methods=['get'])
    def video_reviews(self, request):
        """
        管理员分页查看各课程课时视频的审核列表。

        URL: GET /api/courses/video_reviews/?video_status=&keyword=&page=&page_size=
        权限: 仅 admin 角色。

        :param request: video_status 按审核状态过滤，keyword 匹配课程名/技艺/课时标题
        :return: 视频条目列表；传入 page 或 page_size 时返回分页结构
        """
        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可查看视频审核列表'}, status=status.HTTP_403_FORBIDDEN)
        vstatus = request.query_params.get('video_status')
        kw = (request.query_params.get('keyword') or '').strip().lower()
        items = []
        # 课时是 JSON 字段，需要遍历课程后把每节课展开成扁平列表
        for c in Course.objects.all():
            for idx, les in enumerate(c.lessons or []):
                video = _les(les, 'video') or ''
                # 没有视频的课时不进入审核列表
                if not video:
                    continue
                st = _les(les, 'videoStatus') or ''
                # 按视频审核状态过滤
                if vstatus and st != vstatus:
                    continue
                if kw:
                    hay = f"{c.name} {c.craft or ''} {_les(les, 'title')}".lower()
                    if kw not in hay:
                        continue
                items.append({
                    'course_id': c.id,
                    'course_name': c.name,
                    'craft': c.craft or '',
                    'owner': c.owner.name if c.owner else '',
                    'lesson_index': idx,
                    'num': _les(les, 'num', idx + 1),
                    'title': _les(les, 'title'),
                    'desc': _les(les, 'desc'),
                    'schedule_date': _les(les, 'scheduleDate'),
                    'schedule_time': _les(les, 'scheduleTime'),
                    'video': video,
                    'video_name': _les(les, 'videoName') or video.rsplit('/', 1)[-1],
                    'video_status': st,
                    'video_review_comment': _les(les, 'videoReviewComment'),
                })
        # 数据来自 JSON 展开，直接对列表分页；未传分页参数时返回全量
        paginator = OptInPagination()
        page = paginator.paginate_queryset(items, request, view=self)
        if page is None:
            return Response(items)
        return paginator.get_paginated_response(page)

    @action(detail=True, methods=['post'])
    def review_video(self, request, pk=None):
        """
        管理员审核课程中某一课时的教学视频。

        URL: POST /api/courses/{id}/review_video/
        权限: 仅 admin 角色。

        :param request: 含 lesson_index、action(approve/reject)、review_comment 的请求
        :param pk: 课程主键
        :return: 审核后的课程序列化数据
        """
        if request.user.role != 'admin':
            return Response({'msg': '无权审核视频'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        s = VideoReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        idx = s.validated_data['lesson_index']
        action = s.validated_data['action']
        comment = (s.validated_data.get('review_comment') or '').strip()
        # 驳回必须写明原因
        if action == 'reject' and not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        lessons = obj.lessons or []
        # 下标越界保护，防止写入不存在的课时
        if idx >= len(lessons):
            return Response({'msg': '课时不存在'}, status=status.HTTP_400_BAD_REQUEST)
        # 审核结果写回驼峰键，并清理可能残留的下划线旧键
        lessons[idx]['videoStatus'] = 'approved' if action == 'approve' else 'rejected'
        lessons[idx]['videoReviewComment'] = '' if action == 'approve' else comment
        lessons[idx].pop('video_status', None)
        lessons[idx].pop('video_review_comment', None)
        # JSONField 需整体重新赋值才会被识别为已修改
        obj.lessons = lessons
        obj.save()
        title = _les(lessons[idx], 'title') or f'第{idx + 1}课时'
        write_log(
            request, 'review', '课时视频审核',
            f'{"通过" if action == "approve" else "驳回"}课程「{obj.name}」{title}的视频'
            + (f'，原因：{comment}' if comment else ''),
        )
        return Response(self.get_serializer(obj).data)
