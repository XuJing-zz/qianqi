/*传承人档案接口：传承人列表/新增/修改/删除、启停状态、我的档案、证书上传*/
import { api } from './client'
import { qs } from './utils'

/*获取传承人列表：参数 params 可含分页、级别、工艺、关键词等筛选条件；返回传承人数组或分页结果。
   后端接口：GET /api/heritage/profiles/。*/
export function apiListInheritors(params = {}) {
  return api.get(`/heritage/profiles/${qs(params)}`)
}

/*新增传承人档案：参数 payload 包含姓名、级别、工艺、简介、证书等；返回创建后的档案。
   后端接口：POST /api/heritage/profiles/。*/
export function apiCreateInheritor(payload) {
  return api.post('/heritage/profiles/', payload)
}

/*修改传承人档案：参数 id 是档案 id，payload 是要修改的字段；返回更新后的档案。
   后端接口：PATCH /api/heritage/profiles/{id}/。*/
export function apiUpdateInheritor(id, payload) {
  return api.patch(`/heritage/profiles/${id}/`, payload)
}

/*删除传承人档案：参数 id 是档案 id；返回删除结果。
   后端接口：DELETE /api/heritage/profiles/{id}/。*/
export function apiDeleteInheritor(id) {
  return api.del(`/heritage/profiles/${id}/`)
}

/*切换传承人展示状态（启用/停用）：参数 id 是档案 id；返回更新后的档案。
   后端接口：POST /api/heritage/profiles/{id}/toggle_status/。*/
export function apiToggleInheritorStatus(id) {
  return api.post(`/heritage/profiles/${id}/toggle_status/`)
}

/*获取当前登录用户自己的传承人档案：无参数；返回档案对象。
   后端接口：GET /api/heritage/profiles/my/。*/
export function apiMyInheritor() {
  return api.get('/heritage/profiles/my/')
}

/*上传传承人证书：参数 file 是证书文件；返回文件地址/信息。
   后端接口：POST /api/heritage/profiles/upload_cert/（multipart 表单，字段名 file）。*/
export function apiUploadCert(file) {
  const fd = new FormData()
  fd.append('file', file)
  return api.upload('/heritage/profiles/upload_cert/', fd)
}
