/*联系留言接口：用户提交留言，管理员查询、处理、删除留言*/
import { api } from './client'
import { qs } from './utils'

/*提交联系留言：参数 payload 包含姓名、联系方式、留言内容等；返回创建结果。
   后端接口：POST /api/system/messages/。*/
export function submitContactMessage(payload) {
  return api.post('/system/messages/', payload)
}

/*查询留言列表（管理员）：参数 params 可含分页、状态、关键词等；返回留言数组或分页结果。
   后端接口：GET /api/system/messages/，params 会拼成查询串。*/
export function listContactMessages(params = {}) {
  return api.get('/system/messages/' + qs(params))
}

/*处理留言：参数 id 是留言 id，payload 通常是 { status, reply } 等处理结果；返回更新后的留言。
   后端接口：PATCH /api/system/messages/{id}/。*/
export function handleContactMessage(id, payload) {
  return api.patch(`/system/messages/${id}/`, payload)
}

/*删除留言：参数 id 是留言 id；返回删除结果。
   后端接口：DELETE /api/system/messages/{id}/。*/
export function removeContactMessage(id) {
  return api.del(`/system/messages/${id}/`)
}
