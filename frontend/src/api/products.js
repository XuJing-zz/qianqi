/*商品接口：商品列表/新增/修改/删除、审核/提交、筛选选项、库存出入库与流水、收藏*/
import { api } from './client'
import { qs } from './utils'

/*获取商品列表：参数 params 可含分页、分类、工艺、价格、关键词等；返回商品数组或分页结果。
   后端接口：GET /api/products/products/。*/
export function listProducts(params = {}) {
  return api.get('/products/products/' + qs(params))
}
/*新增商品：参数 payload 是商品表单数据（名称、价格、库存、图片、传承人等）；返回创建后的商品。
   后端接口：POST /api/products/products/。*/
export function createProduct(payload) {
  return api.post('/products/products/', payload)
}
/*修改商品：参数 id 商品 id，payload 是要修改的字段；返回更新后的商品。
   后端接口：PATCH /api/products/products/{id}/。*/
export function updateProduct(id, payload) {
  return api.patch(`/products/products/${id}/`, payload)
}
/*删除商品：参数 id 商品 id；返回删除结果。
   后端接口：DELETE /api/products/products/{id}/。*/
export function deleteProduct(id) {
  return api.del(`/products/products/${id}/`)
}
/*审核商品：参数 id 商品 id，action 审核动作（如 approve/reject），reviewComment 审核备注；
   返回处理结果。后端接口：POST /api/products/products/{id}/review/。*/
export function reviewProduct(id, action, reviewComment) {
  return api.post(`/products/products/${id}/review/`, { action, review_comment: reviewComment })
}
/*提交商品审核：参数 id 商品 id；把商品提交给管理员审核。
   后端接口：POST /api/products/products/{id}/submit/。*/
export function submitProduct(id) {
  return api.post(`/products/products/${id}/submit/`)
}
/*获取商品筛选选项：无参数；返回可用的分类、工艺、传承人等筛选项，供列表页下拉框使用。
   后端接口：GET /api/products/products/filters/。*/
export function fetchProductFilters() {
  return api.get('/products/products/filters/')
}

/*商品库存出入库：参数 id 商品 id，payload 含类型（in/out）、数量、备注等；返回更新后的商品或流水。
   后端接口：POST /api/products/products/{id}/stock_in_out/。*/
export function stockInOut(id, payload) {
  return api.post(`/products/products/${id}/stock_in_out/`, payload)
}
/*查询商品库存流水：参数 params 可含商品、类型、时间范围、分页等；返回流水数组或分页结果。
   后端接口：GET /api/products/stock-records/。*/
export function listStockRecords(params = {}) {
  return api.get('/products/stock-records/' + qs(params))
}

/*获取我的收藏列表：无参数；返回收藏商品数组。
   后端接口：GET /api/products/favorites/。*/
export function listFavorites() {
  return api.get('/products/favorites/')
}
/*添加收藏：参数 productId 商品 id；返回创建结果。
   后端接口：POST /api/products/favorites/，请求体为 { product_id }。*/
export function addFavorite(productId) {
  return api.post('/products/favorites/', { product_id: productId })
}
/*取消收藏：参数 productId 商品 id；返回删除结果。
   后端接口：DELETE /api/products/favorites/remove/?product_id={id}。*/
export function removeFavorite(productId) {
  return api.del('/products/favorites/remove/' + qs({ product_id: productId }))
}
