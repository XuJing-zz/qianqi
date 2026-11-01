/*学员（报名）与培训记录接口：学员增删改查、审核/结课，培训记录增删改查与导出*/
import { api } from './client'
import { qs } from './utils'

/*获取学员/报名列表：参数 params 可含分页、课程、审核状态、关键词等；返回数组或分页结果。
   后端接口：GET /api/students/students/。*/
export const listStudents = (params = {}) => api.get('/students/students/' + qs(params))
/*创建学员报名：参数 payload 包含学员姓名、课程、教师、价格等；返回创建后的报名记录。
   后端接口：POST /api/students/students/。*/
export const createStudent = (payload) => api.post('/students/students/', payload)
/*修改学员/报名信息：参数 id 报名记录 id，payload 是要修改的字段（如进度、已完成课节）；返回更新后的记录。
   后端接口：PATCH /api/students/students/{id}/。*/
export const updateStudent = (id, payload) => api.patch(`/students/students/${id}/`, payload)
/*删除学员/报名记录：参数 id 记录 id；返回删除结果。
   后端接口：DELETE /api/students/students/{id}/。*/
export const deleteStudent = (id) => api.del(`/students/students/${id}/`)
/*标记学员已结课：参数 id 记录 id；返回更新后的记录。
   后端接口：POST /api/students/students/{id}/mark_done/。*/
export const markStudentDone = (id) => api.post(`/students/students/${id}/mark_done/`)
/*审核通过报名：参数 id 记录 id；返回更新后的记录。
   后端接口：POST /api/students/students/{id}/approve/。*/
export const approveStudent = (id) => api.post(`/students/students/${id}/approve/`)
/*审核驳回报名：参数 id 记录 id，reviewComment 驳回原因；返回更新后的记录。
   后端接口：POST /api/students/students/{id}/reject/。*/
export const rejectStudent = (id, reviewComment) =>
  api.post(`/students/students/${id}/reject/`, { review_comment: reviewComment })

/*获取培训记录列表：参数 params 可含分页、学员、时间范围等；返回数组或分页结果。
   后端接口：GET /api/students/training-records/。*/
export const listTrainingRecords = (params = {}) => api.get('/students/training-records/' + qs(params))
/*新增培训记录：参数 payload 包含学员、日期、内容、时长等；返回创建后的记录。
   后端接口：POST /api/students/training-records/。*/
export const createTrainingRecord = (payload) => api.post('/students/training-records/', payload)
/*修改培训记录：参数 id 记录 id，payload 是要修改的字段；返回更新后的记录。
   后端接口：PATCH /api/students/training-records/{id}/。*/
export const updateTrainingRecord = (id, payload) => api.patch(`/students/training-records/${id}/`, payload)
/*删除培训记录：参数 id 记录 id；返回删除结果。
   后端接口：DELETE /api/students/training-records/{id}/。*/
export const deleteTrainingRecord = (id) => api.del(`/students/training-records/${id}/`)

/*导出培训记录：无参数；返回 Promise<Blob>（CSV 文件内容），失败时抛出“导出失败”。
   流程：从本地读取 token -> 用 fetch 请求导出接口（需要手动加 Authorization 头）-> 检查状态 -> 返回二进制 Blob。
   后端接口：GET /api/students/training-records/export/。*/
export async function exportTrainingRecords() {
  const token = localStorage.getItem('qianqi_token')
  const res = await fetch('/api/students/training-records/export/', {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error('导出失败')
  return res.blob()   // 二进制文件内容交给调用方下载
}
