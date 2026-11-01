<!-- 个人中心 · 我的报名页：按状态筛选报名记录，并提供查看课程/进入学习入口 -->
<template>
  <div class="enroll-page">
    <Nav />

    <!-- 页面主体：左侧个人中心侧边栏 + 右侧报名列表 -->
    <div class="me-wrap">
      <ProfileAside />

      <div class="me-main">
        <header class="me-head">
          <h1 class="me-title">我的报名</h1>
          <span class="me-en">MY ENROLLMENTS</span>
        </header>

        <!-- 工具栏：状态筛选标签与当前结果数量 -->
        <div class="me-toolbar">
          <div class="me-tabs">
            <button
              v-for="s in statusLabels"
              :key="s.key"
              class="me-tab"
              :class="{ 'me-tab-active': status === s.key }"
              @click="status = s.key"
            >
              {{ s.label }}
            </button>
          </div>
          <span class="me-count">共 {{ filtered.length }} 门</span>
        </div>

        <!-- 报名卡片列表：点击卡片或有状态变化时进入对应页面 -->
        <div class="me-list" v-if="filtered.length">
          <div
            v-for="e in filtered"
            :key="e.id"
            class="me-card"
            @click="cardClick(e)"
          >
            <div class="me-cover" :style="coverStyle(e)">
              <span class="me-glyph">{{ glyphOf(e) }}</span>
            </div>
            <div class="me-body">
              <div class="me-top">
                <h3 class="me-name">{{ courseTitle(e) }}</h3>
                <span class="me-status" :class="'me-status-' + e.status">{{ statusText(e.status) }}</span>
              </div>
              <p class="me-teacher">
                <span class="me-verified">✓</span>
                {{ e.teacher }} · {{ craftOf(e) }}
              </p>
              <p class="me-meta">{{ metaOf(e) }}</p>
              <!-- 根据报名状态展示不同提示：进行中显示进度，其他状态显示说明 -->
              <div v-if="e.status === 'ongoing'" class="me-progress">
                <div class="me-progress-bar"><i :style="{ width: progressOf(e) + '%' }"></i></div>
                <span class="me-progress-text">已录取 · 进行中 {{ progressOf(e) }}%</span>
              </div>
              <div v-else-if="e.status === 'done'" class="me-progress">
                <span class="me-progress-text">已结课 · 全部课时完成</span>
              </div>
              <div v-else-if="e.status === 'review'" class="me-progress">
                <span class="me-progress-text">报名已提交，等待管理员审核录取</span>
              </div>
              <div v-else-if="e.status === 'rejected'" class="me-progress">
                <span class="me-progress-text">
                  报名未通过<template v-if="e.reviewComment">：{{ e.reviewComment }}</template>，可重新报名
                </span>
              </div>
              <div class="me-foot">
                <span class="me-price"><em>¥</em>{{ e.price }}</span>
                <template v-if="e.status === 'rejected'">
                  <span class="me-btn me-btn-solid" @click.stop="goPay(e.courseId)">重新报名</span>
                </template>
                <template v-else>
                  <span class="me-btn" @click.stop="footClick(e)">查看课程</span>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="me-empty">
          <!-- 空状态：没有符合条件的报名时引导去选课 -->
          <p class="me-empty-text">暂无相关报名记录</p>
          <button class="me-btn me-btn-solid" @click="goCourses">去选课</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import ProfileAside from './ProfileAside.vue'
import { enrollmentState, courses, loadEnrollments, ensureCourses } from '@/store'

const router = useRouter()

// Promise.allSettled：Promise.allSettled 会等所有传入的 Promise 都结束（无论成功失败），返回各自的结果状态
// 页面加载时并行拉取报名记录和课程数据，其中一项失败不影响另一项
onMounted(() => {
  Promise.allSettled([loadEnrollments(), ensureCourses()])
})

// 状态筛选标签配置：key 对应报名状态，all 表示全部
const statusLabels = [
  { key: 'all', label: '全部' },
  { key: 'review', label: '待审核' },
  { key: 'ongoing', label: '进行中' },
  { key: 'rejected', label: '已驳回' },
  { key: 'done', label: '已结课' },
]

// 当前筛选状态，默认显示全部
const status = ref('all')

// 根据当前筛选状态过滤报名列表
const filtered = computed(() => {
  if (status.value === 'all') return enrollmentState.list
  return enrollmentState.list.filter((e) => e.status === status.value)
})

// 把报名状态码转换成中文文案
function statusText(s) {
  return { review: '待审核', ongoing: '已录取 · 进行中', rejected: '已驳回', done: '已结课' }[s] || s
}

// 从课程数据中取用于封面占位的字形
function glyphOf(e) {
  const c = courses.find((c) => c.id === e.courseId)
  return c ? c.glyph : '课'
}

// 课程标题：优先按课程 ID 匹配课程数据，匹配不到时用报名记录里的名称
function courseTitle(e) {
  if (e.courseId) {
    const c = courses.find((x) => x.id === e.courseId)
    if (c && c.name) return c.name
  }
  return e.courseName || e.name || '课程'
}

// 工艺信息：优先用报名记录中的 craft，没有则从课程数据中补
function craftOf(e) {
  return e.craft || (e.courseId ? courses.find((c) => c.id === e.courseId)?.craft : '') || ''
}

// 学习进度归一化：非数字按 0 处理，并限制在 0~100 之间
function progressOf(e) {
  const p = Number(e.progress)
  if (!Number.isFinite(p)) return 0
  return Math.max(0, Math.min(100, Math.round(p)))
}

// 组合开课阶段和报名时间等元信息，用“·”连接显示
function metaOf(e) {
  const c = e.courseId ? courses.find((x) => x.id === e.courseId) : null
  const stage = e.stage || (c && c.stage) || ''
  const parts = []
  if (stage) parts.push(stage)
  if (e.enrollTime) parts.push(e.enrollTime + ' 报名')
  return parts.join(' · ')
}

// 有封面图时生成背景图样式，否则使用默认占位样式
function coverStyle(e) {
  if (e.cover) return { backgroundImage: 'url(' + e.cover + ')' }
  return {}
}

// 页面跳转辅助函数：分别进入学习页、课程详情页、支付页和课程列表
function goLearn(courseId) {
  router.push('/learn/' + courseId)
}
function goCourseDetail(courseId) {
  router.push('/course/' + courseId)
}
function goPay(courseId) {
  router.push('/pay/' + courseId)
}
function goCourses() {
  router.push('/course')
}

// 点击卡片：进行中/已结课进入学习页，其他状态进入课程详情
function cardClick(e) {
  if (e.status === 'ongoing' || e.status === 'done') goLearn(e.courseId)
  else goCourseDetail(e.courseId)
}
// 底部“查看课程”按钮：逻辑与卡片点击一致
function footClick(e) {
  if (e.status === 'ongoing' || e.status === 'done') goLearn(e.courseId)
  else goCourseDetail(e.courseId)
}
</script>

<style src="./MyEnroll.css"></style>
