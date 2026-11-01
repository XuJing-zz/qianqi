<!-- 管理员学员管理页面：按报名状态分页查看学员，支持搜索、录取/驳回报名与标记结课。 -->
<template>
  <AdminLayout>
    <div class="ast-wrap">
      <div class="ast-head">
        <div class="ast-head-left">
          <h2 class="ast-title">学员管理</h2>
          <p class="ast-sub">共 {{ allCount }} 名学员，可筛选与结课</p>
        </div>
      </div>

      <!-- 筛选区：关键字搜索与报名状态选项卡 -->
      <div class="ast-filter">
        <el-input v-model="keyword" placeholder="搜索姓名 / 账号 / 电话 / 课程" clearable style="width: 260px" />
        <div class="ast-status-tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="ast-tab"
            :class="{ 'ast-tab-active': activeTab === t.value }"
            @click="switchTab(t.value)"
          >
            {{ t.label }}<span class="ast-tab-count">{{ tabCounts[t.value] }}</span>
          </button>
        </div>
      </div>

      <!-- 表格区：展示学员账号、报名课程、状态与学习进度，并按状态给出操作 -->
      <div v-if="loading" class="ast-loading">加载中…</div>
      <div v-else-if="rows.length" class="ast-table">
        <div class="ast-row ast-row-head">
          <span class="ast-col ast-col-name">学员</span>
          <span class="ast-col">账号</span>
          <span class="ast-col">报名课程</span>
          <span class="ast-col">技艺</span>
          <span class="ast-col">任课老师</span>
          <span class="ast-col">费用</span>
          <span class="ast-col">报名时间</span>
          <span class="ast-col">状态</span>
          <span class="ast-col">进度</span>
          <span class="ast-col ast-col-act">操作</span>
        </div>
        <div v-for="s in rows" :key="s.id" class="ast-row">
          <span class="ast-col ast-col-name">
            <span class="ast-avatar">{{ s.avatarGlyph || s.name.charAt(0) }}</span>
            <span class="ast-name-wrap">
              <span class="ast-name">{{ s.name }}</span>
              <span class="ast-phone">{{ s.phone }}</span>
            </span>
          </span>
          <span class="ast-col ast-col-account">
            <template v-if="s.username">
              <span class="ast-account">{{ s.username }}</span>
              <span v-if="s.nick" class="ast-account-nick">{{ s.nick }}</span>
              <span v-if="s.userStatus === 'disabled'" class="ast-account-off">已禁用</span>
            </template>
            <span v-else class="ast-account-none">未注册账号</span>
          </span>
          <span class="ast-col ast-col-course">{{ s.courseName }}</span>
          <span class="ast-col">{{ s.craft }}</span>
          <span class="ast-col">{{ s.teacher }}</span>
          <span class="ast-col">¥{{ s.price }}</span>
          <span class="ast-col ast-col-time">{{ s.enrollTime }}</span>
          <span class="ast-col">
            <span class="ast-badge" :style="{ color: statusMap[s.status].color, borderColor: statusMap[s.status].color }">
              {{ statusMap[s.status].label }}
            </span>
          </span>
          <span class="ast-col ast-col-progress">
            <span class="ast-progress-bar"><span class="ast-progress-fill" :style="{ width: s.progress + '%' }"></span></span>
            <span class="ast-progress-num">{{ s.progress }}%</span>
          </span>
          <span class="ast-col ast-col-act">
            <template v-if="s.status === 'review'">
              <button class="ast-btn" @click="approve(s)">录取</button>
              <button class="ast-btn ast-btn-danger" @click="rejectEnroll(s)">驳回</button>
            </template>
            <button v-else-if="s.status === 'ongoing'" class="ast-btn" @click="markDone(s)">标记结课</button>
            <span v-else class="ast-done">{{ s.status === 'rejected' ? '已驳回' : '已完成' }}</span>
          </span>
        </div>
      </div>

      <div v-else class="ast-empty">
        <span class="ast-empty-glyph">员</span>
        <p class="ast-empty-text">暂无相关学员</p>
      </div>

      <!-- 分页区：学员数量超过一页时显示 -->
      <div v-if="total > pageSize" class="ast-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listStudents, approveStudent, rejectStudent } from '@/api/students'
import { mapKeys } from '@/api/utils'
import { studentStatusMap, markStudentDoneAction, addLog, authState } from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 报名/学习状态配置（标签与颜色），来自 store
const statusMap = studentStatusMap

// 报名状态选项卡：value 与后端 status 参数对应，all 表示全部
const tabs = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'review' },
  { label: '进行中', value: 'ongoing' },
  { label: '已驳回', value: 'rejected' },
  { label: '已完成', value: 'done' },
]
const activeTab = ref('all') // 当前选中的报名状态
const keyword = ref('') // 搜索关键字（姓名 / 账号 / 电话 / 课程）

// 各状态选项卡的学员数量，用于按钮角标与头部总数
const tabCounts = ref({ all: 0, review: 0, ongoing: 0, rejected: 0, done: 0 })

// 头部展示的学员总数（即“全部”数量）
const allCount = computed(() => tabCounts.value.all)

// 规范化后端学员数据：补齐价格、课程、进度、已完成课时等字段的默认值
function mapStudentRow(s) {
  const m = mapKeys(s)
  return { ...m, price: Number(m.price ?? 0), avatarGlyph: m.avatarGlyph || (m.name ? m.name.charAt(0) : '学'), courseId: m.courseId ?? 0, enrollTime: m.enrollTime || '', progress: m.progress ?? 0, completed: Array.isArray(m.completed) ? m.completed.map(String) : [], materialPlan: Array.isArray(m.materialPlan) ? m.materialPlan : [] }
}

// 统计某个报名状态下的学员总数：只取 1 条记录读取 count，失败时返回 0
async function countTotal(statusVal) {
  try {
    const res = await listStudents({ status: statusVal, page_size: 1 })
    return Array.isArray(res) ? res.length : res.count || 0
  } catch (e) {
    return 0
  }
}

// 并行统计全部状态的数量，一次性更新选项卡角标
async function refreshTabCounts() {
  const [all, review, ongoing, rejected, done] = await Promise.all([
    countTotal(''), countTotal('review'), countTotal('ongoing'), countTotal('rejected'), countTotal('done'),
  ])
  tabCounts.value = { all, review, ongoing, rejected, done }
}

/* 分页列表：usePagedList 统一管理分页状态，
   fetchPage 按关键字与状态请求学员，“全部”状态不传 status 参数。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapStudentRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: keyword.value.trim() }
    if (activeTab.value !== 'all') params.status = activeTab.value
    return listStudents(params)
  },
})

// 切换报名状态选项卡，并重新加载第一页
function switchTab(v) {
  activeTab.value = v
  onFilter()
}

// 首次进入页面时加载列表与各状态数量
onMounted(() => {
  loadRows()
  refreshTabCounts()
})
// 状态变化时立即回到第一页重新查询
watch(activeTab, onFilter)
let kwTimer = null // 关键字防抖定时器
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300) // 停止输入 300ms 后再查询
})

// 操作人名称：写入操作日志时使用，取不到登录用户时兜底为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

/* 标记结课：确认后把学员状态改为已完成，并刷新列表与选项卡数量。 */
function markDone(s) {
  ElMessageBox.confirm(`确定将学员「${s.name}」标记为已结课吗？`, '标记结课', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await markStudentDoneAction(s.id)
      addLog('update', operator(), '学员结课', `学员「${s.name}」已结课`)
      ElMessage.success('已标记结课')
      await loadRows()
      await refreshTabCounts()
    })
    .catch(() => {})
}

/* 录取报名：录取后计入课程名额，学员可进入学习；成功后记录日志并刷新数据。 */
function approve(s) {
  ElMessageBox.confirm(`确定录取学员「${s.name}」的「${s.courseName}」报名吗？录取后计入课程名额并可进入学习。`, '录取报名', {
    confirmButtonText: '确认录取',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      try {
        await approveStudent(s.id)
        addLog('review', operator(), '报名录取', `学员「${s.name}」报名「${s.courseName}」已录取`)
        ElMessage.success('已录取，学员可进入学习')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '录取失败')
      }
      await loadRows()
      await refreshTabCounts()
    })
    .catch(() => {})
}

/* 驳回报名：弹窗填写原因（可留空使用默认提示），提交后反馈给学员。 */
function rejectEnroll(s) {
  ElMessageBox.prompt('请填写驳回原因（将反馈给学员），或留空使用默认提示', '驳回报名', {
    confirmButtonText: '确认驳回',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '例如：报名信息不完整，请补充后重新报名',
    inputValidator: (val) => {
      if (val && val.trim().length > 200) return '原因不能超过 200 字'
      return true
    },
    type: 'warning',
  })
    .then(async ({ value }) => {
      try {
        await rejectStudent(s.id, (value || '').trim())
        addLog('review', operator(), '报名驳回', `学员「${s.name}」报名「${s.courseName}」被驳回`)
        ElMessage.success('已驳回该报名')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '驳回失败')
      }
      await loadRows()
      await refreshTabCounts()
    })
    .catch(() => {})
}
</script>

<style src="./AdminStudents.css"></style>

<style scoped>
/* 加载提示与分页条的基础布局 */
.ast-loading { padding: 40px 0; text-align: center; color: #8a93a3; }
.ast-pager { display: flex; justify-content: flex-end; margin-top: 18px; }
</style>
