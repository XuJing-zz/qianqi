/*学员报名状态：维护课程报名学员列表、学习进度与材料计划，并提供编辑、删除、完成等操作*/
import { reactive } from 'vue'
import { listStudents, createStudent, updateStudent, deleteStudent, markStudentDone } from '@/api/students'
import { mapKeys, mapToSnake } from '@/api/utils'


/*学员列表：由 loadStudents 整体替换；后台学员页、传承端学员页及材料计划派生逻辑都依赖它*/
export const heritageStudents = reactive([])

/*报名状态映射表：review 待审核、rejected 已驳回、ongoing 进行中、done 已完成*/
export const studentStatusMap = {
  review: { label: '待审核', color: '#e6a23c' },
  rejected: { label: '已驳回', color: '#f56c6c' },
  ongoing: { label: '进行中', color: '#1e6fb8' },
  done: { label: '已完成', color: '#9e9e9e' },
}

/*
 * 学员字段映射：统一成驼峰命名，把价格/进度转成数字，补全头像字、课程、报名时间等默认值；
 * 已完成章节统一转成字符串数组，材料计划保证是数组。
 * 参数 s：后端学员数据；返回值：前端学员对象。
 */
function mapStudent(s) {
  const m = mapKeys(s)
  return {
    ...m,
    price: Number(m.price ?? 0),
    avatarGlyph: m.avatarGlyph || (m.name ? m.name.charAt(0) : '学'),
    courseId: m.courseId ?? 0,
    enrollTime: m.enrollTime || '',
    progress: m.progress ?? 0,
    username: m.username || '',
    nick: m.nick || '',
    userPhone: m.userPhone || '',
    userStatus: m.userStatus || '',
    userStatusLabel: m.userStatusLabel || '',
    completed: Array.isArray(m.completed) ? m.completed.map(String) : [],
    materialPlan: Array.isArray(m.materialPlan) ? m.materialPlan : [],
  }
}

/*
 * 加载学员列表：调用 listStudents()，映射后整体替换 heritageStudents；
 * 返回值：更新后的学员列表。
 */
export async function loadStudents() {
  const data = await listStudents()
  heritageStudents.splice(0, heritageStudents.length, ...data.map(mapStudent))
  return heritageStudents
}

/*
 * 新增学员报名：把前端字段转成下划线命名后调用 createStudent，
 * 创建成功后插入列表开头；返回值：映射后的新学员。
 */
export async function addStudent(payload) {
  const created = await createStudent(mapToSnake(payload))
  const mapped = mapStudent(created)
  heritageStudents.unshift(mapped)
  return mapped
}

/*
 * 编辑学员信息：调用 updateStudent(id, snake)，成功后按 id 原地合并更新学员；
 * 返回值：映射后的最新学员。
 */
export async function updateStudentAction(id, payload) {
  const updated = await updateStudent(id, mapToSnake(payload))
  const idx = heritageStudents.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageStudents[idx], mapStudent(updated))
  return mapStudent(updated)
}

/*
 * 删除学员：调用 deleteStudent(id)，成功后从 heritageStudents 中移除；
 * 无返回值。
 */
export async function removeStudent(id) {
  await deleteStudent(id)
  const idx = heritageStudents.findIndex((s) => s.id === id)
  if (idx >= 0) heritageStudents.splice(idx, 1)
}

/*
 * 保存学员材料计划：复用 updateStudent 接口，提交 { material_plan: plan }；
 * 成功后原地更新本地学员；返回值：后端返回的最新学员（未映射）。
 */
export async function saveStudentMaterialPlan(id, plan) {
  const updated = await updateStudent(id, { material_plan: plan })
  const idx = heritageStudents.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageStudents[idx], mapStudent(updated))
  return updated
}

/*
 * 标记学员课程完成：调用 markStudentDone(id)，成功后原地更新学员状态；
 * 返回值：映射后的最新学员。
 */
export async function markStudentDoneAction(id) {
  const updated = await markStudentDone(id)
  const idx = heritageStudents.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageStudents[idx], mapStudent(updated))
  return mapStudent(updated)
}
