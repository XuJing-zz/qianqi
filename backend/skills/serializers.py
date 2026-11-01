"""技艺档案序列化模块。

定义对外输出与校验技艺档案的 SkillSerializer，以及审核动作专用的
SkillReviewSerializer，负责模型对象与接口 JSON 之间的相互转换。
"""
from rest_framework import serializers
from .models import Skill


class SkillSerializer(serializers.ModelSerializer):
    """技艺档案序列化器：输出档案全部展示字段，并补充只读的中文状态与传承人姓名。

    用于列表、详情、审核、提交、上下架等接口的返回，也用于新增/修改时校验入参。
    参数：instance 为 Skill 实例（序列化时）或 data 为请求字典（反序列化时），二者择一。
    返回：序列化时给出 OrderedDict，反序列化校验通过后由 save() 落库。
    """

    # 只读派生字段：状态中文名与传承人姓名，省去前端再查字典或关联表
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        """声明绑定的模型、参与序列化的字段清单与只读字段。"""

        model = Skill
        # 字段顺序即接口返回顺序，前端据此渲染列表与详情页
        fields = [
            'id', 'name', 'glyph', 'image', 'level', 'difficulty', 'category', 'school', 'region', 'origin', 'abstract',
            'years', 'desc', 'steps', 'raw_materials', 'tools', 'hard_points', 'cautions',
            'body', 'attachments', 'works', 'works_product_ids', 'courses', 'status', 'status_label',
            'submit_time', 'review_comment', 'owner', 'owner_name', 'created_at', 'updated_at',
        ]
        # 创建/更新时间由模型自动维护，接口只读不写
        read_only_fields = ['created_at', 'updated_at']


class SkillReviewSerializer(serializers.Serializer):
    """审核动作的入参校验器：只校验 action 与 review_comment 两个字段。

    参数：action 必填，取 approve（通过）或 reject（驳回）；
        review_comment 可选，是否必填由视图层按动作决定（驳回时必须填原因）。
    返回：校验通过后可通过 validated_data 取到上述字段。
    """

    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_comment = serializers.CharField(required=False, allow_blank=True)
