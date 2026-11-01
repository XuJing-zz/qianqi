/*材料库存状态：管理材料/工具库存、出入库流水、学员材料包寄送单，并派生待寄送清单*/
import { reactive, computed } from 'vue'
import { heritageStudents } from './heritageStudents'
import {
  listMaterials, createMaterial, updateMaterial, deleteMaterial, stockInOut,
  listShipments, createShipment, shipShipment, signShipment,
  listStockRecords,
} from '@/api/inventory'
import { mapKeys, mapToSnake } from '@/api/utils'


/*材料/工具库存列表：由 loadMaterials 填充，新增、编辑、出入库后同步更新*/
export const inventoryMaterials = reactive([])
/*材料出入库流水列表：由 loadMaterialStockRecords 填充，用于库存记录页展示*/
export const materialStockRecords = reactive([])
/*材料包寄送单列表：由 loadShipments 填充，发货/签收后原地更新对应记录*/
export const shipments = reactive([])

/*
 * 计算材料库存状态：库存为 0 显示缺货，低于等于预警阈值显示告急，否则充足。
 * 参数 m：材料对象（含 stock、alertThreshold）；返回值：{ label, color }。
 */
export function materialState(m) {
  if (m.stock <= 0) return { label: '缺货', color: '#c62828' }
  if (m.stock <= m.alertThreshold) return { label: '告急', color: '#b8860b' }
  return { label: '充足', color: '#2e7d32' }
}

/*材料流水类型映射表：in 入库、out 领用出库、loss 损耗*/
export const materialRecordTypeMap = {
  in: { label: '入库', color: '#2e7d32' },
  out: { label: '领用出库', color: '#1e6fb8' },
  loss: { label: '损耗', color: '#c62828' },
}

/*物料类型映射表：material 基础材料、tool 工具*/
export const materialTypeMap = {
  material: { label: '基础材料', color: '#8b2e1c' },
  tool: { label: '工具', color: '#1e6fb8' },
}

/*寄送单状态映射表：pending 待寄、shipped 已寄、signed 已签收*/
export const shipmentStatusMap = {
  pending: { label: '待寄', color: '#b8860b' },
  shipped: { label: '已寄', color: '#1e6fb8' },
  signed: { label: '已签收', color: '#2e7d32' },
}

/*
 * 材料字段映射：统一成驼峰命名，并把库存转成数字、补预警阈值和关联课程默认值。
 * 参数 m：后端材料数据；返回值：前端材料对象。
 */
function mapMaterial(m) {
  const mm = mapKeys(m)
  return {
    ...mm,
    stock: Number(mm.stock ?? 0),
    alertThreshold: mm.alertThreshold ?? 5,
    linkedCourseId: mm.linkedCourseId ?? 0,
  }
}

/*
 * 寄送单字段映射：补全快递单号、发货时间，并确保 items 始终是数组。
 * 参数 s：后端寄送单；返回值：前端寄送单对象。
 */
function mapShipment(s) {
  const m = mapKeys(s)
  return {
    ...m,
    trackingNo: m.trackingNo || '',
    shipTime: m.shipTime || '',
    items: Array.isArray(m.items) ? m.items : [],
  }
}

/*
 * 加载材料/工具库存：调用 listMaterials()，映射后整体替换 inventoryMaterials；
 * 返回值：更新后的 inventoryMaterials。
 */
export async function loadMaterials() {
  const data = await listMaterials()
  inventoryMaterials.splice(0, inventoryMaterials.length, ...data.map(mapMaterial))
  return inventoryMaterials
}

/*
 * 加载寄送单：调用 listShipments()，映射后整体替换 shipments；
 * 返回值：更新后的 shipments。
 */
export async function loadShipments() {
  const data = await listShipments()
  shipments.splice(0, shipments.length, ...data.map(mapShipment))
  return shipments
}

/*
 * 加载材料出入库流水：调用 listStockRecords()，映射后整体替换 materialStockRecords；
 * 返回值：更新后的流水列表。
 */
export async function loadMaterialStockRecords() {
  const data = await listStockRecords()
  materialStockRecords.splice(0, materialStockRecords.length, ...data.map((r) => mapKeys(r)))
  return materialStockRecords
}

/*
 * 新增材料：把前端字段转成下划线命名后调用 createMaterial，
 * 创建成功后插入库存列表开头；返回值：映射后的新材料。
 */
export async function addMaterial(payload) {
  const created = await createMaterial(mapToSnake(payload))
  const mapped = mapMaterial(created)
  inventoryMaterials.unshift(mapped)
  return mapped
}

/*
 * 编辑材料：调用 updateMaterial(id, snake)，成功后按 id 原地合并更新库存项；
 * 返回值：映射后的最新材料。
 */
export async function updateMaterialAction(id, payload) {
  const updated = await updateMaterial(id, mapToSnake(payload))
  const idx = inventoryMaterials.findIndex((m) => m.id === id)
  if (idx >= 0) Object.assign(inventoryMaterials[idx], mapMaterial(updated))
  return mapMaterial(updated)
}

/*
 * 删除材料：调用 deleteMaterial(id)，成功后从 inventoryMaterials 中移除；
 * 无返回值。
 */
export async function removeMaterial(id) {
  await deleteMaterial(id)
  const idx = inventoryMaterials.findIndex((m) => m.id === id)
  if (idx >= 0) inventoryMaterials.splice(idx, 1)
}

/*
 * 材料出入库：先校验材料和数量，再调用 stockInOut(material.id, type, qty, note)，
 * 成功后原地更新该材料库存；返回值 { ok:true } 或 { ok:false, msg }。
 * operator 参数当前未提交给后端，仅保留调用方传入的操作人信息。
 */
export async function materialStockInOut(material, type, qty, note, operator) {
  if (!material) return { ok: false, msg: '物料不存在' }
  if (!qty || qty <= 0) return { ok: false, msg: '数量必须大于 0' }
  try {
    const updated = await stockInOut(material.id, type, qty, note)
    const idx = inventoryMaterials.findIndex((m) => m.id === material.id)
    if (idx >= 0) Object.assign(inventoryMaterials[idx], mapMaterial(updated))
    return { ok: true }
  } catch (e) {
    return { ok: false, msg: e.message || '操作失败' }
  }
}

/*
 * 读取学员材料计划：返回 student.materialPlan，没有时返回空数组。
 * 参数 student：学员对象；返回值：材料计划数组。
 */
export function getStudentMaterialPlan(student) {
  return (student && student.materialPlan) || []
}

/*
 * 设置学员材料计划：直接修改传入学员对象的 materialPlan 字段（原地修改，不请求后端）。
 * 每条计划会用 materialId 从库存中查出材料名并补进去，数量缺省为 1。
 * 参数 student：学员对象；plan：{ materialId, qty } 数组。
 */
export function setStudentMaterialPlan(student, plan) {
  if (!student) return
  if (!plan || !plan.length) {
    student.materialPlan = []
    return
  }
  student.materialPlan = plan.map((p) => {
    const m = inventoryMaterials.find((x) => x.id === p.materialId)
    return { materialId: p.materialId, materialName: m ? m.name : '', qty: p.qty || 1 }
  })
}

// some：some(回调) 判断数组中是否至少有一个元素满足条件，返回 true/false；这里用于判断该学员是否已有已寄/已签收的寄送单
/*
 * 判断某学员是否已经发过材料：存在状态为 shipped 或 signed 的寄送单即视为已寄。
 * 参数 studentId：学员 ID；返回值：布尔值。
 */
function alreadyShipped(studentId) {
  return shipments.some((s) => s.studentId === studentId && (s.status === 'shipped' || s.status === 'signed'))
}

/*
 * 派生“待生成寄送单”清单：遍历进行中的学员，过滤掉已寄送和没有材料计划的，
 * 把学员信息与其材料计划整理成寄送单结构。该列表只读，随依赖数据自动更新。
 */
export const derivedShipments = computed(() => {
  const list = []
  for (const stu of heritageStudents) {
    if (stu.status !== 'ongoing') continue
    if (alreadyShipped(stu.id)) continue
    const plan = getStudentMaterialPlan(stu)
    if (!plan.length) continue
    list.push({
      studentId: stu.id,
      studentName: stu.name,
      courseId: stu.courseId,
      courseName: stu.courseName,
      items: plan.map((p) => ({ materialId: p.materialId, materialName: p.materialName, qty: p.qty })),
    })
  }
  return list
})

// filter：filter(回调) 返回由满足条件的元素组成的新数组，不修改原数组；这里筛出关联到指定课程的材料
/*
 * 查询某课程关联的材料：按 linkedCourseId 过滤库存列表。
 * 参数 courseId：课程 ID；返回值：材料数组。
 */
export function courseMaterials(courseId) {
  return inventoryMaterials.filter((m) => m.linkedCourseId === courseId)
}

/*
 * 检查寄送单库存是否充足：逐项对比材料库存与所需数量，
 * 不存在材料或库存不足时记录缺口；返回值：缺口数组 [{ materialName, need, have }]，空数组表示可发货。
 * 参数 shipment：含 items 的寄送单对象。
 */
export function checkStock(shipment) {
  const shortage = []
  for (const it of shipment.items) {
    const mat = inventoryMaterials.find((m) => m.id === it.materialId)
    if (!mat || mat.stock < (it.qty || 1)) {
      shortage.push({ materialName: it.materialName, need: it.qty || 1, have: mat ? mat.stock : 0 })
    }
  }
  return shortage
}

/*
 * 创建寄送单：把前端寄送单转成后端下划线字段后调用 createShipment，
 * 创建成功后插入 shipments 开头；返回值：映射后的寄送单。
 */
export async function createShipmentAction(shipment) {
  const created = await createShipment({
    student_id: shipment.studentId,
    student_name: shipment.studentName,
    course_id: shipment.courseId,
    course_name: shipment.courseName,
    items: shipment.items,
  })
  const mapped = mapShipment(created)
  shipments.unshift(mapped)
  return mapped
}

/*
 * 寄送发货：参数可传寄送单对象或 ID，调用 shipShipment(id, company, trackingNo)；
 * 成功后原地更新寄送单，并重新加载材料库存（发货会扣减库存）；
 * 返回值 { ok:true } 或 { ok:false, msg }。
 */
export async function shipOut(shipmentOrId, company, trackingNo) {
  const id = typeof shipmentOrId === 'object' ? shipmentOrId.id : shipmentOrId
  try {
    const updated = await shipShipment(id, company, trackingNo)
    const idx = shipments.findIndex((s) => s.id === id)
    if (idx >= 0) Object.assign(shipments[idx], mapShipment(updated))
    await loadMaterials()
    return { ok: true }
  } catch (e) {
    return { ok: false, msg: e.message || '发货失败' }
  }
}

/*
 * 寄送单签收：调用 signShipment(id)，成功后原地更新寄送单状态；
 * 返回值：映射后的最新寄送单。
 */
export async function signShipmentAction(id) {
  const updated = await signShipment(id)
  const idx = shipments.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(shipments[idx], mapShipment(updated))
  return mapShipment(updated)
}
