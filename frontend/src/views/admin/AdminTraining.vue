<!-- 培训记录页：按课程归档培训台账，支持搜索筛选、分页、新建/编辑/删除与 CSV 导出 -->
<template>
  <AdminLayout>
    <div class="atr-wrap">
      <!-- 页头区：标题、记录总数与「导出 CSV」「新建记录」操作 -->
      <div class="atr-head">
        <div class="atr-head-left">
          <h2 class="atr-title">培训记录</h2>
          <p class="atr-sub">共 {{ total }} 条培训台账，统一归档可导出</p>
        </div>
        <div class="atr-actions">
          <button class="atr-btn" @click="exportCsv">导出 CSV</button>
          <button class="atr-btn atr-btn-primary" @click="openCreate">＋ 新建记录</button>
        </div>
      </div>

      <!-- 筛选区：关键字搜索与按课程筛选，变化后自动重新请求 -->
      <div class="atr-filter">
        <el-input v-model="keyword" placeholder="搜索课程名 / 传承人 / 内容" clearable style="width: 240px" />
        <el-select v-model="courseFilter" placeholder="按课程筛选" clearable filterable style="width: 220px">
          <el-option v-for="c in courseOptions" :key="c.id" :label="c.label" :value="c.id" />
        </el-select>
      </div>

      <!-- 表格区：展示课程、授课传承人、培训内容、出勤、考核与培训时间 -->
      <div v-if="loading" class="atr-loading">加载中…</div>
      <div v-else-if="rows.length" class="atr-table">
        <div class="atr-row atr-row-head">
          <span class="atr-col atr-col-course">课程</span>
          <span class="atr-col">授课传承人</span>
          <span class="atr-col">培训内容</span>
          <span class="atr-col">出勤</span>
          <span class="atr-col">考核</span>
          <span class="atr-col atr-col-time">培训时间</span>
          <span class="atr-col atr-col-act">操作</span>
        </div>
        <div v-for="r in rows" :key="r.id" class="atr-row">
          <span class="atr-col atr-col-course">{{ r.courseName || '—' }}</span>
          <span class="atr-col">{{ r.teacher || '—' }}</span>
          <span class="atr-col atr-col-content" :title="r.content">{{ r.content || '—' }}</span>
          <span class="atr-col">
            <span class="atr-badge atr-badge-green">{{ presentCount(r) }} 人出勤</span>
            <span v-if="absentCount(r)" class="atr-badge atr-badge-red">{{ absentCount(r) }} 人缺勤</span>
          </span>
          <span class="atr-col atr-col-content">{{ assessmentSummary(r) }}</span>
          <span class="atr-col atr-col-time">{{ formatTime(r.recordTime) }}</span>
          <span class="atr-col atr-col-act">
            <button class="atr-btn atr-btn-sm" @click="openEdit(r)">编辑</button>
            <button class="atr-btn atr-btn-sm atr-btn-danger" @click="removeRecord(r)">删除</button>
          </span>
        </div>
      </div>

      <!-- 空状态：没有符合筛选条件的培训记录时显示 -->
      <div v-else class="atr-empty">
        <span class="atr-empty-glyph">训</span>
        <p class="atr-empty-text">暂无培训记录</p>
      </div>

      <!-- 分页区：总条数超过每页数量时显示分页器 -->
      <div v-if="total > pageSize" class="atr-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>

    <!-- 弹窗区：新建/编辑培训记录，包含关联课程、出勤表、考核表与备注 -->
    <el-dialog
      v-model="dialog"
      :title="editingId ? '编辑培训记录' : '新建培训记录'"
      width="680px"
      :close-on-click-modal="false"
    >
      <div v-if="form" class="atr-form">
        <label class="atr-form-row">
          <span class="atr-form-label">关联课程 *</span>
          <el-select v-model="form.courseId" placeholder="选择课程" filterable style="width: 100%" @change="onCourseChange">
            <el-option v-for="c in courseOptions" :key="c.id" :label="c.label" :value="c.id" />
          </el-select>
        </label>

        <label class="atr-form-row">
          <span class="atr-form-label">授课传承人</span>
          <el-input v-model="form.teacher" placeholder="默认取课程传承人" />
        </label>

        <label class="atr-form-row">
          <span class="atr-form-label">培训内容 *</span>
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="本次培训讲解 / 示范 / 实操的要点" />
        </label>

        <div class="atr-form-row">
          <span class="atr-form-label">出勤表</span>
          <div class="atr-rows">
            <div v-for="(row, i) in form.attendance" :key="i" class="atr-row-item">
              <el-input v-model="row.name" placeholder="学员姓名" style="width: 180px" />
              <el-select v-model="row.status" style="width: 120px">
                <el-option label="出勤" value="present" />
                <el-option label="缺勤" value="absent" />
              </el-select>
              <button class="atr-row-del" @click="form.attendance.splice(i, 1)">✕</button>
            </div>
            <div class="atr-row-tools">
              <button class="atr-row-add" @click="form.attendance.push({ name: '', status: 'present' })">＋ 添加学员</button>
              <el-button size="small" type="primary" plain @click="fillAttendance">从报名学员生成出勤表</el-button>
            </div>
          </div>
        </div>

        <div class="atr-form-row">
          <span class="atr-form-label">考核表</span>
          <div class="atr-rows">
            <div v-for="(row, i) in form.assessment" :key="i" class="atr-row-item">
              <el-input v-model="row.name" placeholder="学员姓名" style="width: 180px" />
              <el-input v-model="row.result" placeholder="考核结果，如：优秀" style="width: 220px" />
              <button class="atr-row-del" @click="form.assessment.splice(i, 1)">✕</button>
            </div>
            <button class="atr-row-add" @click="form.assessment.push({ name: '', result: '' })">＋ 添加考核</button>
          </div>
        </div>

        <label class="atr-form-row">
          <span class="atr-form-label">备注</span>
          <el-input v-model="form.remark" placeholder="如：教学现场照片已归档" />
        </label>
      </div>

      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="saveRecord">保存</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import {
  addTrainingRecord,
  updateTrainingRecordAction,
  removeTrainingRecord,
  heritageCourses,
  loadHeritageCourses,
  addLog,
  authState,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'
import { exportTrainingRecords, listStudents, listTrainingRecords } from '@/api/students'
import { mapKeys } from '@/api/utils'

// 页面挂载时并行加载第一页培训记录和课程下拉选项；课程接口失败不阻断记录展示
onMounted(() => {
  Promise.all([loadRows(), loadHeritageCourses().catch(() => {})])
})

// 筛选条件：关键字（匹配课程名/传承人/内容）与课程 ID
const keyword = ref('')
const courseFilter = ref('')

// 课程下拉选项：把 store 里的课程列表映射成 { id, label, teacher }
const courseOptions = computed(() =>
  heritageCourses.map((c) => ({ id: c.id, label: c.name || `课程 #${c.id}`, teacher: c.ownerName || '' }))
)


/* 把后端返回的一条记录整理成页面统一使用的结构：
   统一字段名，缺失的文本给空串，出勤表兜底为数组、考核表兜底为对象。 */
function mapRecordRow(r) {
  const m = mapKeys(r)
  return { ...m, courseName: m.courseName || '', teacher: m.teacher || '', content: m.content || '', attendance: Array.isArray(m.attendance) ? m.attendance : [], assessment: m.assessment && typeof m.assessment === 'object' && !Array.isArray(m.assessment) ? m.assessment : {}, remark: m.remark || '' }
}

/* 分页加载培训记录：
   fetchPage 每次按当前页码、每页条数、关键字与课程筛选组装请求参数，
   返回给 usePagedList 统一维护 rows/total/page/loading 等状态。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapRecordRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: keyword.value.trim() }
    if (courseFilter.value) params.course_id = courseFilter.value
    return listTrainingRecords(params)
  },
})

// 课程筛选变化后立即回到第一页并重新加载
watch(courseFilter, onFilter)
// 关键字输入做 300ms 防抖，避免每输入一个字就发一次请求
let kwTimer = null
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300)
})

// 统计一条记录中状态为“出勤”的人数
function presentCount(r) {
  return (r.attendance || []).filter((a) => a.status === 'present').length
}
// 统计一条记录中非“出勤”的人数（即缺勤）
function absentCount(r) {
  return (r.attendance || []).filter((a) => a.status !== 'present').length
}
// 把考核对象拼成「姓名：结果；姓名：结果」的摘要文本，空对象显示占位符
function assessmentSummary(r) {
  return Object.keys(r.assessment || {}).map((k) => `${k}：${r.assessment[k]}`).join('；') || '—'
}

/* 格式化培训时间：合法时间转为 YYYY-MM-DD HH:mm；
   空值返回空串，无法解析时原样返回，避免显示 Invalid Date。 */
function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (Number.isNaN(d.getTime())) return t
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

// 当前操作人：取登录管理员姓名，未登录时显示“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 弹窗状态：是否显示、正在编辑的记录 ID（null 表示新建）以及表单数据
const dialog = ref(false)
const editingId = ref(null)
const form = reactive({})

// 生成一份空白的培训记录表单，供新建时复用
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

/* 打开新建弹窗：清空编辑 ID，把空白表单覆盖到 form 上。 */
function openCreate() {
  editingId.value = null
  Object.assign(form, newForm())
  dialog.value = true
}

/* 打开编辑弹窗：记录当前行 ID，并把后端行数据转换成表单结构。
   出勤、考核为空时各补一行空白输入，保证弹窗里始终可编辑。 */
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

// 切换关联课程时，若该课程配置了授课传承人，则自动带入表单
function onCourseChange(id) {
  const c = courseOptions.value.find((x) => x.id === id)
  if (c && c.teacher) form.teacher = c.teacher
}

/* 从报名学员生成出勤表：
   先校验已选课程，再按课程 ID 拉取学员；
   用 Set 记录已有姓名去重，只追加尚未出现在出勤表中的学员。 */
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

/* 保存培训记录：
   先校验关联课程与培训内容，再把出勤/考核数组清洗成后端需要的格式；
   编辑时调用更新接口，新建时调用新增接口，成功后关闭弹窗并刷新列表。 */
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
    await loadRows()
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '保存失败')
  }
}

/* 删除培训记录：先弹确认框，确认后调用删除接口、写操作日志并刷新列表。 */
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
      await loadRows()
    })
    .catch(() => {})
}

/* 导出 CSV：后端返回文件流后，在浏览器里临时生成下载链接并触发下载，
   下载结束释放 URL，避免占用内存。 */
async function exportCsv() {
  try {
    const blob = await exportTrainingRecords()
    // 把文件流包装成浏览器可访问的临时 URL
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

<style src="./AdminTraining.css"></style>

<style scoped>
/* 加载提示：居中显示并留出上下间距 */
.atr-loading { padding: 40px 0; text-align: center; color: #8a93a3; }
/* 分页条：右对齐，与表格拉开距离 */
.atr-pager { display: flex; justify-content: flex-end; margin-top: 18px; }
</style>
