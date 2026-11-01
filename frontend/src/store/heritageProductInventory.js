/*作品库存状态：读取作品库存流水，并负责作品出入库、库存状态判断*/
import { reactive } from 'vue'
import { heritageProducts } from './heritageProducts'
import { listStockRecords, stockInOut as apiStockInOut } from '@/api/products'
import { mapKeys } from '@/api/utils'


/*作品库存流水类型映射表：in 入库、out 出库、order 销售出库、loss 损耗*/
export const stockRecordTypeMap = {
  in: { label: '入库', color: '#2e7d32' },
  out: { label: '出库', color: '#1e6fb8' },
  order: { label: '销售出库', color: '#7b1fa2' },
  loss: { label: '损耗', color: '#c62828' },
}

/*
 * 库存流水字段映射：统一成前端字段并补默认值，时间优先取 time，没有再取 createdAt。
 * 参数 r：后端流水记录；返回值：前端流水对象。
 */
function mapRecord(r) {
  const m = mapKeys(r)
  return {
    id: m.id,
    productId: m.productId,
    productName: m.productName || '',
    type: m.type || 'in',
    qty: m.qty ?? 0,
    note: m.note || '',
    operator: m.operator || '管理员',
    time: m.time || m.createdAt || '',
  }
}

/*作品库存流水列表：由 loadStockRecords 整体替换，出入库后重新加载*/
export const stockRecords = reactive([])

/*
 * 加载作品库存流水：调用 listStockRecords()，映射后整体替换 stockRecords；
 * 返回值：更新后的流水列表。
 */
export async function loadStockRecords() {
  const data = await listStockRecords()
  stockRecords.splice(0, stockRecords.length, ...data.map(mapRecord))
  return stockRecords
}

/*
 * 查询作品当前库存：从 heritageProducts 中按 id 找作品，找不到返回 0。
 * 参数 productId：作品 ID；返回值：库存数字。
 */
export function stockOf(productId) {
  const p = heritageProducts.find((x) => x.id === productId)
  return p ? (p.stock ?? 0) : 0
}

/*
 * 计算作品库存状态：非卖品显示“非卖”；库存为 0 缺货；低于等于预警阈值告急；否则充足。
 * 参数 product：作品对象；返回值：{ label, color }。
 */
export function productStockState(product) {
  if (!product) return { label: '—', color: '#9e9e9e' }
  const s = product.stock ?? 0
  const threshold = product.alertThreshold ?? 5
  if (!product.saleable) return { label: '非卖', color: '#9e9e9e' }
  if (s <= 0) return { label: '缺货', color: '#c62828' }
  if (s <= threshold) return { label: '告急', color: '#b8860b' }
  return { label: '充足', color: '#2e7d32' }
}

/*
 * 作品出入库：先校验作品和数量，再调用 apiStockInOut(product.id, { type, qty, note })；
 * 成功后用返回数据原地更新 heritageProducts 中的该作品，并重新加载库存流水；
 * 返回值 { ok:true } 或 { ok:false, msg }（优先使用后端返回的错误详情）。
 */
export async function stockInOut(product, type, qty, note, operator) {
  if (!product) return { ok: false, msg: '请选择作品' }
  if (!qty || qty <= 0) return { ok: false, msg: '数量必须大于 0' }
  try {
    const updated = await apiStockInOut(product.id, { type, qty, note: note || '' })
    const idx = heritageProducts.findIndex((p) => p.id === product.id)
    if (idx >= 0) Object.assign(heritageProducts[idx], mapKeys(updated))
    await loadStockRecords()
    return { ok: true }
  } catch (e) {
    const msg = (e.data && (e.data.msg || e.data.detail)) || e.message || '操作失败'
    return { ok: false, msg }
  }
}
