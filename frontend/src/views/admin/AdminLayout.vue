<!-- 管理后台整体布局：左侧导航侧边栏 + 顶部栏 + 内容出口，统一承载各后台页面 -->
<template>
  <div class="adl-shell">
    <!-- 侧边栏区：品牌标识、分组导航、折叠按钮与当前管理员信息 -->
    <aside class="adl-sidebar" :class="{ 'adl-collapsed': collapsed }">
      <!-- 品牌区：优先显示后台配置的 LOGO，没有配置时用文字图标兜底 -->
      <div class="adl-logo">
        <span class="adl-logo-glyph">
          <img v-if="brandLogo" :src="brandLogo" class="adl-logo-img" alt="LOGO" />
          <template v-else>{{ brandGlyph }}</template>
        </span>
        <span v-if="!collapsed" class="adl-logo-text">
          <span class="adl-logo-title">{{ brandShort }} · 管理后台</span>
          <span class="adl-logo-sub">管理员</span>
        </span>
      </div>

      <!-- 导航菜单区：按「工作台 / 内容审核 / 运营管理 / 系统」分组渲染菜单 -->
      <nav class="adl-menu">
        <div v-for="group in groups" :key="group.label" class="adl-group">
          <div v-if="!collapsed" class="adl-group-label">{{ group.label }}</div>
          <!-- 单个菜单项：点击跳转到对应后台路由，右侧角标显示待处理数量 -->
          <div
            v-for="m in group.items"
            :key="m.to"
            class="adl-item"
            :class="{ 'adl-item-active': m.to === route.path }"
            @click="router.push(m.to)"
          >
            <span class="adl-item-glyph">{{ m.glyph }}</span>
            <span v-if="!collapsed" class="adl-item-label">{{ m.label }}</span>
            <span v-if="!collapsed && badgeOf(m.to)" class="adl-item-badge">{{ badgeOf(m.to) }}</span>
          </div>
        </div>
      </nav>

      <!-- 侧边栏底部：折叠开关、当前管理员信息与退出登录按钮 -->
      <div class="adl-sidebar-bottom">
        <button class="adl-collapse-btn" @click="collapsed = !collapsed">
          <span class="adl-collapse-icon">{{ collapsed ? '»' : '«' }}</span>
          <span v-if="!collapsed" class="adl-collapse-text">收起侧栏</span>
        </button>
        <div class="adl-user">
          <span class="adl-user-avatar">{{ userName.charAt(0) }}</span>
          <span v-if="!collapsed" class="adl-user-info">
            <span class="adl-user-name">{{ userName }}</span>
            <span class="adl-user-role">{{ userRole }}</span>
          </span>
          <button v-if="!collapsed" class="adl-logout" title="退出登录" @click="logout">⏻</button>
        </div>
      </div>
    </aside>

    <!-- 主内容区：顶部栏 + 各后台页面内容 -->
    <div class="adl-main">
      <!-- 顶栏区：折叠按钮、当前页面标题与当天日期 -->
      <header class="adl-topbar">
        <div class="adl-topbar-left">
          <button class="adl-toggle" @click="collapsed = !collapsed">☰</button>
          <span class="adl-current-title">{{ currentTitle }}</span>
        </div>
        <div class="adl-topbar-right">
          <span class="adl-date">{{ dateStr }}</span>
        </div>
      </header>
      <!-- 路由出口：各后台页面作为 AdminLayout 的默认插槽内容渲染到这里 -->
      <main class="adl-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  authState,
  brandLogo,
  brandGlyph,
  brandShort,
  logout as doLogout,
  heritageCourses,
  heritageSkills,
  heritageProducts,
  heritageOrders,
  loadHeritageCourses,
  loadSkills,
  loadProducts,
  loadHeritageOrders,
  contactMessages,
  loadContactMessages,
} from '@/store'

// 路由相关：route 用来读取当前路径以高亮菜单，router 用来执行页面跳转
// useRouter：useRouter 是 vue-router 提供的组合式函数，返回路由器实例；调用 router.push('/路径') 就能在不刷新整页的情况下切换路由
const route = useRoute()
const router = useRouter()

// 侧边栏是否收起；点击底部折叠按钮或顶栏菜单按钮时切换
const collapsed = ref(false)

// 当前登录管理员信息，取不到时统一显示为“管理员”
const userName = computed(() => authState.user?.name || '管理员')
const userRole = computed(() => authState.user?.title || '管理员')

/* 侧边栏菜单配置：按业务分组列出后台全部页面。
   每项包含 label（显示名称）、glyph（文字图标）、to（目标路由），
   模板遍历这份配置即可生成导航菜单。 */
const groups = [
  {
    label: '工作台',
    items: [
      { label: '后台概览', glyph: '台', to: '/admin' },
    ],
  },
  {
    label: '内容审核',
    items: [
      { label: '课程审核', glyph: '课', to: '/admin/courses' },
      { label: '视频审核', glyph: '视', to: '/admin/videos' },
      { label: '技艺档案审核', glyph: '档', to: '/admin/skills' },
      { label: '作品审核', glyph: '作', to: '/admin/product-review' },
    ],
  },
  {
    label: '运营管理',
    items: [
      { label: '订单管理', glyph: '单', to: '/admin/orders' },
      { label: '学员管理', glyph: '员', to: '/admin/students' },
      { label: '培训记录', glyph: '训', to: '/admin/training' },
      { label: '传承人管理', glyph: '人', to: '/admin/inheritors' },
      { label: '库存管理', glyph: '库', to: '/admin/products' },
    ],
  },
  {
    label: '系统',
    items: [
      { label: '留言管理', glyph: '信', to: '/admin/messages' },
      { label: '系统配置', glyph: '设', to: '/admin/config' },
      { label: '操作日志', glyph: '志', to: '/admin/logs' },
      { label: '账号管理', glyph: '账', to: '/admin/accounts' },
    ],
  },
]

// 把所有分组里的菜单项扁平化成一个数组，便于按路径查找页面标题
const allItems = computed(() => groups.flatMap((g) => g.items))
// 顶栏标题：用当前路由路径在菜单中匹配名称，匹配不到时显示“管理后台”
const currentTitle = computed(
  () => allItems.value.find((m) => m.to === route.path)?.label || '管理后台'
)

// 顶栏右侧展示的当天日期（中文格式，包含星期）
const dateStr = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long',
})

/* 进入后台布局时预加载各模块数据，供菜单角标和概览页统计使用。
   allSettled 会等所有请求结束，单个接口失败不会影响其余数据。 */
onMounted(() => {
  Promise.allSettled([loadHeritageCourses(), loadSkills(), loadProducts(), loadHeritageOrders(), loadContactMessages()])
})

/* 各菜单的待处理数量统计：
   课程、技艺档案、作品按 status === 'pending' 计数；
   视频统计所有课程课时中 videoStatus === 'pending' 的数量；
   订单统计已支付（待发货）数量；留言统计新留言数量。 */
const pendingCourseCount = computed(() => heritageCourses.filter((c) => c.status === 'pending').length)
const pendingVideoCount = computed(() => {
  let n = 0
  heritageCourses.forEach((c) => {
    ;(c.lessons || []).forEach((les) => {
      if (les.videoStatus === 'pending') n++
    })
  })
  return n
})
const pendingSkillCount = computed(() => heritageSkills.filter((s) => s.status === 'pending').length)
const pendingProductCount = computed(() => heritageProducts.filter((p) => p.status === 'pending').length)
const paidOrderCount = computed(() => heritageOrders.filter((o) => o.status === 'paid').length)
const pendingMessageCount = computed(() => contactMessages.filter((m) => m.status === 'new').length)

// 路由路径到待处理数量的映射，用于菜单右侧小角标
const badgeMap = {
  '/admin/courses': pendingCourseCount,
  '/admin/videos': pendingVideoCount,
  '/admin/skills': pendingSkillCount,
  '/admin/product-review': pendingProductCount,
  '/admin/orders': paidOrderCount,
  '/admin/messages': pendingMessageCount,
}
/* 取出某个路由对应的待处理数量；未配置或数量为 0 时返回 0。 */
function badgeOf(to) {
  const c = badgeMap[to]
  return c && c.value ? c.value : 0
}

/* 退出登录：先调用 store 的 logout 清理登录状态，成功后再跳转登录页。 */
async function logout() {
  await doLogout()
  // 清理完登录态再跳转，避免在登录页残留旧用户信息
  router.push('/login')
}
</script>

<style src="./AdminLayout.css"></style>
