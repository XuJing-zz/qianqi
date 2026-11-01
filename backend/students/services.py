"""
students 应用的业务逻辑层。

把报名、审核录取、删除回退名额、学习进度重算等跨模型的操作集中在此，
供 views 与 serializers 复用，保证事务与计数（课程 enrolled）的一致性。
"""
from datetime import datetime

from django.db import transaction
from django.db.models import F
from rest_framework import serializers


def lesson_keys(course):
    """提取课程全部课时的标识列表。

    参数 course：Course 实例，其 lessons 为课时字典列表，可带 num 字段。
    返回值：字符串列表；缺少 num 的课时按顺序用序号（从 1 开始）兜底。
    """

    keys = []
    for i, les in enumerate(course.lessons or []):
        num = les.get('num')
        # 课时编号优先用 num，未填写时退化为当前位置序号，保证键值唯一可用
        keys.append(str(num) if num not in (None, '') else str(i + 1))
    return keys


def refresh_student_progress(student, commit=True):
    """根据已学课时重算学员学习进度。

    参数 student：Student 实例；commit 为 True 时立即写库。
    规则：先剔除课程中已不存在的课时编号，再按“已完成课时数 / 总课时数”计算百分比。
    返回值：处理后的 student 实例。
    """

    from courses.models import Course
    course = Course.objects.filter(pk=student.course_id).first()
    # 课程已被删除时无法计算进度，直接归零
    if course is None:
        student.progress = 0
        if commit:
            student.save(update_fields=['progress'])
        return student
    keys = lesson_keys(course)
    # 过滤掉课程已删除或改编号的课时，防止进度虚高
    cleaned = [str(k) for k in (student.completed or []) if str(k) in keys]
    student.completed = cleaned
    student.progress = round(len(cleaned) / len(keys) * 100) if keys else 0
    if commit:
        student.save(update_fields=['completed', 'progress'])
    return student


def _user_display_name(user):
    """取用户展示名：优先真实姓名，其次昵称、登录名，最终去掉首尾空格返回。"""

    return (user.name or user.nick or user.username or '').strip()


def enroll_user(serializer, request):
    """处理普通用户的线上报名。

    参数 serializer：已校验的 StudentSerializer；request：携带当前登录用户的请求。
    流程：加锁读取课程并校验是否开放报名 -> 拦截重复报名 -> 用课程信息回填报名快照。
    返回值：保存后的 Student 实例；校验不通过时抛出 ValidationError。
    """

    from courses.models import Course
    from .models import Student

    course_id = serializer.validated_data.get('course_id') or 0
    # 事务 + 行锁：防止同一课程并发报名时重复写入或名额数据错乱
    with transaction.atomic():
        course = Course.objects.select_for_update().filter(pk=course_id).first()
        if course is None or course.status != 'approved':
            raise serializers.ValidationError('课程不存在或未开放报名')
        user = request.user
        existed = Student.objects.filter(user=user, course_id=course.id).first()
        # 已有未驳回的报名记录即视为重复报名；被驳回的记录允许重新报名
        if existed is not None and existed.status != 'rejected':
            raise serializers.ValidationError('你已报名该课程，请勿重复报名')
        if existed is not None:
            existed.delete()

        name = _user_display_name(user)
        data = serializer.validated_data
        # 报名快照全部以服务端数据为准，忽略前端传入的同名字段
        data.update({
            'name': name,
            'phone': user.phone or '',
            'avatar_glyph': name[:1] or '学',
            'course_id': course.id,
            'course_name': course.name,
            'teacher': (course.owner.name if course.owner_id else '') or '',
            'craft': course.craft or '',
            'price': course.price_num,
            'enroll_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status': 'review',
            'progress': 0,
            'completed': [],
        })
        instance = serializer.save(user=user)
        return instance


def enroll_staff_proxy(serializer, request):
    """处理管理员或传承人的代报名。

    参数 serializer：已校验的 StudentSerializer；request：当前请求。
    规则：优先使用请求中填写的老师；传承人代报名且未填写时以本人作为任课老师。
    返回值：保存后的 Student 实例。
    """

    data = serializer.validated_data
    teacher = data.get('teacher') or (
        (request.user.name or '') if request.user.role == 'heritage' else ''
    )
    if teacher:
        data['teacher'] = teacher
    return serializer.save()


def dec_enrolled_on_delete(student):
    """删除报名前回退课程的已报名人数。

    参数 student：即将删除的 Student 实例；返回值：无。
    只有已录取（进行中/已完成）的报名才占用了名额，因此仅这两种状态需要回退。
    """

    from courses.models import Course
    if getattr(student, 'user_id', None) is None:
        return
    # 待审核、已驳回的报名未占用名额，无需回退
    if student.status not in ('ongoing', 'done'):
        return
    Course.objects.filter(pk=student.course_id, enrolled__gt=0).update(enrolled=F('enrolled') - 1)


def approve_enrollment(student):
    """审核通过报名：待审核 -> 进行中，并占用一个课程名额。

    参数 student：待审核的 Student 实例。
    返回值：元组 (是否成功, 失败原因)；成功时原因为空字符串。
    校验点：状态必须为待审核、课程必须存在且开放报名、课程名额未满。
    """

    from courses.models import Course
    if student.status != 'review':
        return False, '仅待审核报名可录取'
    # 加行锁读取课程，避免并发录取导致 enrolled 超过 capacity
    course = Course.objects.select_for_update().filter(pk=student.course_id).first()
    if course is None or course.status != 'approved':
        return False, '关联课程不存在或未开放，无法录取'
    # capacity 为 0 表示不限名额，仅在设置了容量时才判断是否已满
    if course.capacity and course.enrolled >= course.capacity:
        return False, '该课程名额已满，无法录取'
    student.status = 'ongoing'
    student.review_comment = ''
    student.save(update_fields=['status', 'review_comment'])
    # 用 F 表达式原子自增，避免并发下的读改写丢失更新
    Course.objects.filter(pk=course.id).update(enrolled=F('enrolled') + 1)
    return True, ''
