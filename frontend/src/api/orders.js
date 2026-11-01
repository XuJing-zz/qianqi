/*订单接口：订单查询/创建（课程下单、商品下单）、支付、发货、完成、取消、审核与状态修改*/
import { api } from './client'
import { qs } from './utils'

/*获取订单列表：参数 params 可含分页、状态、类型、关键词等；返回订单数组或分页结果。
   后端接口：GET /api/orders/orders/。*/
export const listOrders = (params = {}) => api.get('/orders/orders/' + qs(params))
/*创建课程订单：参数 payload 包含课程、价格、购买人等；返回创建后的订单。
   后端接口：POST /api/orders/orders/。*/
export const createOrder = (payload) => api.post('/orders/orders/', payload)
/*购买商品下单：参数 payload 包含商品 id、数量、收货地址、支付方式等；返回创建后的订单。
   后端接口：POST /api/orders/orders/buy_product/。*/
export const buyProductOrder = (payload) => api.post('/orders/orders/buy_product/', payload)
/*支付订单：参数 id 订单 id，payload 通常含 pay_method 支付方式；返回支付后的订单。
   后端接口：POST /api/orders/orders/{id}/pay/。*/
export const payOrder = (id, payload = {}) => api.post(`/orders/orders/${id}/pay/`, payload)
/*订单发货：参数 id 订单 id，payload 含物流公司、快递单号等；返回发货后的订单。
   后端接口：POST /api/orders/orders/{id}/ship/。*/
export const shipOrder = (id, payload = {}) => api.post(`/orders/orders/${id}/ship/`, payload)
/*确认完成订单（用户确认收货）：参数 id 订单 id；返回完成后的订单。
   后端接口：POST /api/orders/orders/{id}/complete/。*/
export const completeOrder = (id) => api.post(`/orders/orders/${id}/complete/`)
/*取消订单：参数 id 订单 id；返回取消后的订单。
   后端接口：POST /api/orders/orders/{id}/cancel/。*/
export const cancelOrder = (id) => api.post(`/orders/orders/${id}/cancel/`)
/*审核订单（管理员）：参数 id 订单 id，payload 含审核动作和备注；返回审核后的订单。
   后端接口：POST /api/orders/orders/{id}/audit/。*/
export const auditOrder = (id, payload) => api.post(`/orders/orders/${id}/audit/`, payload)
/*手动创建订单（管理员/后台代下单）：参数 payload 是完整订单信息；返回创建后的订单。
   后端接口：POST /api/orders/orders/manual_create/。*/
export const manualCreateOrder = (payload) => api.post('/orders/orders/manual_create/', payload)
/*直接修改订单状态（管理员）：参数 id 订单 id，payload 含目标状态等；返回更新后的订单。
   后端接口：POST /api/orders/orders/{id}/set_status/。*/
export const setOrderStatus = (id, payload) => api.post(`/orders/orders/${id}/set_status/`, payload)
