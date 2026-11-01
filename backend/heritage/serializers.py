# heritage/serializers.py —— 传承人档案的序列化层
# 负责档案模型与 JSON 之间的转换：声明对前端暴露的字段，补充账号名、账号 id、
# 中文状态等只读展示字段，并把创建 / 更新时间锁定为只读，防止前端篡改。

from rest_framework import serializers
from .models import HeritageProfile


class HeritageProfileSerializer(serializers.ModelSerializer):
    """传承人档案序列化器，供列表、详情与新增 / 编辑接口复用。

    fields 覆盖档案全部业务字段，另外输出 account_username、account_id、status_label
    三个只读字段，前端无需再查账号或做状态翻译；account 本身不可写，
    账号绑定在 views.create 中通过 account_id 单独完成。
    """

    # 以下三个字段由关联对象或模型方法派生，只读输出，不参与写入校验
    account_username = serializers.CharField(source='account.username', read_only=True)
    account_id = serializers.IntegerField(source='account.id', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        """序列化器元信息：绑定模型、声明字段清单，并把时间戳字段设为只读。"""

        model = HeritageProfile
        fields = [
            'id', 'name', 'gender', 'age', 'phone', 'mentor', 'years', 'level',
            'craft', 'honors', 'cert_files', 'intro', 'qual', 'status', 'status_label',
            'account_id', 'account_username', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
