<!-- 登录页：账号密码登录，支持已登录提示、演示账号快速填充与按角色跳转 -->
<template>
  <div class="login-page">
    <!-- 左侧品牌展示区：LOGO、平台名称与标语 -->
    <div class="lg-brand">
      <div class="lg-brand-inner">
        <span class="lg-brand-seal">
          <img v-if="brandLogo" :src="brandLogo" class="lg-brand-seal-img" alt="LOGO" />
          <template v-else>{{ brandGlyph }}</template>
        </span>
        <h1 class="lg-brand-name">{{ brandShort }}</h1>
        <span class="lg-brand-en">QIANQI · 非遗漆器技艺传承平台</span>
        <div class="lg-brand-line"></div>
        <p class="lg-brand-slogan">以漆为媒，让千年技艺活在当下</p>
      </div>
    </div>

    <!-- 右侧登录表单区 -->
    <div class="lg-panel">
      <div class="lg-form-wrap">
        <h2 class="lg-title">欢迎回来</h2>
        <p class="lg-sub">登录后进入您的工作站</p>
        <!-- 已登录提示：重新登录会切换到所选账号 -->
        <p v-if="loggedIn" class="lg-switch-tip">
          当前已登录：{{ currentName }} · 重新登录将切换到所选账号
        </p>

        <!-- 登录表单：账号、密码与提交按钮 -->
        <form class="lg-form" @submit.prevent="submit">
          <label class="lg-field">
            <span class="lg-field-label">账号</span>
            <input
              v-model="form.username"
              type="text"
              class="lg-input"
              placeholder="请输入账号"
              autocomplete="username"
            />
          </label>

          <label class="lg-field">
            <span class="lg-field-label">密码</span>
            <input
              v-model="form.password"
              type="password"
              class="lg-input"
              placeholder="请输入密码"
              autocomplete="current-password"
            />
          </label>

          <button type="submit" class="lg-btn lg-btn-solid" :disabled="submitting">
            {{ submitting ? '登录中...' : '登 录' }}
          </button>
        </form>

        <!-- 注册入口 -->
        <div class="lg-register-hint">
          还没有账号？
          <router-link class="lg-register-link" to="/register">注册</router-link>
        </div>

        <!-- 演示账号：点击后自动填充账号和默认密码 -->
        <div class="lg-demo">
          <p class="lg-demo-title">演示账号（点击自动填充）</p>
          <div class="lg-demo-list">
            <button
              v-for="a in demoAccounts"
              :key="a.username"
              class="lg-demo-item"
              @click="fill(a)"
            >
              <span class="lg-demo-role">{{ a.roleLabel }}</span>
              <span class="lg-demo-user">{{ a.username }}</span>
              <span class="lg-demo-arrow">→</span>
            </button>
          </div>
          <p class="lg-demo-pwd">密码均为 : 123456</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、路由、消息提示、登录 / 落地页逻辑与品牌配置
import { reactive, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, resolveLanding, authState, isLoggedIn, brandLogo, brandGlyph, brandShort } from '@/store'

// 路由器与当前路由：登录成功后读取 redirect 参数并完成跳转
const router = useRouter()
const route = useRoute()

// 是否已登录，用于顶部切换账号提示
const loggedIn = computed(() => isLoggedIn())
// 当前登录用户的显示名，优先昵称，其次姓名、账号
const currentName = computed(() => {
  const u = authState.user
  return (u && (u.nick || u.name || u.username)) || ''
})

// 登录表单数据：账号与密码
const form = reactive({
  username: '',
  password: '',
})
// 是否正在提交，防止重复点击
const submitting = ref(false)

// 演示账号配置：账号、角色名称
const demoAccounts = [
  { username: 'user01', roleLabel: '普通用户' },
  { username: 'heritage01', roleLabel: '传承人' },
  { username: 'admin', roleLabel: '管理员' },
]

/* 点击演示账号时，填充账号和统一演示密码 */
function fill(a) {
  form.username = a.username
  form.password = '123456'
}

// @submit.prevent：表单上的 @submit.prevent 会阻止浏览器默认的提交刷新，改由 submit 处理
/* 登录流程：校验账号密码 → 调用 login → 失败提示 → 成功后按角色和 redirect 跳转 */
async function submit() {
  if (!form.username.trim()) {
    ElMessage.warning('请输入账号')
    return
  }
  if (!form.password) {
    ElMessage.warning('请输入密码')
    return
  }

  submitting.value = true
  const res = await login(form.username.trim(), form.password)
  submitting.value = false
  if (!res.ok) {
    ElMessage.error(res.msg)
    return
  }
  ElMessage.success('登录成功，欢迎回来')
  // resolveLanding 根据角色决定落地页；若地址带 redirect 参数则优先回到原页面
  router.replace(resolveLanding(res.role, route.query.redirect))
}
</script>

<style src="./Login.css"></style>
