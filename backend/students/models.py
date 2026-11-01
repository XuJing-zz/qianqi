"""
students 应用的模型定义。

定义学员报名记录（Student）与培训记录（TrainingRecord）两张数据表的结构、
报名状态枚举以及各字段的含义，是报名、审核、结课等业务的数据基础。
"""
from django.conf import settings
from django.db import models


class Student(models.Model):
    """学员报名记录模型。

    一条记录代表“某用户报名某课程”的一次报名，保存报名时的课程快照
    （课程名、老师、技艺、费用）、审核状态 status、学习进度 progress
    以及材料包、已完成课时等配置信息。
    """

    # 报名状态枚举：待审核 -> 进行中 / 已驳回，学完全部课时后置为已完成
    STATUS_CHOICES = (
        ('review', '待审核'),
        ('rejected', '已驳回'),
        ('ongoing', '进行中'),
        ('done', '已完成'),
    )

    # 关联报名账号；账号被删除时置空（SET_NULL），报名记录本身保留
    user = models.ForeignKey(
        'accounts.User', verbose_name='报名用户',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollments',
    )
    name = models.CharField('学员昵称', max_length=50)
    phone = models.CharField('联系方式', max_length=20, blank=True)
    avatar_glyph = models.CharField('头像占位字', max_length=10, blank=True, default='学')
    course_id = models.PositiveIntegerField('课程ID', default=0)
    course_name = models.CharField('报名课程', max_length=200, blank=True)
    teacher = models.CharField('任课老师', max_length=50, blank=True)
    craft = models.CharField('所属技艺', max_length=50, blank=True)
    price = models.DecimalField('报名费用', max_digits=10, decimal_places=2, default=0)
    enroll_time = models.CharField('报名时间', max_length=30, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='ongoing')
    review_comment = models.TextField('报名审核意见', blank=True)
    progress = models.PositiveIntegerField('学习进度', default=0)
    note = models.TextField('备注', blank=True)
    # 材料包配置与已学课时标识用 JSON 存储，避免为此再建关联表
    material_plan = models.JSONField('材料包配置', default=list, blank=True)
    completed = models.JSONField('已学课时标识', default=list, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元数据：指定表名、后台显示名称，并按 id 倒序返回最新报名。"""

        db_table = 'students_student'
        verbose_name = '学员'
        verbose_name_plural = '学员'
        ordering = ['-id']

    def __str__(self):
        """后台与日志中使用的可读名称，格式为“学员昵称-课程名”。"""

        return f'{self.name}-{self.course_name}'


class TrainingRecord(models.Model):
    """培训记录模型。

    记录一次课程培训的时间、内容、学员出勤情况（attendance）与考核结果
    （assessment），后两者以 JSON 列表/字典保存，便于前端直接渲染表格。
    """

    # 关联课程；课程删除后置空，但保留下面的 course_name 快照
    course = models.ForeignKey(
        'courses.Course', verbose_name='课程',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='training_records',
    )
    course_name = models.CharField('课程名', max_length=200, blank=True)
    teacher = models.CharField('授课传承人', max_length=50, blank=True)
    record_time = models.DateTimeField('培训时间', auto_now_add=True)
    content = models.TextField('培训内容', blank=True)
    # attendance 形如 [{'name': '张三', 'status': 'present'}]，assessment 形如 {'张三': '优秀'}
    attendance = models.JSONField('学员出勤表', default=list, blank=True)
    assessment = models.JSONField('学员考核表', default=dict, blank=True)
    remark = models.TextField('备注', blank=True)

    class Meta:
        """模型元数据：指定表名、后台显示名称，并按 id 倒序排列。"""

        db_table = 'training_record'
        verbose_name = '培训记录'
        verbose_name_plural = '培训记录'
        ordering = ['-id']

    def __str__(self):
        """后台与日志中使用的可读名称：优先显示课程名，缺失时回退到课程 ID。"""

        return f'{self.course_name or self.course_id}(培训记录)'
