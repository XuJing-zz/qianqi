"""inventory 应用的序列化器：输出的模型字段转换与请求参数校验。

Material/StockRecord/Shipment 三个 ModelSerializer 负责接口返回的字段与
中文标签；StockInOutSerializer、ShipOutSerializer 负责出入库、发货入参校验。
"""
from rest_framework import serializers
from .models import Material, StockRecord, Shipment


class MaterialSerializer(serializers.ModelSerializer):
    """物料序列化器：输出物料业务字段，并附加类型中文名。

    type_label 为只读展示字段，由模型 get_type_display 生成；
    其余字段与 Material 模型字段一一对应。
    """

    # 只读展示字段：把 type 的英文枚举值转成中文标签
    type_label = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        """声明序列化的模型、字段列表与只读字段。"""

        model = Material
        fields = [
            'id', 'name', 'spec', 'type', 'type_label', 'stock', 'alert_threshold',
            'linked_course_id', 'linked_course_name', 'created_at',
        ]
        read_only_fields = ['created_at']


class StockRecordSerializer(serializers.ModelSerializer):
    """出入库流水序列化器：输出流水字段及类型中文名。

    type_label 为只读展示字段；material 输出关联物料 ID，
    material_name 为冗余保存的物料名，便于列表直接展示。
    """

    # 只读展示字段：把流水类型转成“入库/领用出库/损耗”
    type_label = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        """声明序列化的模型、字段列表与只读字段。"""

        model = StockRecord
        fields = [
            'id', 'material', 'material_name', 'type', 'type_label', 'qty',
            'note', 'operator', 'time', 'created_at',
        ]
        read_only_fields = ['created_at']


class ShipmentSerializer(serializers.ModelSerializer):
    """材料邮寄单序列化器：输出邮寄单字段及状态中文名。

    status_label 为只读展示字段；items 以 JSON 列表返回物料清单。
    """

    # 只读展示字段：把 status 转成“待寄/已寄/已签收”
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        """声明序列化的模型、字段列表与只读字段。"""

        model = Shipment
        fields = [
            'id', 'student_id', 'student_name', 'course_id', 'course_name',
            'items', 'status', 'status_label', 'company', 'tracking_no',
            'ship_time', 'created_at',
        ]
        read_only_fields = ['created_at']


class StockInOutSerializer(serializers.Serializer):
    """出入库动作的入参校验：type、qty、note。

    不绑定模型，仅用于校验请求体；qty 必须为正整数，
    note 可选且允许空串。
    """

    # 只允许入库、领用出库、损耗三种操作类型
    type = serializers.ChoiceField(choices=['in', 'out', 'loss'])
    # 数量至少为 1，避免 0 或负数写入流水
    qty = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True)


class ShipOutSerializer(serializers.Serializer):
    """发货动作的入参校验：快递公司与快递单号。

    company、tracking_no 均为必填，校验时会去除首尾空白。
    """

    # 自定义 required/blank 文案，把中文提示直接返回给前端
    company = serializers.CharField(
        max_length=50, error_messages={'required': '请选择快递公司', 'blank': '请选择快递公司'},
    )
    tracking_no = serializers.CharField(
        max_length=100, error_messages={'required': '请填写快递单号', 'blank': '请填写快递单号'},
    )

    def validate_company(self, value):
        """校验并清洗快递公司名称。

        参数 value 为原始输入；去空格后为空则抛出校验错误，
        返回清洗后的字符串。
        """
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('请选择快递公司')
        return value

    def validate_tracking_no(self, value):
        """校验并清洗快递单号。

        参数 value 为原始输入；去空格后为空则抛出校验错误，
        返回清洗后的字符串。
        """
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('请填写快递单号')
        return value
