<!-- 传承人工作台 · 学员管理：按课程分组查看学员，维护课时进度、材料包、出勤记录与结课状态 -->
<template>
  <!-- 工作台统一布局 -->
  <ConsoleLayout>
    <div class="cst-wrap">
      <!-- 页头：学员总数、全部展开/收起与进行中/已完成统计 -->
      <div class="cst-head">
        <div class="cst-head-left">
          <h2 class="cst-title">学员名单</h2>
          <p class="cst-sub">共 {{ studentList.length }} 名学员，按课程分组</p>
        </div>
        <div class="cst-summary">
          <button class="cst-toggle-all" @click="expandAll">全部展开</button>
          <button class="cst-toggle-all" @click="collapseAll">全部收起</button>
          <span class="cst-summary-item">进行中 <em>{{ countOf('ongoing') }}</em></span>
          <span class="cst-summary-item">已完成 <em>{{ countOf('done') }}</em></span>
        </div>
      </div>

      <!-- 状态标签：全部 / 进行中 / 已完成，并显示各状态人数 -->
      <div class="cst-tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="cst-tab"
          :class="{ 'cst-tab-active': activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
          <span class="cst-tab-count">{{ countOf(t.value) }}</span>
        </button>
      </div>

      <!-- 学员分组列表：同一课程的学员归为一组，组头可点击展开/收起 -->
      <div v-if="grouped.length" class="cst-groups">
        <section v-for="g in grouped" :key="g.courseName" class="cst-group">
          <div class="cst-group-head" @click="toggleGroup(g.courseName)">
            <span class="cst-group-toggle" :class="{ 'cst-group-toggle-open': isGroupOpen(g.courseName) }">▸</span>
            <h3 class="cst-group-title">{{ g.courseName }}</h3>
            <span class="cst-group-count">{{ g.students.length }} 人</span>
          </div>

          <!-- 组内学员卡片列表 -->
          <div v-show="isGroupOpen(g.courseName)" class="cst-list">
            <div v-for="s in g.students" :key="s.id" class="cst-card">
              <!-- 学员头像：没有头像字时取姓名首字 -->
              <div class="cst-avatar">{{ s.avatarGlyph || s.name.charAt(0) }}</div>
              <div class="cst-body">
                <div class="cst-body-top">
                  <div class="cst-name-line">
                    <h4 class="cst-name">{{ s.name }}</h4>
                    <span class="cst-badge" :style="{ color: statusMap[s.status].color, borderColor: statusMap[s.status].color }">
                      {{ statusMap[s.status].label }}
                    </span>
                  </div>
                  <span class="cst-phone">{{ s.phone }}</span>
                </div>

                <!-- 账号与报名信息：线下代录学员可能尚未注册平台账号 -->
                <div class="cst-meta">
                  <span class="cst-meta-item">
                    账号
                    <template v-if="s.username">
                      <span class="cst-account">{{ s.username }}</span>
                      <span v-if="s.nick" class="cst-nick">（{{ s.nick }}）</span>
                      <span v-if="s.userStatus === 'disabled'" class="cst-account-off">已禁用</span>
                    </template>
                    <span v-else class="cst-account-none">未注册平台账号（线下代录）</span>
                  </span>
                  <span class="cst-meta-item">报名于 {{ s.enrollTime }}</span>
                </div>

                <!-- 学习进度条：百分比由已学课时数或后端存储的进度计算 -->
                <div class="cst-progress">
                  <span class="cst-progress-label">学习进度</span>
                  <div class="cst-progress-bar"><i class="cst-progress-fill" :style="{ width: progInfo(s).pct + '%' }"></i></div>
                  <span class="cst-progress-num">{{ progInfo(s).text }}</span>
                </div>

                <!-- 材料包摘要：显示为该学员配置的物料名称与数量 -->
                <div class="cst-material">
                  <span class="cst-material-label">材料包：</span>
                  <template v-if="planOf(s).length">
                    <span v-for="(p, i) in planOf(s)" :key="i" class="cst-plan-tag">{{ p.materialName }} ×{{ p.qty }}</span>
                  </template>
                  <span v-else class="cst-plan-empty">未配置</span>
                </div>
              </div>

              <!-- 学员操作：配置材料包、维护课时、记出勤、结课（已结课不再显示结课按钮） -->
              <div class="cst-actions">
                <button class="cst-btn" @click="openPlan(s)">配置材料包</button>
                <button class="cst-btn" :disabled="!courseOf(s)" @click="openLessons(s)">维护课时</button>
                <button class="cst-btn" @click="openAttendance(s)">记一次出勤</button>
                <button v-if="s.status !== 'done'" class="cst-btn cst-btn-primary" @click="completeStudent(s)">结课</button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 空状态：当前筛选条件下没有学员 -->
      <div v-else class="cst-empty">
        <span class="cst-empty-glyph">学</span>
        <p class="cst-empty-text">暂无{{ activeTabLabel }}学员</p>
      </div>
    </div>

    <!-- 材料包配置弹窗：按物料/工具分组勾选数量，保存后由管理员发货 -->
    <el-dialog
      v-model="planDialog"
      title="配置材料包"
      width="min(640px, calc(100vw - 32px))"
      :close-on-click-modal="false"
      class="cst-plan-dialog-wrap"
    >
      <div v-if="planTarget" class="cst-plan-dialog">
        <p class="cst-dialog-line">
          为学员 <strong>{{ planTarget.name }}</strong>（{{ planTarget.courseName }}）配置待寄材料，发货操作由管理员执行。
        </p>

        <!-- 按物料名称/规格搜索，减少长列表查找成本 -->
        <div class="cst-plan-search">
          <el-input
            v-model="materialKeyword"
            placeholder="搜索物料名称 / 规格"
            clearable
            :prefix-icon="Search"
          />
        </div>

        <!-- 已选物料种类数与总件数汇总 -->
        <div class="cst-plan-summary" v-if="selectedCount > 0">
          已选 <em>{{ selectedCount }}</em> 项，共 <em>{{ selectedTotalQty }}</em> 件
        </div>

        <!-- 物料分组（材料 / 工具）；没有匹配项的分组自动隐藏 -->
        <div v-for="g in materialGroups" :key="g.type" class="cst-plan-group" v-show="g.items.length">
          <div class="cst-plan-group-head">
            <span class="cst-plan-group-title" :style="{ color: g.color }">{{ g.label }}</span>
            <span class="cst-plan-group-count">{{ g.items.length }} 项</span>
          </div>
          <div class="cst-plan-options">
            <label v-for="m in g.items" :key="m.id" class="cst-plan-option" :class="{ 'cst-plan-option-selected': planQty[m.id] > 0 }">
              <div class="cst-plan-option-info">
                <span class="cst-plan-option-name">{{ m.name }}</span>
                <span class="cst-plan-option-spec">{{ m.spec }}</span>
              </div>
              <span class="cst-plan-option-stock" :style="{ color: m.stock <= 0 ? '#c62828' : m.stock <= m.alertThreshold ? '#b8860b' : '#8a7660' }">
                库存 {{ m.stock }}
              </span>
              <el-input-number
                v-model="planQty[m.id]"
                :min="0"
                :max="99"
                size="small"
                style="width: 110px"
              />
            </label>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="planDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmPlan">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 课时维护弹窗：勾选学员已学完的课时，保存后由后端重算学习进度 -->
    <el-dialog
      v-model="lessonDialog"
      :title="lessonDialogTitle"
      width="min(560px, calc(100vw - 32px))"
      :close-on-click-modal="false"
    >
      <p class="cst-dialog-line">勾选该学员已学完的课时，保存后学习进度会按课程全部课时自动重算。</p>
      <div v-if="lessonRows.length" class="cst-lesson-list">
        <label
          v-for="r in lessonRows"
          :key="r.key"
          class="cst-lesson-row"
          :class="{ 'cst-lesson-row-on': lessonChecks[r.key] }"
        >
          <el-checkbox v-model="lessonChecks[r.key]">{{ r.title }}</el-checkbox>
        </label>
      </div>
      <p v-else class="cst-lesson-empty">该课程暂无课时，请先在「课时内容」里编排</p>
      <template #footer>
        <el-button @click="lessonDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmLessons">保存进度</el-button>
      </template>
    </el-dialog>

    <!-- 出勤记录弹窗：填写培训内容，并为该课程学员逐人标记出勤/缺勤 -->
    <el-dialog
      v-model="attDialog"
      :title="attDialogTitle"
      width="min(620px, calc(100vw - 32px))"
      :close-on-click-modal="false"
    >
      <p class="cst-dialog-line">记录本次授课出勤：已带入该课程报名学员，请勾选实际出勤情况。</p>
      <el-form label-width="80px" class="cst-att-form">
        <el-form-item label="培训内容">
          <el-input v-model="attForm.content" placeholder="如：第 3 次课 螺钿镶嵌实操" />
        </el-form-item>
      </el-form>
      <div class="cst-att-list" v-if="attForm.attendance.length">
        <div v-for="(row, i) in attForm.attendance" :key="i" class="cst-att-row">
          <span class="cst-att-name">{{ row.name }}</span>
          <el-select v-model="row.status" size="small" style="width: 120px">
            <el-option label="出勤" value="present" />
            <el-option label="缺勤" value="absent" />
          </el-select>
        </div>
      </div>
      <p v-else class="cst-lesson-empty">正在获取该课程报名学员…</p>
      <template #footer>
        <el-button @click="attDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAttendance">保存出勤</el-button>
      </template>
    </el-dialog>
  </ConsoleLayout>
</template>

<script setup>
/* 页面逻辑：学员分组展示与筛选、课时进度维护、材料包配置、出勤登记和结课操作 */
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import ConsoleLayout from './ConsoleLayout.vue'
import {
  heritageStudents,
  studentStatusMap,
  loadStudents,
  loadHeritageCourses,
  heritageCourses,
  updateStudentAction,
  markStudentDoneAction,
  loadTrainingRecords,
  addTrainingRecord,
  addLog,
  authState,
  inventoryMaterials,
  materialTypeMap,
  getStudentMaterialPlan,
  setStudentMaterialPlan,
  saveStudentMaterialPlan,
  loadMaterials,
} from '@/store'
import { listStudents } from '@/api/students'

// 进入页面时并行加载学员、课程（用于课时列表）和库存物料（用于材料包配置）
onMounted(() => {
  Promise.allSettled([loadStudents(), loadHeritageCourses(), loadMaterials()])
})

// 直接引用 store 中的响应式数组，加载完成后自动刷新
const studentList = heritageStudents
// 学员状态 → 文案/颜色映射（进行中 / 已完成）
const statusMap = studentStatusMap

/* 状态筛选标签配置 */
const tabs = [
  { label: '全部', value: 'all' },
  { label: '进行中', value: 'ongoing' },
  { label: '已完成', value: 'done' },
]
// 当前选中的状态标签
const activeTab = ref('all')

const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')

// 按状态过滤学员；「全部」直接返回原数组
const filtered = computed(() => {
  if (activeTab.value === 'all') return studentList
  return studentList.filter((s) => s.status === activeTab.value)
})

/* 统计某个状态的学员人数，用于标签和页头汇总 */
function countOf(v) {
  if (v === 'all') return studentList.length
  return studentList.filter((s) => s.status === v).length
}

/* 把筛选后的学员按课程名分组，输出 [{ courseName, students }]；没有课程名的归入「未分配课程」 */
const grouped = computed(() => {
  const map = {}
  for (const s of filtered.value) {
    const key = s.courseName || '未分配课程'
    if (!map[key]) map[key] = []
    map[key].push(s)
  }
  return Object.keys(map).map((courseName) => ({ courseName, students: map[courseName] }))
})

// 记录每个课程分组是否展开：key 为课程名，value 为布尔值
const openGroups = reactive({})
// 是否执行过「全部展开」，仅用于界面状态标识
const expandedAll = ref(false)

/* 判断某个课程分组当前是否展开 */
function isGroupOpen(name) {
  return !!openGroups[name]
}

/* 点击组头时切换该分组的展开状态 */
function toggleGroup(name) {
  openGroups[name] = !openGroups[name]
}

/* 展开当前筛选结果中的所有课程分组 */
function expandAll() {
  expandedAll.value = true
  for (const g of grouped.value) openGroups[g.courseName] = true
}

/* 收起当前筛选结果中的所有课程分组 */
function collapseAll() {
  expandedAll.value = false
  for (const g of grouped.value) openGroups[g.courseName] = false
}

/* 取学员已配置的材料包明细 */
function planOf(s) {
  return getStudentMaterialPlan(s)
}

/* 当前操作人名称，写入日志 */
function operator() {
  return authState.user?.name || '传承人'
}

/* 根据学员的 courseId 找到对应课程；找不到返回 null */
function courseOf(s) {
  if (!s) return null
  return heritageCourses.find((c) => Number(c.id) === Number(s.courseId)) || null
}

/* 计算学习进度：优先进度按已学课时数/总课时数，其次使用后端存储的百分比 */
function progInfo(s) {
  const total = (courseOf(s)?.lessons || []).length
  const done = (Array.isArray(s.completed) ? s.completed : []).filter(Boolean).length
  const stored = Math.max(0, Math.min(100, Math.round(Number(s.progress) || 0)))
  if (total > 0 && done > 0) {
    const pct = Math.round((done / total) * 100)
    return { pct, text: `${done}/${total} 课时 · ${pct}%` }
  }
  if (total > 0 && stored > 0) return { pct: stored, text: `进度 ${stored}%` }
  if (total > 0) return { pct: 0, text: `0/${total} 课时` }
  return { pct: stored, text: `进度 ${stored}%` }
}

// 课时维护弹窗状态：maintTarget 为正在维护的学员，lessonChecks 记录每个课时的勾选情况
const lessonDialog = ref(false)
const maintTarget = ref(null)
const lessonChecks = reactive({})

/* 弹窗标题：带上学员姓名和课程名 */
const lessonDialogTitle = computed(() => {
  const s = maintTarget.value
  if (!s) return '维护课时'
  const c = courseOf(s)
  return `维护课时 · ${s.name}` + (c ? `（${c.name}）` : '')
})

/* 课时行数据：key 优先用课时序号，避免不同课程间冲突；没有标题时用「课时 N」兜底 */
const lessonRows = computed(() => {
  const c = courseOf(maintTarget.value)
  if (!c) return []
  return (c.lessons || []).map((l, i) => ({
    key: String((l.num != null && l.num !== '') ? l.num : (i + 1)),
    title: l.title || '课时' + (i + 1),
  }))
})

/* 打开课时维护弹窗：清空上次勾选，再按学员 completed 列表回填 */
function openLessons(s) {
  const c = courseOf(s)
  if (!c || !Array.isArray(c.lessons) || !c.lessons.length) {
    ElMessage.info('该课程暂无可维护的课时，请先在课程「课时内容」里编排')
    return
  }
  maintTarget.value = s
  for (const k of Object.keys(lessonChecks)) delete lessonChecks[k]
  const doneSet = new Set((Array.isArray(s.completed) ? s.completed : []).map(String))
  lessonRows.value.forEach((r) => { lessonChecks[r.key] = doneSet.has(r.key) })
  lessonDialog.value = true
}

/* 保存课时进度：收集勾选的课时 key，提交后由后端重算进度 */
async function confirmLessons() {
  const s = maintTarget.value
  if (!s) return
  const nums = lessonRows.value.filter((r) => lessonChecks[r.key]).map((r) => r.key)
  try {
    await updateStudentAction(s.id, { completed: nums })
    addLog('update', operator(), '维护学员课时', `「${s.name}」已学 ${nums.length} 个课时`)
    ElMessage.success('课时进度已保存')
    lessonDialog.value = false
    maintTarget.value = null
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '保存失败，请重试')
  }
}

// 出勤弹窗状态：attTarget 为触发操作的学员，attendance 为该课程所有报名学员的出勤标记
const attDialog = ref(false)
const attTarget = ref(null)
const attForm = reactive({ content: '', attendance: [] })

const attDialogTitle = computed(() => (attTarget.value ? `记一次出勤 · ${attTarget.value.name}` : '记一次出勤'))

/* 打开出勤弹窗：先清空表单，再拉取该课程的全部报名学员，默认全部标记为出勤 */
async function openAttendance(s) {
  attTarget.value = s
  attForm.content = ''
  attForm.attendance = []
  attDialog.value = true
  try {
    const list = await listStudents({ course_id: s.courseId })
    attForm.attendance = (list || [])
      .filter((x) => x && x.name)
      .map((x) => ({ name: x.name, status: 'present' }))
  } catch (e) {
    ElMessage.error('获取该课程报名学员失败')
  }
}

/* 保存出勤：培训内容必填，出勤名单统一写入培训台账 */
async function confirmAttendance() {
  const s = attTarget.value
  if (!s) return
  const content = attForm.content.trim()
  if (!content) {
    ElMessage.warning('请填写本次培训内容')
    return
  }
  const c = courseOf(s)
  const payload = {
    courseId: s.courseId,
    courseName: (c && c.name) || s.courseName || '',
    teacher: operator(),
    content,
    attendance: attForm.attendance
      .filter((r) => r.name && r.name.trim())
      .map((r) => ({ name: r.name.trim(), status: r.status === 'present' ? 'present' : 'absent' })),
    assessment: {},
    remark: '',
  }
  try {
    await addTrainingRecord(payload)
    addLog('create', operator(), '记录出勤', `「${payload.courseName}」${content}`)
    loadTrainingRecords().catch(() => {})
    ElMessage.success('出勤已记录，可在培训台账查看')
    attDialog.value = false
    attTarget.value = null
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '保存失败')
  }
}

/* 学员结课：二次确认后调用结课接口，后端会补全全部课时并结束本期学习 */
function completeStudent(s) {
  ElMessageBox.confirm(`确认给学员「${s.name}」结课？将补全全部课时并结束本期学习。`, '学员结课', {
    confirmButtonText: '确认结课',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      try {
        await markStudentDoneAction(s.id)
        addLog('update', operator(), '学员结课', `「${s.name}」${s.courseName ? '(' + s.courseName + ')' : ''}`)
        ElMessage.success('已结课')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '结课失败')
      }
    })
    .catch(() => {})
}

// 材料包弹窗状态：planQty 以物料 id 为 key 记录选择数量，materialKeyword 为搜索词
const planDialog = ref(false)
// 当前正在配置材料包的学员
let planTarget = null
const planQty = reactive({})
const materialKeyword = ref('')

/* 物料分组：按「材料 / 工具」两类组织，并按搜索词过滤名称或规格 */
const materialGroups = computed(() => {
  const kw = materialKeyword.value.trim().toLowerCase()
  const order = ['material', 'tool']
  return order.map((type) => ({
    type,
    label: materialTypeMap[type]?.label || type,
    color: materialTypeMap[type]?.color || '#8b2e1c',
    items: inventoryMaterials.filter((m) => {
      if (m.type !== type) return false
      if (!kw) return true
      return m.name.toLowerCase().includes(kw) || (m.spec || '').toLowerCase().includes(kw)
    }),
  }))
})

// 已选物料种类数（数量大于 0 的条目）
const selectedCount = computed(() => Object.keys(planQty).filter((k) => planQty[k] > 0).length)
// 已选物料总件数
const selectedTotalQty = computed(() =>
  Object.keys(planQty).reduce((sum, k) => sum + (planQty[k] > 0 ? planQty[k] : 0), 0)
)

/* 打开材料包弹窗：先把所有物料数量清零，再回填该学员已保存的配置 */
function openPlan(s) {
  planTarget = s
  materialKeyword.value = ''
  for (const k of Object.keys(planQty)) delete planQty[k]
  for (const m of inventoryMaterials) planQty[m.id] = 0
  const plan = getStudentMaterialPlan(s)
  for (const p of plan) if (p.materialId != null) planQty[p.materialId] = p.qty
  planDialog.value = true
}

/* 保存材料包：先乐观更新本地缓存，接口失败时回滚到保存前的配置 */
async function confirmPlan() {
  if (!planTarget) return
  const plan = Object.keys(planQty)
    .map((mid) => ({ materialId: Number(mid), qty: planQty[mid] }))
    .filter((p) => p.qty > 0)
  // 备份当前配置，接口失败时用于回滚
  const prevPlan = (getStudentMaterialPlan(planTarget) || []).slice()
  const fullPlan = plan.map((p) => {
    const m = inventoryMaterials.find((x) => x.id === p.materialId)
    return { materialId: p.materialId, materialName: m ? m.name : '', qty: p.qty }
  })
  setStudentMaterialPlan(planTarget, fullPlan)
  try {
    await saveStudentMaterialPlan(planTarget.id, fullPlan)
    ElMessage.success(fullPlan.length ? '材料包已配置，等待管理员发货' : '已清空材料配置')
    planDialog.value = false
    planTarget = null
  } catch (e) {
    setStudentMaterialPlan(planTarget, prevPlan)
    ElMessage.error((e && e.message) || '保存失败，请重试')
  }
}
</script>

<style src="./ConsoleStudents.css"></style>
