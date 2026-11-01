/*课程接口：课程列表/详情/新增/修改，审核、提交、下线，视频审核与视频/封面上传*/
import { api } from './client'
import { qs } from './utils'

/*获取课程列表：参数 params 可含分页、分类、关键词、状态等筛选条件；返回课程数组或分页结果。
   后端接口：GET /api/courses/courses/。*/
export function listCourses(params = {}) {
  return api.get('/courses/courses/' + qs(params))
}
/*新增课程：参数 payload 是课程表单数据（名称、简介、价格、封面、课节等）；返回创建后的课程。
   后端接口：POST /api/courses/courses/。*/
export function createCourse(payload) {
  return api.post('/courses/courses/', payload)
}
/*修改课程：参数 id 是课程 id，payload 是要修改的字段；返回更新后的课程。
   后端接口：PATCH /api/courses/courses/{id}/。*/
export function updateCourse(id, payload) {
  return api.patch(`/courses/courses/${id}/`, payload)
}
/*获取课程详情：参数 id 是课程 id；返回课程对象（含课节、教师、价格等）。
   后端接口：GET /api/courses/courses/{id}/。*/
export function getCourse(id) {
  return api.get(`/courses/courses/${id}/`)
}
/*审核课程：参数 id 课程 id，action 审核动作（如 approve/reject），reviewComment 审核备注；
   返回处理结果。后端接口：POST /api/courses/courses/{id}/review/。*/
export function reviewCourse(id, action, reviewComment) {
  return api.post(`/courses/courses/${id}/review/`, { action, review_comment: reviewComment })
}
/*提交课程审核：参数 id 课程 id；把课程从草稿/驳回状态提交给管理员审核。
   后端接口：POST /api/courses/courses/{id}/submit/。*/
export function submitCourse(id) {
  return api.post(`/courses/courses/${id}/submit/`)
}
/*下线课程：参数 id 课程 id；让课程不再对用户展示。
   后端接口：POST /api/courses/courses/{id}/offline/。*/
export function offlineCourse(id) {
  return api.post(`/courses/courses/${id}/offline/`)
}
/*获取待审核的视频列表（管理员）：参数 params 可含分页/课程等筛选；返回视频审核记录。
   后端接口：GET /api/courses/courses/video_reviews/。*/
export function listVideoReviews(params = {}) {
  return api.get('/courses/courses/video_reviews/' + qs(params))
}
/*审核课节视频：参数 courseId 课程 id，lessonIndex 课节序号，action 审核动作，reviewComment 备注；
   返回处理结果。后端接口：POST /api/courses/courses/{courseId}/review_video/。*/
export function reviewVideo(courseId, lessonIndex, action, reviewComment) {
  return api.post(`/courses/courses/${courseId}/review_video/`, {
    lesson_index: lessonIndex,
    action,
    review_comment: reviewComment,
  })
}
/*上传课程视频：参数 file 是用户选择的文件对象；返回后端保存后的文件地址/信息。
   流程：用 FormData 包装文件 -> 调用上传接口 POST /api/courses/courses/upload/。*/
export function uploadCourseVideo(file) {
  const fd = new FormData()
  fd.append('file', file)   // 后端约定文件字段名为 file
  return api.upload('/courses/courses/upload/', fd)
}
/*上传课程封面图：参数 file 是图片文件；返回图片地址/信息。
   后端接口：POST /api/courses/courses/cover/（multipart 表单，字段名 file）。*/
export function uploadCourseCover(file) {
  const fd = new FormData()
  fd.append('file', file)
  return api.upload('/courses/courses/cover/', fd)
}
