# heritage/models.py —— 传承人档案的数据模型层
# 负责定义传承人公开档案的表结构：基本信息、师承与技艺、荣誉证书、在职状态，
# 以及与登录账号（accounts.Inheritor）的一对一关联。
# 本文件只做数据建模，读写逻辑分别位于 serializers.py 和 views.py。

from django.conf import settings
from django.db import models


class HeritageProfile(models.Model):
    """传承人档案模型。

    一条记录对应一位传承人的公开主页；account 绑定登录账号后，该传承人可在前台查看并维护自己的档案。
    未绑定账号的档案由管理员单独录入，用于展示尚未开通账号的传承人。
    """

    # 档案状态枚举：离岗（leave）档案对非管理员不可见，过滤逻辑见 views.get_queryset
    STATUS_CHOICES = (
        ('active', '在职'),
        ('leave', '离岗'),
    )

    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=10, blank=True, default='男')
    age = models.PositiveIntegerField('年龄', default=0)
    phone = models.CharField('联系方式', max_length=20, blank=True)
    mentor = models.CharField('师承关系', max_length=100, blank=True)
    years = models.PositiveIntegerField('从艺年限', default=0)
    level = models.CharField('传承等级', max_length=20, blank=True)
    craft = models.CharField('代表技艺', max_length=100, blank=True)
    honors = models.TextField('所获荣誉', blank=True)
    # 证书附件以 JSON 数组保存上传接口返回的文件信息（url/name/size/ext），文件本体存放在媒体目录
    cert_files = models.JSONField('荣誉证书附件', default=list, blank=True)
    intro = models.TextField('个人简介', blank=True)
    qual = models.CharField('教学资质', max_length=100, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    # 一对一关联登录账号：一个账号最多一份档案；账号被删除时仅置空（SET_NULL），档案本身保留
    account = models.OneToOneField(
        'accounts.Inheritor',
        verbose_name='关联账号',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heritage_profile',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        """模型元信息：固定数据库表名，并设置后台显示用的单复数名称。"""

        db_table = 'heritage_profile'
        verbose_name = '传承人'
        verbose_name_plural = '传承人'

    def __str__(self):
        """返回传承人姓名，用于后台列表、日志和字符串拼接时的对象展示。"""
        return self.name
