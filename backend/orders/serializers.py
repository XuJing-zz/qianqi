# 订单模块 —— 序列化层
# 负责订单、订单状态日志、收货地址的字段定义与输出格式，
# 以及下单、支付、发货、审核、手动录入、改状态等接口的入参校验规则。

import re

from rest_framework import serializers
from .models import Order, Address, OrderStatusLog


class OrderStatusLogSerializer(serializers.ModelSerializer):
    """订单状态日志序列化器：在原始状态码之外补充中文状态名，供前端时间线展示。"""

    from_status_label = serializers.SerializerMethodField()
    to_status_label = serializers.SerializerMethodField()

    class Meta:
        """模型元信息：指定序列化模型与对外输出的字段列表。"""

        model = OrderStatusLog
        fields = ['id', 'from_status', 'from_status_label', 'to_status', 'to_status_label',
                  'operator', 'note', 'time', 'created_at']

    def _label(self, code):
        """把状态码转换成中文名称，未知或空状态返回原值。

        参数:
            code: 状态码，如 'paid'。
        返回:
            对应的中文名称；查不到时返回原状态码或空字符串。
        """
        return dict(Order.STATUS_CHOICES).get(code, code or '')

    def get_from_status_label(self, obj):
        """输出字段 from_status_label：原状态的中文名称。"""
        return self._label(obj.from_status)

    def get_to_status_label(self, obj):
        """输出字段 to_status_label：新状态的中文名称。"""
        return self._label(obj.to_status)


class OrderSerializer(serializers.ModelSerializer):
    """订单详情序列化器：输出订单全部业务字段、类型/状态中文名及状态流转日志。"""

    # 直接复用模型 choices 生成的中文展示方法，省去前端维护映射表
    type_label = serializers.CharField(source='get_type_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    # 嵌套输出该订单的所有状态日志，用于详情页展示流转过程
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        """模型元信息：订单字段白名单，订单编号与创建时间由后端生成、只读。"""

        model = Order
        fields = [
            'id', 'order_no', 'type', 'type_label', 'item_name', 'glyph', 'buyer', 'buyer_phone',
            'seller', 'price', 'status', 'status_label', 'pay_method',
            'buyer_user', 'order_time', 'pay_time', 'receiver', 'address', 'phone', 'remark',
            'source', 'product_id', 'qty', 'review_comment',
            'company', 'tracking_no', 'ship_time', 'status_logs', 'created_at',
        ]
        read_only_fields = ['created_at', 'order_no']


class OrderStatusSetSerializer(serializers.Serializer):
    """管理员手动改状态接口的入参校验：目标状态必填，备注可选。"""

    status = serializers.ChoiceField(choices=[c[0] for c in Order.STATUS_CHOICES])
    note = serializers.CharField(required=False, allow_blank=True)


class OrderShipSerializer(serializers.Serializer):
    """发货接口的入参校验：物流公司与物流单号均必填，并去掉首尾空格。"""

    company = serializers.CharField(
        max_length=50, error_messages={'required': '请选择物流公司', 'blank': '请选择物流公司'},
    )
    tracking_no = serializers.CharField(
        max_length=100, error_messages={'required': '请填写物流单号', 'blank': '请填写物流单号'},
    )

    def validate_company(self, value):
        """校验物流公司：去除首尾空白后不能为空。

        参数:
            value: 客户端提交的物流公司名称。
        返回:
            去空格后的物流公司名称。
        """
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('请选择物流公司')
        return value

    def validate_tracking_no(self, value):
        """校验物流单号：去除首尾空白后不能为空。

        参数:
            value: 客户端提交的物流单号。
        返回:
            去空格后的物流单号。
        """
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('请填写物流单号')
        return value


class OrderAuditSerializer(serializers.Serializer):
    """订单审核接口的入参校验：action 只能是通过或驳回，驳回原因可选。"""

    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_comment = serializers.CharField(required=False, allow_blank=True)


class OrderManualSerializer(serializers.Serializer):
    """管理员手动录入订单的入参校验：可关联作品，也可直接填写商品名与金额。"""

    # 未传 product_id 时走自定义商品分支，此时 item_name、price 才生效
    type = serializers.ChoiceField(choices=['product', 'course'], default='product')
    product_id = serializers.IntegerField(required=False, allow_null=True)
    item_name = serializers.CharField(required=False, allow_blank=True)
    qty = serializers.IntegerField(min_value=1, default=1)
    buyer = serializers.CharField(max_length=50, required=False, allow_blank=True)
    buyer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    receiver = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    pay_method = serializers.CharField(max_length=20, required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class OrderBuyProductSerializer(serializers.Serializer):
    """学员购买作品的入参校验：作品ID 必填，数量最少 1 件，收货信息可选。"""

    product_id = serializers.IntegerField()
    receiver = serializers.CharField(max_length=50, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    pay_method = serializers.CharField(required=False, allow_blank=True)
    qty = serializers.IntegerField(min_value=1, default=1)


class OrderPaySerializer(serializers.Serializer):
    """支付接口的入参校验：支付方式可选，不填则沿用订单原值。"""

    pay_method = serializers.CharField(max_length=20, required=False, allow_blank=True)


class AddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器：输出地址字段与拼接好的完整地址，并校验手机号格式。"""

    # full 来自模型的同名只读属性，仅用于输出、不接受写入
    full = serializers.CharField(read_only=True)

    class Meta:
        """模型元信息：地址字段白名单，完整地址与创建时间只读。"""

        model = Address
        fields = ['id', 'receiver', 'phone', 'province', 'city', 'district',
                  'detail', 'full', 'is_default', 'created_at']
        read_only_fields = ['created_at', 'full']

    def validate_phone(self, value):
        """校验联系电话：允许为空；非空时必须为 1 开头的 11 位手机号。

        参数:
            value: 客户端提交的电话号码。
        返回:
            去空格后的号码；空值返回空字符串。
        """
        v = (value or '').strip()
        if not v:
            return ''
        if not re.fullmatch(r'^1\d{10}$', v):
            raise serializers.ValidationError('请输入正确的 11 位手机号')
        return v
