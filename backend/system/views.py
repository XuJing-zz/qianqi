# system/views.py —— 系统管理模块的接口实现
# 提供操作日志的查询与 CSV 导出、联系留言的提交与处理、系统配置的读取与保存、
# LOGO 上传以及演示数据初始化。统一挂载在 /api/system/ 前缀下，路由见 system/urls.py。

import csv
import io
import os
import subprocess
import sys
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from common.logging import AutoLogMixin, client_ip, write_log
from common.pagination import OptInPagination
from common.uploads import save_upload_file
from .models import OperationLog, SystemConfig, FeedbackMessage
from .serializers import OperationLogSerializer, SystemConfigSerializer, FeedbackMessageSerializer


class OperationLogViewSet(viewsets.ModelViewSet):
    """操作日志接口：日志列表/详情查询、手工补记日志、导出 Excel 可读的 CSV。

    路由：GET    /api/system/logs/            分页查询日志（支持 type、keyword、page、page_size）
         GET    /api/system/logs/{id}/       查看单条日志
         POST   /api/system/logs/            新增日志（ip、time 由后端自动填充）
         GET    /api/system/logs/export/     导出全部日志为 CSV
    权限：需登录且用户 role 为 admin；仅开放查询与新增，不提供修改和删除。
    """

    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptInPagination
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        """按角色和查询条件过滤日志列表。

        参数：从 URL 查询串读取 type（日志类型）与 keyword（模糊匹配操作人/操作/详情/IP）。
        返回：过滤后的 QuerySet；非管理员返回空集，保证越权时也查不到任何日志。
        """
        qs = super().get_queryset()
        # 权限判断：只有管理员能看到日志，其他角色一律返回空结果
        if self.request.user.role != 'admin':
            qs = qs.none()
        type_q = self.request.query_params.get('type')
        if type_q:
            qs = qs.filter(type=type_q)
        # 关键字检索：多个字段做 OR 模糊匹配，关键词前后空格先去掉
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(operator__icontains=kw) | Q(action__icontains=kw)
                | Q(detail__icontains=kw) | Q(ip__icontains=kw)
            )
        return qs

    def perform_create(self, serializer):
        """新增日志时由服务端补齐时间与来源 IP，避免前端伪造。

        参数：serializer 为已校验的操作日志序列化器；无返回值。
        """
        serializer.save(
            time=timezone.now().strftime('%Y-%m-%d %H:%M'),
            ip=client_ip(self.request),
        )

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出操作日志为 CSV 文件。

        路由：GET /api/system/logs/export/
        参数：沿用列表接口的 type、keyword 过滤条件。
        返回：CSV 附件响应（HttpResponse），文件名带导出时间戳；
             非管理员返回 403。
        """
        # 导出属于批量读取，再次校验管理员身份，避免绕过列表权限
        if request.user.role != 'admin':
            return Response({'msg': '无权导出'}, status=status.HTTP_403_FORBIDDEN)
        qs = self.get_queryset().order_by('-id')
        buf = io.StringIO()
        # 先写入 UTF-8 BOM，否则用 Excel 打开中文会乱码
        buf.write('﻿')
        writer = csv.writer(buf)
        writer.writerow(['日志ID', '时间', '类型', '操作人', '操作IP', '操作', '详情'])
        for log in qs:
            writer.writerow([
                log.id, log.time, log.get_type_display(),
                log.operator, log.ip, log.action, log.detail,
            ])
        filename = 'operation_logs_{}.csv'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
        # 用 attachment 让浏览器直接下载而不是在线预览
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


class FeedbackMessageViewSet(AutoLogMixin, viewsets.ModelViewSet):
    """联系留言接口：前台访客提交留言，后台管理员查看、回复和删除。

    路由：POST   /api/system/messages/          访客提交留言（公开，无需登录）
         GET    /api/system/messages/          管理员分页查询留言（支持 status、keyword）
         PATCH  /api/system/messages/{id}/     修改处理状态或填写回复
         DELETE /api/system/messages/{id}/     删除留言
    权限：仅 create 允许匿名访问，其余操作需登录且 role 为 admin。
    说明：继承 AutoLogMixin，新增/修改/删除会自动写入操作日志。
    """

    auto_log_name = '留言'
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackMessageSerializer
    pagination_class = OptInPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        """按当前 action 动态返回权限类。

        返回：create 动作返回 [AllowAny()]（前台可匿名提交留言），
             其他动作返回 [IsAuthenticated()] 要求登录。
        """
        # 只有提交留言开放给未登录访客，其余接口必须登录
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """按角色和查询条件过滤留言列表。

        参数：从查询串读取 status（new/handled）与 keyword（多字段模糊匹配）。
        返回：过滤后的 QuerySet；非管理员返回空集，防止看到他人留言。
        """
        qs = super().get_queryset()
        # 权限判断：留言只对管理员可见，普通用户无法浏览
        if self.request.user.role != 'admin':
            return qs.none()
        # 状态筛选：只接受约定的两个值，非法值忽略而不报错
        status_q = self.request.query_params.get('status')
        if status_q in ('new', 'handled'):
            qs = qs.filter(status=status_q)
        kw = (self.request.query_params.get('keyword') or '').strip()
        if kw:
            qs = qs.filter(
                Q(name__icontains=kw) | Q(contact__icontains=kw)
                | Q(subject__icontains=kw) | Q(message__icontains=kw)
                | Q(reply__icontains=kw)
            )
        return qs


class SystemConfigViewSet(viewsets.ViewSet):
    """系统配置接口：读取站点基础配置与首页配置、保存配置、上传 LOGO、初始化演示数据。

    路由：GET  /api/system/config/all/           读取 system 与 home 两组配置（公开）
         POST /api/system/config/save/          保存配置（仅管理员）
         POST /api/system/config/upload_logo/   上传系统 LOGO（仅管理员）
         POST /api/system/config/init/          重建演示数据（仅管理员）
    权限：默认需登录，all 动作额外放开为允许匿名访问。
    """

    permission_classes = [IsAuthenticated]

    def _get_or_default(self, key, default=None):
        """取出指定键的配置对象，不存在则按默认值创建。

        参数：key 配置键；default 默认配置内容，为空时用空字典。
        返回：SystemConfig 实例（保证一定存在）。
        """
        # get_or_create 避免并发或首次访问时因记录缺失而报错
        obj, _ = SystemConfig.objects.get_or_create(key=key, defaults={'value': default or {}})
        return obj

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def all(self, request):
        """一次性返回前台需要的全部配置。

        路由：GET /api/system/config/all/
        权限：允许匿名访问，前台首页渲染前无需登录即可读取。
        返回：{'system': 基础配置字典, 'home': 首页配置字典}。
        """
        system = self._get_or_default('system', {}).value
        home = self._get_or_default('home', {}).value
        return Response({'system': system, 'home': home})

    @action(detail=False, methods=['post'])
    def save(self, request):
        """保存系统基础配置和首页配置。

        路由：POST /api/system/config/save/
        参数：请求体中的 system、home 两组配置，传 null 表示该组不修改。
        返回：成功时 {'msg': '已保存'}；非管理员返回 403。
        """
        # 权限判断：配置影响全站，仅管理员可写
        if request.user.role != 'admin':
            return Response({'msg': '无权修改配置'}, status=status.HTTP_403_FORBIDDEN)
        system_val = request.data.get('system')
        home_val = request.data.get('home')
        # 分组更新：只保存请求里显式传入的那一组，未传的保持原值
        if system_val is not None:
            obj = self._get_or_default('system', {})
            obj.value = system_val
            obj.save()
        if home_val is not None:
            obj = self._get_or_default('home', {})
            obj.value = home_val
            obj.save()
        # 配置变更属于敏感操作，写一条操作日志便于追溯
        write_log(request, 'update', '系统配置修改', '管理员保存了系统基础配置/首页内容配置')
        return Response({'msg': '已保存'})

    @action(detail=False, methods=['post'])
    def upload_logo(self, request):
        """上传系统 LOGO 图片并返回访问地址。

        路由：POST /api/system/config/upload_logo/，表单字段名 file。
        参数：file 为图片文件；由 save_upload_file 校验类型与大小（仅图片、最大 5MB）。
        返回：{'url', 'name', 'size', 'ext'}；非管理员返回 403，校验失败抛 ValidationError。
        """
        # 权限判断：LOGO 属于站点配置，仅管理员可替换
        if request.user.role != 'admin':
            return Response({'msg': '无权修改配置'}, status=status.HTTP_403_FORBIDDEN)
        # 上传校验（扩展名白名单 + 大小上限）统一在 common.uploads 中完成
        data = save_upload_file(request, folder='system_logos', allow=('image',), max_mb=5)
        write_log(request, 'update', '上传系统LOGO', f'上传 LOGO 图片「{data["name"]}」')
        return Response(data)

    @action(detail=False, methods=['post'])
    def init(self, request):
        """调用管理命令 init_demo_data 重建演示数据。

        路由：POST /api/system/config/init/
        权限：仅管理员；会清空并重建业务演示数据，属于高风险操作。
        返回：成功时 {'msg', 'log'}（log 为命令输出最后若干行）；
             超时或命令失败时返回 500 及错误详情。
        """
        # 权限判断：初始化会重置数据，严禁非管理员触发
        if request.user.role != 'admin':
            return Response({'msg': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        # 定位后端根目录（本文件在 system/ 下，向上两级即 backend 根目录）
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        manage = os.path.join(backend_dir, 'manage.py')
        try:
            # 以子进程执行管理命令，设置 600 秒超时避免请求长期挂起
            proc = subprocess.run(
                [sys.executable, manage, 'init_demo_data'],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            return Response(
                {'msg': '初始化超时，请稍后重试（也可在服务器手动执行 python manage.py init_demo_data）'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # 命令返回非 0 视为失败，截取 stderr 末尾 400 字回传，避免暴露过多内部信息
        if proc.returncode != 0:
            err = ((proc.stderr or '').strip() or '未知错误')[-400:]
            return Response({'msg': '初始化失败', 'detail': err}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 只回传输出的最后 14 行，前端用于展示执行过程摘要
        tail = (proc.stdout or '').strip().splitlines()[-14:]
        return Response({'msg': '数据已初始化，演示数据已重建，请重新登录', 'log': tail})
