/*传承人档案状态：维护传承人列表及等级/技艺选项，并提供档案的增删改与在职状态切换*/
import { reactive } from 'vue'
import {
  apiListInheritors,
  apiCreateInheritor,
  apiUpdateInheritor,
  apiDeleteInheritor,
  apiToggleInheritorStatus,
} from '@/api/heritage'


/*传承人列表：loadInheritors 会整体替换；前台展示、后台管理都读取这份缓存*/
export const inheritors = reactive([])

/*传承人等级选项：用于表单下拉框和筛选*/
export const inheritorLevels = ['国家级', '省级', '市级']
/*传承技艺选项：用于档案表单的技艺选择*/
export const inheritorCrafts = ['髹漆', '镏金', '雕漆', '螺钿', '描金', '素髹', '犀皮', '填漆', '款彩', '堆漆', '百宝嵌']

/*在职状态映射表：active 在职、leave 离岗，用于状态标签展示*/
export const inheritorStatusMap = {
  active: { label: '在职', color: '#2e7d32' },
  leave: { label: '离岗', color: '#9e9e9e' },
}

/*
 * 补全传承人档案字段：兼容后端下划线命名（account_id/account_username）
 * 与前端驼峰命名（accountId/accountUsername），统一输出驼峰字段。
 */
function mapProfile(p) {
  return {
    ...p,
    accountId: p.account_id ?? (p.accountId ?? null),
    accountUsername: p.account_username ?? (p.accountUsername ?? ''),
  }
}

/*
 * 加载传承人列表：调用 apiListInheritors()，映射后整体替换 inheritors；
 * 返回值：更新后的 inheritors。
 */
export async function loadInheritors() {
  const data = await apiListInheritors()
  inheritors.splice(0, inheritors.length, ...data.map(mapProfile))
  return inheritors
}

/*
 * 新增传承人档案：整理表单字段并补默认值（性别男、等级市级、状态在职等），
 * 调用 apiCreateInheritor；若传入 accountId 会转成后端字段 account_id 建立账号关联。
 * 创建成功后插入列表开头；返回值：新档案的 id。
 */
export async function addInheritor(payload) {
  const body = {
    name: payload.name,
    gender: payload.gender || '男',
    age: payload.age || 0,
    phone: payload.phone || '',
    mentor: payload.mentor || '',
    years: payload.years || 0,
    level: payload.level || '市级',
    craft: payload.craft || '',
    honors: payload.honors || '',
    cert_files: Array.isArray(payload.cert_files) ? payload.cert_files : [],
    intro: payload.intro || '',
    qual: payload.qual || '',
    status: 'active',
  }
  if (payload.accountId) body.account_id = payload.accountId
  const created = await apiCreateInheritor(body)
  const mapped = mapProfile(created)
  inheritors.unshift(mapped)
  return mapped.id
}

/*
 * 编辑传承人档案：整理字段后调用 apiUpdateInheritor(id, body)，
 * 成功后按 id 找到本地档案并原地合并更新；返回值：后端返回的最新档案。
 */
export async function updateInheritor(id, payload) {
  const body = {
    name: payload.name,
    gender: payload.gender || '男',
    age: payload.age || 0,
    phone: payload.phone || '',
    mentor: payload.mentor || '',
    years: payload.years || 0,
    level: payload.level || '市级',
    craft: payload.craft || '',
    honors: payload.honors || '',
    cert_files: Array.isArray(payload.cert_files) ? payload.cert_files : [],
    intro: payload.intro || '',
    qual: payload.qual || '',
  }
  const updated = await apiUpdateInheritor(id, body)
  const idx = inheritors.findIndex((i) => i.id === id)
  if (idx >= 0) Object.assign(inheritors[idx], mapProfile(updated))
  return updated
}

/*
 * 删除传承人档案：调用 apiDeleteInheritor(id)，成功后从本地 inheritors 中移除该项；
 * 无返回值。
 */
export async function removeInheritor(id) {
  await apiDeleteInheritor(id)
  const idx = inheritors.findIndex((i) => i.id === id)
  if (idx >= 0) inheritors.splice(idx, 1)
}

/*
 * 切换传承人在职/离岗状态：调用 apiToggleInheritorStatus(id)，
 * 成功后原地合并更新本地档案；返回值：后端返回的最新档案。
 */
export async function toggleInheritorStatus(id) {
  const updated = await apiToggleInheritorStatus(id)
  const idx = inheritors.findIndex((i) => i.id === id)
  if (idx >= 0) {
    Object.assign(inheritors[idx], mapProfile(updated))
  }
  return updated
}
