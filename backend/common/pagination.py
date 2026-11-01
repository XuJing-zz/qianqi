# common/pagination.py —— 全站统一的分页配置
# 基于 DRF 的 PageNumberPagination 扩展出「按需分页」：请求不带分页参数时返回完整列表，
# 带了 page 或 page_size 才分页，并统一返回前端约定好的分页字段结构。

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# 默认每页条数，前端表格一屏约放 8 条
DEFAULT_PAGE_SIZE = 8
# 单页上限，防止前端传超大 page_size 拖慢查询
MAX_PAGE_SIZE = 100


class OptInPagination(PageNumberPagination):
    """可选分页器：前端显式传 page/page_size 才分页，否则返回全部数据。

    配置：page_size 默认 8 条；page_size_query_param 为 'page_size'；单页最多 100 条。
    """

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE

    def paginate_queryset(self, queryset, request, view=None):
        """判断是否需要分页并执行分页。

        参数：queryset 待分页数据；request 当前请求；view 当前视图（可选）。
        返回：分页后的 page 对象；未传分页参数时返回 None，DRF 会直接返回完整列表。
        """
        params = request.query_params
        # 下拉框、导出等场景不需要分页，只有显式带参数时才走分页逻辑
        if 'page' not in params and 'page_size' not in params:
            return None
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        """组装统一的分页响应结构。

        参数：data 当前页的序列化数据列表。
        返回：包含 count 总数、page 当前页、page_size 每页条数、results 数据的响应对象。
        """
        return Response({
            # 总条数供前端计算总页数
            'count': self.page.paginator.count,
            'page': self.page.number,
            # 回传实际生效的每页条数，便于前端确认是否被上限截断
            'page_size': self.get_page_size(self.request),
            'results': data,
        })
