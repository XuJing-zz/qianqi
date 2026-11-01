<!-- 我的课程页：按状态筛选传承人的课程，支持新建、编辑、提交审核与下架 -->
<template>
  <ConsoleLayout>
    <div class="ccr-wrap">
      <!-- 页面标题与新建课程入口 -->
      <div class="ccr-head">
        <div class="ccr-head-left">
          <h2 class="ccr-title">我的课程</h2>
          <p class="ccr-sub">共 {{ courseList.length }} 门课程</p>
        </div>
        <button class="ccr-add-btn" @click="goCreate">＋ 新建课程</button>
      </div>

      <!-- 课程状态筛选标签：全部 / 草稿 / 待审核 / 已通过 / 已驳回 / 已下架 -->
      <div class="ccr-tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="ccr-tab"
          :class="{ 'ccr-tab-active': activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
          <span class="ccr-tab-count">{{ countOf(t.value) }}</span>
        </button>
      </div>

      <!-- 课程卡片列表 -->
      <div v-if="filtered.length" class="ccr-list">
        <div v-for="c in filtered" :key="c.id" class="ccr-card">
          <div class="ccr-cover">
            <img v-if="c.cover" :src="c.cover" class="ccr-cover-img" alt="课程封面" />
            <span v-else class="ccr-cover-glyph">{{ c.craft.charAt(0) || '课' }}</span>
          </div>
          <div class="ccr-body">
            <div class="ccr-body-top">
              <h3 class="ccr-name">{{ c.name }}</h3>
              <span class="ccr-badge" :style="{ color: statusMap[c.status].color, borderColor: statusMap[c.status].color }">
                {{ statusMap[c.status].label }}
              </span>
            </div>
            <div class="ccr-meta">
              <span class="ccr-meta-item">{{ c.craft }}</span>
              <span class="ccr-meta-item">{{ c.stage }}</span>
              <span class="ccr-meta-item">{{ c.difficulty }}</span>
              <span class="ccr-meta-item">{{ c.duration }}</span>
              <span v-if="c.schedule" class="ccr-meta-item ccr-meta-time">🕘 {{ dateRangeText(c) }}</span>
            </div>
            <div class="ccr-meta ccr-meta-num">
              <span class="ccr-meta-item">费用 ¥{{ c.priceNum }}</span>
              <span class="ccr-meta-item">招生 {{ c.capacity }} 人</span>
              <span class="ccr-meta-item" title="名额以录取为准，待审核/已驳回的报名记录不占名额">已录 {{ c.enrolled }} 人</span>
              <span class="ccr-meta-item">课时 {{ (c.lessons || []).length }} 节</span>
            </div>
            <!-- 管理员驳回时显示驳回意见 -->
            <div v-if="c.status === 'rejected' && c.reviewComment" class="ccr-reject">
              <span class="ccr-reject-label">驳回意见：</span>{{ c.reviewComment }}
            </div>
            <!-- 按课程状态显示编辑、提交审核、下架等操作 -->
            <div class="ccr-actions">
              <button class="ccr-btn ccr-btn-primary" @click="openEdit(c)">编辑</button>
              <button v-if="c.status === 'draft' || c.status === 'rejected' || c.status === 'offline'" class="ccr-btn ccr-btn-warn" @click="submitReview(c)">提交审核</button>
              <button v-if="c.status === 'pending'" class="ccr-btn ccr-btn-plain" disabled>审核中，不可编辑提交</button>
              <button v-if="c.status === 'approved'" class="ccr-btn ccr-btn-warn" @click="toggleOffline(c)">下架</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="ccr-empty">
        <span class="ccr-empty-glyph">课</span>
        <p class="ccr-empty-text">暂无{{ activeTabLabel }}课程</p>
      </div>
    </div>
  </ConsoleLayout>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、路由、消息 / 确认框、工作台布局与课程状态层
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import { heritageCourses, courseStatusMap, loadHeritageCourses, submitCourseAction, offlineCourseAction } from '@/store'

// 路由实例，用于跳转到新建 / 编辑课程页面
const router = useRouter()
// 课程状态与标签 / 颜色的映射
const statusMap = courseStatusMap

/* 页面挂载时加载课程列表；失败时保持空列表，不阻塞页面渲染 */
onMounted(() => {
  loadHeritageCourses().catch(() => {})
})

// 当前传承人的课程列表（直接引用全局状态）
const courseList = heritageCourses

// 状态筛选标签配置
const tabs = [
  { label: '全部', value: 'all' },
  { label: '草稿', value: 'draft' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
  { label: '已下架', value: 'offline' },
]
const activeTab = ref('all')

// 当前标签名称，用于空状态提示
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')

/* 按当前标签筛选课程；all 直接返回全部 */
const filtered = computed(() => {
  if (activeTab.value === 'all') return courseList
  return courseList.filter((c) => c.status === activeTab.value)
})

/* 统计某个状态下的课程数；all 表示全部 */
function countOf(v) {
  if (v === 'all') return courseList.length
  return courseList.filter((c) => c.status === v).length
}

/* 拼接开课日期与结束日期；没有结束日期时只显示开始日期 */
function dateRangeText(c) {
  const start = c.schedule || ''
  return c.endDate ? start + ' ~ ' + c.endDate : start
}

// 跳转到新建课程页面
function goCreate() {
  router.push('/console/courses/new')
}

// 跳转到指定课程的编辑页面
function openEdit(c) {
  router.push('/console/courses/' + c.id + '/edit')
}

/* 提交审核 / 重新上架：先弹确认框，再调用提交接口；下架课程需重新经管理员审核 */
function submitReview(c) {
  const isOffline = c.status === 'offline'
  const verb = isOffline ? '重新上架' : '提交审核'
  ElMessageBox.confirm(isOffline
    ? '重新上架需提交管理员重新审核，审核通过前课程不公开。确定提交？'
    : '提交后管理员将进行审核，审核通过后课程将公开显示。确定提交？', verb, {
    confirmButtonText: '提交',
    cancelButtonText: '再想想',
    type: 'info',
  })
    .then(async () => {
      try {
        await submitCourseAction(c.id)
        ElMessage.success('已提交审核，请等待管理员审核')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '提交失败')
      }
    })
    .catch(() => {})
}

/* 下架课程：确认后调用下架接口；下架后学员将无法继续报名 */
async function toggleOffline(c) {
  ElMessageBox.confirm('下架后学员将无法报名该课程；如需修改课时视频，下架后需重新审核上架。确定下架？', '下架课程', {
    confirmButtonText: '下架',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await offlineCourseAction(c.id)
        ElMessage.success('课程已下架')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '下架失败')
      }
    })
    .catch(() => {})
}
</script>

<style src="./ConsoleCourses.css"></style>
