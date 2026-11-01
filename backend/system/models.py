# system/models.py —— 系统管理模块的数据模型定义
# 包含操作日志、联系留言、系统配置三张表，供后台审计、留言处理和站点配置使用。
# 所有模型均显式指定 db_table，便于答辩时对照数据库表结构讲解。

from django.db import models


class OperationLog(models.Model):
    """操作日志模型：记录后台每一次登录、增删改、审核、发货等关键操作，用于事后审计追溯。

    主要字段：type 日志类型、operator 操作人、action 操作摘要、detail 详细内容、
    ip 操作来源 IP、time 展示用时间字符串。
    """

    # 日志类型枚举：数据库存英文值，界面通过 get_type_display() 显示中文
    TYPE_CHOICES = (
        ('login', '登录'),
        ('create', '新增'),
        ('update', '修改'),
        ('delete', '删除'),
        ('review', '审核'),
        ('order', '订单'),
        ('ship', '发货'),
    )

    type = models.CharField('日志类型', max_length=20, choices=TYPE_CHOICES, default='update')
    operator = models.CharField('操作人', max_length=50)
    action = models.CharField('操作', max_length=200)
    detail = models.TextField('详情', blank=True)
    ip = models.CharField('操作IP', max_length=50, blank=True, default='')
    time = models.CharField('时间', max_length=30, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元信息：指定数据库表名、后台显示名称，并按 id 倒序排列（最新日志在前）。"""

        db_table = 'system_operationlog'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-id']

    def __str__(self):
        """返回日志的可读摘要，供 Django 后台和调试输出使用，格式如「[登录] 张三 - 登录系统」。"""
        return f'[{self.get_type_display()}] {self.operator} - {self.action}'


class FeedbackMessage(models.Model):
    """联系留言模型：保存前台访客提交的咨询/建议，管理员后台可查看并回复。

    主要字段：name 称呼、contact 联系方式、message 留言内容、
    status 处理状态（new 待处理 / handled 已处理）、reply 管理员回复。
    """

    # 处理状态枚举：新增留言默认 new，管理员回复后改为 handled
    STATUS_CHOICES = (
        ('new', '待处理'),
        ('handled', '已处理'),
    )

    name = models.CharField('称呼', max_length=50)
    contact = models.CharField('联系方式', max_length=100, blank=True, default='')
    subject = models.CharField('留言事项', max_length=100, blank=True, default='')
    message = models.TextField('留言内容')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='new')
    reply = models.TextField('回复', blank=True, default='')
    created_at = models.DateTimeField('提交时间', auto_now_add=True)

    class Meta:
        """模型元信息：指定表名、后台显示名称，并按 id 倒序排列（最新留言在前）。"""

        db_table = 'system_feedbackmessage'
        verbose_name = '联系留言'
        verbose_name_plural = '联系留言'
        ordering = ['-id']

    def __str__(self):
        """返回留言摘要，包含处理状态、称呼和内容前 20 个字，便于后台列表识别。"""
        return f'[{self.get_status_display()}] {self.name} - {self.message[:20]}'


class SystemConfig(models.Model):
    """系统配置模型：以「键 - JSON 值」形式保存站点基础配置和首页内容配置。

    主要字段：key 配置键（唯一）、value 配置内容（JSON，便于一次保存多条配置）、
    updated_at 最后更新时间。
    """

    key = models.CharField('配置键', max_length=50, unique=True)
    value = models.JSONField('配置值', default=dict, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        """模型元信息：指定表名和后台显示名称；配置按 key 唯一，无固定排序。"""

        db_table = 'system_systemconfig'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self):
        """返回配置键本身，后台下拉和调试时可直接看出是哪一项配置。"""
        return self.key
