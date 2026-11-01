<!-- 全站顶部导航：品牌、栏目菜单、登录状态与退出入口，页面滚动后切换为实色背景 -->
<template>
  <nav class="nav" :class="{ 'nav-solid': scrolled }">
    <div class="nav-inner">
      <!-- 品牌区：有 LOGO 显示图片，否则显示品牌字形 -->
      <div class="nav-brand">
        <span class="nav-seal">
          <img v-if="brandLogo" :src="brandLogo" class="nav-seal-img" alt="LOGO" />
          <template v-else>{{ brandGlyph }}</template>
        </span>
        <span class="nav-name">{{ brandShort }}</span>
      </div>

      <!-- 栏目菜单：根据当前路由自动高亮对应项 -->
      <ul class="nav-list">
        <li v-for="m in menus" :key="m.label" class="nav-item">
          <router-link :to="m.to" class="nav-link" :class="{ 'nav-active': m.label === active }">
            {{ m.label }}
          </router-link>
        </li>
      </ul>
      <!-- 已登录：显示头像与退出按钮；未登录：显示登录按钮 -->
      <div v-if="loggedIn" class="nav-user">
        <div class="nav-avatar" @click="goProfile" title="个人中心">
          <span class="avatar-glyph">{{ avatarGlyph }}</span>
        </div>
        <button class="nav-logout" title="退出登录" @click="onLogout">退出</button>
      </div>
      <button v-else class="nav-login" @click="goLogin">登录</button>
    </div>
  </nav>
</template>

<script>
import { ElMessageBox } from 'element-plus'
import { authState, isLoggedIn, logout, brandLogo, brandGlyph, brandShort } from '@/store'
import { apiMe } from '@/api/auth'

/* 导航组件：Options API 写法，负责菜单高亮、登录状态展示和退出登录 */
export default {
  data() {
    return {
      // 页面是否已向下滚动，用于切换导航栏样式
      scrolled: false,
      // 栏目菜单配置
      menus: [
        { label: '首页', to: '/' },
        { label: '技艺档案', to: '/archive' },
        { label: '培训课程', to: '/course' },
        { label: '文创作品', to: '/product' },
        { label: '传承人', to: '/inheritor' },
      ],
    }
  },
  computed: {
    /* 根据当前路径判断要高亮的菜单项；个人中心、支付、学习页不高亮任何栏目 */
    active() {
      const path = this.$route.path
      if (path.startsWith('/archive')) return '技艺档案'
      if (path.startsWith('/inheritor')) return '传承人'
      if (path === '/') return '首页'
      if (path.startsWith('/profile') || path.startsWith('/pay') || path.startsWith('/learn')) return ''
      const hit = this.menus.find((m) => m.to !== '#' && m.to !== '/' && path.startsWith(m.to))
      return hit ? hit.label : ''
    },
    /* 登录状态与品牌信息，均来自全局共享状态 */
    loggedIn() {
      return isLoggedIn()
    },
    brandLogo() {
      return brandLogo.value
    },
    brandGlyph() {
      return brandGlyph.value
    },
    brandShort() {
      return brandShort.value
    },
    /* 头像文字：取用户昵称或姓名的首字，没有用户时用「漆」兜底 */
    avatarGlyph() {
      const user = authState.user
      const n = (user && (user.nick || user.name)) || ''
      return n ? n.charAt(0) : '漆'
    },
  },
  mounted() {
    // 监听页面滚动，用于切换导航栏背景
    window.addEventListener('scroll', this.onScroll)
    // 已登录时再拉取一次最新用户资料，保证头像等信息是最新的
    if (!isLoggedIn()) return
    apiMe()
      .then((me) => {
        if (me && me.nick) {
          authState.user = { ...(authState.user || {}), ...me }
        }
      })
      .catch(() => {})
  },
  // 组件卸载前移除滚动监听，避免事件残留
  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll)
  },
  methods: {
    /* 页面滚动超过 40 像素时，给导航栏加上实色背景 */
    onScroll() {
      this.scrolled = window.scrollY > 40
    },
    /* 跳转到个人中心 */
    goProfile() {
      this.$router.push('/profile')
    },
    /* 跳转登录页，并记下当前页面，登录后可跳回 */
    goLogin() {
      this.$router.push({ path: '/login', query: { redirect: this.$route.fullPath } })
    },
    /* 退出登录：先弹确认框，确认后清除登录状态并回到登录页 */
    async onLogout() {
      try {
        await ElMessageBox.confirm('退出后可直接登录其他角色账号，确定退出？', '退出登录', {
          confirmButtonText: '退出',
          cancelButtonText: '取消',
          type: 'warning',
        })
      } catch (e) {
        // 用户点击取消时不做任何处理
        return
      }
      // 确认退出：清除登录状态并跳转到登录页
      await logout()
      this.$router.push('/login')
    },
  },
}
</script>

<style src="./nav.css"></style>
