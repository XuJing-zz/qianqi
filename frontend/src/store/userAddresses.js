/*收货地址状态：维护当前用户的收货地址列表，支持默认地址排序及增删改*/
import { reactive } from 'vue'
import { listAddresses, createAddress, updateAddress, deleteAddress } from '@/api/addresses'
import { mapKeys, mapToSnake } from '@/api/utils'


/*收货地址列表：由 loadAddresses 填充，默认地址排在最前面*/
export const addresses = reactive([])

/*
 * 地址字段映射：统一成驼峰命名，并同时提供 receiver/name 两种收件人字段，
 * 兼容不同页面使用的字段名；isDefault 统一转成布尔值。
 * 参数 a：后端地址数据；返回值：前端地址对象。
 */
function mapAddr(a) {
  const m = mapKeys(a)
  return {
    id: m.id,
    receiver: m.receiver || '',
    name: m.receiver || '',
    phone: m.phone || '',
    province: m.province || '',
    city: m.city || '',
    district: m.district || '',
    detail: m.detail || '',
    full: m.full || '',
    isDefault: !!m.isDefault,
  }
}

// sort：sort(比较函数) 原地排序数组；比较函数返回负数表示 a 排前面
/*
 * 地址排序：默认地址优先，其次按 id 从大到小（新地址靠前）。
 * 原地修改 addresses，无返回值。
 */
function sortList() {
  addresses.sort((a, b) => (b.isDefault ? 1 : 0) - (a.isDefault ? 1 : 0) || b.id - a.id)
}

/*
 * 加载收货地址：调用 listAddresses()，映射后整体替换 addresses，并重新排序；
 * 返回值：更新后的地址列表。
 */
export async function loadAddresses() {
  const data = await listAddresses()
  addresses.splice(0, addresses.length, ...data.map(mapAddr))
  sortList()
  return addresses
}

/*
 * 新增收货地址：把前端字段转成下划线命名后调用 createAddress，
 * 成功后插入列表并重新排序；返回值：映射后的新地址。
 */
export async function addAddress(payload) {
  const created = await createAddress(mapToSnake(payload))
  addresses.unshift(mapAddr(created))
  sortList()
  return mapAddr(created)
}

/*
 * 编辑收货地址：调用 updateAddress(id, snake)，成功后按下标直接替换该地址项并重新排序；
 * 返回值：映射后的最新地址。
 */
export async function updateAddressAction(id, payload) {
  const updated = await updateAddress(id, mapToSnake(payload))
  const mapped = mapAddr(updated)
  const idx = addresses.findIndex((a) => a.id === id)
  if (idx >= 0) addresses[idx] = mapped
  sortList()
  return mapped
}

/*
 * 删除收货地址：调用 deleteAddress(id)，成功后从 addresses 中移除并重新排序；
 * 无返回值。
 */
export async function removeAddress(id) {
  await deleteAddress(id)
  const idx = addresses.findIndex((a) => a.id === id)
  if (idx >= 0) addresses.splice(idx, 1)
  sortList()
}
