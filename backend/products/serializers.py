# products 应用的序列化器层（DRF Serializer）。
# 负责作品数据与接口 JSON 之间的相互转换，包括字段暴露、只读控制，
# 以及作品照片上传时的数量与单张大小校验；同时定义审核、出入库、收藏等辅助入参校验。

from rest_framework import serializers
from .models import Product, Favorite, ProductStockRecord


class ProductSerializer(serializers.ModelSerializer):
    """
    文创作品序列化器：用于作品的增删改查接口。

    在模型字段之外额外输出 status_label（状态中文名）和 owner_name（归属人姓名），
    并通过 validate_images 对照片集做上传校验；输出为作品完整字段的字典结构。
    """

    # 只读附加字段：状态中文展示、归属账号姓名，避免前端再做映射
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    @staticmethod
    def _data_url_size_mb(value):
        """
        估算 data URL 形式的图片解码后的体积（MB）。

        参数 value：可能是普通 URL 或 "data:image/...;base64,..." 字符串。
        返回 float 体积（MB）；非字符串或不是 data URL 时返回 None，表示无需校验。
        """
        if not isinstance(value, str) or not value.startswith('data:'):
            return None
        # 逗号后是 base64 主体；base64 每 4 字符对应 3 字节，再换算成 MB
        b64 = value.split(',', 1)[1] if ',' in value else value
        return len(b64) * 3 / 4 / 1024 / 1024

    def validate_images(self, value):
        """
        校验作品照片集：数量不超过系统上限，单张 data URL 图片不超过大小上限。

        参数 value：图片地址/数据列表。校验通过时原样返回该列表；
        超出数量或大小限制时抛出 serializers.ValidationError，由 DRF 转成 400 响应。
        """
        from common.uploads import get_upload_limits
        limits = get_upload_limits()
        # 未配置时使用兜底值：单张 50MB、最多 9 张
        cap = limits['max_mb'] or 50
        count_cap = limits['max_count'] or 9
        # 先校验数量，避免无意义的逐张体积计算
        if len(value) > count_cap:
            raise serializers.ValidationError(f'最多上传 {count_cap} 张照片')
        for img in value:
            mb = self._data_url_size_mb(img)
            # 仅对 data URL（前端直传的 base64 图）做体积校验，普通 URL 跳过
            if mb is not None and mb > cap:
                raise serializers.ValidationError(f'单张照片不能超过 {cap}MB')
        return value

    class Meta:
        """序列化器元信息：声明参与读写的全部字段，创建/更新时间由后端维护故设为只读。"""

        model = Product
        fields = [
            'id', 'glyph', 'name', 'craft', 'category', 'material', 'size',
            'inheritor', 'level', 'saleable', 'price', 'cost_price', 'stock',
            'alert_threshold', 'cover', 'images', 'story',
            'highlights', 'status', 'status_label', 'flag', 'submit_time',
            'review_comment', 'owner', 'owner_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductReviewSerializer(serializers.Serializer):
    """作品审核入参序列化器：校验审核动作（approve/reject）与可选的审核意见。"""

    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_comment = serializers.CharField(required=False, allow_blank=True)


class ProductStockRecordSerializer(serializers.ModelSerializer):
    """库存流水序列化器：输出流水明细，并额外暴露所属作品的 product_id。"""

    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        """序列化器元信息：列出流水展示字段，created_at 由系统写入故设为只读。"""

        model = ProductStockRecord
        fields = ['id', 'product_id', 'product_name', 'type', 'qty', 'note', 'operator', 'time', 'created_at']
        read_only_fields = ['created_at']


class ProductStockInOutSerializer(serializers.Serializer):
    """作品出入库入参序列化器：校验流水类型、数量（正整数）与备注。"""

    type = serializers.ChoiceField(choices=['in', 'out', 'order', 'loss'])
    qty = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True)


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化器：输出收藏记录，并平铺作品的关键展示字段，方便前端直接渲染收藏卡片。"""

    product_id = serializers.IntegerField(source='product.id', read_only=True)
    glyph = serializers.CharField(source='product.glyph', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    inheritor = serializers.CharField(source='product.inheritor', read_only=True)
    craft = serializers.CharField(source='product.craft', read_only=True)
    cover = serializers.CharField(source='product.cover', read_only=True)

    class Meta:
        """序列化器元信息：收藏记录字段 + 平铺的作品字段，created_at 为只读。"""

        model = Favorite
        fields = ['id', 'product_id', 'glyph', 'name', 'inheritor', 'craft', 'cover', 'created_at']
        read_only_fields = ['created_at']
