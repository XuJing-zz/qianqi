# heritage/admin.py —— 传承人档案的 Django 后台配置
# 把 HeritageProfile 注册进 admin，并设定列表列、筛选器、搜索字段和默认排序，
# 方便管理员在后台直接查看和维护档案数据。
# 本文件只影响后台管理界面，不参与前台接口逻辑。

from django.contrib import admin
from .models import HeritageProfile


@admin.register(HeritageProfile)
class HeritageProfileAdmin(admin.ModelAdmin):
    """传承人档案的后台管理类。

    列表页展示姓名、性别、年龄、等级、技艺、状态和关联账号，
    右侧提供等级 / 状态筛选，搜索支持姓名、技艺、师承，默认按创建时间倒序。
    """

    # 列表列：末尾两项展示关联账号对象及其 id，便于核对档案与账号的绑定情况
    list_display = ('name', 'gender', 'age', 'level', 'craft', 'status', 'account', 'account_id')
    # 右侧筛选面板：按传承等级与在职状态过滤
    list_filter = ('level', 'status')
    # 顶部搜索框匹配的字段（当前为 icontains 模糊匹配）
    search_fields = ('name', 'craft', 'mentor')
    # 默认排序：新建的档案排在前面
    ordering = ('-created_at',)
