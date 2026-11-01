/*账号管理接口（管理员后台）：账号列表、创建、修改、开通传承人、启停、重置密码、删除*/
import { api } from './client'
import { qs } from './utils'   // 把参数对象拼成查询字符串

/*获取账号列表：参数 params 可含分页/角色/关键词等筛选条件；返回账号数组或分页结果。
   后端接口：GET /api/accounts/admin/list/，params 会拼到查询串上（如 ?page=1&role=user）。*/
export function listAccounts(params = {}) {
  return api.get('/accounts/admin/list/' + qs(params))
}

/*创建账号：参数 payload 包含用户名、密码、角色等；返回创建结果。
   后端接口：POST /api/accounts/admin/create/。*/
export function createAccount(payload) {
  return api.post('/accounts/admin/create/', payload)
}

/*修改账号信息：参数 payload 包含账号 id 及要修改的字段（如昵称、角色、状态）；返回更新结果。
   后端接口：POST /api/accounts/admin/update-account/。*/
export function updateAccount(payload) {
  return api.post('/accounts/admin/update-account/', payload)
}

/*为账号开通/绑定传承人身份：参数 payload 包含账号 id 和传承人资料；返回处理结果。
   后端接口：POST /api/accounts/admin/issue-inheritor/。*/
export function issueInheritor(payload) {
  return api.post('/accounts/admin/issue-inheritor/', payload)
}

/*启用或禁用账号：参数 payload 包含账号 id（通常还有目标状态）；返回更新结果。
   后端接口：POST /api/accounts/admin/toggle-status/。*/
export function toggleAccountStatus(payload) {
  return api.post('/accounts/admin/toggle-status/', payload)
}

/*重置账号密码：参数 payload 包含账号 id 和新密码；返回处理结果。
   后端接口：POST /api/accounts/admin/reset-password/。*/
export function resetAccountPassword(payload) {
  return api.post('/accounts/admin/reset-password/', payload)
}

/*删除账号：参数 payload 包含账号 id；返回删除结果。
   后端接口：POST /api/accounts/admin/delete-account/。*/
export function deleteAccount(payload) {
  return api.post('/accounts/admin/delete-account/', payload)
}
