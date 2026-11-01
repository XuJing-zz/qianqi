# 订单模块 —— 数据模型层
# 负责定义订单主表（Order）、订单状态变更日志（OrderStatusLog）与收货地址（Address）
# 三张数据表，并集中维护订单类型、订单状态等枚举，为下单/支付/发货等业务提供数据基础。

import random
from datetime import datetime

from django.conf import settings
from django.db import models


def gen_order_no():
    """生成订单编号，格式为 QQ + 14 位时间戳 + 6 位随机数。

    返回：字符串类型的订单编号，如 QQ20250101120000123456。
    """
    return 'QQ{}{:06d}'.format(datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(0, 999999))


class Order(models.Model):
    """订单主表：记录一笔订单的商品信息、买卖双方、金额与全流程状态。

    订单类型区分“作品”（线上购买传承人作品，需要物流发货）与“课程”；
    状态按 review→pending→paid→shipped→done 正向流转，另有 cancelled、rejected 两个终态。
    """

    # 订单类型：商品（作品）订单、课程订单
    TYPE_CHOICES = (
        ('product', '作品'),
        ('course', '课程'),
    )
    # 订单状态：review 待审核（管理员手录单）、pending 待付款、paid 待发货、
    # shipped 已发货、done 已完成；cancelled 已取消、rejected 已驳回为终止状态
    STATUS_CHOICES = (
        ('review', '待审核'),
        ('pending', '待付款'),
        ('paid', '待发货'),
        ('shipped', '已发货'),
        ('done', '已完成'),
        ('cancelled', '已取消'),
        ('rejected', '已驳回'),
    )

    # 订单号为业务编号（非主键），创建时自动生成；类型默认作品订单，来源标记自动下单或后台录入
    order_no = models.CharField('订单编号', max_length=50, blank=True, default='', db_index=True)
    type = models.CharField('订单类型', max_length=20, choices=TYPE_CHOICES, default='product')
    source = models.CharField('订单来源', max_length=20, blank=True, default='auto')
    item_name = models.CharField('商品名称', max_length=200)
    glyph = models.CharField('图标字', max_length=10, blank=True, default='盏')
    # 买家账号：账号注销时置空而不删除订单，便于保留历史交易记录
    buyer_user = models.ForeignKey(
        'accounts.User', verbose_name='买家账号',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='my_orders',
    )
    buyer = models.CharField('买家昵称', max_length=50, blank=True)
    buyer_phone = models.CharField('买家电话', max_length=20, blank=True)
    # 卖家为作品所属传承人，用于传承人视角筛选“我卖出的订单”
    seller = models.ForeignKey(
        'accounts.Inheritor', verbose_name='卖家(传承人)',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='sold_orders',
    )
    # 实付金额按下单价 × 数量在业务层计算后写入，不在此处存单价
    price = models.DecimalField('实付金额', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    pay_method = models.CharField('支付方式', max_length=20, blank=True)
    # 时间类字段统一存字符串（yyyy-mm-dd HH:MM），便于前端直接展示、无需再做格式化
    order_time = models.CharField('下单时间', max_length=30, blank=True)
    pay_time = models.CharField('支付时间', max_length=30, blank=True)
    receiver = models.CharField('收件人', max_length=50, blank=True)
    address = models.CharField('收货地址', max_length=200, blank=True)
    phone = models.CharField('收货电话', max_length=20, blank=True)
    remark = models.TextField('备注', blank=True)
    # 关联作品ID 仅作品订单有值，用于状态流转时回写库存；课程订单固定为 0
    product_id = models.PositiveIntegerField('关联作品ID', default=0)
    qty = models.PositiveIntegerField('购买数量', default=1)
    review_comment = models.TextField('审核意见/驳回原因', blank=True)
    # 物流信息在发货环节写入，包含物流公司、物流单号与发货时间
    company = models.CharField('物流公司', max_length=50, blank=True)
    tracking_no = models.CharField('物流单号', max_length=100, blank=True)
    ship_time = models.CharField('发货时间', max_length=30, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元信息：指定表名、后台显示名称，并默认按下单先后倒序排列。"""

        db_table = 'orders_order'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-id']

    def __str__(self):
        """订单的字符串表示，后台与日志中显示为“类型-商品名(买家)”。"""
        return f'{self.get_type_display()}-{self.item_name}({self.buyer})'

    def save(self, *args, **kwargs):
        """保存订单：新建时若订单编号为空则自动生成，其余逻辑沿用父类。"""
        if not self.order_no:
            self.order_no = gen_order_no()
        return super().save(*args, **kwargs)

    def log_status(self, to_status, operator='', note='', from_status=None):
        """写入一条订单状态变更日志，供订单详情页展示流转时间线。

        参数:
            to_status: 变更后的状态码，如 'paid'。
            operator: 操作人昵称，为空时记为系统。
            note: 本次流转的中文说明。
            from_status: 原状态码，默认取订单当前状态；新建订单可显式传 ''。
        返回:
            新建的 OrderStatusLog 实例。
        """
        return self.status_logs.create(
            from_status=self.status if from_status is None else from_status,
            to_status=to_status,
            operator=operator or '',
            note=note or '',
            time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        )


# 状态日志表：订单每次流转都追加一条记录，只增不改，便于追溯操作人
class OrderStatusLog(models.Model):
    """订单状态变更日志：记录每次状态流转的原状态、新状态、操作人与说明。"""

    order = models.ForeignKey(
        Order, verbose_name='订单', on_delete=models.CASCADE, related_name='status_logs',
    )
    from_status = models.CharField('原状态', max_length=20, blank=True, default='')
    to_status = models.CharField('新状态', max_length=20, blank=True, default='')
    operator = models.CharField('操作人', max_length=50, blank=True, default='')
    note = models.CharField('说明', max_length=200, blank=True, default='')
    time = models.CharField('操作时间', max_length=30, blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元信息：表名与后台显示名称，按写入顺序正序排列形成时间线。"""

        db_table = 'orders_status_log'
        verbose_name = '订单状态变更'
        verbose_name_plural = '订单状态变更'
        ordering = ['id']

    def __str__(self):
        """日志的字符串表示，形如“订单ID: 原状态->新状态”。"""
        return f'{self.order_id}: {self.from_status}->{self.to_status}'


# 收货地址表：一个用户可有多条地址，其中最多一条为默认地址
class Address(models.Model):
    """收货地址：属于某个普通用户，支持下单时默认地址的自动维护。"""

    user = models.ForeignKey(
        'accounts.User', verbose_name='所属用户',
        on_delete=models.CASCADE, related_name='addresses',
    )
    receiver = models.CharField('收货人', max_length=50)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    province = models.CharField('省', max_length=50, blank=True)
    city = models.CharField('市', max_length=50, blank=True)
    district = models.CharField('区/县', max_length=50, blank=True)
    detail = models.CharField('详细地址', max_length=200, blank=True)
    is_default = models.BooleanField('是否默认', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        """模型元信息：表名与后台显示名称，默认地址排在最前，其余按新建倒序。"""

        db_table = 'orders_address'
        verbose_name = '收货地址'
        verbose_name_plural = '收货地址'
        ordering = ['-is_default', '-id']

    def __str__(self):
        """地址的字符串表示，显示为“收货人 · 完整地址”。"""
        return f'{self.receiver} · {self.province}{self.city}{self.district}{self.detail}'

    @property
    def full(self):
        """只读属性：拼省市区与详细地址，供前端列表和订单收货信息直接展示。"""
        return f'{self.province}{self.city}{self.district}{self.detail}'
