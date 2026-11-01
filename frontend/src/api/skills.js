/*技艺/技能接口：技艺列表与分类、新增/修改/删除、审核/提交/上下线、图片与文档上传*/
import { api } from './client'

/*获取技艺列表：参数 params 可含分页、分类、级别、关键词等；返回技艺数组或分页结果。
   后端接口：GET /api/skills/skills/。*/
export const listSkills = (params = {}) => api.get('/skills/skills/' + qs(params))
/*获取技艺分类选项：无参数；返回分类数组，供筛选下拉框使用。
   后端接口：GET /api/skills/skills/categories/。*/
export const listSkillCategories = () => api.get('/skills/skills/categories/')
/*新增技艺：参数 payload 是技艺表单数据（名称、分类、级别、简介、图片等）；返回创建后的技艺。
   后端接口：POST /api/skills/skills/。*/
export const createSkill = (payload) => api.post('/skills/skills/', payload)
/*修改技艺：参数 id 技艺 id，payload 是要修改的字段；返回更新后的技艺。
   后端接口：PATCH /api/skills/skills/{id}/。*/
export const updateSkill = (id, payload) => api.patch(`/skills/skills/${id}/`, payload)
/*删除技艺：参数 id 技艺 id；返回删除结果。
   后端接口：DELETE /api/skills/skills/{id}/。*/
export const deleteSkill = (id) => api.del(`/skills/skills/${id}/`)
/*审核技艺：参数 id 技艺 id，action 审核动作，reviewComment 审核备注；返回处理结果。
   后端接口：POST /api/skills/skills/{id}/review/。*/
export const reviewSkill = (id, action, reviewComment) => api.post(`/skills/skills/${id}/review/`, { action, review_comment: reviewComment })
/*提交技艺审核：参数 id 技艺 id；返回处理结果。
   后端接口：POST /api/skills/skills/{id}/submit/。*/
export const submitSkill = (id) => api.post(`/skills/skills/${id}/submit/`)
/*切换技艺上下线：参数 id 技艺 id；返回更新后的技艺。
   后端接口：POST /api/skills/skills/{id}/toggle_offline/。*/
export const toggleSkillOffline = (id) => api.post(`/skills/skills/${id}/toggle_offline/`)
/*上传技艺图片：参数 file 是图片文件；返回图片地址/信息。
   流程：用 FormData 包装文件 -> POST /api/skills/skills/upload/（字段名 file）。*/
export const uploadSkillImage = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.upload('/skills/skills/upload/', fd)
}
/*上传技艺文档：参数 file 是文档文件；返回文件地址/信息。
   流程：用 FormData 包装文件 -> POST /api/skills/skills/upload_doc/（字段名 file）。*/
export const uploadSkillDoc = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.upload('/skills/skills/upload_doc/', fd)
}

/*本文件内部使用的查询串拼接函数：参数 params 是键值对象；返回 "?a=1&b=2" 或空字符串。
   与 api/utils.js 中的 qs 类似，但这里没有过滤空值（调用方需自行保证参数有效）。*/
function qs(params) {
  const s = new URLSearchParams(params).toString()
  return s ? '?' + s : ''
}
