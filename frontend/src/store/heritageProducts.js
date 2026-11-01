/*作品管理状态：维护传承人/后台的作品列表，并提供新增、编辑、删除、提交审核和审核操作*/
import { reactive } from 'vue'
import { listProducts, createProduct, updateProduct, deleteProduct, reviewProduct, submitProduct } from '@/api/products'
import { mapKeys, mapToSnake } from '@/api/utils'


/*作品列表：包含草稿/待审核/已通过/已驳回/已下架等状态，由 loadProducts 填充*/
export const heritageProducts = reactive([])

/*作品审核状态映射表：draft 草稿、pending 待审核、approved 已通过、rejected 已驳回、offline 已下架*/
export const productStatusMap = {
  draft: { label: '草稿', color: '#6b5a44' },
  pending: { label: '待审核', color: '#b8860b' },
  approved: { label: '已通过', color: '#2e7d32' },
  rejected: { label: '已驳回', color: '#c62828' },
  offline: { label: '已下架', color: '#9e9e9e' },
}

/*
 * 作品字段映射：统一成驼峰命名，把价格转成数字，
 * 并确保图片、亮点始终是数组，补全提交时间和审核意见默认值。
 * 参数 p：后端作品数据；返回值：前端作品对象。
 */
function mapProduct(p) {
  const m = mapKeys(p)
  return {
    ...m,
    price: Number(m.price ?? 0),
    images: Array.isArray(m.images) ? m.images : [],
    highlights: Array.isArray(m.highlights) ? m.highlights : [],
    submitTime: m.submitTime || '',
    reviewComment: m.reviewComment || '',
  }
}

/*
 * 加载作品列表：调用 listProducts()，映射后整体替换 heritageProducts；
 * 返回值：更新后的作品列表。
 */
export async function loadProducts() {
  const data = await listProducts()
  heritageProducts.splice(0, heritageProducts.length, ...data.map(mapProduct))
  return heritageProducts
}

/*
 * 新增作品：把前端字段转成下划线命名后调用 createProduct，
 * 创建成功后插入作品列表开头；返回值：映射后的新作品。
 */
export async function addProduct(payload) {
  const created = await createProduct(mapToSnake(payload))
  const mapped = mapProduct(created)
  heritageProducts.unshift(mapped)
  return mapped
}

/*
 * 编辑作品：调用 updateProduct(id, snake)，成功后按 id 原地合并更新作品；
 * 返回值：映射后的最新作品。
 */
export async function updateProductAction(id, payload) {
  const updated = await updateProduct(id, mapToSnake(payload))
  const idx = heritageProducts.findIndex((p) => p.id === id)
  if (idx >= 0) Object.assign(heritageProducts[idx], mapProduct(updated))
  return mapProduct(updated)
}

/*
 * 删除作品：调用 deleteProduct(id)，成功后从 heritageProducts 中移除；
 * 无返回值。
 */
export async function removeProduct(id) {
  await deleteProduct(id)
  const idx = heritageProducts.findIndex((p) => p.id === id)
  if (idx >= 0) heritageProducts.splice(idx, 1)
}

/*
 * 提交作品审核：调用 submitProduct(id)，成功后原地更新作品状态；
 * 返回值：映射后的最新作品。
 */
export async function submitProductAction(id) {
  const updated = await submitProduct(id)
  const idx = heritageProducts.findIndex((p) => p.id === id)
  if (idx >= 0) Object.assign(heritageProducts[idx], mapProduct(updated))
  return mapProduct(updated)
}

/*
 * 审核作品：调用 reviewProduct(id, action, reviewComment)，
 * action 通常是通过/驳回；成功后原地更新作品；返回值：映射后的最新作品。
 */
export async function reviewProductAction(id, action, reviewComment) {
  const updated = await reviewProduct(id, action, reviewComment)
  const idx = heritageProducts.findIndex((p) => p.id === id)
  if (idx >= 0) Object.assign(heritageProducts[idx], mapProduct(updated))
  return mapProduct(updated)
}
