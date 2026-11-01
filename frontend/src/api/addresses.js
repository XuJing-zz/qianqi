/*收货地址接口：查询地址列表、新增、修改、删除（用户个人中心与下单页使用）*/
import { api } from './client'

/*获取当前用户的收货地址列表：无参数；返回地址数组。
   后端接口：GET /api/orders/addresses/。*/
export const listAddresses = () => api.get('/orders/addresses/')

/*新增收货地址：参数 payload 包含收货人、电话、省市区、详细地址、是否默认等；返回创建后的地址。
   后端接口：POST /api/orders/addresses/。*/
export const createAddress = (payload) => api.post('/orders/addresses/', payload)

/*修改收货地址：参数 id 是地址 id，payload 是要修改的字段；返回更新后的地址。
   后端接口：PATCH /api/orders/addresses/{id}/（只提交传入的字段）。*/
export const updateAddress = (id, payload) => api.patch(`/orders/addresses/${id}/`, payload)

/*删除收货地址：参数 id 是地址 id；返回删除结果。
   后端接口：DELETE /api/orders/addresses/{id}/。*/
export const deleteAddress = (id) => api.del(`/orders/addresses/${id}/`)
