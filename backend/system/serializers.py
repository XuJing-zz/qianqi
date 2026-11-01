# system/serializers.py —— 系统管理模块的序列化器
# 负责操作日志、联系留言、系统配置三类数据的出入参转换与字段校验。
# 额外补充 *_label 只读字段，前端可直接显示中文，无需自己维护枚举映射。

from rest_framework import serializers
from .models import OperationLog, SystemConfig, FeedbackMessage


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器：输出日志字段，并附加中文类型名称。

    字段 type_label 只读，取模型的 get_type_display()；
    ip、time、created_at 由后端生成，前端不可写。
    """

    # source='get_type_display' 直接调用模型方法，得到「登录/新增/修改」等中文文案
    type_label = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        """指定模型与字段列表，并将服务端生成的字段标记为只读。"""

        model = OperationLog
        fields = ['id', 'type', 'type_label', 'operator', 'action', 'detail', 'ip', 'time', 'created_at']
        read_only_fields = ['ip', 'time', 'created_at']


class FeedbackMessageSerializer(serializers.ModelSerializer):
    """联系留言序列化器：供前台提交留言、后台查看与回复使用。

    字段 status_label 只读，取 get_status_display() 显示「待处理/已处理」；
    id、created_at、status_label 由系统维护，不接受前端传入。
    """

    # 冗余一个中文状态字段，前端表格可直接渲染
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        """指定模型与字段列表，防止前端篡改提交时间和主键。"""

        model = FeedbackMessage
        fields = ['id', 'name', 'contact', 'subject', 'message', 'status', 'status_label', 'reply', 'created_at']
        read_only_fields = ['id', 'created_at', 'status_label']


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器：以 key/value 形式读写一组 JSON 配置。

    字段 value 为 JSON 类型，可整体保存多项配置；updated_at 由模型自动维护。
    """

    class Meta:
        """指定模型与字段列表，更新时间只读。"""

        model = SystemConfig
        fields = ['key', 'value', 'updated_at']
        read_only_fields = ['updated_at']
