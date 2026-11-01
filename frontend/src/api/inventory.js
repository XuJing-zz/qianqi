/*库存接口：原材料增删改查与出入库、库存流水、发货单创建/发货/签收*/
import { api } from './client'
import { qs } from './utils'

/*获取原材料列表：参数 params 可含分页、类型、状态、关键词等；返回原材料数组或分页结果。
   后端接口：GET /api/inventory/materials/。*/
export function listMaterials(params = {}) {
  return api.get('/inventory/materials/' + qs(params))
}
/*新增原材料：参数 payload 包含名称、类型、单位、库存数量、预警值等；返回创建后的材料。
   后端接口：POST /api/inventory/materials/。*/
export function createMaterial(payload) {
  return api.post('/inventory/materials/', payload)
}
/*修改原材料：参数 id 材料 id，payload 是要修改的字段；返回更新后的材料。
   后端接口：PATCH /api/inventory/materials/{id}/。*/
export function updateMaterial(id, payload) {
  return api.patch(`/inventory/materials/${id}/`, payload)
}
/*删除原材料：参数 id 材料 id；返回删除结果。
   后端接口：DELETE /api/inventory/materials/{id}/。*/
export function deleteMaterial(id) {
  return api.del(`/inventory/materials/${id}/`)
}
/*原材料出入库：参数 id 材料 id，type 类型（in=入库/out=出库），qty 数量，note 备注；
   返回更新后的材料或流水记录。后端接口：POST /api/inventory/materials/{id}/stock_in_out/。*/
export function stockInOut(id, type, qty, note) {
  return api.post(`/inventory/materials/${id}/stock_in_out/`, { type, qty, note })
}

/*查询库存流水记录：参数 params 可含材料、类型、时间范围、分页等；返回流水数组或分页结果。
   后端接口：GET /api/inventory/stock-records/。*/
export function listStockRecords(params = {}) {
  return api.get('/inventory/stock-records/' + qs(params))
}

/*获取发货单列表：参数 params 可含分页、状态、关键词等；返回发货单数组或分页结果。
   后端接口：GET /api/inventory/shipments/。*/
export function listShipments(params = {}) {
  return api.get('/inventory/shipments/' + qs(params))
}
/*创建发货单：参数 payload 包含学员/订单、材料明细、收货信息等；返回创建后的发货单。
   后端接口：POST /api/inventory/shipments/。*/
export function createShipment(payload) {
  return api.post('/inventory/shipments/', payload)
}
/*发货：参数 id 发货单 id，company 物流公司，trackingNo 快递单号；返回更新后的发货单。
   后端接口：POST /api/inventory/shipments/{id}/ship/。*/
export function shipShipment(id, company, trackingNo) {
  return api.post(`/inventory/shipments/${id}/ship/`, { company, tracking_no: trackingNo })
}
/*签收发货单：参数 id 发货单 id；把状态标记为已签收，返回更新后的发货单。
   后端接口：POST /api/inventory/shipments/{id}/sign/。*/
export function signShipment(id) {
  return api.post(`/inventory/shipments/${id}/sign/`)
}
