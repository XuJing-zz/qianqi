"""inventory 应用的模型定义：物料、出入库流水与材料邮寄单。

Material 维护物料库存与告警阈值；StockRecord 记录每次入库/领用/损耗；
Shipment 跟踪寄给学员的材料包从待寄到签收的状态流转。
"""
from django.conf import settings
from django.db import models


class Material(models.Model):
    """物料主数据：一种课程材料或工具，以及它的当前库存。

    stock 为当前库存量，alert_threshold 为低库存告警阈值；
    linked_course_id/linked_course_name 标记该物料关联的课程。
    """

    # 物料类型：基础材料或工具，供 type 字段选择
    TYPE_CHOICES = (
        ('material', '基础材料'),
        ('tool', '工具'),
    )

    name = models.CharField('物料名', max_length=100)
    spec = models.CharField('规格说明', max_length=100, blank=True)
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='material')
    stock = models.PositiveIntegerField('当前库存', default=0)
    alert_threshold = models.PositiveIntegerField('告警阈值', default=0)
    linked_course_id = models.PositiveIntegerField('关联课程ID', default=0)
    linked_course_name = models.CharField('关联课程名', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """数据库表名、后台显示名称与默认排序。"""

        db_table = 'inventory_material'
        verbose_name = '物料'
        verbose_name_plural = '物料'
        ordering = ['id']

    def __str__(self):
        """返回物料名称，用于后台列表和日志展示。"""
        return self.name


class StockRecord(models.Model):
    """出入库流水：记录一次入库、领用出库或损耗操作。

    material 为可空的关联物料（兼容历史或导入数据），
    material_name 冗余保存名称，便于流水列表直接展示。
    """

    # 流水类型：in 入库、out 领用出库、loss 损耗
    TYPE_CHOICES = (
        ('in', '入库'),
        ('out', '领用出库'),
        ('loss', '损耗'),
    )

    # 关联物料允许为空，删除物料时按 CASCADE 一并删除其流水
    material = models.ForeignKey(Material, verbose_name='物料', on_delete=models.CASCADE, related_name='stock_records', null=True, blank=True)
    material_name = models.CharField('物料名', max_length=100, blank=True)
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='in')
    qty = models.PositiveIntegerField('数量', default=0)
    note = models.CharField('备注', max_length=200, blank=True)
    operator = models.CharField('操作人', max_length=50, blank=True)
    time = models.CharField('时间', max_length=30, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """数据库表名、后台显示名称，并按 id 倒序展示最新流水。"""

        db_table = 'inventory_stockrecord'
        verbose_name = '出入库流水'
        verbose_name_plural = '出入库流水'
        ordering = ['-id']

    def __str__(self):
        """返回“物料名(流水类型)”形式，便于后台识别。"""
        return f'{self.material_name}({self.get_type_display()})'


class Shipment(models.Model):
    """材料邮寄单：跟踪给学员寄送材料包的发货与签收状态。

    items 以 JSON 保存物料清单，发货时据此扣减库存；
    status 由 pending → shipped → signed 单向流转。
    """

    # 邮寄状态：待寄 → 已寄 → 已签收，依次单向流转
    STATUS_CHOICES = (
        ('pending', '待寄'),
        ('shipped', '已寄'),
        ('signed', '已签收'),
    )

    student_id = models.PositiveIntegerField('学员ID', default=0)
    student_name = models.CharField('学员名', max_length=50, blank=True)
    course_id = models.PositiveIntegerField('课程ID', default=0)
    course_name = models.CharField('课程名', max_length=200, blank=True)
    # 物料清单，元素形如 {"materialId": 1, "materialName": "剪刀", "qty": 2}
    items = models.JSONField('物料清单', default=list, blank=True)
    # 状态取值见 STATUS_CHOICES，默认待寄
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    company = models.CharField('快递公司', max_length=50, blank=True)
    tracking_no = models.CharField('快递单号', max_length=100, blank=True)
    ship_time = models.CharField('发货时间', max_length=30, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """数据库表名、后台显示名称，并按 id 倒序展示最新邮寄单。"""

        db_table = 'inventory_shipment'
        verbose_name = '邮寄记录'
        verbose_name_plural = '邮寄记录'
        ordering = ['-id']

    def __str__(self):
        """返回“学员名-课程名(邮寄状态)”形式，便于后台识别。"""
        return f'{self.student_name}-{self.course_name}({self.get_status_display()})'
