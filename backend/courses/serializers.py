"""
课程相关的序列化器。

CourseSerializer 负责课程字段输出、按角色裁剪课时视频等敏感字段，
并校验课时日期与视频上传/修改规则；另外两个序列化器用于审核入参。
"""

from rest_framework import serializers
from .models import Course


def _to_snake(name):
    """
    把驼峰字段名转成下划线命名，用于兼容前端提交的两种键名。

    :param name: 驼峰字符串，如 videoStatus
    :return: 下划线字符串，如 video_status
    """
    return ''.join('_' + ch.lower() if ch.isupper() else ch for ch in name)


class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化器：输出课程字段，并按请求者角色裁剪课时视频等信息。

    同时承担业务校验——课时日期须落在开课与结课区间内，教学视频仅在课程
    审核通过后才能上传，已过审课时的视频不允许直接替换。
    """

    status_label = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    region = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    master_bio = serializers.SerializerMethodField()

    class Meta:
        """序列化配置：指定模型、输出字段与只读字段。"""

        model = Course
        fields = [
            'id', 'name', 'craft', 'stage', 'difficulty', 'duration', 'location', 'schedule', 'end_date',
            'capacity', 'price_num', 'cover', 'video', 'desc', 'status', 'status_label',
            'enrolled', 'submit_time', 'review_comment', 'lessons',
            'owner', 'owner_name', 'region', 'level', 'master_bio',
            'created_at', 'updated_at',
        ]
        # 状态、报名人数与时间戳由服务端维护，客户端不可直接写入
        read_only_fields = ['created_at', 'updated_at', 'status', 'enrolled']

    def _owner_parts(self, obj):
        """
        汇总课程所属传承人的等级、地区与简介。

        :param obj: Course 实例
        :return: (level, region, bio) 三元组，缺失项为空字符串
        """
        owner = obj.owner
        if owner is None:
            return '', '', ''
        profile = None
        # 传承人档案是一对一关系，未建档时取不到，这里按账号字段兜底
        try:
            profile = owner.heritage_profile
        except Exception:
            profile = None
        level = (profile.level if profile and profile.level else owner.level) or ''
        region = owner.region or ''
        bio = (profile.intro if profile and profile.intro else owner.bio) or ''
        return level, region, bio

    def get_level(self, obj):
        """返回传承人等级，供前端展示讲师资质。"""
        return self._owner_parts(obj)[0]

    def get_region(self, obj):
        """返回传承人所在地区，供前端展示课程归属地。"""
        return self._owner_parts(obj)[1]

    def get_master_bio(self, obj):
        """返回传承人简介，供课程详情页展示讲师信息。"""
        return self._owner_parts(obj)[2]

    def _request_user(self):
        """从序列化上下文中取当前请求用户，无请求时返回 None。"""
        request = self.context.get('request')
        return getattr(request, 'user', None) if request is not None else None

    def _request_role(self):
        """返回当前请求用户的角色，未登录或取不到用户时返回 None。"""
        user = self._request_user()
        return getattr(user, 'role', None) if user is not None else None

    def _is_admin_write(self):
        """判断当前请求者是否为管理员；管理员提交时跳过部分业务校验。"""
        return self._request_role() == 'admin'

    @staticmethod
    def _k(les, camel):
        """
        读取课时字典中的驼峰字段，兼容下划线键名。

        :param les: 课时字典
        :param camel: 驼峰键名
        :return: 字段值，缺失或非字典时返回空字符串
        """
        if isinstance(les, dict):
            if camel in les:
                return les[camel]
            return les.get(_to_snake(camel))
        return ''

    def _course_range(self):
        """
        取本次提交（或已有实例）的开课日期与结课日期，用于课时日期校验。

        :return: (start, end) 字符串二元组，start 只保留日期前 10 位
        """
        inst = self.instance
        raw_schedule = self.initial_data.get('schedule')
        raw_end = self.initial_data.get('end_date')
        # 局部更新时可能未传日期，需要回退到数据库中的旧值
        if raw_schedule is None and inst is not None:
            raw_schedule = getattr(inst, 'schedule', '') or ''
        if raw_end is None and inst is not None:
            raw_end = getattr(inst, 'end_date', '') or ''
        start = str(raw_schedule or '')[:10] if raw_schedule else ''
        end = (str(raw_end or '').strip()) if raw_end else ''
        return start, end

    def validate_capacity(self, value):
        """
        校验容量字段：已上架或已下架课程不允许非管理员直接改容量。

        :param value: 待校验的容量值
        :return: 校验通过的容量值
        """
        inst = self.instance
        if inst is not None and getattr(inst, 'pk', None) is not None:
            if not self._is_admin_write() and inst.status in ('approved', 'offline') and value != inst.capacity:
                raise serializers.ValidationError('上架/已下架课程容量不可直接修改，请先转为草稿或驳回态再调整')
        return value

    @staticmethod
    def _normalize_video_status(les, old, video):
        """
        计算并写入课时的视频审核状态。

        视频新增或替换后重置为 pending；视频被清空则回到 draft；
        地址未变时保留原审核状态与审核意见。

        :param les: 当前课时字典，会被就地修改
        :param old: 修改前的课时字典，可为 None
        :param video: 当前课时的视频地址
        """
        old_video = (CourseSerializer._k(old or {}, 'video') or '').strip()
        old_status = (CourseSerializer._k(old or {}, 'videoStatus') or '').strip()
        if video:
            if video != old_video or old_status in ('draft', 'rejected', ''):
                status, comment = 'pending', ''
            else:
                status = old_status
                comment = CourseSerializer._k(old or {}, 'videoReviewComment') or ''
        else:
            status, comment = 'draft', ''
        # 统一写驼峰键，并清理历史数据里可能存在的下划线键
        les['videoStatus'] = status
        les['videoReviewComment'] = comment
        les.pop('video_status', None)
        les.pop('video_review_comment', None)

    def validate_lessons(self, value):
        """
        校验课时列表的日期区间与视频修改规则，并同步视频审核状态。

        管理员提交时只补齐缺失的视频状态；其他角色需满足：课时日期不早于开课、
        不晚于结课，日期存在时必须填写时间与地址；视频需课程审核通过后才可上传，
        已上架课程不可替换或删除已过审课时的视频。

        :param value: 课时 JSON 列表
        :return: 处理后的课时列表
        """
        if self._is_admin_write():
            for les in (value or []):
                if (self._k(les, 'video') or '').strip() and not (self._k(les, 'videoStatus') or '').strip():
                    les['videoStatus'] = 'pending'
                    les.pop('video_status', None)
            return value
        inst = self.instance
        is_new = inst is None or getattr(inst, 'pk', None) is None
        # 按课时编号缓存旧数据，用于判断视频是否被替换
        old_map = {
            str(self._k(l, 'num')): l
            for l in (inst.lessons or [])
            if self._k(l, 'num')
        } if not is_new else {}
        # 记录已过审课时的视频，用于阻止上架课程直接替换视频
        approved_old = {
            str(self._k(l, 'num')): self._k(l, 'video')
            for l in (inst.lessons or [])
            if self._k(l, 'videoStatus') == 'approved' and self._k(l, 'video')
        } if not is_new else {}
        start, end = self._course_range()

        for les in (value or []):
            num = str(self._k(les, 'num') or '')
            date = (self._k(les, 'scheduleDate') or '').strip()
            time = (self._k(les, 'scheduleTime') or '').strip()
            address = (self._k(les, 'address') or '').strip()
            video = (self._k(les, 'video') or '').strip()
            label = les.get('title') or (('课时 ' + num) if num else '某课时')

            if date:
                # 课时日期必须落在课程的开课与结课区间内
                if start and date < start:
                    raise serializers.ValidationError(f'课时「{label}」的上课日期不能早于开课日期 {start}')
                if end and date > end:
                    raise serializers.ValidationError(f'课时「{label}」的上课日期不能晚于结课日期 {end}')
                # 有上课日期就必须写清时间和地点，便于学员到场
                if not time:
                    raise serializers.ValidationError(f'课时「{label}」请填写上课时间')
                if not address:
                    raise serializers.ValidationError(f'课时「{label}」请填写上课地址')

            if video:
                # 新课程本身尚未过审，不允许先挂课时视频
                if is_new:
                    raise serializers.ValidationError('新课程尚未通过审核，请通过审核后再上传课时视频')
                old_video = (self._k(old_map.get(num, {}), 'video') or '').strip() if num else ''
                # 非上架状态下，只有课程审核通过才允许新增或替换视频
                if inst.status != 'approved' and video != old_video:
                    raise serializers.ValidationError('课程需通过管理员审核后才能上传课时视频')
                # 上架后保护已过审视频，替换或删除都要求先下架
                if inst.status == 'approved' and num and approved_old.get(num) and approved_old.get(num) != video:
                    raise serializers.ValidationError('课程已上架，不能替换或删除已过审课时的视频，请先下架再修改')

            # 无论是否修改视频，都重新计算一次视频审核状态
            self._normalize_video_status(les, old_map.get(num) if num else None, video)
        return value

    def validate(self, attrs):
        """
        整对象校验：非管理员提交时必须具备封面、开课时间与结课日期。

        :param attrs: 已通过字段级校验的数据
        :return: 校验通过的 attrs
        """
        attrs = super().validate(attrs)
        if self._is_admin_write():
            return attrs
        inst = self.instance

        def pick(field):
            """优先取本次提交的值，未提交时回退到实例上的旧值。"""
            if field in attrs:
                return (attrs.get(field) or '').strip()
            if inst is not None:
                return (getattr(inst, field, '') or '').strip()
            return ''

        cover = pick('cover')
        schedule = pick('schedule')
        end = pick('end_date')
        # 前台展示需要的三项必填信息，缺一不可
        if not cover:
            raise serializers.ValidationError({'cover': '请上传课程封面图'})
        if not schedule:
            raise serializers.ValidationError({'schedule': '请选择开课日期与时间'})
        if not end:
            raise serializers.ValidationError({'end_date': '请选择结课日期'})
        # 日期均为 YYYY-MM-DD 字符串，可直接按字典序比较
        sdate = schedule[:10]
        if len(sdate) != 10 or len(end) != 10 or end < sdate:
            raise serializers.ValidationError({'end_date': '结课日期不能早于开课日期'})
        return attrs

    def to_representation(self, instance):
        """
        输出前按角色裁剪字段：无权查看者拿不到课时视频与审核意见。

        :param instance: Course 实例
        :return: 裁剪后的字典数据
        """
        data = super().to_representation(instance)
        role = self._request_role()
        full = False
        if role == 'admin':
            full = True
        elif role == 'heritage':
            # 传承人仅对本人课程拥有完整视图
            user = self._request_user()
            full = instance.owner_id is not None and user is not None and instance.owner_id == user.id
        elif role == 'user':
            # 学员报名后才能看到已报课程的完整课时信息
            full = instance.id in (self.context.get('enrolled_ids') or set())
        if full:
            return data
        # 其余情况剔除视频相关字段和审核意见
        lessons = data.get('lessons') or []
        stripped = []
        for les in lessons:
            les = dict(les)
            for k in ('video', 'videoName', 'videoStatus', 'videoReviewComment'):
                les.pop(k, None)
            stripped.append(les)
        data['lessons'] = stripped
        data.pop('review_comment', None)
        return data


class CourseReviewSerializer(serializers.Serializer):
    """
    课程审核入参：action 为 approve/reject，驳回时需附 review_comment。
    """

    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_comment = serializers.CharField(required=False, allow_blank=True)


class VideoReviewSerializer(serializers.Serializer):
    """
    课时视频审核入参：用 lesson_index 定位课时，再由 action 决定通过或驳回。
    """

    lesson_index = serializers.IntegerField(min_value=0)
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_comment = serializers.CharField(required=False, allow_blank=True)
