<!-- 关于页：介绍千漆平台的定位、创办理念、服务内容与数据里程碑 -->
<template>
  <div class="about-page">
    <!-- 全站顶部导航 -->
    <Nav />

    <!-- 首屏：页面标题、品牌印章与标语 -->
    <header class="ab-hero">
      <span class="ab-hero-seal">漆</span>
      <h1 class="ab-hero-title">关于千漆</h1>
      <span class="ab-hero-en">ABOUT QIANQI</span>
      <div class="ab-hero-line"></div>
      <p class="ab-hero-note">以漆为媒，让千年技艺活在当下</p>
    </header>

    <div class="ab-wrap">
      <!-- 平台定位：左侧介绍文案，右侧「千」字印章装饰 -->
      <section class="ab-intro">
        <div class="ab-intro-text">
          <h2 class="ab-section-cn">平台定位</h2>
          <span class="ab-section-en">POSITION</span>
          <p class="ab-lead">
            千漆，是一个专注漆器技艺传承与文创推广的非遗数字化平台。
            我们连接技艺精湛的传承人与热爱东方美学的普通人，
            以系统课程传承技艺，以文创作品进入生活。
          </p>
          <p class="ab-body">
            生漆，取自漆树，是华夏大地上使用逾七千年的天然材料。
            髹漆、雕漆、螺钿、描金、百宝嵌……一道道工序，皆是时间与心手的沉淀。
            千漆希望这些古老的技艺，不再只是博物馆里的展品，
            而能回到餐桌、书案与腕间，成为可触、可用、可传承的日常。
          </p>
        </div>
        <div class="ab-intro-seal">
          <span class="ab-seal-glyph">千</span>
          <span class="ab-seal-caption">守 艺</span>
        </div>
      </section>

      <!-- 创办理念：循环渲染 values 中的三张理念卡片 -->
      <section class="ab-section">
        <div class="ab-section-head">
          <h2 class="ab-section-cn">创办理念</h2>
          <span class="ab-section-en">PHILOSOPHY</span>
        </div>
        <div class="ab-values">
          <div v-for="v in values" :key="v.title" class="ab-value">
            <span class="ab-value-glyph">{{ v.glyph }}</span>
            <h3 class="ab-value-title">{{ v.title }}</h3>
            <p class="ab-value-desc">{{ v.desc }}</p>
          </div>
        </div>
      </section>

      <!-- 服务内容：循环渲染 services 中的三项服务 -->
      <section class="ab-section">
        <div class="ab-section-head">
          <h2 class="ab-section-cn">我们能做什么</h2>
          <span class="ab-section-en">WHAT WE DO</span>
        </div>
        <div class="ab-do">
          <div v-for="d in services" :key="d.title" class="ab-do-item">
            <div class="ab-do-head">
              <span class="ab-do-num">{{ d.num }}</span>
              <h3 class="ab-do-title">{{ d.title }}</h3>
            </div>
            <p class="ab-do-desc">{{ d.desc }}</p>
          </div>
        </div>
      </section>

      <!-- 数据里程碑：循环渲染 stats 中的演示统计数据 -->
      <section class="ab-section ab-stats">
        <div class="ab-section-head">
          <h2 class="ab-section-cn">一路走来</h2>
          <span class="ab-section-en">MILESTONES</span>
        </div>
        <div class="ab-stat-grid">
          <div v-for="s in stats" :key="s.label" class="ab-stat">
            <span class="ab-stat-num">{{ s.num }}</span>
            <span class="ab-stat-label">{{ s.label }}</span>
          </div>
        </div>
        <p class="ab-stats-note">* 数据为演示数据，随平台运营持续更新</p>
      </section>

      <!-- 底部行动区：引导用户前往联系页 -->
      <section class="ab-cta">
        <p class="ab-cta-title">想了解更多？</p>
        <p class="ab-cta-sub">合作、商务、意见建议，欢迎联系我们</p>
        <button class="ab-btn ab-btn-solid" @click="goContact">联系我们</button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'

// 路由实例：用于「联系我们」按钮跳转
const router = useRouter()

/* 创办理念：真、传、用三个关键词，供模板循环渲染 */
const values = [
  { glyph: '真', title: '守真', desc: '材料真、工序真、传承人真，拒绝以化工漆冒充天然生漆' },
  { glyph: '传', title: '传习', desc: '以课程与师徒相传，让技艺可学、可练、可成' },
  { glyph: '用', title: '致用', desc: '让漆器回到日常，成为可亲可近的生活之物' },
]

/* 平台提供的三类服务 */
const services = [
  { num: '壹', title: '技艺教学', desc: '体验课·系统课·大师亲授，三位一体体系化传承漆器技艺' },
  { num: '贰', title: '文创推广', desc: '策展式展示传承人作品，让东方美学被更多人看见、收藏' },
  { num: '叁', title: '传承人扶持', desc: '为传承人提供展示、教学与销售的数字阵地' },
]

/* 平台里程碑演示数据（页面上已注明为演示数据） */
const stats = [
  { num: '8+', label: '认证传承人' },
  { num: '10+', label: '体系化课程' },
  { num: '12+', label: '文创作品' },
  { num: '5', label: '技艺门类' },
]

/* 跳转到「联系我们」页面 */
function goContact() {
  router.push('/contact')
}
</script>

<style src="./About.css"></style>
