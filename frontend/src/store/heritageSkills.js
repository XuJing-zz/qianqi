/*技艺档案状态：维护非遗技艺列表及等级/流派选项，并提供技艺增删改、提交审核、上下架、审核操作*/
import { reactive } from 'vue'
import { listSkills, createSkill, updateSkill, deleteSkill, reviewSkill, submitSkill, toggleSkillOffline } from '@/api/skills'
import { mapKeys, mapToSnake } from '@/api/utils'


/*技艺档案列表：由 loadSkills 整体替换；前台档案页、后台审核页都读取这份缓存*/
export const heritageSkills = reactive([])

/*技艺等级选项*/
export const skillLevels = ['国家级', '省级', '市级']

/*技艺流派选项：供档案表单选择所属流派*/
export const skillSchools = [
  '京作', '扬作', '苏作', '晋作', '蜀作', '闽作', '浙作', '徽作', '楚作', '赣作',
  '秦作', '鲁作', '桂作', '广作', '滇作', '中原', '关东', '彝族漆器', '鄂西制漆',
]

/*技艺审核状态映射表：draft 草稿、pending 待审核、approved 已通过、rejected 已驳回、offline 已下架*/
export const skillStatusMap = {
  draft: { label: '草稿', color: '#6b5a44' },
  pending: { label: '待审核', color: '#b8860b' },
  approved: { label: '已通过', color: '#2e7d32' },
  rejected: { label: '已驳回', color: '#c62828' },
  offline: { label: '已下架', color: '#9e9e9e' },
}

/*
 * 技艺字段映射：统一成驼峰命名，并补全提交时间和审核意见默认值。
 * 参数 s：后端技艺数据；返回值：前端技艺对象。
 */
function mapSkill(s) {
  const m = mapKeys(s)
  return {
    ...m,
    submitTime: m.submitTime || '',
    reviewComment: m.reviewComment || '',
  }
}

/*
 * 加载技艺档案：调用 listSkills()，映射后整体替换 heritageSkills；
 * 返回值：更新后的技艺列表。
 */
export async function loadSkills() {
  const data = await listSkills()
  heritageSkills.splice(0, heritageSkills.length, ...data.map(mapSkill))
  return heritageSkills
}

/*
 * 新增技艺：把前端字段转成下划线命名后调用 createSkill，
 * 创建成功后插入列表开头；返回值：映射后的新技艺。
 */
export async function addSkill(payload) {
  const created = await createSkill(mapToSnake(payload))
  const mapped = mapSkill(created)
  heritageSkills.unshift(mapped)
  return mapped
}

/*
 * 编辑技艺：调用 updateSkill(id, snake)，成功后按 id 原地合并更新技艺；
 * 返回值：映射后的最新技艺。
 */
export async function updateSkillAction(id, payload) {
  const updated = await updateSkill(id, mapToSnake(payload))
  const idx = heritageSkills.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageSkills[idx], mapSkill(updated))
  return mapSkill(updated)
}

/*
 * 删除技艺：调用 deleteSkill(id)，成功后从 heritageSkills 中移除；
 * 无返回值。
 */
export async function removeSkill(id) {
  await deleteSkill(id)
  const idx = heritageSkills.findIndex((s) => s.id === id)
  if (idx >= 0) heritageSkills.splice(idx, 1)
}

/*
 * 提交技艺审核：调用 submitSkill(id)，成功后原地更新技艺状态；
 * 返回值：映射后的最新技艺。
 */
export async function submitSkillAction(id) {
  const updated = await submitSkill(id)
  const idx = heritageSkills.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageSkills[idx], mapSkill(updated))
  return mapSkill(updated)
}

/*
 * 切换技艺上下架：调用 toggleSkillOffline(id)，成功后原地更新技艺；
 * 返回值：映射后的最新技艺。
 */
export async function toggleOfflineSkill(id) {
  const updated = await toggleSkillOffline(id)
  const idx = heritageSkills.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageSkills[idx], mapSkill(updated))
  return mapSkill(updated)
}

/*
 * 审核技艺：调用 reviewSkill(id, action, reviewComment)，
 * action 通常是通过/驳回；成功后原地更新技艺；返回值：映射后的最新技艺。
 */
export async function reviewSkillAction(id, action, reviewComment) {
  const updated = await reviewSkill(id, action, reviewComment)
  const idx = heritageSkills.findIndex((s) => s.id === id)
  if (idx >= 0) Object.assign(heritageSkills[idx], mapSkill(updated))
  return mapSkill(updated)
}
