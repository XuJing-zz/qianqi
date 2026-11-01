"""技艺档案模型模块。

定义「技艺档案」Skill 模型：保存传承人技艺的展示信息、结构化详情（正文/附件）、
审核状态以及归属传承人，是 skills 应用的数据核心，后台管理与前台展示共用同一份数据。
"""
from django.conf import settings
from django.db import models


class Skill(models.Model):
    """技艺档案实体：一条记录对应一项技艺的完整档案。

    关键字段：
        status: 审核状态，取值见 STATUS_CHOICES，决定前台是否可见；
        owner: 所属传承人（accounts.Inheritor），传承人只能维护自己名下的档案；
        body/attachments: 用 JSON 存结构化正文与附件列表，前端可直接渲染。
    """

    # 状态流转：draft(草稿) -> pending(待审核) -> approved(已通过)/rejected(已驳回)；
    # 已通过(approved)与已下架(offline)之间由传承人自行切换上下架
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('offline', '已下架'),
    )

    # 基础展示信息：名称、图标字、封面图
    name = models.CharField('技艺名称', max_length=100)
    glyph = models.CharField('图标字', max_length=10, blank=True, default='技')
    image = models.CharField('技艺图片(URL)', max_length=500, blank=True, default='')
    # 分类检索维度：级别、难度、分类、流派、地区、发源地，用于列表页的筛选项
    level = models.CharField('技艺级别', max_length=20, blank=True)
    difficulty = models.CharField('技艺难度等级', max_length=20, blank=True)
    category = models.CharField('技艺分类', max_length=50, blank=True)
    school = models.CharField('工艺流派', max_length=50, blank=True)
    region = models.CharField('所在地区', max_length=50, blank=True)
    origin = models.CharField('发源地', max_length=100, blank=True)
    # 详情文案：概述用于列表摘要，简介与工序等用于详情页长文本展示
    abstract = models.TextField('技艺概述', blank=True)
    years = models.PositiveIntegerField('从艺年限', default=0)
    desc = models.TextField('技艺简介', blank=True)
    # 以下列表型文本统一用「｜」分隔，前端按分隔符拆成多条展示
    steps = models.TextField('工序步骤(｜分隔)', blank=True)
    raw_materials = models.TextField('原材料清单', blank=True)
    tools = models.TextField('专用工具', blank=True)
    hard_points = models.TextField('制作难点', blank=True)
    cautions = models.TextField('注意事项', blank=True)
    # 结构化内容：body 存详情正文的段落结构，attachments 存附件文档列表（含 url 等元信息）
    body = models.JSONField('详情正文结构', default=dict, blank=True)
    attachments = models.JSONField('附件文档', default=list, blank=True)
    works = models.TextField('代表作品(｜分隔)', blank=True)
    works_product_ids = models.JSONField('勾选代表作(本人作品id列表)', default=list, blank=True)
    courses = models.TextField('关联课程(｜分隔)', blank=True)
    # 审核相关：状态、提交时间（文本存储，由接口写入）、管理员审核意见
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    submit_time = models.CharField('提交时间', max_length=30, blank=True)
    review_comment = models.TextField('审核意见', blank=True)
    # 归属传承人：传承人注销时置空而不是连带删除档案，related_name 便于反向查询其全部技艺
    owner = models.ForeignKey(
        'accounts.Inheritor', verbose_name='所属传承人',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='skills',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        """模型元信息：指定数据表名、后台显示名称与默认排序。"""

        db_table = 'skills_skill'
        verbose_name = '技艺档案'
        verbose_name_plural = '技艺档案'
        # 默认按 id 倒序，新档案优先返回
        ordering = ['-id']

    def __str__(self):
        """返回「名称(状态中文)」形式的可读字符串，供后台列表、日志与调试展示。

        参数：无。
        返回：str，例如 '剪纸(已通过)'。
        """
        return f'{self.name}({self.get_status_display()})'
