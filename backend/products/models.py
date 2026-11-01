# products 应用的数据模型层。
# 负责定义文创作品（Product）、学员收藏（Favorite）和作品出入库流水（ProductStockRecord）
# 三张表的结构、字段约束与表级配置，是整个作品模块的数据基础。

from django.conf import settings
from django.db import models


class Product(models.Model):
    """文创作品主模型：保存作品基本信息、图片素材、审核状态、价格与库存等核心字段。"""

    # 审核状态枚举：可选值为草稿/待审核/已通过/已驳回/已下架；普通用户查询时只放行“已通过”。
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('offline', '已下架'),
    )

    # 基础展示信息：图标字、名称、技艺、分类、材质、尺寸、作者与传承等级。
    glyph = models.CharField('图标字', max_length=10, blank=True, default='作')
    name = models.CharField('作品名称', max_length=200)
    craft = models.CharField('技艺', max_length=50, blank=True)
    category = models.CharField('分类', max_length=50, blank=True)
    material = models.CharField('材质', max_length=200, blank=True)
    size = models.CharField('尺寸', max_length=200, blank=True)
    inheritor = models.CharField('作者/传承人', max_length=100, blank=True)
    level = models.CharField('传承等级', max_length=20, blank=True)

    # 售卖与库存信息：saleable 控制是否上架销售，stock 与 alert_threshold 用于库存预警。
    saleable = models.BooleanField('是否可售', default=True)
    price = models.DecimalField('售价', max_digits=10, decimal_places=2, default=0)
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField('当前库存', default=0)
    alert_threshold = models.PositiveIntegerField('库存预警值', default=5)

    # 媒体与文案：cover 存封面地址，images 与 highlights 直接存 JSON 数组。
    cover = models.CharField('封面图', max_length=300, blank=True)
    images = models.JSONField('照片集', default=list, blank=True)
    story = models.TextField('作品故事', blank=True)
    highlights = models.JSONField('作品亮点', default=list, blank=True)

    # 审核相关：status 为当前状态，flag 为前台角标，review_comment 保存审核意见（驳回原因）。
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    flag = models.CharField('角标', max_length=20, blank=True)
    submit_time = models.CharField('提交时间', max_length=30, blank=True)
    review_comment = models.TextField('审核意见', blank=True)

    # 归属关系：作品挂在一名传承人名下，传承人账号被删除时置空而不删除作品。
    owner = models.ForeignKey(
        'accounts.Inheritor', verbose_name='所属传承人',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        """模型元信息：指定表名、后台显示名称，并默认按 id 倒序返回。"""

        db_table = 'products_product'
        verbose_name = '文创作品'
        verbose_name_plural = '文创作品'
        ordering = ['-id']

    def __str__(self):
        """返回“作品名(中文状态)”，方便后台列表、日志和调试时直接识别对象。"""
        return f'{self.name}({self.get_status_display()})'


class Favorite(models.Model):
    """学员收藏模型：记录某个用户收藏了哪件作品，并保证同一用户对同一作品只收藏一次。"""

    user = models.ForeignKey(
        'accounts.User', verbose_name='收藏用户',
        on_delete=models.CASCADE, related_name='favorites',
    )
    product = models.ForeignKey(
        Product, verbose_name='收藏作品',
        on_delete=models.CASCADE, related_name='favorited_by',
    )
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        """模型元信息：unique_together 从数据库层保证“用户+作品”组合唯一。"""

        db_table = 'products_favorite'
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        ordering = ['-id']
        # 联合唯一约束：避免同一用户重复收藏同一件作品。
        unique_together = ('user', 'product')

    def __str__(self):
        """返回“用户名 收藏 作品名”，用于后台与日志展示。"""
        return f'{self.user.username} 收藏 {self.product.name}'


class ProductStockRecord(models.Model):
    """作品出入库流水模型：每次入库、出库、销售或损耗都会新增一条记录，用于库存追溯。"""

    # 流水类型：in 入库、out 手工出库、order 销售出库、loss 损耗出库。
    TYPE_CHOICES = (
        ('in', '入库'),
        ('out', '出库'),
        ('order', '销售出库'),
        ('loss', '损耗'),
    )

    # product 允许为空（兼容手工流水）；product_name 冗余保存作品名，列表展示时无需再关联查询。
    product = models.ForeignKey(
        Product, verbose_name='作品',
        on_delete=models.CASCADE, related_name='stock_records', null=True, blank=True,
    )
    product_name = models.CharField('作品名', max_length=200, blank=True)
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='in')
    qty = models.PositiveIntegerField('数量', default=0)
    note = models.CharField('备注', max_length=200, blank=True)
    operator = models.CharField('操作人', max_length=50, blank=True)
    time = models.CharField('时间', max_length=30, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元信息：指定表名、后台显示名称，并按 id 倒序展示最新流水。"""

        db_table = 'products_stockrecord'
        verbose_name = '作品出入库流水'
        verbose_name_plural = '作品出入库流水'
        ordering = ['-id']

    def __str__(self):
        """返回“作品名(中文流水类型)”，方便后台快速查看流水明细。"""
        return f'{self.product_name}({self.get_type_display()})'
