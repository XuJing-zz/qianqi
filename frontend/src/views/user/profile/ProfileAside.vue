<!-- 个人中心侧边栏：显示登录用户信息、菜单导航与退出登录入口 -->
<template>
  <aside class="profile-aside">
    <!-- 已登录分支：用户信息 + 菜单 + 退出登录 -->
    <template v-if="isLoggedIn()">
      <!-- 用户信息区：头像、昵称、手机号 -->
      <div class="pa-user">
        <div class="pa-avatar">
          <img v-if="avatarUrl" :src="avatarUrl" class="pa-avatar-img" alt="头像" />
          <span v-else class="pa-glyph">{{ avatarGlyph }}</span>
        </div>
        <div class="pa-user-info">
          <h3 class="pa-nick">{{ nick }}</h3>
          <p class="pa-phone">{{ phoneDisplay }}</p>
        </div>
      </div>

      <!-- 导航菜单：个人资料、我的报名、我的订单、我的收藏、收货地址 -->
      <ul class="pa-menu">
        <li v-for="m in menus" :key="m.to" class="pa-menu-item">
          <router-link
            :to="m.to"
            class="pa-link"
            :class="{ 'pa-active': m.to === active }"
          >
            <span class="pa-icon">{{ m.icon }}</span>
            <span class="pa-label">{{ m.label }}</span>
          </router-link>
        </li>
      </ul>

      <!-- 退出登录按钮 -->
      <div class="pa-logout-wrap">
        <button class="pa-logout" @click="onLogout">
          <span class="pa-logout-icon">⏻</span>
          <span class="pa-logout-label">退出登录</span>
        </button>
      </div>
    </template>

    <div v-else class="pa-guest">
      <!-- 未登录分支：提示登录并给出登录入口 -->
      <div class="pa-guest-avatar"><span class="pa-guest-glyph">客</span></div>
      <p class="pa-guest-title">您还未登录</p>
      <p class="pa-guest-desc">登录后可查看个人资料、报名课程、收藏作品</p>
      <button class="pa-guest-btn" @click="goLogin">立即登录</button>
      <router-link to="/" class="pa-guest-back">返回首页 ›</router-link>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { logout, isLoggedIn } from '@/store'
import { apiMe } from '@/api/auth'

// 当前路由对象：用于判断哪个菜单项处于激活状态
const route = useRoute()
const router = useRouter()

// 侧边栏展示的用户信息
const nick = ref('')
const phone = ref('')
const avatarUrl = ref('')

// 取昵称首字作为无头像时的占位字符
const avatarGlyph = computed(() => {
  const n = (nick.value || '').trim()
  return n ? n.charAt(0) : '客'
})

// 未绑定手机号时显示占位文案
const phoneDisplay = computed(() => {
  const p = (phone.value || '').trim()
  if (!p) return '未绑定手机'
  return p
})

// 从后端拉取当前用户信息，填充昵称、手机号和头像；未登录时不请求
async function loadMe() {
  if (!isLoggedIn()) return
  try {
    const data = await apiMe()
    nick.value = data.nick || data.name || data.username || ''
    phone.value = data.phone || ''
    avatarUrl.value = data.avatar || ''
  } catch (e) {
  }
}
onMounted(loadMe)

// 菜单配置：label 为文案，icon 为字形图标，to 为目标路由
const menus = [
  { label: '个人资料', icon: '人', to: '/profile' },
  { label: '我的报名', icon: '习', to: '/profile/enroll' },
  { label: '我的订单', icon: '物', to: '/profile/order' },
  { label: '我的收藏', icon: '藏', to: '/profile/favorite' },
  { label: '收货地址', icon: '址', to: '/profile/address' },
]

// 当前路径：与菜单项的 to 比较后决定高亮
const active = computed(() => route.path)

// ElMessageBox：ElMessageBox.confirm 是 element-plus 的确认框，返回 Promise：点确定走 then，点取消走 catch
// 退出登录：先二次确认，再调用 store 的 logout，最后回到登录页
function onLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await logout()
      router.push('/login')
    })
    .catch(() => {})
}

// 未登录时跳转登录页，并记录登录后要回到个人中心
function goLogin() {
  router.push({ path: '/login', query: { redirect: '/profile' } })
}
</script>

<style src="./ProfileAside.css"></style>
