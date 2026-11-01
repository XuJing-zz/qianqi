<!-- 培训记录页：展示、筛选、新建、编辑、删除培训台账，支持生成出勤表和导出 CSV -->
<template>
  <ConsoleLayout>
    <div class="ctr-wrap">
      <!-- 页面标题与操作区：导出 CSV、新建培训记录 -->
      <div class="ctr-head">
        <div class="ctr-head-left">
          <h2 class="ctr-title">培训记录</h2>
          <p class="ctr-sub">共 {{ trainingRecords.length }} 条培训台账，出勤 / 考核一表归档</p>
        </div>
        <div class="ctr-actions">
          <button class="ctr-toggle-all" @click="exportCsv">导出 CSV</button>
          <button class="ctr-btn-primary" @click="openCreate">＋ 新建培训记录</button>
        </div>
      </div>

      <!-- 状态筛选标签：当前仅“全部”，后面可扩展更多状态 -->
      <div class="ctr-tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="ctr-tab"
          :class="{ 'ctr-tab-active': activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
          <span class="ctr-tab-count">{{ countOf(t.value) }}</span>
        </button>
      </div>

      <!-- 培训记录卡片列表 -->
      <div v-if="filtered.length" class="ctr-list">
        <div v-for="r in filtered" :key="r.id" class="ctr-card">
          <div class="ctr-card-head">
            <div class="ctr-card-title-line">
              <span class="ctr-card-glyph">训</span>
              <div>
                <h3 class="ctr-card-name">{{ r.courseName || '未关联课程' }}</h3>
                <span class="ctr-card-meta">{{ formatTime(r.recordTime) }} · 授课 {{ r.teacher || '—' }}</span>
              </div>
            </div>
            <!-- 每条培训记录的编辑 / 删除操作 -->
            <div class="ctr-card-actions">
              <button class="ctr-btn" @click="openEdit(r)">编辑</button>
              <button class="ctr-btn ctr-btn-danger" @click="removeRecord(r)">删除</button>
            </div>
          </div>

          <p class="ctr-content">{{ r.content || '（暂无培训内容）' }}</p>

          <!-- 出勤明细与考核明细 -->
          <div class="ctr-sections">
            <div class="ctr-section">
              <h4 class="ctr-section-title">出勤明细</h4>
              <div v-if="r.attendance.length" class="ctr-tags">
                <span
                  v-for="(a, i) in r.attendance"
                  :key="i"
                  class="ctr-tag"
                  :class="{ 'ctr-tag-absent': a.status !== 'present' }"
                >
                  {{ a.name }}{{ a.status === 'present' ? '·出勤' : '·缺勤' }}
                </span>
              </div>
              <span v-else class="ctr-empty-txt">未登记</span>
            </div>

            <div class="ctr-section">
              <h4 class="ctr-section-title">考核明细</h4>
              <div v-if="assessmentList(r).length" class="ctr-tags">
                <span v-for="(a, i) in assessmentList(r)" :key="i" class="ctr-tag ctr-tag-score">
                  {{ a.name }}：{{ a.result }}
                </span>
              </div>
              <span v-else class="ctr-empty-txt">未登记</span>
            </div>
          </div>

          <div v-if="r.remark" class="ctr-remark">备注：{{ r.remark }}</div>
        </div>
      </div>

      <div v-else class="ctr-empty">
        <span class="ctr-empty-glyph">训</span>
        <p class="ctr-empty-text">暂无{{ activeTabLabel }}培训记录</p>
      </div>
    </div>

    <!-- 新建 / 编辑培训记录弹窗 -->
    <el-dialog
      v-model="dialog"
      :title="editingId ? '编辑培训记录' : '新建培训记录'"
      width="min(680px, calc(100vw - 32px))"
      :close-on-click-modal="false"
    >
      <div v-if="form" class="ctr-form">
        <!-- 关联课程与授课传承人 -->
        <label class="ctr-form-row">
          <span class="ctr-form-label">关联课程 *</span>
          <el-select v-model="form.courseId" placeholder="选择课程" filterable style="width: 100%" @change="onCourseChange">
            <el-option
              v-for="c in courseOptions"
              :key="c.id"
              :label="c.label"
              :value="c.id"
            />
          </el-select>
        </label>

        <label class="ctr-form-row">
          <span class="ctr-form-label">授课传承人</span>
          <el-input v-model="form.teacher" placeholder="默认取课程传承人" />
        </label>

        <label class="ctr-form-row">
          <span class="ctr-form-label">培训内容 *</span>
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="本次培训讲解 / 示范 / 实操的要点" />
        </label>

        <!-- 出勤表：可手动添加学员，或从课程报名学员批量生成 -->
        <div class="ctr-form-row">
          <span class="ctr-form-label">出勤表</span>
          <div class="ctr-rows">
            <div v-for="(row, i) in form.attendance" :key="i" class="ctr-row">
              <el-input v-model="row.name" placeholder="学员姓名" style="width: 180px" />
              <el-select v-model="row.status" style="width: 120px">
                <el-option label="出勤" value="present" />
                <el-option label="缺勤" value="absent" />
              </el-select>
              <button class="ctr-row-del" @click="form.attendance.splice(i, 1)">✕</button>
            </div>
            <div class="ctr-row-tools">
              <button class="ctr-row-add" @click="form.attendance.push({ name: '', status: 'present' })">＋ 添加学员</button>
              <el-button size="small" type="primary" plain @click="fillAttendance">从报名学员生成出勤表</el-button>
            </div>
          </div>
        </div>

        <!-- 考核表：按学员填写考核结果 -->
        <div class="ctr-form-row">
          <span class="ctr-form-label">考核表</span>
          <div class="ctr-rows">
            <div v-for="(row, i) in form.assessment" :key="i" class="ctr-row">
              <el-input v-model="row.name" placeholder="学员姓名" style="width: 180px" />
              <el-input v-model="row.result" placeholder="考核结果，如：优秀" style="width: 220px" />
              <button class="ctr-row-del" @click="form.assessment.splice(i, 1)">✕</button>
            </div>
            <button class="ctr-row-add" @click="form.assessment.push({ name: '', result: '' })">＋ 添加考核</button>
          </div>
        </div>

        <!-- 备注 -->
        <label class="ctr-form-row">
          <span class="ctr-form-label">备注</span>
          <el-input v-model="form.remark" placeholder="如：教学现场照片已归档" />
        </label>
      </div>

      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="saveRecord">保存</el-button>
      </template>
    </el-dialog>
  </ConsoleLayout>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、消息 / 确认框、工作台布局、状态层与学员接口
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import {
  trainingRecords,
  loadTrainingRecords,
  addTrainingRecord,
  updateTrainingRecordAction,
  removeTrainingRecord,
  heritageCourses,
  loadHeritageCourses,
  addLog,
  authState,
} from '@/store'
import { exportTrainingRecords, listStudents } from '@/api/students'

/* 页面挂载时并行加载培训记录与课程数据，单个失败不影响另一个 */
onMounted(() => {
  Promise.all([loadTrainingRecords().catch(() => {}), loadHeritageCourses().catch(() => {})])
})

// 筛选标签配置；目前只有“全部”，后续可按状态扩展
const tabs = [
  { label: '全部', value: 'all' },
]
const activeTab = ref('all')
// 当前标签的显示名称，用于空状态提示
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')

// 当前筛选结果（预留状态筛选，目前直接返回全部记录）
const filtered = computed(() => trainingRecords)

/* 统计某个状态标签下的记录数；all 表示全部 */
function countOf(v) {
  if (v === 'all') return trainingRecords.length
  return trainingRecords.filter((r) => r.status === v).length
}

/* 把时间字符串格式化为 YYYY-MM-DD HH:mm；无法解析时原样返回 */
function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (Number.isNaN(d.getTime())) return t
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

/* 把 {学员姓名: 考核结果} 对象转成数组，便于模板遍历显示 */
function assessmentList(r) {
  return Object.keys(r.assessment || {}).map((name) => ({ name, result: r.assessment[name] }))
}

/* 当前操作人名称，用于写操作日志 */
function operator() {
  return authState.user?.name || '传承人'
}

// 弹窗状态：是否显示、正在编辑的记录 ID（为空表示新建）、表单对象
const dialog = ref(false)
const editingId = ref(null)
const form = reactive({})

// 课程下拉选项：把课程列表映射为 id / 显示名 / 授课传承人
const courseOptions = computed(() =>
  heritageCourses.map((c) => ({ id: c.id, label: c.name || `课程 #${c.id}`, teacher: c.ownerName || '' }))
)

/* 生成一份空培训记录表单；出勤与考核各保留一行默认输入 */
function newForm() {
  return reactive({
    courseId: null,
    teacher: '',
    content: '',
    attendance: [{ name: '', status: 'present' }],
    assessment: [{ name: '', result: '' }],
    remark: '',
  })
}

/* 打开新建弹窗：清空编辑 ID，并用空表单覆盖当前表单 */
function openCreate() {
  editingId.value = null
  Object.assign(form, newForm())
  dialog.value = true
}

/* 打开编辑弹窗：把记录字段回填到表单，出勤 / 考核为空时补一行占位 */
function openEdit(r) {
  editingId.value = r.id
  Object.assign(form, {
    courseId: r.courseId ?? null,
    teacher: r.teacher || '',
    content: r.content || '',
    attendance: (r.attendance && r.attendance.length ? r.attendance : [{ name: '', status: 'present' }])
      .map((a) => ({ name: a.name || '', status: a.status || 'present' })),
    assessment: Object.keys(r.assessment || {})
      .map((name) => ({ name, result: r.assessment[name] || '' }))
      .concat(r.assessment && Object.keys(r.assessment).length ? [] : [{ name: '', result: '' }]),
    remark: r.remark || '',
  })
  dialog.value = true
}

/* 选择课程后，自动把课程负责传承人带入授课人输入框 */
function onCourseChange(id) {
  const c = courseOptions.value.find((x) => x.id === id)
  if (c && c.teacher) form.teacher = c.teacher
}

/* 从报名学员生成出勤表：按课程查询学员，去重后追加到当前出勤列表 */
async function fillAttendance() {
  if (!form.courseId) {
    ElMessage.warning('请先选择关联课程')
    return
  }
  try {
    const list = await listStudents({ course_id: form.courseId })
    if (!list || !list.length) {
      ElMessage.info('该课程暂无已报名学员')
      return
    }
    const existing = new Set(form.attendance.map((a) => (a.name || '').trim()).filter(Boolean))
    let added = 0
    list.forEach((s) => {
      const nm = (s.name || '').trim()
      if (nm && !existing.has(nm)) {
        form.attendance.push({ name: nm, status: 'present' })
        existing.add(nm)
        added++
      }
    })
    ElMessage.success(`已带入 ${list.length} 名报名学员（新增 ${added} 条），请逐条勾选出勤状态`)
  } catch (e) {
    ElMessage.error('获取报名学员失败')
  }
}

/* 保存培训记录：校验课程和内容 → 清洗出勤 / 考核数据 → 新增或更新 → 写日志并关闭弹窗 */
async function saveRecord() {
  if (!form.courseId) {
    ElMessage.warning('请选择关联课程')
    return
  }
  if (!form.content.trim()) {
    ElMessage.warning('请填写培训内容')
    return
  }
  const attendance = form.attendance
    .filter((a) => a.name && a.name.trim())
    .map((a) => ({ name: a.name.trim(), status: a.status || 'present' }))
  const assessment = {}
  form.assessment
    .filter((a) => a.name && a.name.trim())
    .forEach((a) => { assessment[a.name.trim()] = (a.result && a.result.trim()) || '合格' })

  const payload = {
    courseId: form.courseId,
    courseName: courseOptions.value.find((c) => c.id === form.courseId)?.label || '',
    teacher: form.teacher.trim() || operator(),
    content: form.content.trim(),
    attendance,
    assessment,
    remark: form.remark.trim(),
  }

  try {
    if (editingId.value) {
      await updateTrainingRecordAction(editingId.value, payload)
      addLog('update', operator(), '编辑培训记录', `「${payload.courseName}」培训记录已更新`)
      ElMessage.success('已更新')
    } else {
      await addTrainingRecord(payload)
      addLog('create', operator(), '新建培训记录', `「${payload.courseName}」培训记录已新建`)
      ElMessage.success('已保存')
    }
    dialog.value = false
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '保存失败')
  }
}

/* 删除培训记录：二次确认后调用删除接口并写操作日志 */
function removeRecord(r) {
  ElMessageBox.confirm(`确定删除「${r.courseName || '该'}」培训记录吗？`, '删除记录', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await removeTrainingRecord(r.id)
      addLog('delete', operator(), '删除培训记录', `「${r.courseName}」培训记录已删除`)
      ElMessage.success('已删除')
    })
    .catch(() => {})
}

/* 导出 CSV：请求后端返回文件内容，再创建临时下载链接并触发点击 */
async function exportCsv() {
  try {
    const blob = await exportTrainingRecords()
    // URL.createObjectURL：为 Blob 生成临时访问地址，下载完成后需 revokeObjectURL 释放
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '培训记录.csv'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('已导出 CSV')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}
</script>

<style src="./ConsoleTraining.css"></style>
