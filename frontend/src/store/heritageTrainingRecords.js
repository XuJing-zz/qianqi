/*培训记录状态：维护学员培训记录列表，并提供记录的增删改操作*/
import { reactive } from 'vue'
import {
  listTrainingRecords,
  createTrainingRecord,
  updateTrainingRecord,
  deleteTrainingRecord,
} from '@/api/students'
import { mapKeys, mapToSnake } from '@/api/utils'


/*培训记录列表：由 loadTrainingRecords 整体替换，后台培训页和传承端培训页共用*/
export const trainingRecords = reactive([])

/*
 * 培训记录字段映射：统一成驼峰命名，补全课程名、教师、内容、备注默认值；
 * attendance 保证是数组，assessment 保证是非数组的对象（避免页面按对象读取时出错）。
 * 参数 r：后端培训记录；返回值：前端培训记录对象。
 */
function mapRecord(r) {
  const m = mapKeys(r)
  return {
    ...m,
    courseName: m.courseName || '',
    teacher: m.teacher || '',
    content: m.content || '',
    attendance: Array.isArray(m.attendance) ? m.attendance : [],
    assessment:
      m.assessment && typeof m.assessment === 'object' && !Array.isArray(m.assessment)
        ? m.assessment
        : {},
    remark: m.remark || '',
  }
}

/*
 * 加载培训记录：调用 listTrainingRecords(params)（如按学员/课程筛选），
 * 映射后整体替换 trainingRecords；返回值：更新后的记录列表。
 */
export async function loadTrainingRecords(params = {}) {
  const data = await listTrainingRecords(params)
  trainingRecords.splice(0, trainingRecords.length, ...data.map(mapRecord))
  return trainingRecords
}

/*
 * 新增培训记录：把前端字段转成下划线命名后调用 createTrainingRecord，
 * 创建成功后插入列表开头；返回值：映射后的新记录。
 */
export async function addTrainingRecord(payload) {
  const created = await createTrainingRecord(mapToSnake(payload))
  const mapped = mapRecord(created)
  trainingRecords.unshift(mapped)
  return mapped
}

/*
 * 编辑培训记录：调用 updateTrainingRecord(id, snake)，成功后按 id 原地合并更新记录；
 * 返回值：映射后的最新记录。
 */
export async function updateTrainingRecordAction(id, payload) {
  const updated = await updateTrainingRecord(id, mapToSnake(payload))
  const idx = trainingRecords.findIndex((r) => r.id === id)
  if (idx >= 0) Object.assign(trainingRecords[idx], mapRecord(updated))
  return mapRecord(updated)
}

/*
 * 删除培训记录：调用 deleteTrainingRecord(id)，成功后从 trainingRecords 中移除；
 * 无返回值。
 */
export async function removeTrainingRecord(id) {
  await deleteTrainingRecord(id)
  const idx = trainingRecords.findIndex((r) => r.id === id)
  if (idx >= 0) trainingRecords.splice(idx, 1)
}
