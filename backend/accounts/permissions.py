"""角色权限模块：按 role 区分学员、管理员、传承人的访问范围。

各权限类都继承 DRF 的权限基类，在视图里通过 permission_classes 引用即可生效。
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdminRole(IsAuthenticated):
    """仅管理员可访问：先要求已登录，再校验 role 为 admin。"""

    def has_permission(self, request, view):
        """返回本次请求是否放行：已登录且当前账号身份为管理员。"""
        return super().has_permission(request, view) and request.user.role == 'admin'


class IsHeritageRole(IsAuthenticated):
    """仅传承人可访问：先要求已登录，再校验 role 为 heritage。"""

    def has_permission(self, request, view):
        """返回本次请求是否放行：已登录且当前账号身份为传承人。"""
        return super().has_permission(request, view) and request.user.role == 'heritage'


class IsStaffRole(IsAuthenticated):
    """后台工作人员可访问：管理员与传承人共用的“非学员”权限。"""

    def has_permission(self, request, view):
        """返回本次请求是否放行：已登录且身份为管理员或传承人。"""
        return super().has_permission(request, view) and request.user.role in ('admin', 'heritage')


class OwnerOrAdminWrite(BasePermission):
    """对象级权限：管理员可操作任意对象，传承人只能操作自己名下的对象。

    用于详情、修改、删除等已锁定单个对象的场景，需配合视图的
    check_object_permissions 使用。
    """

    def has_object_permission(self, request, view, obj):
        """判断当前用户能否操作 obj 这条记录。

        参数：
            request: 当前请求，request.user 为已认证账号。
            view: 触发校验的视图实例。
            obj: 被访问的数据对象，需带 owner_id 字段才能判归属。
        返回：
            管理员恒为 True；传承人仅当 obj.owner_id 等于本人 id 时为 True；
            学员一律 False。
        """
        role = request.user.role
        if role == 'admin':
            return True
        if role == 'heritage':
            # 只有带 owner 归属的对象才能判断，其余按无权限处理
            owner_id = getattr(obj, 'owner_id', None)
            return owner_id is not None and owner_id == request.user.id
        return False
