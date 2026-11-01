"""
students 应用的序列化层。

负责学员报名与培训记录两个模型的 JSON 序列化/反序列化：
在基础字段之外补充前端需要的关联账号信息、状态中文名，
并在学员更新“已学课时”后触发学习进度重算。
"""
from rest_framework import serializers
from .models import Student, TrainingRecord
from .services import refresh_student_progress


class StudentSerializer(serializers.ModelSerializer):
    """学员报名序列化器。

    输出报名记录全部业务字段，并额外返回报名账号的 username、昵称、
    手机号与账号状态等只读信息，减少前端二次请求。
    """

    # status_label 由 get_status_display 生成，前端可直接展示“待审核/进行中”等中文状态
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    completed = serializers.JSONField(required=False)
    # 以下字段通过 SerializerMethodField 从关联的 user 对象取值，均为只读
    username = serializers.SerializerMethodField()
    nick = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    user_status_label = serializers.SerializerMethodField()

    class Meta:
        """序列化配置：声明字段清单，并锁定创建时间与进度不可由前端直接写入。"""

        model = Student
        fields = [
            'id', 'name', 'phone', 'avatar_glyph', 'course_id', 'course_name',
            'teacher', 'craft', 'price', 'enroll_time', 'status', 'status_label',
            'progress', 'note', 'review_comment', 'user', 'material_plan', 'completed', 'created_at',
            'username', 'nick', 'user_phone', 'user_status', 'user_status_label',
        ]
        read_only_fields = ['created_at', 'progress']

    def get_username(self, obj):
        """返回报名账号的登录名，未关联账号时返回空字符串。"""

        return getattr(obj.user, 'username', '') or ''

    def get_nick(self, obj):
        """返回账号昵称，昵称为空时依次回退到真实姓名，最终返回空字符串。"""

        u = obj.user
        if u is None:
            return ''
        return u.nick or u.name or ''

    def get_user_phone(self, obj):
        """返回报名账号绑定的手机号，未关联账号时返回空字符串。"""

        return getattr(obj.user, 'phone', '') or ''

    def get_user_status(self, obj):
        """返回报名账号的状态码（如正常/禁用），用于前端展示账号状态。"""

        return getattr(obj.user, 'status', '') or ''

    def get_user_status_label(self, obj):
        """返回报名账号状态的中文名称，未关联账号时返回空字符串。"""

        u = obj.user
        return u.get_status_display() if u is not None else ''

    def to_representation(self, instance):
        """序列化输出钩子：把已学课时编号统一转成字符串，便于前端与课程课时 ID 比较。"""

        data = super().to_representation(instance)
        data['completed'] = [str(c) for c in (data.get('completed') or [])]
        return data

    def update(self, instance, validated_data):
        """更新报名记录；若本次修改了 completed，则同步重算学习进度百分比。

        参数 instance：待更新的 Student 实例；validated_data：已校验的字段字典。
        返回值：更新后的 Student 实例。
        """

        instance = super().update(instance, validated_data)
        # 课时勾选变化后重新计算 progress，避免前端直接篡改进度值
        if 'completed' in validated_data:
            refresh_student_progress(instance)
        return instance


class TrainingRecordSerializer(serializers.ModelSerializer):
    """培训记录序列化器。

    除模型字段外，把 course_id 显式声明为可空整数，允许新增记录时不关联课程。
    """

    # 允许前端只传课程 ID 而不传完整课程对象
    course_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        """序列化配置：声明字段清单，培训时间由服务端自动生成故设为只读。"""

        model = TrainingRecord
        fields = [
            'id', 'course_id', 'course_name', 'teacher', 'record_time',
            'content', 'attendance', 'assessment', 'remark',
        ]
        read_only_fields = ['record_time']
