<!-- 联系我们页：展示联系方式、咨询事项，并提供留言表单 -->
<template>
  <div class="contact-page">
    <!-- 全站顶部导航 -->
    <Nav />

    <!-- 首屏：页面标题与标语 -->
    <header class="ct-hero">
      <span class="ct-hero-seal">联</span>
      <h1 class="ct-hero-title">联系我们</h1>
      <span class="ct-hero-en">CONTACT US</span>
      <div class="ct-hero-line"></div>
      <p class="ct-hero-note">合作、咨询、反馈，欢迎来信</p>
    </header>

    <div class="ct-wrap">
      <!-- 联系方式：电话、邮箱、地址、公众号等信息卡片 -->
      <section class="ct-contact">
        <div class="ct-section-head">
          <h2 class="ct-section-cn">联系方式</h2>
          <span class="ct-section-en">REACH US</span>
        </div>
        <div class="ct-info-grid">
          <div v-for="c in contacts" :key="c.label" class="ct-info">
            <span class="ct-info-glyph">{{ c.glyph }}</span>
            <div class="ct-info-body">
              <span class="ct-info-label">{{ c.label }}</span>
              <span class="ct-info-value">{{ c.value }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 联系事项：商务合作、课程咨询、作品收藏、意见建议 -->
      <section class="ct-section">
        <div class="ct-section-head">
          <h2 class="ct-section-cn">联系我们事项</h2>
          <span class="ct-section-en">SUBJECT</span>
        </div>
        <div class="ct-subjects">
          <div v-for="s in subjects" :key="s.title" class="ct-subject">
            <span class="ct-subject-glyph">{{ s.glyph }}</span>
            <h3 class="ct-subject-title">{{ s.title }}</h3>
            <p class="ct-subject-desc">{{ s.desc }}</p>
          </div>
        </div>
      </section>

      <!-- 留言表单：称呼、事项、内容，提交时调用后端接口 -->
      <section class="ct-section">
        <div class="ct-section-head">
          <h2 class="ct-section-cn">给我们留言</h2>
          <span class="ct-section-en">MESSAGE</span>
        </div>
        <div class="ct-form">
          <label class="ct-field">
            <span class="ct-field-label">您的称呼</span>
            <input v-model="form.name" type="text" class="ct-input" placeholder="怎么称呼您" />
          </label>
          <label class="ct-field">
            <span class="ct-field-label">留言事项</span>
            <select v-model="form.subject" class="ct-input ct-select">
              <option value="">请选择（可选）</option>
              <option v-for="s in subjects" :key="s.title" :value="s.title">{{ s.title }}</option>
            </select>
          </label>
          <label class="ct-field">
            <span class="ct-field-label">留言内容</span>
            <textarea v-model="form.message" class="ct-input ct-textarea" rows="5" placeholder="请写下您想说的话"></textarea>
          </label>
          <div class="ct-form-foot">
            <p class="ct-form-tip">提交后，我们将在 1-2 个工作日内回复您</p>
            <button class="ct-btn ct-btn-solid" :disabled="submitting" @click="submit">
              {{ submitting ? '提交中...' : '提交留言' }}
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import { authState } from '@/store'
import { submitContactMessage } from '@/api/contact'

/* 联系方式静态数据 */
const contacts = [
  { glyph: '话', label: '客服电话', value: '400-000-0000' },
  { glyph: '邮', label: '联系邮箱', value: 'contact@qianqi.com' },
  { glyph: '址', label: '工作室地址', value: '四川省成都市 · 千漆非遗技艺传习所' },
  { glyph: '信', label: '微信 / 公众号', value: '千漆 QianQi' },
]

/* 留言事项选项，同时作为下拉框和事项卡片的数据源 */
const subjects = [
  { glyph: '合', title: '商务合作', desc: '品牌联名、渠道合作、企业定制' },
  { glyph: '课', title: '课程咨询', desc: '课程报名、团体体验、大师课预约' },
  { glyph: '藏', title: '作品收藏', desc: '文创作品详情、定制、收藏咨询' },
  { glyph: '建', title: '意见建议', desc: '平台反馈、功能建议、投诉' },
]

/* 留言表单数据：称呼、事项与内容 */
const form = reactive({
  name: '',
  subject: '',
  message: '',
})
// 提交状态：为 true 时按钮显示「提交中...」并禁用，防止重复提交
const submitting = ref(false)

/* 已登录时用账号昵称预填称呼，避免用户重复输入 */
function prefillName() {
  if (!form.name && authState.user) {
    form.name = authState.user.name || authState.user.username || ''
  }
}
prefillName()

/* 提交留言：先做前端校验，再调用接口，成功后清空表单并恢复预填称呼 */
async function submit() {
  const name = form.name.trim()
  const subject = form.subject
  const message = form.message.trim()

  if (!name) {
    ElMessage.warning('请填写您的称呼')
    return
  }
  if (!message) {
    ElMessage.warning('请填写留言内容')
    return
  }
  if (name.length > 50) {
    ElMessage.warning('称呼不能超过 50 个字符')
    return
  }

  submitting.value = true
  try {
    // 调用后端留言接口；成功后提示并重置表单
    await submitContactMessage({ name, subject, message })
    ElMessage.success('留言已提交，我们会尽快处理')
    Object.assign(form, { name: '', subject: '', message: '' })
    prefillName()
  } catch (e) {
    ElMessage.error((e && e.message) || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style src="./Contact.css"></style>
