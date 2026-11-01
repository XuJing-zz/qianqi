/*平台订单状态：维护后台订单列表，并提供发货、取消、完成等状态流转操作*/
import { reactive } from 'vue'
import { listOrders, shipOrder, completeOrder, cancelOrder } from '@/api/orders'
import { mapKeys } from '@/api/utils'


/*后台订单列表：由 loadOrders 填充，状态变更后原地更新对应订单*/
export const heritageOrders = reactive([])

/*订单状态映射表：覆盖审核、付款、发货、完成、取消、驳回等状态，供后台表格展示标签*/
export const orderStatusMap = {
  review: { label: '待审核', color: '#e6a23c' },
  pending: { label: '待付款', color: '#b8860b' },
  paid: { label: '待发货', color: '#1e6fb8' },
  shipped: { label: '已发货', color: '#2e7d32' },
  done: { label: '已完成', color: '#9e9e9e' },
  cancelled: { label: '已取消', color: '#9e9e9e' },
  rejected: { label: '已驳回', color: '#f56c6c' },
}

/*
 * 订单字段映射：统一字段命名，把价格转成数字，
 * 补全订单号、状态日志、商品名、买家电话、支付/发货信息等默认值。
 * 参数 o：后端订单；返回值：前端订单对象。
 */
function mapOrder(o) {
  const m = mapKeys(o)
  return {
    ...m,
    price: Number(m.price ?? 0),
    // padStart：padStart(总长度, 填充字符) 在字符串开头补字符到指定长度；后端没给订单号时生成 QQ+8 位数字
    orderNo: m.orderNo || ('QQ' + String(m.id ?? 0).padStart(8, '0')),
    statusLogs: Array.isArray(m.statusLogs) ? m.statusLogs : [],
    itemName: m.itemName || '',
    name: m.itemName || '',
    buyerPhone: m.buyerPhone || '',
    payMethod: m.payMethod || '',
    orderTime: m.orderTime || '',
    payTime: m.payTime || '',
    company: m.company || '',
    trackingNo: m.trackingNo || '',
    shipTime: m.shipTime || '',
  }
}

/*
 * 加载后台订单：调用 listOrders()，映射后整体替换 heritageOrders；
 * 返回值：更新后的订单列表。
 */
export async function loadOrders() {
  const data = await listOrders()
  heritageOrders.splice(0, heritageOrders.length, ...data.map(mapOrder))
  return heritageOrders
}

/*
 * 订单发货：调用 shipOrder(id, { company, tracking_no })，其中 trackingNo 会转成后端字段 tracking_no；
 * 成功后按 id 原地更新订单；返回值：映射后的最新订单。
 */
export async function shipOrderAction(id, { company = '', trackingNo = '' } = {}) {
  const updated = await shipOrder(id, { company, tracking_no: trackingNo })
  const idx = heritageOrders.findIndex((o) => o.id === id)
  if (idx >= 0) Object.assign(heritageOrders[idx], mapOrder(updated))
  return mapOrder(updated)
}

/*
 * 取消订单：调用 cancelOrder(id)，成功后原地更新本地订单；
 * 返回值：映射后的最新订单。
 */
export async function cancelOrderAction(id) {
  const updated = await cancelOrder(id)
  const idx = heritageOrders.findIndex((o) => o.id === id)
  if (idx >= 0) Object.assign(heritageOrders[idx], mapOrder(updated))
  return mapOrder(updated)
}

/*
 * 完成订单：调用 completeOrder(id)，成功后原地更新本地订单；
 * 返回值：映射后的最新订单。
 */
export async function completeOrderAction(id) {
  const updated = await completeOrder(id)
  const idx = heritageOrders.findIndex((o) => o.id === id)
  if (idx >= 0) Object.assign(heritageOrders[idx], mapOrder(updated))
  return mapOrder(updated)
}
