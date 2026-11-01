/*传承端课程管理状态：维护传承人后台的课程列表，并提供新增、编辑、提交审核、下架、审核课程/视频等操作*/
import { reactive } from 'vue'
import { listCourses, createCourse, updateCourse, reviewCourse, submitCourse, offlineCourse, reviewVideo } from '@/api/courses'
import { mapKeys, mapToSnake } from '@/api/utils'


/*传承端课程列表：包含各种审核状态（草稿/待审核/已通过/已驳回/已下架），由 loadCourses 填充*/
export const heritageCourses = reactive([])

/*章节视频审核状态映射表：用于后台视频列表展示状态标签*/
export const videoStatusMap = {
  draft: { label: '未上传', color: '#9e9e9e' },
  pending: { label: '待审核', color: '#b8860b' },
  approved: { label: '已通过', color: '#2e7d32' },
  rejected: { label: '已驳回', color: '#c62828' },
}

/*课程审核状态映射表：draft 草稿、pending 待审核、approved 已通过、rejected 已驳回、offline 已下架*/
export const courseStatusMap = {
  draft: { label: '草稿', color: '#6b5a44' },
  pending: { label: '待审核', color: '#b8860b' },
  approved: { label: '已通过', color: '#2e7d32' },
  rejected: { label: '已驳回', color: '#c62828' },
  offline: { label: '已下架', color: '#9e9e9e' },
}

/*
 * 把后端课程数据映射成传承端使用的结构：
 * 先统一字段命名，再补价格、提交时间、审核意见、报名人数等默认值，
 * 最后逐章节补全视频与排课字段，并生成章节序号。
 * 参数 c：后端单条课程；返回值：映射后的课程对象。
 */
function mapCourse(c) {
  const m = mapKeys(c)
  return {
    ...m,
    priceNum: m.priceNum ?? 0,
    submitTime: m.submitTime || '',
    reviewComment: m.reviewComment || '',
    endDate: m.endDate || '',
    location: m.location || '',
    enrolled: m.enrolled ?? 0,
    lessons: (m.lessons || []).map((l, i) => ({
      ...l,
      title: l.title || '',
      desc: l.desc || '',
      address: l.address || '',
      video: l.video || '',
      videoName: l.videoName || '',
      videoStatus: l.videoStatus || 'draft',
      videoReviewComment: l.videoReviewComment || '',
      scheduleDate: l.scheduleDate || '',
      scheduleTime: l.scheduleTime || '',
      num: l.num || String(i + 1),
    })),
  }
}

/*
 * 加载传承端全部课程：调用 listCourses()（不带状态过滤），用结果整体替换 heritageCourses。
 * 返回值：更新后的 heritageCourses。
 */
export async function loadCourses() {
  const data = await listCourses()
  heritageCourses.splice(0, heritageCourses.length, ...data.map(mapCourse))
  return heritageCourses
}

/*
 * 新增课程：先用 mapToSnake 把前端驼峰字段转成后端下划线字段，再调用 createCourse；
 * 创建成功后插入列表开头并返回映射后的课程。
 */
export async function addCourse(payload) {
  const snake = mapToSnake(payload)
  const created = await createCourse(snake)
  const mapped = mapCourse(created)
  heritageCourses.unshift(mapped)
  return mapped
}

/*
 * 编辑课程：把 payload 转成下划线字段后调用 updateCourse(id, snake)；
 * 成功后按 id 找到本地课程并原地合并更新；返回值：映射后的最新课程。
 */
export async function updateCourseAction(id, payload) {
  const snake = mapToSnake(payload)
  const updated = await updateCourse(id, snake)
  const idx = heritageCourses.findIndex((c) => c.id === id)
  if (idx >= 0) Object.assign(heritageCourses[idx], mapCourse(updated))
  return mapCourse(updated)
}

/*
 * 提交课程审核：调用 submitCourse(id)，把课程状态推进到待审核；
 * 成功后原地更新本地课程；返回值：映射后的最新课程。
 */
export async function submitCourseAction(id) {
  const updated = await submitCourse(id)
  const idx = heritageCourses.findIndex((c) => c.id === id)
  if (idx >= 0) Object.assign(heritageCourses[idx], mapCourse(updated))
  return mapCourse(updated)
}

/*
 * 下架课程：调用 offlineCourse(id)，成功后原地更新本地课程状态；
 * 返回值：映射后的最新课程。
 */
export async function offlineCourseAction(id) {
  const updated = await offlineCourse(id)
  const idx = heritageCourses.findIndex((c) => c.id === id)
  if (idx >= 0) Object.assign(heritageCourses[idx], mapCourse(updated))
  return mapCourse(updated)
}

/*
 * 审核课程：调用 reviewCourse(id, action, reviewComment)，
 * action 通常是通过/驳回，reviewComment 是审核意见；成功后原地更新本地课程；
 * 返回值：映射后的最新课程。
 */
export async function reviewCourseAction(id, action, reviewComment) {
  const updated = await reviewCourse(id, action, reviewComment)
  const idx = heritageCourses.findIndex((c) => c.id === id)
  if (idx >= 0) Object.assign(heritageCourses[idx], mapCourse(updated))
  return mapCourse(updated)
}

/*
 * 审核章节视频：调用 reviewVideo(courseId, lessonIndex, action, reviewComment)，
 * 其中 lessonIndex 是章节下标；后端返回整门课程，成功后按 courseId 原地更新本地课程；
 * 返回值：映射后的最新课程。
 */
export async function reviewVideoAction(courseId, lessonIndex, action, reviewComment) {
  const updated = await reviewVideo(courseId, lessonIndex, action, reviewComment)
  const idx = heritageCourses.findIndex((c) => c.id === courseId)
  if (idx >= 0) Object.assign(heritageCourses[idx], mapCourse(updated))
  return mapCourse(updated)
}

/*
 * 根据课程时长文案估算章节数量：
 * - 含“半日”算 2 节；
 * - “N 天”按每天 4 节计算；
 * - “N 课时”直接取 N；
 * 无法识别时返回 0。参数 duration 是时长文案字符串。
 */
export function durationToLessonCount(duration) {
  const d = (duration || '').trim()
  if (!d) return 0
  if (d.includes('半日')) return 2
  const dayMatch = d.match(/([0-9]+)\s*天/)
  if (dayMatch) return Number(dayMatch[1]) * 4
  const cntMatch = d.match(/([0-9]+)\s*课时/)
  if (cntMatch) return Number(cntMatch[1])
  return 0
}
