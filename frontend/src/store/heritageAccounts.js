/*后台账号管理状态：维护用户/管理员/传承人账号列表，并提供增删改、启禁用、重置密码等操作*/
import { reactive } from 'vue'
import { addInheritor } from './heritageInheritors'
import { listAccounts, createAccount, updateAccount as apiUpdateAccount, issueInheritor, toggleAccountStatus as apiToggleStatus, resetAccountPassword, deleteAccount as apiDeleteAccount } from '@/api/accounts'
import { mapKeys } from '@/api/utils'


/*账号列表：loadAccounts / loadAllAccounts 会整体替换这里的数据，后台账号页按角色展示*/
export const accounts = reactive([])

/*角色映射表：把后端角色代码翻译成中文标签和标签颜色，供表格/徽章渲染*/
export const accountRoleMap = {
  admin: { label: '管理员', color: '#1e6fb8' },
  heritage: { label: '传承人', color: '#2e7d32' },
  user: { label: '学员', color: '#6b5a44' },
}

/*账号状态映射表：active 正常、disabled 禁用，用于状态标签展示*/
export const accountStatusMap = {
  active: { label: '正常', color: '#2e7d32' },
  disabled: { label: '禁用', color: '#c62828' },
}

/*
 * 把后端账号对象映射成前端使用的结构：先统一字段命名，再补 createdAt 默认值。
 * 参数 u：后端单条账号；返回值：可直接存入 accounts 的账号对象。
 */
function mapUser(u) {
  const m = mapKeys(u)
  return {
    ...m,
    createdAt: m.createdAt || '',
  }
}

/*
 * 按角色加载账号：调用 listAccounts({ role })，默认只取学员（user），
 * 用结果整体替换 accounts；参数 role 可传 admin / heritage；返回值：accounts。
 */
export async function loadAccounts(role = 'user') {
  const data = await listAccounts({ role })
  accounts.splice(0, accounts.length, ...data.map(mapUser))
  return accounts
}

/*
 * 加载全部角色的账号：依次请求 user、admin、heritage 三个角色并合并结果，
 * 最后整体替换 accounts；返回值：包含所有角色的 accounts。
 */
export async function loadAllAccounts() {
  const all = []
  for (const role of ['user', 'admin', 'heritage']) {
    const data = await listAccounts({ role })
    all.push(...data.map(mapUser))
  }
  accounts.splice(0, accounts.length, ...all)
  return accounts
}

/*
 * 新增账号：调用 createAccount(payload)，密码未填时默认 123456；
 * 创建成功后把新账号插入列表开头；返回值 { ok, id } 或 { ok:false, msg }。
 */
export async function addAccount(payload) {
  try {
    const created = await createAccount({
      username: payload.username,
      password: payload.password || '123456',
      name: payload.name,
      role: payload.role,
      phone: payload.phone || '',
      email: payload.email || '',
    })
    // unshift：unshift(值) 把元素插到数组开头，这里让最新创建的账号显示在最前面
    accounts.unshift(mapUser(created))
    return { ok: true, id: created.id }
  } catch (e) {
    return { ok: false, msg: e.message || '创建失败' }
  }
}

/*
 * 按引用或 ID 找到列表中的账号：
 * 传对象时直接返回该对象；传 ID 时在 accounts 中查找；找不到返回 undefined。
 */
function byRef(idOrObj) {
  return typeof idOrObj === 'object' ? idOrObj : accounts.find((a) => a.id === idOrObj)
}

// Object.assign：Object.assign(目标, 来源) 把来源对象的字段合并进目标对象并返回目标对象；这里原地更新账号项，页面持有的引用不会失效
/*
 * 修改账号资料：调用 apiUpdateAccount（后端要求同时带 role 和 id），
 * payload 中未传的字段沿用原值；成功后原地合并更新 accounts；返回值 { ok } 或 { ok:false, msg }。
 */
export async function updateAccountAction(acc, payload) {
  const a = byRef(acc)
  try {
    if (!a) return { ok: false, msg: '账号不存在' }
    const updated = await apiUpdateAccount({
      role: a.role,
      id: a.id,
      username: payload.username ?? a.username,
      name: payload.name ?? a.name,
      phone: payload.phone ?? a.phone,
      email: payload.email ?? a.email,
    })
    Object.assign(a, mapUser(updated))
    return { ok: true }
  } catch (e) {
    return { ok: false, msg: e.message || '保存失败' }
  }
}

/*
 * 切换账号启用/禁用：调用 apiToggleStatus({ role, id })，成功后原地更新该账号；
 * 无返回值，状态由后端返回结果决定。
 */
export async function toggleAccountStatus(acc) {
  const a = byRef(acc)
  if (a) {
    const updated = await apiToggleStatus({ role: a.role, id: a.id })
    Object.assign(a, mapUser(updated))
  }
}

/*
 * 修改账号角色：后端没有直接的改角色接口，这里用 createAccount 以新角色重新创建账号
 *（用户名、姓名、手机号沿用原值，密码重置为 123456），原账号不会被删除。
 * 返回值 { ok, created } 或 { ok:false, msg }。
 */
export async function changeAccountRole(acc, role) {
  const a = byRef(acc)
  try {
    if (!a) return { ok: false, msg: '账号不存在' }
    const created = await createAccount({
      username: a.username,
      password: '123456',
      name: a.name,
      role,
      phone: a.phone || '',
    })
    return { ok: true, created }
  } catch (e) {
    return { ok: false, msg: e.message || '修改失败' }
  }
}

/*
 * 重置密码：调用 resetAccountPassword({ role, id })，后端会把密码重置为 123456；
 * 返回值 { ok, msg } 或 { ok:false, msg }。
 */
export async function resetPassword(acc) {
  const a = byRef(acc)
  try {
    await resetAccountPassword({ role: a.role, id: a.id })
    return { ok: true, msg: `已重置 ${a.name} 的密码为 123456` }
  } catch (e) {
    return { ok: false, msg: e.message || '重置失败' }
  }
}

// findIndex：findIndex(回调) 返回第一个满足条件的元素下标，找不到返回 -1；这里按 id 找到要删除的账号位置
/*
 * 删除账号：调用 apiDeleteAccount({ role, id, confirm })；
 * 若账号名下仍有数据，后端返回 need_confirm，此时返回 { ok:false, needConfirm:true, impact } 让页面二次确认；
 * 删除成功后从 accounts 中移除该项；返回值 { ok, msg } 或失败信息。
 */
export async function removeAccount(acc, { confirm = false } = {}) {
  const a = byRef(acc)
  if (!a) return { ok: false, msg: '账号不存在' }
  try {
    const res = await apiDeleteAccount({ role: a.role, id: a.id, confirm })
    const idx = accounts.findIndex((x) => x.id === a.id && x.role === a.role)
    if (idx >= 0) accounts.splice(idx, 1)
    return { ok: true, msg: res.msg || '已删除' }
  } catch (e) {
    const data = e && e.data
    if (data && data.need_confirm) {
      return {
        ok: false,
        needConfirm: true,
        msg: data.msg || '该账号名下仍有数据',
        impact: Array.isArray(data.impact) ? data.impact : [],
      }
    }
    return { ok: false, msg: (e && e.message) || '删除失败' }
  }
}

/*
 * 发放传承人账号：分两步——
 * 1. 调用 issueInheritor 创建 role=heritage 的登录账号；
 * 2. 调用 addInheritor 创建传承人档案，并用 accountId 关联刚创建的账号。
 * 返回值 { ok, accountId, inheritorId } 或 { ok:false, msg }。
 */
export async function issueHeritageAccount(payload) {
  try {
    const created = await issueInheritor({
      username: payload.username,
      name: payload.name,
      password: payload.password || '123456',
      phone: payload.phone || '',
      email: payload.email || '',
    })
    const accountId = created.id

    const inheritorId = await addInheritor({
      name: payload.name,
      gender: '',
      age: 0,
      phone: payload.phone || '',
      mentor: '',
      years: 0,
      level: '',
      craft: '',
      qual: '',
      honors: '',
      intro: '',
      accountId,
    })

    return { ok: true, accountId, inheritorId }
  } catch (e) {
    return { ok: false, msg: e.message || '发放失败' }
  }
}
