<!-- 课程详情页：展示课程介绍、大纲、授课传承人、报名须知与报名入口 -->
<template>
  <div class="course-detail-page">
    <!-- 课程首屏：有视频时自动静音循环播放，否则显示封面/字形 -->
    <div
      v-if="course"
      class="detail-hero"
      :class="{ 'hero-plain': !course.cover }"
      :style="coverStyle(course)"
    >
      <video
        v-if="course.video"
        class="hero-video"
        :src="course.video"
        autoplay
        muted
        loop
        playsinline
      ></video>
      <span v-else class="hero-glyph">{{ course.glyph }}</span>
      <!-- 封面上的课程档位、名称与授课人信息 -->
      <div class="hero-mask">
        <div class="hero-badges">
          <span class="badge-stage" :class="'cd-stage-' + stageClass(course.stage)">{{ course.stage }}</span>
          <span v-if="course.flag" class="cd-badge-flag">{{ course.flag }}</span>
        </div>
        <h1 class="hero-name">{{ course.name }}</h1>
        <p class="hero-maker">
          <span class="cd-verified">✓ 已认证</span>{{ teacherTitle(course) }} · {{ course.teacher }}
        </p>
      </div>
    </div>

    <Nav />

    <div class="cd-detail-wrap" v-if="course">
      <!-- 返回课程列表 -->
      <button class="cd-back-btn" @click="goBack">‹ 返回课程</button>

      <div class="cd-detail-main">
        <!-- 左侧内容区：简介、大纲、传承人、报名须知 -->
        <div class="detail-left">
          <!-- 课程简介 -->
          <section class="cd-block">
            <div class="cd-section-head">
              <h2 class="cd-section-cn">课程简介</h2>
              <span class="cd-section-en">INTRO</span>
            </div>
            <p class="intro-desc">{{ course.desc }}</p>
          </section>

          <!-- 课程大纲：按 lessons 数组逐课渲染 -->
          <section class="cd-block">
            <div class="cd-section-head">
              <h2 class="cd-section-cn">课程大纲</h2>
              <span class="cd-section-en">SYLLABUS</span>
            </div>
            <div class="syllabus">
              <div v-for="(les, i) in course.lessons" :key="i" class="lesson">
                <span class="lesson-num">{{ '壹贰叁肆伍陆柒捌玖拾'[i] || (i + 1) }}课</span>
                <div class="lesson-body">
                  <h4 class="lesson-title">{{ les.title }}</h4>
                  <p class="lesson-desc">{{ les.desc }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- 授课传承人卡片，可跳转到传承人主页 -->
          <section class="cd-block">
            <div class="cd-section-head">
              <h2 class="cd-section-cn">授课传承人</h2>
              <span class="cd-section-en">MASTER</span>
            </div>
            <div class="cd-master-card">
              <div class="cd-master-avatar">
                <span class="cd-master-glyph">{{ course.teacher.charAt(0) }}</span>
              </div>
              <div class="cd-master-body">
                <h4 class="cd-master-name">{{ course.teacher }}</h4>
                <p class="cd-master-title">{{ teacherTitle(course) }} · {{ course.craft }}传承人</p>
                <p class="cd-master-bio">{{ course.masterBio || '深耕' + (course.craft || '漆') + '技艺多年，长期面向爱好者开设课程。' }}</p>
                <button class="cd-master-link" @click="goInheritor">查看传承人主页 ›</button>
              </div>
            </div>
          </section>

          <!-- 报名须知：逐条展示注意事项 -->
          <section v-if="course.notices && course.notices.length" class="cd-block">
            <div class="cd-section-head">
              <h2 class="cd-section-cn">报名须知</h2>
              <span class="cd-section-en">NOTICE</span>
            </div>
            <ul class="notice-list">
              <li v-for="(n, i) in course.notices" :key="i" class="notice-item">{{ n }}</li>
            </ul>
          </section>
        </div>

        <!-- 右侧报名卡：价格、课程规格、名额与报名按钮 -->
        <div class="detail-right">
          <div class="enroll-card">
            <div class="enroll-price">
              <span class="enroll-price-num">{{ course.price }}</span>
              <span class="enroll-price-note">材料全含</span>
            </div>
            <div class="enroll-spec">
              <div class="es-row"><span class="es-label">课程档位</span><span class="es-val">{{ course.stage }}</span></div>
              <div class="es-row"><span class="es-label">难度</span><span class="es-val">{{ course.difficulty }}</span></div>
              <div class="es-row"><span class="es-label">课时</span><span class="es-val">{{ course.duration }}</span></div>
              <div class="es-row"><span class="es-label">授课地</span><span class="es-val">{{ course.region }}</span></div>
              <div v-if="course.location" class="es-row"><span class="es-label">上课地点</span><span class="es-val">{{ course.location }}</span></div>
              <div class="es-row"><span class="es-label">名额</span><span class="es-val">{{ seatText(course) }}</span></div>
              <div class="es-row"><span class="es-label">所属技艺</span><span class="es-val">{{ course.craft }}</span></div>
            </div>
            <button class="cd-btn" @click="enroll(course)">
              {{ enrollBtn }}
            </button>
            <p class="enroll-tip">报名后由传承人确认，材料费用已含</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 课程不存在时的空状态 -->
    <div v-else class="cd-detail-empty">
      <p class="cd-empty-text">未找到该课程</p>
      <button class="cd-btn" @click="goBack">返回课程列表</button>
    </div>
  </div>
</template>

<script setup>
/* 课程详情：根据路由 id 找到课程，并处理报名状态与跳转 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import { courses, ensureCourses, inheritors, loadInheritors, isLoggedIn, enrollmentOf, isEnrolled, authState, homeOf, loadEnrollments } from '@/store'

const route = useRoute()
const router = useRouter()

// 加载课程与传承人数据；已登录用户额外加载报名记录，用于判断报名状态
onMounted(() => {
  const jobs = [ensureCourses(), loadInheritors()]
  if (isLoggedIn()) jobs.push(loadEnrollments())
  // 等所有加载任务结束，某个请求失败也不影响其他数据
  Promise.allSettled(jobs)
})

/* 当前课程：把路由参数转成数字后查找，找不到返回 null */
const course = computed(() => {
  const id = Number(route.params.id)
  return courses.find((c) => c.id === id) || null
})

/* 当前用户对该课程的报名记录 */
const enrollment = computed(() => (course.value ? enrollmentOf(course.value.id) : null))
/* 报名按钮文案：根据是否存在报名记录及其审核状态变化 */
const enrollBtn = computed(() => {
  const e = enrollment.value
  if (!e) return '立即报名'
  if (e.status === 'review') return '已报名 · 审核中'
  if (e.status === 'rejected') return '重新报名'
  return '已报名 · 进入学习'
})

/* 名额文案：有人报名时显示已招人数，否则只显示总名额 */
function seatText(c) {
  const en = Number(c.enrolled ?? 0)
  return en > 0 ? `已招 ${en} / ${c.capacity} 席` : `仅 ${c.capacity} 席`
}

/* 课程档位到 CSS 类名后缀的映射 */
function stageClass(s) {
  return s === '体验工作坊' ? 'workshop' : s === '系统课程' ? 'course' : 'master'
}

/* 根据传承人级别返回完整头衔 */
function teacherTitle(c) {
  const map = { 国家级: '国家级非遗传承人', 省级: '省级非遗传承人', 市级: '市级非遗传承人' }
  return map[c.level] || '非遗传承人'
}

/* 有封面时生成背景图样式 */
function coverStyle(c) {
  if (c.cover) {
    return { backgroundImage: 'url(' + c.cover + ')' }
  }
  return {}
}

function goDetail(id) {
  router.push('/course/' + id)
}

function goBack() {
  router.push('/course')
}

/* 按授课人姓名查找传承人，找到后进入其主页，否则回到传承人列表 */
function goInheritor() {
  if (!course.value) return
  const master = inheritors.find((m) => m.name === course.value.teacher)
  if (master) {
    router.push('/inheritor/' + master.id)
  } else {
    router.push('/inheritor')
  }
}

/* 报名入口：依次处理未登录、角色不符、已有报名等分支，最后进入支付流程 */
function enroll(c) {
  // 未登录先跳到登录页，登录后回到当前课程
  if (!isLoggedIn()) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  // 只有普通学员账号可以报名，其他角色引导回各自首页
  if (authState.user?.role !== 'user') {
    ElMessage.warning('仅普通用户账号可报名课程，请先退出并用学员账号登录')
    router.replace(homeOf(authState.user?.role))
    return
  }
  const e = enrollmentOf(c.id)
  if (e) {
    // 审核中：提示等待，并跳到报名记录页
    if (e.status === 'review') {
      ElMessage.info('报名正在等待管理员审核，录取后可进入学习')
      router.push('/profile/enroll')
      return
    }
    // 已通过：直接进入学习页
    if (e.status !== 'rejected') {
      router.push('/learn/' + c.id)
      return
    }
    // 已被拒绝则继续往下走，重新报名
  }
  // 尚未报名或需要重新报名：进入支付页
  router.push('/pay/' + c.id)
}
</script>

<style src="./CourseDetail.css"></style>
