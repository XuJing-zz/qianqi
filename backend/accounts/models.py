"""账号模块的数据模型定义。

学员（User）、管理员（Admin）、传承人（Inheritor）分别落在三张独立用户表上，
三者共用自定义管理器 BaseAccountManager 创建账号，并通过 role 属性区分身份，
status 字段用于业务层面的启用与停用。
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class BaseAccountManager(BaseUserManager):
    """三张账号表共用的自定义管理器。

    继承 BaseUserManager，保证 create_user / create_superuser 的密码加密与
    保存逻辑在三张表之间保持一致。
    """

    def create_user(self, username, password=None, **extra_fields):
        """创建并保存一个普通账号。

        参数：
            username: 登录账号，为空时抛 ValueError。
            password: 明文密码，入库前会被加密；允许为 None。
            **extra_fields: 其余账号字段（name、phone、status 等）。
        返回：
            已保存的账号实例。
        """
        if not username:
            raise ValueError('用户名不能为空')
        user = self.model(username=username, **extra_fields)
        # 必须走 set_password 做哈希，不能直接保存明文密码
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """创建后台超级管理员账号。

        参数：
            username / password: 含义同 create_user。
            **extra_fields: 额外字段，未显式传入时默认把 is_staff、is_superuser 置为 True。
        返回：
            已保存的账号实例。
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """学员账号模型，对应数据库表 user。

    继承 AbstractUser 复用其登录名、密码、权限字段，再扩展姓名、地区、
    技艺等展示信息；status 为业务状态，与 is_active 共同决定能否登录。
    """

    # 业务状态：active 正常，disabled 表示被管理员停用
    STATUS_CHOICES = (
        ('active', '正常'),
        ('disabled', '禁用'),
    )
    name = models.CharField('姓名', max_length=50, blank=True)
    nick = models.CharField('昵称', max_length=50, blank=True)
    gender = models.CharField('性别', max_length=10, blank=True)
    region = models.CharField('地区', max_length=50, blank=True)
    bio = models.TextField('个人简介', blank=True, default='')
    avatar = models.TextField('头像', blank=True, default='')
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.CharField('邮箱', max_length=50, blank=True)
    level = models.CharField('传承级别', max_length=20, blank=True, default='')
    craft = models.CharField('技艺方向', max_length=100, blank=True, default='')
    years = models.IntegerField('从艺年限', blank=True, null=True)
    intro = models.CharField('一句话签名', max_length=100, blank=True, default='')
    honor = models.CharField('荣誉', max_length=200, blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    # 指定自定义管理器，使 User.objects.create_user 走上面的加密逻辑
    objects = BaseAccountManager()

    USERNAME_FIELD = 'username'

    # 覆盖 AbstractUser 的多对多字段并改用独立 related_name，
    # 避免三张账号表反向查询名（user_set 等）互相冲突
    groups = models.ManyToManyField(
        'auth.Group', verbose_name='groups', blank=True,
        help_text='The groups this user belongs to.',
        related_name='user_account_groups', related_query_name='user_account',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='user permissions', blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_account_permissions', related_query_name='user_account',
    )

    @property
    def role(self):
        """只读身份标识，供权限判断、序列化与 JWT 载荷使用；固定返回 'user'。"""
        return 'user'

    class Meta:
        """模型元信息：指定表名与后台展示用的中文名称。"""

        db_table = 'user'
        verbose_name = '学员'
        verbose_name_plural = '学员'

    def __str__(self):
        """后台与操作日志中的可读名称，优先用姓名，姓名空时回退到用户名。"""
        return f'{self.name or self.username}(学员)'


class Admin(AbstractUser):
    """管理员账号模型，对应数据库表 admin。

    字段与学员表一致但独立存储，便于分别授权与停用；
    系统约定只保留一个管理员账号，该限制在视图层校验。
    """

    # 业务状态：active 正常，disabled 表示被停用
    STATUS_CHOICES = (
        ('active', '正常'),
        ('disabled', '禁用'),
    )
    name = models.CharField('姓名', max_length=50, blank=True)
    nick = models.CharField('昵称', max_length=50, blank=True)
    gender = models.CharField('性别', max_length=10, blank=True)
    region = models.CharField('地区', max_length=50, blank=True)
    bio = models.TextField('个人简介', blank=True, default='')
    avatar = models.TextField('头像', blank=True, default='')
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.CharField('邮箱', max_length=50, blank=True)
    level = models.CharField('传承级别', max_length=20, blank=True, default='')
    craft = models.CharField('技艺方向', max_length=100, blank=True, default='')
    years = models.IntegerField('从艺年限', blank=True, null=True)
    intro = models.CharField('一句话签名', max_length=100, blank=True, default='')
    honor = models.CharField('荣誉', max_length=200, blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    # 指定自定义管理器，使 Admin.objects.create_user 走上面的加密逻辑
    objects = BaseAccountManager()

    USERNAME_FIELD = 'username'

    # 覆盖 AbstractUser 的多对多字段，改用独立 related_name 避免反向查询名冲突
    groups = models.ManyToManyField(
        'auth.Group', verbose_name='groups', blank=True,
        help_text='The groups this user belongs to.',
        related_name='admin_account_groups', related_query_name='admin_account',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='user permissions', blank=True,
        help_text='Specific permissions for this user.',
        related_name='admin_account_permissions', related_query_name='admin_account',
    )

    @property
    def role(self):
        """只读身份标识，供权限判断、序列化与 JWT 载荷使用；固定返回 'admin'。"""
        return 'admin'

    class Meta:
        """模型元信息：指定表名与后台展示用的中文名称。"""

        db_table = 'admin'
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def __str__(self):
        """后台与操作日志中的可读名称，优先用姓名，姓名空时回退到用户名。"""
        return f'{self.name or self.username}(管理员)'


class Inheritor(AbstractUser):
    """传承人账号模型，对应数据库表 inheritor。

    传承人既可前台展示个人档案，也可作为技艺、课程、作品的归属人，
    其 role 返回 heritage，与前端和权限判断保持一致。
    """

    # 业务状态：active 正常，disabled 表示被停用
    STATUS_CHOICES = (
        ('active', '正常'),
        ('disabled', '禁用'),
    )
    name = models.CharField('姓名', max_length=50, blank=True)
    nick = models.CharField('昵称', max_length=50, blank=True)
    gender = models.CharField('性别', max_length=10, blank=True)
    region = models.CharField('地区', max_length=50, blank=True)
    bio = models.TextField('个人简介', blank=True, default='')
    avatar = models.TextField('头像', blank=True, default='')
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.CharField('邮箱', max_length=50, blank=True)
    level = models.CharField('传承级别', max_length=20, blank=True, default='')
    craft = models.CharField('技艺方向', max_length=100, blank=True, default='')
    years = models.IntegerField('从艺年限', blank=True, null=True)
    intro = models.CharField('一句话签名', max_length=100, blank=True, default='')
    honor = models.CharField('荣誉', max_length=200, blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    # 指定自定义管理器，使 Inheritor.objects.create_user 走上面的加密逻辑
    objects = BaseAccountManager()

    USERNAME_FIELD = 'username'

    # 覆盖 AbstractUser 的多对多字段，改用独立 related_name 避免反向查询名冲突
    groups = models.ManyToManyField(
        'auth.Group', verbose_name='groups', blank=True,
        help_text='The groups this user belongs to.',
        related_name='inheritor_account_groups', related_query_name='inheritor_account',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name='user permissions', blank=True,
        help_text='Specific permissions for this user.',
        related_name='inheritor_account_permissions', related_query_name='inheritor_account',
    )

    @property
    def role(self):
        """只读身份标识，供权限判断、序列化与 JWT 载荷使用；固定返回 'heritage'。"""
        return 'heritage'

    class Meta:
        """模型元信息：指定表名与后台展示用的中文名称。"""

        db_table = 'inheritor'
        verbose_name = '传承人'
        verbose_name_plural = '传承人'

    def __str__(self):
        """后台与操作日志中的可读名称，优先用姓名，姓名空时回退到用户名。"""
        return f'{self.name or self.username}(传承人)'
