<!-- 首页：首屏开篇、数据概览、技艺档案拼贴、传承人 3D 环形展示与课程入口 -->
<template>
  <div class="home">

    <!-- 首屏开篇：平台标语与「入卷 / 传人」快捷锚点 -->
    <section class="opening">
      <div class="opening-grid">
        <div class="opening-title">
          <span class="seal">非遗</span>
          <h1 class="opening-main">漆<br />承<br />千<br />载</h1>
        </div>
        <div class="opening-text">
          <p class="opening-poem">髹漆成器，历千年而不朽；</p>
          <p class="opening-poem">匠心传灯，承一脉而不息。</p>
          <div class="opening-line"></div>
          <p class="opening-note">
            中国漆器非物质文化遗产·数字化传承平台
          </p>
          <div class="opening-actions">
            <a class="btn-solid" href="#archives">入 卷</a>
            <a class="btn-void" href="#masters">传 人</a>
          </div>
        </div>
      </div>
    </section>

    <Nav />

    <!-- 过渡文案区 -->
    <section class="prelude">
      <p class="prelude-text">
        漆，取于木，结于器。<br />
        七千年髹饰，三千年成器。
      </p>
    </section>

    <!-- 数据概览：技艺档案、传承人、课程、作品的已发布数量 -->
    <section class="scroll" id="archives">
      <div class="scroll-num" v-for="s in stats" :key="s.label">
        <div class="scroll-num-val">{{ s.num }}</div>
        <div class="scroll-num-label">{{ s.label }}</div>
      </div>
    </section>

    <!-- 技艺档案拼贴：根据 LAYOUT 配置做大小不一的网格排布，滚动进入时触发动画 -->
    <section class="craft">
      <h2 class="craft-title">技 艺 档 案</h2>
      <span class="craft-en">CRAFT ARCHIVES</span>
      <div class="craft-list">
        <router-link
          class="craft-item"
          v-for="a in archives"
          :key="a.id"
          :to="a.to"
          :class="{ 'craft-tall': a.r >= 3, 'craft-hasimg': !!a.image }"
          :style="craftStyle(a)"
        >
          <div v-if="a.image" class="craft-scrim"></div>
          <div v-else class="craft-glyph">{{ a.glyph }}</div>
          <div class="craft-info" :class="{ 'craft-info-img': a.image }">
            <h3 class="craft-name" :class="{ 'craft-name-img': a.image }">{{ a.name }}</h3>
            <p v-if="!a.image" class="craft-desc">{{ a.desc }}</p>
            <span class="craft-tag" :class="{ 'craft-tag-img': a.image }">{{ a.tag }}</span>
          </div>
        </router-link>
      </div>
      <div class="craft-more">
        <router-link class="craft-more-btn" to="/archive">查看更多技艺</router-link>
      </div>
    </section>

    <!-- 传承人环形展台：用 rotateY + translateZ 把卡片排成一个 3D 圆环，可左右旋转 -->
    <section class="masters" id="masters">
      <h2 class="masters-title">匠 心 传 人</h2>
      <div class="masters-stage">
        <div class="masters-ring" :style="{ transform: 'rotateY(' + angle + 'deg)' }">
          <router-link
            class="master"
            v-for="(m, i) in masters"
            :key="m.id"
            :to="m.to"
            :style="{ transform: 'rotateY(' + (i * seg) + 'deg) translateZ(' + radius + 'px)' }"
          >
            <div class="master-glyph">{{ m.glyph }}</div>
            <div class="master-name">{{ m.name }}</div>
            <div class="master-role">{{ m.title }}</div>
          </router-link>
        </div>
        <button class="ring-btn prev" @click="prev">‹</button>
        <button class="ring-btn next" @click="next">›</button>
      </div>
      <div class="masters-more">
        <router-link class="masters-more-btn" to="/inheritor">查看更多传人</router-link>
      </div>
    </section>

    <!-- 课程引导区：跳转到培训课程列表 -->
    <section class="enroll">
      <div class="enroll-seal">习 漆 · 传 艺</div>
      <p class="enroll-text">想亲手髹一把漆器？非遗传承人，亲自授艺。</p>
      <router-link class="btn-solid" to="/course">查看培训课程</router-link>
    </section>

  </div>
</template>

<script setup>
/* 首页：组合共享状态中的技艺、传承人、课程、作品数据，并实现环形展台与滚动入场动画 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Nav from '@/views/user/common/nav.vue'
import {
  homeConfig, heritageSkills, loadSkills,
  inheritors, loadInheritors,
  courses, ensureCourses,
  heritageProducts, loadProducts,
  loadConfig,
} from '@/store'

/* 数据概览：只统计审核通过或处于启用状态的数据 */
const stats = computed(() => [
  { num: String(heritageSkills.filter((s) => s.status === 'approved').length), label: '技艺档案' },
  { num: String(inheritors.filter((m) => m.status === 'active').length), label: '非遗传承人' },
  { num: String(courses.length), label: '培训课程' },
  { num: String(heritageProducts.filter((p) => p.status === 'approved').length), label: '文创作品' },
])

/* 拼贴布局配置：c 表示横跨列数，r 表示横跨行数 */
const LAYOUT = [
  { c: 5, r: 2 },
  { c: 3, r: 3 },
  { c: 4, r: 2 },
  { c: 2, r: 3 },
  { c: 4, r: 2 },
  { c: 3, r: 3 },
  { c: 3, r: 2 },
  { c: 5, r: 3 },
  { c: 4, r: 2 },
  { c: 2, r: 3 },
  { c: 5, r: 2 },
  { c: 3, r: 2 },
]

/* 首页展示的技艺：优先取后台配置的 id，配置为空时回退到全部已审核技艺 */
const archives = computed(() => {
  let list = homeConfig.archives
    .map((id) => heritageSkills.find((s) => s.id === id && s.status === 'approved'))
    .filter(Boolean)
  if (!list.length) {
    list = heritageSkills.filter((s) => s.status === 'approved')
  }
  return list.slice(0, LAYOUT.length).map((a, i) => {
    const lay = LAYOUT[i % LAYOUT.length]
    return {
      id: a.id,
      to: '/archive/' + a.id,
      glyph: a.glyph || a.name.charAt(0),
      image: a.image || '',
      name: a.name,
      desc: a.desc || a.abstract || '',
      tag: a.level || a.category || '',
      c: lay.c,
      r: lay.r,
    }
  })
})

/* 根据布局配置生成网格跨度样式；有图片时再叠加背景图 */
function craftStyle(a) {
  const s = { gridColumn: 'span ' + a.c, gridRow: 'span ' + a.r }
  if (a.image) s.backgroundImage = 'url(' + a.image + ')'
  return s
}

/* 环形展台展示的传承人：同样优先取后台配置，最多 12 位 */
const masters = computed(() => {
  let list = homeConfig.masters
    .map((id) => inheritors.find((m) => m.id === id && m.status === 'active'))
    .filter(Boolean)
  if (!list.length) {
    list = inheritors.filter((m) => m.status === 'active')
  }
  return list.slice(0, 12).map((m) => ({
    id: m.id,
    glyph: (m.craft || m.name || '匠').charAt(0),
    name: m.name,
    title: m.level + '传承人',
    to: '/inheritor/' + m.id,
  }))
})

/* 圆环旋转角度、每位传承人占用的角度、圆环半径 */
const angle = ref(0)
const count = computed(() => masters.value.length || 1)
const seg = computed(() => 360 / count.value)
const radius = 300
/* 左右切换：每次旋转一个卡片角度 */
function next() { angle.value -= seg.value }
function prev() { angle.value += seg.value }

/* craftList 预留的模板引用；io 保存滚动观察器实例 */
const craftList = ref(null)
let io = null
// 页面挂载后先加载全部首页数据，再等 DOM 渲染完成，最后为技艺卡片绑定入场动画
onMounted(async () => {
  await Promise.allSettled([
    loadConfig(),
    loadSkills(),
    loadInheritors(),
    ensureCourses(),
    loadProducts(),
  ])
  // nextTick：nextTick 返回一个 Promise，等 DOM 更新完成后再继续执行；这里要等卡片渲染出来才能查询到 .craft-item
  await nextTick()
  const cards = document.querySelectorAll('.craft-item')
  // 创建观察器：卡片进入视口时添加 in 类触发动画
  io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // 进入视口：按列位置错开动画延迟，形成依次浮现的效果
          const i = Array.prototype.indexOf.call(cards, entry.target)
          entry.target.style.transitionDelay = (i % 4) * 0.12 + 's'
          entry.target.classList.add('in')
        } else {
          // 离开视口：移除动画状态，下次进入时可以重新播放
          entry.target.classList.remove('in')
          entry.target.style.transitionDelay = '0s'
        }
      })
    },
    { threshold: 0.15 }
  )
  cards.forEach((card) => io.observe(card))
})
// 组件卸载时断开观察器，避免继续监听已经销毁的 DOM
onBeforeUnmount(() => {
  if (io) io.disconnect()
})
</script>

<style src="./Home.css"></style>

<style scoped>

/* 有图片的卡片：图片作为背景铺满，文字压在底部遮罩上 */
.craft-item.craft-hasimg {
  position: relative;
  justify-content: flex-end;
  align-items: stretch;
  gap: 0;
  padding: 0;
  background-size: cover;
  background-position: center;
  border: none;
}
/* 底部渐变遮罩：保证浅色图片上的白色文字也能看清 */
.craft-scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(43, 33, 23, 0) 28%, rgba(43, 33, 23, 0.45) 72%, rgba(43, 33, 23, 0.78) 100%);
}
.craft-hasimg .craft-info {
  position: relative;
  width: 100%;
  box-sizing: border-box;
  align-self: stretch;
  justify-content: flex-end;
  align-items: flex-start;
  text-align: left;
  padding: 28px 18px 16px;
}
.craft-name-img {
  color: #fff;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.4);
  margin: 0 0 8px;
}
.craft-tag-img {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.9);
  background: rgba(43, 33, 23, 0.18);
}
</style>
