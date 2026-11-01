"""
课程模块的数据模型。

定义 Course（申报课程）模型，用字段描述课程基本信息、封面与教学视频、
审核状态以及课时 JSON 明细，并声明数据库表名与后台显示名称。
"""

from django.conf import settings
from django.db import models


class Course(models.Model):
    """
    申报课程模型。

    课程由传承人创建后提交审核，状态在 draft/pending/approved/rejected/offline
    之间流转；课时明细以 JSON 数组存放在 lessons 字段中，每个元素描述一节课的
    上课时间、地址与教学视频。
    """

    # 课程状态流转：草稿 -> 待审核 -> 已通过/已驳回，已通过后可下架
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('offline', '已下架'),
    )

    name = models.CharField('课程名称', max_length=200)
    craft = models.CharField('技艺', max_length=50, blank=True)
    stage = models.CharField('课程阶段', max_length=50, blank=True)
    difficulty = models.CharField('难度', max_length=50, blank=True)
    duration = models.CharField('课时/时长', max_length=50, blank=True)
    location = models.CharField('上课地点', max_length=200, blank=True)
    schedule = models.CharField('开课时间', max_length=50, blank=True)
    end_date = models.CharField('结课日期', max_length=10, blank=True)
    capacity = models.PositiveIntegerField('容量', default=0)
    price_num = models.DecimalField('价格', max_digits=10, decimal_places=2, default=0)
    cover = models.CharField('封面图', max_length=300, blank=True)
    video = models.CharField('教学视频', max_length=300, blank=True)
    desc = models.TextField('课程简介', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    enrolled = models.PositiveIntegerField('已报名人数', default=0)
    submit_time = models.CharField('提交时间', max_length=30, blank=True)
    # 管理员驳回时填写的原因，审核通过后会清空
    review_comment = models.TextField('课程审核意见', blank=True)
    # 课时明细整体存 JSON，避免为每节课单独建表
    lessons = models.JSONField('课时', default=list, blank=True)
    # 课程归属的传承人，删除账号时置空而不是级联删除课程
    owner = models.ForeignKey(
        'accounts.Inheritor', verbose_name='所属传承人',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='courses',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        """模型元信息：指定数据库表名、后台显示名称与按 id 倒序的默认排序。"""

        db_table = 'courses_course'
        verbose_name = '申报课程'
        verbose_name_plural = '申报课程'
        ordering = ['-id']

    def __str__(self):
        """返回「课程名(状态中文名)」形式的展示字符串，供后台与日志输出使用。"""
        return f'{self.name}({self.get_status_display()})'
