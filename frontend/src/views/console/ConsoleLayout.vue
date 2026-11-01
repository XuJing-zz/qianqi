<!-- 传承人工作台布局：左侧可折叠导航栏 + 顶部标题栏 + 页面内容插槽 -->
<template>
  <div class="console-layout" :class="{ 'cns-collapsed': collapsed }">
    <!-- 左侧侧边栏：品牌标识、分组导航、折叠按钮与用户信息 -->
    <aside class="cns-side">
      <!-- 品牌区：优先显示系统 LOGO，未配置时显示文字印记 -->
      <div class="cns-brand">
        <span class="cns-brand-seal">
          <img v-if="brandLogo" :src="brandLogo" class="cns-brand-img" alt="LOGO" />
          <template v-else>{{ brandGlyph }}</template>
        </span>
        <div class="cns-brand-text" v-show="!collapsed">
          <span class="cns-brand-name">{{ brandShort }} · 工作站</span>
          <span class="cns-brand-sub">传承人端</span>
        </div>
      </div>

      <!-- 分组导航；当前路由对应的菜单项会自动高亮 -->
      <nav class="cns-nav">
        <div class="cns-nav-group" v-for="g in groups" :key="g.title">
          <span class="cns-group-title" v-show="!collapsed">{{ g.title }}</span>
          <router-link
            v-for="m in g.menus"
            :key="m.to"
            :to="m.to"
            class="cns-nav-item"
            :class="{ 'cns-nav-active': isActive(m) }"
            :title="collapsed ? m.label : ''"
          >
            <span class="cns-nav-icon">{{ m.icon }}</span>
            <span class="cns-nav-label" v-show="!collapsed">{{ m.label }}</span>
            <span v-if="m.badge" class="cns-nav-badge">{{ m.badge }}</span>
          </router-link>
        </div>
      </nav>

      <!-- 侧边栏底部：折叠开关与当前登录用户信息 -->
      <div class="cns-side-foot">
        <div class="cns-collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? '展开' : '收起'">
          <span class="cns-collapse-icon">{{ collapsed ? '›' : '‹' }}</span>
        </div>

        <div class="cns-user" v-show="!collapsed">
          <span class="cns-user-avatar">{{ userInitial }}</span>
          <div class="cns-user-body">
            <span class="cns-user-name">{{ userName }}</span>
            <span class="cns-user-role">{{ userRole }}</span>
          </div>
          <button class="cns-user-logout" title="退出登录" @click="logout">⏻</button>
        </div>
      </div>
    </aside>

    <!-- 右侧主区域：顶部栏 + 页面内容 -->
    <div class="cns-main">
      <!-- 顶部栏：当前页面标题、当天日期与用户头像 -->
      <header class="cns-topbar">
        <button class="cns-topbar-toggle" @click="collapsed = !collapsed">
          {{ collapsed ? '☰' : '☰' }}
        </button>
        <div class="cns-topbar-title">
          <h1 class="cns-topbar-cn">{{ currentTitle }}</h1>
          <span class="cns-topbar-en">WORKSTATION</span>
        </div>
        <div class="cns-topbar-right">
          <span class="cns-topbar-date">{{ today }}</span>
          <span class="cns-topbar-avatar">{{ userInitial }}</span>
        </div>
      </header>

      <main class="cns-content">
        <!-- 子页面内容通过默认插槽渲染在这里 -->
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、路由、登录状态 / 登出、学员数据与品牌配置
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState, logout as doLogout, heritageStudents, brandLogo, brandGlyph, brandShort } from '@/store'

// 当前路由与路由器实例：用于菜单高亮、标题匹配和退出后跳转
const route = useRoute()
const router = useRouter()

// 侧边栏是否折叠
const collapsed = ref(false)

// 当前登录用户名，缺失时显示“传承人”
const userName = computed(() => authState.user?.name || '传承人')

/* 在学学员数角标：数量为 0 时返回空字符串，不显示角标 */
const studentBadge = computed(() => {
  const n = heritageStudents.filter((s) => s.status === 'ongoing').length
  return n > 0 ? String(n) : ''
})

// 导航分组配置：每组标题 + 菜单项（路径、图标、可选角标）
const groups = [
  {
    title: '工作台',
    menus: [
      { label: '工作台概览', to: '/console', icon: '台', badge: '' },
    ],
  },
  {
    title: '内容管理',
    menus: [
      { label: '我的作品', to: '/console/works', icon: '作', badge: '' },
      { label: '我的课程', to: '/console/courses', icon: '课', badge: '' },
      { label: '我的技艺', to: '/console/skills', icon: '艺', badge: '' },
    ],
  },
  {
    title: '进销存',
    menus: [
      { label: '库存管理', to: '/console/inventory', icon: '存', badge: '' },
    ],
  },
  {
    title: '教学管理',
    menus: [
      { label: '学员名单', to: '/console/students', icon: '学', badge: studentBadge },
      { label: '培训记录', to: '/console/training', icon: '训', badge: '' },
    ],
  },
  {
    title: '账户',
    menus: [
      { label: '个人主页', to: '/console/profile', icon: '我', badge: '' },
    ],
  },
]

// 用户角色名称与头像首字
const userRole = computed(() => authState.user?.title || '非遗传承人')
const userInitial = computed(() => userName.value.charAt(0))

/* 根据当前路由路径在导航配置中查找页面标题，找不到时回退为“工作台概览” */
const currentTitle = computed(() => {
  for (const g of groups) {
    const hit = g.menus.find((m) => m.to === route.path)
    if (hit) return hit.label
  }
  return '工作台概览'
})

// 生成 YYYY-MM-DD 格式的当天日期
const today = computed(() => {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return y + '-' + m + '-' + day
})

/* 判断菜单是否激活：/console 需精确匹配，其余菜单按路径前缀匹配子页面 */
function isActive(m) {
  if (m.to === '/console') {
    return route.path === '/console'
  }
  return route.path.startsWith(m.to)
}

/* 退出登录：调用状态层的登出逻辑后跳转到登录页 */
async function logout() {
  await doLogout()
  router.push('/login')
}
</script>

<style src="./ConsoleLayout.css"></style>
