"""
students 应用的后端接口层。

提供学员报名（StudentViewSet）与培训记录（TrainingRecordViewSet）两组接口，
负责按角色过滤数据、报名/审核/结课的状态流转、培训记录 CSV 导出，
并统一写入操作日志供后台审计。
"""
import csv
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from courses.models import Course
from common.logging import AutoLogMixin, write_log
from common.pagination import OptInPagination
from .models import Student, TrainingRecord
from .serializers import StudentSerializer, TrainingRecordSerializer
from .services import (
    lesson_keys, enroll_user, enroll_staff_proxy, dec_enrolled_on_delete, approve_enrollment,
)


class StudentViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """学员报名接口集。

    URL 前缀为 /api/students/students/（见 students/urls.py 与 config/urls.py），
    所有接口均要求登录（IsAuthenticated）：
    - GET    /api/students/students/                 学员列表，支持 status、course_id、keyword 过滤
    - POST   /api/students/students/                 新增报名（普通用户/管理员与传承人走不同逻辑）
    - GET    /api/students/students/{id}/            学员详情
    - PUT/PATCH /api/students/students/{id}/         修改报名（普通用户仅能改已完成课时）
    - DELETE /api/students/students/{id}/            删除报名并回退课程报名人数
    - POST   /api/students/students/{id}/mark_done/  结课
    - POST   /api/students/students/{id}/approve/    录取审核（仅管理员）
    - POST   /api/students/students/{id}/reject/     驳回审核（仅管理员）
    列表接口使用 OptInPagination：只有传 page 或 page_size 时才分页。
    """

    auto_log_name = '学员'
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_queryset(self):
        """按当前用户角色和查询参数过滤学员数据。

        权限：管理员可见全部；传承人只看自己任课的学员；普通用户只看自己的报名。
        查询参数：status 状态、course_id 课程、keyword 关键字（昵称/手机/课程/老师等）。
        返回值：过滤后的 QuerySet。
        """

        qs = super().get_queryset()
        user = self.request.user
        # 数据行级权限：不同角色只能看到自己范围内的报名记录
        if user.role == 'heritage':
            qs = qs.filter(teacher=user.name)
        elif user.role == 'user':
            qs = qs.filter(user=user)
        status_q = self.request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            # 关键字同时匹配报名快照字段与关联账号字段，方便后台一个输入框搜索
            qs = qs.filter(
                Q(name__icontains=kw) | Q(phone__icontains=kw)
                | Q(course_name__icontains=kw) | Q(teacher__icontains=kw) | Q(craft__icontains=kw)
                | Q(user__username__icontains=kw) | Q(user__nick__icontains=kw)
                | Q(user__name__icontains=kw) | Q(user__phone__icontains=kw)
            )
        return qs

    def perform_create(self, serializer):
        """保存报名记录。

        参数 serializer：已校验的学员序列化器。
        规则：普通用户走 enroll_user（校验课程状态、防止重复报名并回填快照）；
        管理员/传承人走 enroll_staff_proxy（代报名）。
        返回值：无，DRF 随后用 serializer.instance 组装响应。
        """

        # 普通用户报名需回填课程快照与初始状态，代报名则保留后台填写的值
        if getattr(self.request.user, 'role', None) == 'user':
            enroll_user(serializer, self.request)
        else:
            enroll_staff_proxy(serializer, self.request)
        st = serializer.instance
        write_log(
            self.request, 'create', '学员报名',
            f'报名课程「{getattr(st, "course_name", "")}」的学员「{getattr(st, "name", "")}」已登记',
        )

    def _update_user_completed(self, request, *args, **kwargs):
        """普通用户专用更新逻辑：只允许修改 completed（已学课时）字段。

        参数 request：当前请求；kwargs 中的 partial 决定是整体还是局部更新。
        返回值：DRF Response，内容为更新后的学员数据。
        """

        data = {}
        # 字段白名单：即使请求里带了 status、progress 等字段也会被丢弃
        if 'completed' in request.data:
            data['completed'] = request.data['completed']
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # 清除可能存在的预取缓存，保证返回的是刚写入数据库的数据
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/students/students/{id}/ 局部更新报名信息。

        权限：登录用户；普通用户被限制为只能提交 completed 字段。
        返回值：DRF Response。
        """

        if getattr(request.user, 'role', None) == 'user':
            return self._update_user_completed(request, *args, **kwargs)
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """PUT /api/students/students/{id}/ 整体更新报名信息。

        权限：登录用户；普通用户同样被限制为只能修改 completed 字段。
        返回值：DRF Response。
        """

        if getattr(request.user, 'role', None) == 'user':
            return self._update_user_completed(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """删除报名记录，并同步回退课程的已报名人数。

        参数 instance：待删除的 Student 实例；返回值：无。
        """

        # 先扣减课程 enrolled 计数，再删除报名记录，避免脏数据
        dec_enrolled_on_delete(instance)
        instance.delete()

    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        """学员结课：把已学课时补全，进度置为 100%，状态改为已完成。

        对应 URL：POST /api/students/students/{id}/mark_done/
        权限：仅管理员与传承人，其他角色返回 403。
        参数 pk：学员主键。返回值：DRF Response（更新后的学员数据）。
        """

        obj = self.get_object()
        # 角色校验放在取对象之后，便于同时校验数据可见性（传承人只能结自己的学员）
        if request.user.role not in ('admin', 'heritage'):
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        course = Course.objects.filter(pk=obj.course_id).first()
        # 课程存在时用课程课时编号补全 completed，否则保留原有记录
        obj.completed = lesson_keys(course) if course is not None else (obj.completed or [])
        obj.status = 'done'
        obj.progress = 100
        obj.save(update_fields=['status', 'progress', 'completed'])
        write_log(request, 'update', '学员结课', f'学员「{obj.name}」课程「{obj.course_name}」已结课')
        return Response(StudentSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """报名资格审核通过：把待审核报名转为进行中，并占用一个课程名额。

        对应 URL：POST /api/students/students/{id}/approve/
        权限：仅管理员，其他角色返回 403。
        参数 pk：学员主键。返回值：DRF Response（更新后的学员数据或错误提示）。
        """

        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可审核报名资格'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        # 状态流转与名额校验集中在 services.approve_enrollment 中，失败时返回原因
        ok, msg = approve_enrollment(obj)
        if not ok:
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)
        write_log(request, 'review', '报名资格审核',
                  f'录取学员「{obj.name}」报名课程「{obj.course_name}」')
        return Response(StudentSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """报名资格驳回：记录驳回原因，把待审核报名改为已驳回。

        对应 URL：POST /api/students/students/{id}/reject/
        权限：仅管理员，其他角色返回 403。
        参数 pk：学员主键；请求体需带 review_comment 或 note 作为驳回原因。
        返回值：DRF Response（更新后的学员数据或错误提示）。
        """

        if request.user.role != 'admin':
            return Response({'msg': '仅管理员可审核报名资格'}, status=status.HTTP_403_FORBIDDEN)
        obj = self.get_object()
        # 只有待审核状态可以驳回，已录取/已完成的报名不允许回退
        if obj.status != 'review':
            return Response({'msg': '仅待审核报名可驳回'}, status=status.HTTP_400_BAD_REQUEST)
        comment = (request.data.get('review_comment') or request.data.get('note') or '').strip()
        if not comment:
            return Response({'msg': '请填写驳回原因'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = 'rejected'
        obj.review_comment = comment
        obj.save(update_fields=['status', 'review_comment'])
        write_log(request, 'review', '报名资格驳回',
                  f'驳回学员「{obj.name}」报名「{obj.course_name}」，原因：{comment}')
        return Response(StudentSerializer(obj).data)


class TrainingRecordViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """培训记录接口集。

    URL 前缀为 /api/students/training-records/，所有接口均要求登录：
    - GET    /api/students/training-records/               记录列表（支持 course_id、keyword）
    - POST   /api/students/training-records/               新增培训记录
    - GET    /api/students/training-records/{id}/          记录详情
    - PUT/PATCH /api/students/training-records/{id}/       修改记录
    - DELETE /api/students/training-records/{id}/          删除记录
    - GET    /api/students/training-records/export/        导出 CSV（普通用户无权访问）
    列表接口同样使用 OptInPagination，仅传 page/page_size 时才分页。
    """

    auto_log_name = '培训记录'
    queryset = TrainingRecord.objects.select_related('course').all()
    serializer_class = TrainingRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination

    def get_queryset(self):
        """按角色与查询参数过滤培训记录。

        权限：普通用户不可见（返回空集）；传承人只看自己授课或自己课程下的记录；
        管理员可见全部。
        查询参数：course_id 课程、keyword 关键字（课程名/老师/内容/备注）。
        返回值：过滤后的 QuerySet。
        """

        qs = super().get_queryset()
        user = self.request.user
        # 普通学员与培训记录无关，直接返回空集，避免越权查看教学数据
        if user.role == 'user':
            qs = qs.none()
        elif user.role == 'heritage':
            qs = qs.filter(Q(teacher=user.name) | Q(course__owner=user))
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(course_name__icontains=kw) | Q(teacher__icontains=kw)
                | Q(content__icontains=kw) | Q(remark__icontains=kw)
            )
        return qs

    def perform_create(self, serializer):
        """新增培训记录：未指定授课人时，传承人自动记为本人。

        参数 serializer：已校验的培训记录序列化器；返回值：无。
        """

        data = self.request.data
        # 传承人新增记录时默认以自己作为授课人，管理员可手动指定
        teacher = data.get('teacher') or (
            self.request.user.name if self.request.user.role == 'heritage' else ''
        )
        serializer.save(teacher=teacher)
        self._log_obj(self.request, 'create', '新增', serializer.instance)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出培训记录为 CSV 文件。

        对应 URL：GET /api/students/training-records/export/
        权限：普通用户返回 403，管理员与传承人可导出各自可见的数据。
        参数 request：当前请求。返回值：HttpResponse，浏览器下载 CSV 文件。
        """

        if request.user.role == 'user':
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        # 复用 get_queryset 的结果，保证导出内容与列表看到的数据范围一致
        qs = self.get_queryset()
        filename = '培训记录.csv'
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        # 写入 UTF-8 BOM，避免 Excel 打开中文内容时乱码
        response.write('﻿'.encode('utf-8'))

        writer = csv.writer(response)
        writer.writerow(['记录ID', '课程ID', '课程名', '授课传承人', '培训时间', '培训内容', '出勤人数', '出勤明细', '考核明细', '备注'])
        for r in qs:
            # 把 JSON 形式的出勤表/考核表拼成可读文本，方便用表格软件查看
            attendance = r.attendance or []
            attendance_txt = '；'.join(
                f"{a.get('name', '')}({'出勤' if a.get('status') == 'present' else '缺勤'})"
                for a in attendance
            )
            assessment_txt = '；'.join(f"{k}:{v}" for k, v in (r.assessment or {}).items())
            writer.writerow([
                r.id,
                r.course_id,
                r.course_name,
                r.teacher,
                r.record_time.strftime('%Y-%m-%d %H:%M'),
                r.content,
                len(attendance),
                attendance_txt,
                assessment_txt,
                r.remark,
            ])
        return response
