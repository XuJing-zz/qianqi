<!-- 注册页：普通会员注册，校验账号、密码、昵称、姓名、手机号与邮箱后调用注册接口 -->
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

    <!-- 右侧注册表单区 -->
    <div class="lg-panel">
      <div class="lg-form-wrap">
        <h2 class="lg-title">注册账号</h2>
        <p class="lg-sub">注册普通会员，开启您的漆艺之旅</p>

        <!-- 注册表单：账号、密码、确认密码、昵称、姓名、手机号、邮箱 -->
        <form class="lg-form" @submit.prevent="submit">
          <label class="lg-field">
            <span class="lg-field-label">账号</span>
            <input
              v-model="form.username"
              type="text"
              class="lg-input"
              placeholder="请输入账号（至少 3 位）"
              maxlength="30"
              autocomplete="username"
            />
          </label>

          <label class="lg-field">
            <span class="lg-field-label">密码</span>
            <input
              v-model="form.password"
              type="password"
              class="lg-input"
              placeholder="请输入密码（6~32 位）"
              maxlength="32"
              autocomplete="new-password"
            />
          </label>

          <label class="lg-field">
            <span class="lg-field-label">确认密码</span>
            <input
              v-model="form.confirm"
              type="password"
              class="lg-input"
              placeholder="请再次输入密码"
              maxlength="32"
              autocomplete="new-password"
            />
          </label>

          <label class="lg-field">
            <span class="lg-field-label">昵称 <em class="lg-required">*</em></span>
            <input
              v-model="form.nick"
              type="text"
              class="lg-input"
              placeholder="请输入昵称（最多 20 字）"
              maxlength="20"
              autocomplete="nickname"
            />
          </label>

          <!-- 姓与名分开填写，提交时拼成完整姓名 -->
          <div class="lg-field-row">
            <label class="lg-field">
              <span class="lg-field-label">姓</span>
              <input
                v-model="form.last_name"
                type="text"
                class="lg-input"
                placeholder="请输入姓"
                maxlength="50"
                autocomplete="family-name"
              />
            </label>
            <label class="lg-field">
              <span class="lg-field-label">名</span>
              <input
                v-model="form.first_name"
                type="text"
                class="lg-input"
                placeholder="请输入名"
                maxlength="50"
                autocomplete="given-name"
              />
            </label>
          </div>

          <label class="lg-field">
            <span class="lg-field-label">手机号 <em class="lg-required">*</em></span>
            <input
              v-model="form.phone"
              type="text"
              class="lg-input"
              placeholder="请输入手机号"
              maxlength="11"
              autocomplete="tel"
            />
          </label>

          <label class="lg-field">
            <span class="lg-field-label">邮箱 <em class="lg-required">*</em></span>
            <input
              v-model="form.email"
              type="email"
              class="lg-input"
              placeholder="请输入邮箱"
              maxlength="50"
              autocomplete="email"
            />
          </label>

          <button type="submit" class="lg-btn lg-btn-solid" :disabled="submitting">
            {{ submitting ? '注册中...' : '注 册' }}
          </button>
        </form>

        <!-- 返回登录入口 -->
        <div class="lg-register-hint">
          已有账号？
          <router-link class="lg-register-link" to="/login">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、路由、消息提示、注册接口与品牌配置
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiRegister } from '@/api/auth'
import { brandLogo, brandGlyph, brandShort } from '@/store'

// 路由实例：注册成功后跳转到登录页
const router = useRouter()

// 注册表单数据：账号、密码、确认密码、昵称、姓、名、手机号、邮箱
const form = reactive({
  username: '',
  password: '',
  confirm: '',
  nick: '',
  last_name: '',
  first_name: '',
  phone: '',
  email: '',
})
// 是否正在提交，用于禁用按钮、防止重复注册
const submitting = ref(false)

/* 注册流程：逐项校验 → 组装参数（姓 + 名 合成姓名）→ 调用注册接口 → 成功跳登录页 */
async function submit() {
  // 账号：必填，长度 3~30 位
  const username = form.username.trim()
  if (!username) {
    ElMessage.warning('请输入账号')
    return
  }
  if (username.length < 3 || username.length > 30) {
    ElMessage.warning('账号长度需在 3~30 位之间')
    return
  }
  if (!/^[\p{L}\p{N}_.@+-]+$/u.test(username)) {
    ElMessage.warning('账号仅可包含字母、数字、下划线、中划线、点与中文，且不能包含空格')
    return
  }
  // 密码：必填，长度 6~32 位，且首尾不能有空格
  if (!form.password) {
    ElMessage.warning('请输入密码')
    return
  }
  if (form.password.length < 6 || form.password.length > 32) {
    ElMessage.warning('密码长度需为 6~32 位')
    return
  }
  if (form.password !== form.password.trim()) {
    ElMessage.warning('密码不能以空格开头或结尾')
    return
  }
  // 确认密码：必填，且必须与密码完全一致
  if (!form.confirm) {
    ElMessage.warning('请输入确认密码')
    return
  }
  if (form.confirm !== form.confirm.trim()) {
    ElMessage.warning('确认密码不能以空格开头或结尾')
    return
  }
  if (form.password !== form.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  // 昵称：必填，最多 20 个字符
  const nick = form.nick.trim()
  if (!nick) {
    ElMessage.warning('请输入昵称')
    return
  }
  if (nick.length > 20) {
    ElMessage.warning('昵称不能超过 20 个字符')
    return
  }
  // 姓与名需同时填写或同时留空，避免只填一半
  if (form.last_name.trim() && !form.first_name.trim()) {
    ElMessage.warning('请同时填写名')
    return
  }
  if (!form.first_name.trim() && form.last_name.trim()) {
    ElMessage.warning('请同时填写姓')
    return
  }
  // 手机号：必填，必须是 1 开头的 11 位数字
  if (!form.phone.trim()) {
    ElMessage.warning('请输入手机号')
    return
  }
  if (!/^1\d{10}$/.test(form.phone.trim())) {
    ElMessage.warning('请输入正确的 11 位手机号')
    return
  }
  // 邮箱：必填，需符合基础邮箱格式
  if (!form.email.trim()) {
    ElMessage.warning('请输入邮箱')
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }

  // 姓在前、名在后拼成完整姓名；两者都为空时传空字符串
  const ln = form.last_name.trim()
  const fn = form.first_name.trim()
  const fullName = (ln && fn) ? (ln + fn) : ''

  submitting.value = true
  try {
    // 调用注册接口；成功后统一跳转登录页
    await apiRegister({
      username,
      password: form.password,
      nick: form.nick.trim(),
      name: fullName,
      first_name: fn,
      last_name: ln,
      phone: form.phone.trim(),
      email: form.email.trim(),
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.message || '注册失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style src="./Login.css"></style>
