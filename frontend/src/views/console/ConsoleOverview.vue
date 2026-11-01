<!-- 传承人工作台概览页：展示欢迎信息、数据卡片、待办、快捷入口与上课出勤统计 -->
<template>
  <ConsoleLayout>
    <div class="cvo-wrap">
      <!-- 欢迎区：显示当前传承人姓名、头衔与当天日期 -->
      <div class="cvo-hello">
        <h2 class="cvo-hello-title">欢迎回来，{{ userName }}</h2>
        <p class="cvo-hello-sub">{{ userTitle }} · {{ todayText }}</p>
      </div>

      <!-- 数据卡片区：作品、课程、技艺、在学学员，点击可跳转到对应页面 -->
      <div class="cvo-cards">
        <div
          v-for="c in cards"
          :key="c.label"
          class="cvo-card"
          @click="go(c.to)"
        >
          <span class="cvo-card-glyph">{{ c.glyph }}</span>
          <div class="cvo-card-body">
            <span class="cvo-card-num">{{ c.num }}</span>
            <span class="cvo-card-label">{{ c.label }}</span>
          </div>
          <span v-if="c.badge" class="cvo-card-badge">{{ c.badge }}</span>
        </div>
      </div>

      <!-- 待办事项与快捷入口两栏布局 -->
      <div class="cvo-grid">
        <!-- 待办事项：审核中的课程 / 作品、库存告急，点击可直达处理页面 -->
        <section class="cvo-panel">
          <div class="cvo-panel-head">
            <h3 class="cvo-panel-title">待办事项</h3>
          </div>
          <div v-if="todos.length" class="cvo-todo-list">
            <div
              v-for="(t, i) in todos"
              :key="i"
              class="cvo-todo"
              @click="go(t.to)"
            >
              <span class="cvo-todo-glyph">{{ t.glyph }}</span>
              <div class="cvo-todo-body">
                <span class="cvo-todo-text">{{ t.text }}</span>
                <span class="cvo-todo-sub">{{ t.sub }}</span>
              </div>
              <span class="cvo-todo-arrow">›</span>
            </div>
          </div>
          <div v-else class="cvo-empty">
            <span class="cvo-empty-glyph">✓</span>
            <p class="cvo-empty-text">暂无待办，一切顺利</p>
          </div>
        </section>

        <!-- 快捷入口：常用工作台页面的快速跳转 -->
        <section class="cvo-panel">
          <div class="cvo-panel-head">
            <h3 class="cvo-panel-title">快捷入口</h3>
          </div>
          <div class="cvo-quick-list">
            <div
              v-for="q in quicks"
              :key="q.label"
              class="cvo-quick"
              @click="go(q.to)"
            >
              <span class="cvo-quick-glyph">{{ q.glyph }}</span>
              <span class="cvo-quick-label">{{ q.label }}</span>
            </div>
          </div>
        </section>
      </div>

      <!-- 上课情况统计：基于培训台账中的出勤表计算课时、学员数与出勤率 -->
      <section class="cvo-panel cvo-stats">
        <div class="cvo-panel-head">
          <h3 class="cvo-panel-title">上课情况统计</h3>
          <span class="cvo-panel-sub">基于培训台账出勤表 · 到课率</span>
        </div>

        <!-- 统计总览卡片：培训课时、在册学员、总出勤率、出勤 / 应到 -->
        <div class="cvo-stat-cards">
          <div class="cvo-stat-card">
            <span class="cvo-stat-num">{{ totalSessions }}</span>
            <span class="cvo-stat-label">培训课时</span>
          </div>
          <div class="cvo-stat-card">
            <span class="cvo-stat-num">{{ heritageStudents.length }}</span>
            <span class="cvo-stat-label">在册学员</span>
          </div>
          <div class="cvo-stat-card">
            <span class="cvo-stat-num">{{ attendanceStats.rate }}%</span>
            <span class="cvo-stat-label">总出勤率</span>
          </div>
          <div class="cvo-stat-card">
            <span class="cvo-stat-num">{{ attendanceStats.present }}/{{ attendanceStats.expected }}</span>
            <span class="cvo-stat-label">出勤 / 应到</span>
          </div>
        </div>

        <!-- 明细统计：左侧按课程汇总出勤率，右侧按学员统计到课排行 -->
        <div class="cvo-stat-cols">
          <div class="cvo-stat-col">
            <h4 class="cvo-stat-col-title">各课程出勤率</h4>
            <table class="cvo-stat-table">
              <thead>
                <tr><th>课程</th><th>课时</th><th>出勤率</th></tr>
              </thead>
              <tbody>
                <tr v-for="s in courseStats" :key="s.name">
                  <td class="cvo-stat-name" :title="s.name">{{ s.name }}</td>
                  <td>{{ s.sessions }}</td>
                  <td><span class="cvo-rate" :class="rateClass(s.rate)">{{ s.rate }}%</span></td>
                </tr>
                <tr v-if="!courseStats.length"><td colspan="3" class="cvo-stat-empty">暂无培训记录</td></tr>
              </tbody>
            </table>
          </div>
          <div class="cvo-stat-col">
            <h4 class="cvo-stat-col-title">学员到课排行</h4>
            <table class="cvo-stat-table">
              <thead>
                <tr><th>学员</th><th>出勤/应到</th><th>到课率</th></tr>
              </thead>
              <tbody>
                <tr v-for="s in studentStats" :key="s.name">
                  <td class="cvo-stat-name">{{ s.name }}</td>
                  <td>{{ s.present }}/{{ s.expected }}</td>
                  <td><span class="cvo-rate" :class="rateClass(s.rate)">{{ s.rate }}%</span></td>
                </tr>
                <tr v-if="!studentStats.length"><td colspan="3" class="cvo-stat-empty">暂无出勤数据</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  </ConsoleLayout>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、路由、工作台布局与状态层数据 / 加载函数
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ConsoleLayout from './ConsoleLayout.vue'
import {
  heritageCourses,
  heritageProducts,
  heritageStudents,
  heritageSkills,
  trainingRecords,
  authState,
  heritageProfile,
  loadHeritageCourses,
  loadProducts,
  loadSkills,
  loadStudents,
  loadTrainingRecords,
  loadHeritageProfile,
} from '@/store'

// 路由实例，用于数据卡片、待办和快捷入口的页面跳转
const router = useRouter()

/* 页面挂载时并行加载课程、作品、技艺、学员、培训记录与主页资料；单个请求失败不影响其他数据 */
onMounted(() => {
  Promise.allSettled([
    loadHeritageCourses(), loadProducts(), loadSkills(), loadStudents(),
    loadTrainingRecords(), loadHeritageProfile(),
  ])
})

// 优先使用登录账号的姓名，缺失时回退到传承人主页资料
const userName = computed(() => authState.user?.name || heritageProfile.name || '传承人')
// 头衔优先取账号信息，否则用“级别 · 技艺”拼接
const userTitle = computed(() => {
  if (authState.user?.title) return authState.user.title
  return heritageProfile.level ? `${heritageProfile.level} · ${heritageProfile.craft}` : '非遗传承人'
})

// 生成“几月几日 · 星期几”格式的当天日期文本
const todayText = computed(() => {
  const d = new Date()
  const week = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
  return `${d.getMonth() + 1}月${d.getDate()}日 · 星期${week}`
})

// 待审核作品数、待审核课程数、在学学员数，用于卡片角标和待办
const workPending = computed(() => heritageProducts.filter((p) => p.status === 'pending').length)
const coursePending = computed(() => heritageCourses.filter((c) => c.status === 'pending').length)
const ongoingStudents = computed(() => heritageStudents.filter((s) => s.status === 'ongoing').length)

// 顶部数据卡片配置：数量、名称、跳转地址与审核中角标
const cards = computed(() => [
  { glyph: '作', num: heritageProducts.length, label: '我的作品', to: '/console/works', badge: workPending.value ? `${workPending.value} 待审` : '' },
  { glyph: '课', num: heritageCourses.length, label: '我的课程', to: '/console/courses', badge: coursePending.value ? `${coursePending.value} 待审` : '' },
  { glyph: '艺', num: heritageSkills.length, label: '我的技艺', to: '/console/skills', badge: '' },
  { glyph: '学', num: ongoingStudents.value, label: '在学学员', to: '/console/students', badge: '' },
])

// 培训课时数：每条培训记录计为一次课时
const totalSessions = computed(() => trainingRecords.length)

/* 汇总所有培训记录：应到人数为出勤表条数，实到为状态 present 的条数，并计算百分比 */
const attendanceStats = computed(() => {
  let present = 0
  let expected = 0
  trainingRecords.forEach((r) => {
    const arr = r.attendance || []
    expected += arr.length
    present += arr.filter((a) => a.status === 'present').length
  })
  return { present, expected, rate: expected ? Math.round((present / expected) * 100) : 0 }
})

/* 按课程名分组统计课时与出勤率；未关联课程的记录归入“未关联课程” */
const courseStats = computed(() => {
  const map = {}
  trainingRecords.forEach((r) => {
    const k = r.courseName || '未关联课程'
    if (!map[k]) map[k] = { name: k, sessions: 0, present: 0, expected: 0 }
    map[k].sessions++
    const arr = r.attendance || []
    map[k].expected += arr.length
    map[k].present += arr.filter((a) => a.status === 'present').length
  })
  return Object.values(map).map((s) => ({ ...s, rate: s.expected ? Math.round((s.present / s.expected) * 100) : 0 }))
})

/* 按学员姓名汇总出勤次数与到课率，并按到课率、应到次数从高到低排序 */
const studentStats = computed(() => {
  const map = {}
  trainingRecords.forEach((r) => {
    ;(r.attendance || []).forEach((a) => {
      const nm = (a.name || '').trim()
      if (!nm) return
      if (!map[nm]) map[nm] = { name: nm, present: 0, expected: 0 }
      map[nm].expected++
      if (a.status === 'present') map[nm].present++
    })
  })
  return Object.values(map)
    .map((s) => ({ ...s, rate: s.expected ? Math.round((s.present / s.expected) * 100) : 0 }))
    .sort((a, b) => b.rate - a.rate || b.expected - a.expected)
})

/* 根据出勤率返回颜色样式类：≥90% 良好、≥70% 中等、其余偏低 */
function rateClass(rate) {
  if (rate >= 90) return 'cvo-rate-good'
  if (rate >= 70) return 'cvo-rate-mid'
  return 'cvo-rate-low'
}

// 已通过审核且在售、库存不高于预警值的作品，用于生成库存待办
const lowStockWorks = computed(() =>
  heritageProducts.filter(
    (p) => p.status === 'approved' && p.saleable && Number(p.stock ?? 0) <= Number(p.alertThreshold ?? 5)
  )
)

/* 组装待办列表：有审核中课程 / 作品或库存告急时才产生对应条目 */
const todos = computed(() => {
  const list = []
  if (coursePending.value) {
    list.push({
      glyph: '课',
      text: `${coursePending.value} 门课程审核中`,
      sub: '等待管理员审核，期间可继续编辑完善',
      to: '/console/courses',
    })
  }
  if (workPending.value) {
    list.push({
      glyph: '作',
      text: `${workPending.value} 件作品审核中`,
      sub: '等待管理员审核',
      to: '/console/works',
    })
  }
  if (lowStockWorks.value.length) {
    list.push({
      glyph: '存',
      text: `${lowStockWorks.value.length} 件作品库存告急`,
      sub: '已低于库存预警值，请及时补货',
      to: '/console/inventory',
    })
  }
  return list
})

// 快捷入口配置：图标、名称与目标路由
const quicks = [
  { glyph: '课', label: '课程管理', to: '/console/courses' },
  { glyph: '学', label: '学员管理', to: '/console/students' },
  { glyph: '训', label: '记一次培训', to: '/console/training' },
  { glyph: '作', label: '作品管理', to: '/console/works' },
  { glyph: '存', label: '库存管理', to: '/console/inventory' },
  { glyph: '艺', label: '技艺管理', to: '/console/skills' },
  { glyph: '我', label: '个人主页', to: '/console/profile' },
]

// 统一跳转入口：路径为空时不做任何操作
function go(path) {
  if (path) router.push(path)
}
</script>

<style src="./ConsoleOverview.css"></style>
