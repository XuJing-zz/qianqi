<!-- 个人中心 · 课程报名支付页：订单信息、扫码支付、支付方式切换与模拟支付 -->
<template>
  <div class="pay-page">
    <Nav />

    <!-- 课程存在时显示确认报名主体 -->
    <div class="py-wrap" v-if="course">
      <button class="py-back" @click="goBack">‹ 返回课程详情</button>

      <header class="py-head">
        <h1 class="py-title">确认报名</h1>
        <span class="py-en">CHECKOUT</span>
      </header>

      <div class="py-layout">
        <!-- 左侧：订单信息与金额明细 -->
        <section class="py-card py-order">
          <h2 class="py-card-title">订单信息</h2>

          <div class="py-course">
            <div class="py-course-cover">
              <span class="py-course-glyph">{{ course.glyph }}</span>
            </div>
            <div class="py-course-body">
              <h3 class="py-course-name">{{ course.name }}</h3>
              <p class="py-course-maker">{{ course.teacher }} · {{ course.craft }} · {{ course.stage }}</p>
            </div>
          </div>

          <dl class="py-meta">
            <div class="py-meta-row"><dt>订单编号</dt><dd>{{ orderNo }}</dd></div>
            <div class="py-meta-row"><dt>报名时间</dt><dd>{{ nowText }}</dd></div>
            <div class="py-meta-row"><dt>支付方式</dt><dd>{{ current.name }}</dd></div>
          </dl>

          <div class="py-price">
            <div class="py-price-row"><span>课程费用</span><span>¥{{ course.priceNum }}</span></div>
            <div class="py-price-row"><span>优惠</span><span class="py-free">-¥0.00</span></div>
            <div class="py-price-row py-price-total">
              <span>应付金额</span>
              <span><em>¥</em>{{ course.priceNum }}</span>
            </div>
          </div>
        </section>

        <!-- 右侧：扫码支付面板 -->
        <section class="py-card py-pay">
          <h2 class="py-card-title">扫码支付</h2>

          <div class="py-tabs">
            <button
              v-for="m in methods"
              :key="m.key"
              class="py-tab"
              :class="{ 'py-tab-active': method === m.key }"
              :style="method === m.key ? { color: m.accent, borderColor: m.accent } : null"
              @click="pick(m.key)"
            >
              <span class="py-tab-dot" :style="{ background: m.accent }"></span>
              {{ m.name }}
            </button>
          </div>

          <div class="py-qr" :style="{ '--accent': current.accent }">
            <img :src="current.qr" :alt="current.name + '收款码'" class="py-qr-img" />
            <div v-if="expired" class="py-qr-expired">
              <p>二维码已过期</p>
              <button class="py-btn" @click="reset">刷新二维码</button>
            </div>
          </div>

          <p class="py-countdown">
            <template v-if="!expired">支付剩余 <b>{{ countdownText }}</b></template>
            <template v-else>请刷新二维码后重新支付</template>
          </p>

          <p class="py-scan-tip">打开{{ current.name }}「扫一扫」，扫描二维码完成支付</p>

          <button class="py-btn py-btn-solid py-pay-btn" :disabled="paying || expired" @click="doPay">
            {{ paying ? '支付中...' : '我已完成支付' }}
          </button>

          <p class="py-tip">演示环境：扫码不会真实扣款，点击按钮即模拟支付成功</p>
        </section>
      </div>
    </div>

    <div v-else class="py-empty">
      <!-- 空状态：路由中的课程 ID 找不到对应课程 -->
      <p class="py-empty-text">未找到该课程</p>
      <button class="py-btn" @click="goBack">返回课程列表</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import { courses, ensureCourses, addEnrollment, addOrder, isLoggedIn, enrollmentOf, authState, homeOf } from '@/store'

const route = useRoute()
const router = useRouter()

// 进入页面时确保课程数据已加载，失败时静默处理
onMounted(() => {
  ensureCourses().catch(() => {})
})

// 根据路由中的课程 ID 查找课程；找不到时页面显示空状态
const course = computed(() => {
  const id = Number(route.params.courseId)
  return courses.find((c) => c.id === id) || null
})

// 支付方式：二维码图片放在 public/imgs/pay 下，accent 用于标签和二维码边框
const methods = [
  { key: 'wechat', name: '微信支付', accent: '#2aae67', qr: '/imgs/pay/qr-wechat.png' },
  { key: 'alipay', name: '支付宝', accent: '#1677ff', qr: '/imgs/pay/qr-alipay.png' },
]

const method = ref('wechat')
const current = computed(() => methods.find((m) => m.key === method.value) || methods[0])

// 订单编号与下单时间，仅用于页面展示
const orderNo = 'QX' + String(Date.now()).slice(-12)
const nowText = ref(new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-'))

// 支付倒计时：默认 15 分钟，归零后展示过期遮罩
const left = ref(15 * 60)
let timer = null
const expired = computed(() => left.value <= 0)
const countdownText = computed(() => {
  const m = String(Math.floor(left.value / 60)).padStart(2, '0')
  const s = String(left.value % 60).padStart(2, '0')
  return m + ':' + s
})

function startTimer() {
  clearInterval(timer)
  timer = setInterval(() => {
    if (left.value > 0) left.value -= 1
  }, 1000)
}

// 切换支付方式或刷新二维码时重置倒计时
function pick(key) {
  method.value = key
  reset()
}

function reset() {
  left.value = 15 * 60
  startTimer()
}

onMounted(startTimer)
onBeforeUnmount(() => clearInterval(timer))

// 是否正在提交支付
const paying = ref(false)

/* 支付报名流程：
   1. 校验课程、登录状态、用户角色和是否重复报名；
   2. 先创建报名记录，再创建订单；
   3. 成功后提示并跳转到“我的报名”，失败时提示后端返回的原因。 */
async function doPay() {
  if (!course.value) return
  if (!isLoggedIn()) {
    ElMessage.warning('请先登录后再报名')
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  if (authState.user?.role !== 'user') {
    ElMessage.warning('仅普通用户可报名课程')
    router.replace(homeOf(authState.user?.role))
    return
  }
  const en = enrollmentOf(course.value.id)
  if (en && en.status !== 'rejected') {
    const tip = en.status === 'review' ? '报名正在等待管理员审核，无需重复提交' : '你已录取该课程，无需重复支付'
    ElMessage.info(tip)
    router.push('/profile/enroll')
    return
  }
  paying.value = true
  try {
    await addEnrollment({
      courseId: course.value.id,
      name: course.value.name,
      teacher: course.value.teacher,
      craft: course.value.craft,
      stage: course.value.stage,
      price: course.value.priceNum,
    })
    await addOrder({
      courseId: course.value.id,
      courseName: course.value.name,
      price: course.value.priceNum,
      payMethod: current.value.name,
    })
    ElMessage.success('支付成功，报名已提交，请等待管理员确认录取')
    setTimeout(() => {
      router.push('/profile/enroll')
    }, 600)
  } catch (e) {
    const msg = (e && e.data && (e.data.detail || e.data.msg)) || (e && e.message) || '下单失败，请重试'
    ElMessage.error('支付未完成：' + msg)
  } finally {
    paying.value = false
  }
}

// 返回上一页：有课程时回课程详情，否则回课程列表
function goBack() {
  if (course.value) {
    router.push('/course/' + course.value.id)
  } else {
    router.push('/course')
  }
}
</script>

<style src="./Pay.css"></style>
