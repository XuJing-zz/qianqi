<!-- 技艺详情展示组件：既支持路由页直接使用，也支持作为子组件接收 skill 预览 -->
<template>
  <div class="archive-detail-page">
    <div class="ad-detail" v-if="item">
      <!-- 详情首屏：背景图/纯色底 + 技艺名称、描述与标签 -->
      <header class="ad-hero" :class="{ 'ad-hero-plain': !item.image }">
        <div v-if="item.image" class="ad-hero-img" :style="{ backgroundImage: 'url(' + item.image + ')' }"></div>
        <div class="ad-hero-shade"></div>

        <div class="ad-hero-inner">
          <div class="ad-hero-top">
            <span class="ad-hero-seal">{{ heroGlyph }}</span>
            <span class="ad-hero-en">技艺档案 · CRAFT ARCHIVES</span>
          </div>
          <div class="ad-hero-body">
            <h1 class="ad-hero-title">{{ item.name || '未命名技艺' }}</h1>
            <p v-if="item.desc" class="ad-hero-desc">{{ item.desc }}</p>
            <div class="ad-hero-tags">
              <span v-if="item.level" class="ad-tag" :class="'ad-tag-' + levelClass(item.level)">{{ item.level }}</span>
              <span v-if="item.difficulty" class="ad-tag">难度 · {{ item.difficulty }}</span>
              <span v-if="item.category" class="ad-tag">门类 · {{ item.category }}</span>
              <span v-if="item.school" class="ad-tag">流派 · {{ item.school }}</span>
              <span v-if="item.region" class="ad-tag">地区 · {{ item.region }}</span>
              <span v-if="item.origin" class="ad-tag">发源 · {{ item.origin }}</span>
              <span v-if="item.years" class="ad-tag">从艺 {{ item.years }} 年</span>
            </div>
          </div>
        </div>
      </header>

      <!-- 具名插槽：父组件可在此处插入导航栏等内容 -->
      <slot name="after-hero"></slot>

      <div class="ad-content">

        <!-- 历史背景：富文本模式下按段落数组渲染 -->
        <section v-if="visible('history')" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('history') }}</span>
            <h2 class="ad-section-title">历史背景</h2>
            <span class="ad-section-en">HISTORY</span>
          </div>
          <div class="ad-history">
            <p v-for="(p, i) in bodyArr('history')" :key="i" class="ad-para">{{ p.text }}</p>
          </div>
        </section>

        <!-- 富文本模式下的工艺流程：每道工序含编号、工具、材料、做法与配图 -->
        <section v-if="richMode && bodyArr('steps').length" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('process') }}</span>
            <h2 class="ad-section-title">工艺流程</h2>
            <span class="ad-section-en">PROCESS</span>
          </div>
          <div class="ad-steps-rich">
            <article v-for="(s, i) in bodyArr('steps')" :key="i" class="ad-proc">
              <span class="ad-proc-no">{{ pad(i + 1) }}</span>
              <div class="ad-proc-main">
                <h3 class="ad-proc-name">{{ s.name }}</h3>
                <div class="ad-proc-meta">
                  <div v-if="chips(s.tools).length" class="ad-proc-row">
                    <span class="ad-proc-label">工具</span>
                    <span v-for="(t, ti) in chips(s.tools)" :key="'t' + ti" class="ad-proc-chip">{{ t }}</span>
                  </div>
                  <div v-if="chips(s.materials).length" class="ad-proc-row">
                    <span class="ad-proc-label">材料</span>
                    <span v-for="(m, mi) in chips(s.materials)" :key="'m' + mi" class="ad-proc-chip ad-proc-chip-mat">{{ m }}</span>
                  </div>
                </div>
                <p class="ad-proc-method">{{ s.method }}</p>
                <figure v-if="s.image" class="ad-proc-fig">
                  <img :src="s.image" :alt="s.name" />
                  <figcaption v-if="s.caption">{{ s.caption }}</figcaption>
                </figure>
              </div>
            </article>
          </div>
        </section>

        <!-- 素材与要点：原材料、专用工具、制作难点、注意事项 -->
        <section v-if="visible('essentials')" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('essentials') }}</span>
            <h2 class="ad-section-title">素材与要点</h2>
            <span class="ad-section-en">MATERIALS &amp; NOTES</span>
          </div>
          <div class="ad-essentials">
            <div v-if="item.raw_materials || item.rawMaterials" class="ad-ess">
              <h3 class="ad-ess-title">原材料清单</h3>
              <div class="ad-proc-meta">
                <span v-for="(m, mi) in chips(item.raw_materials || item.rawMaterials)" :key="'rm' + mi" class="ad-proc-chip ad-proc-chip-mat">{{ m }}</span>
              </div>
            </div>
            <div v-if="item.tools" class="ad-ess">
              <h3 class="ad-ess-title">专用工具</h3>
              <div class="ad-proc-meta">
                <span v-for="(t, ti) in chips(item.tools)" :key="'tl' + ti" class="ad-proc-chip">{{ t }}</span>
              </div>
            </div>
            <div v-if="item.hard_points || item.hardPoints" class="ad-ess">
              <h3 class="ad-ess-title">制作难点</h3>
              <p class="ad-para">{{ item.hard_points || item.hardPoints }}</p>
            </div>
            <div v-if="item.cautions" class="ad-ess">
              <h3 class="ad-ess-title">注意事项</h3>
              <p class="ad-para">{{ item.cautions }}</p>
            </div>
          </div>
        </section>

        <!-- 工艺纪实：图文卡片列表 -->
        <section v-if="richMode && bodyArr('cards').length" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('cards') }}</span>
            <h2 class="ad-section-title">工艺纪实</h2>
            <span class="ad-section-en">CRAFT NOTES</span>
          </div>
          <div class="ad-cards">
            <article v-for="(c, i) in bodyArr('cards')" :key="i" class="ad-card">
              <div class="ad-card-body">
                <h3 class="ad-card-title">{{ c.title }}</h3>
                <p class="ad-card-text">{{ c.text }}</p>
              </div>
              <figure v-if="c.image" class="ad-card-fig">
                <img :src="c.image" :alt="c.title" />
                <figcaption v-if="c.caption">{{ c.caption }}</figcaption>
              </figure>
            </article>
          </div>
        </section>

        <!-- 旧版数据模式下的技艺概述 -->
        <section v-if="!richMode && (item.abstract || item.desc)" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('overview') }}</span>
            <h2 class="ad-section-title">技艺概述</h2>
            <span class="ad-section-en">OVERVIEW</span>
          </div>
          <p class="ad-para">{{ item.abstract || item.desc }}</p>
        </section>

        <!-- 旧版数据模式下的工艺流程：把「｜」分隔的字符串拆成有序步骤 -->
        <section v-if="!richMode && parseList(item.steps).length" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('process') }}</span>
            <h2 class="ad-section-title">工艺流程</h2>
            <span class="ad-section-en">PROCESS</span>
          </div>
          <ol class="ad-steps">
            <li v-for="(s, i) in parseList(item.steps)" :key="i" class="ad-step">
              <span class="ad-step-no">{{ pad(i + 1) }}</span>
              <span class="ad-step-name">{{ s }}</span>
            </li>
          </ol>
        </section>

        <!-- 代表作品：优先展示关联的文创作品，没有时回退到旧版文字作品列表 -->
        <section v-if="visible('works')" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('works') }}</span>
            <h2 class="ad-section-title">代表作品</h2>
            <span class="ad-section-en">WORKS</span>
          </div>

          <!-- 关联文创作品卡片；点击跳转到作品详情页 -->
          <div v-if="productWorks.length" class="ad-products">
            <div
              v-for="p in productWorks"
              :key="p.id"
              class="ad-product"
              @click="preview ? null : goProduct(p.id)"
            >
              <div class="ad-product-cover" :style="productCover(p)">
                <span v-if="!p.cover" class="ad-product-glyph">{{ (p.name || '').charAt(0) }}</span>
              </div>
              <div class="ad-product-body">
                <h4 class="ad-product-name">{{ p.name }}</h4>
                <p class="ad-product-sub">{{ p.craft }}<span v-if="p.category"> · {{ p.category }}</span></p>
              </div>
            </div>
          </div>

          <!-- 旧版文字作品列表（无关联作品时显示） -->
          <div v-else class="ad-works">
            <div v-for="(w, i) in parseList(item.works)" :key="i" class="ad-work">
              <span class="ad-work-glyph">{{ glyphOf(w) }}</span>
              <span class="ad-work-name">{{ w }}</span>
            </div>
          </div>
        </section>

        <!-- 当代传承：展示申报该技艺的传承人，非预览模式下可点击进入主页 -->
        <section v-if="visible('master')" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('master') }}</span>
            <h2 class="ad-section-title">当代传承</h2>
            <span class="ad-section-en">MASTER</span>
          </div>
          <div
            class="ad-master"
            :class="{ 'ad-master-link': !preview && !!masterProfile }"
            @click="(!preview && masterProfile) && goMaster(masterProfile.id)"
          >
            <div class="ad-master-glyph">{{ (item.ownerName || '传').charAt(0) }}</div>
            <div class="ad-master-info">
              <h3 class="ad-master-name">{{ item.ownerName || '未填写传承人' }}</h3>
              <p class="ad-master-role">{{ item.level }}非遗传承人<span v-if="item.category"> · {{ item.category }}</span></p>
              <p class="ad-master-sub">该技艺由{{ item.ownerName || '传承人' }}在本平台申报展示</p>
            </div>
            <span v-if="!preview && masterProfile" class="ad-master-go">查看主页 ›</span>
          </div>
        </section>

        <!-- 关联课程：按课程名称查找对应课程 id，找到后可跳转 -->
        <section v-if="visible('courses')" class="ad-section">
          <div class="ad-section-head">
            <span class="ad-section-no">{{ secNo('courses') }}</span>
            <h2 class="ad-section-title">关联课程</h2>
            <span class="ad-section-en">COURSES</span>
          </div>
          <div class="ad-courses">
            <div
              v-for="(c, i) in parseList(item.courses)"
              :key="i"
              class="ad-course"
              :class="{ 'ad-course-link': !preview && !!courseIdOf(c) }"
              @click="(!preview && courseIdOf(c)) && goCourse(courseIdOf(c))"
            >
              <span class="ad-course-glyph">{{ glyphOf(c) }}</span>
              <span class="ad-course-name">{{ c }}</span>
              <span v-if="!preview && courseIdOf(c)" class="ad-course-go">›</span>
            </div>
          </div>
        </section>

        <!-- 附件资料：在新窗口打开上传的文档或图片 -->
        <section v-if="docAtts.length" class="ad-section">
          <div class="ad-section-head">
            <h2 class="ad-section-title">附件资料</h2>
            <span class="ad-section-en">ATTACHMENTS</span>
          </div>
          <div class="ad-files">
            <a
              v-for="(a, i) in docAtts"
              :key="i"
              class="ad-file"
              :href="a.url"
              target="_blank"
              rel="noopener"
            >
              <span class="ad-file-ico">{{ fileIco(a.name) }}</span>
              <span class="ad-file-name">{{ a.name }}</span>
              <span class="ad-file-go">下载 ›</span>
            </a>
          </div>
        </section>

        <!-- 档案录入时间（仅正式详情页显示） -->
        <p v-if="!preview && item.submitTime" class="ad-submit">档案录入于 {{ item.submitTime }}</p>

        <!-- 返回技艺档案列表（仅正式详情页显示） -->
        <div v-if="!preview" class="ad-back">
          <router-link to="/archive" class="ad-back-btn">‹ 返回技艺档案</router-link>
        </div>
      </div>
    </div>

    <!-- 正式详情页找不到数据时的空状态 -->
    <div class="ad-detail-empty" v-else-if="!preview">
      <p>未找到该技艺档案</p>
      <router-link to="/archive" class="ad-back-btn">返回技艺档案</router-link>
    </div>
    <!-- 预览模式且没有数据时的空状态 -->
    <div class="ad-detail-empty" v-else>
      <p>暂无可预览内容</p>
    </div>
  </div>
</template>

<script setup>

/* 组件数据来源：技艺档案，以及关联的作品、传承人、课程共享状态 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  heritageSkills, loadSkills,
  heritageProducts, loadProducts,
  inheritors, loadInheritors,
  courses, ensureCourses,
} from '@/store'

// defineProps：defineProps 是 Vue 3 的编译宏，用于声明父组件传入的属性（props），返回包含这些属性的对象
/* 组件属性：skill 可直接传入技艺对象；preview 为 true 时不显示返回按钮和跳转交互 */
const props = defineProps({
  skill: { type: Object, default: null },
  preview: { type: Boolean, default: false },
})

const route = useRoute()
const router = useRouter()

// 页面挂载时并行拉取技艺、作品、传承人、课程数据；单个请求失败不影响其他数据
onMounted(() => {
  Promise.all([
    loadSkills().catch(() => {}),
    loadProducts().catch(() => {}),
    loadInheritors().catch(() => {}),
    ensureCourses().catch(() => {}),
  ])
})

/* 当前技艺：优先使用父组件传入的 skill；否则按路由 id 在共享状态中查找 */
const item = computed(() => {
  if (props.skill) return props.skill
  const id = Number(route.params.id)
  return heritageSkills.find((s) => s.id === id) || null
})

/* 首屏印章文字：优先用技艺自带字形，其次取名称首字，最后兜底为「艺」 */
const heroGlyph = computed(() =>
  (item.value && (item.value.glyph || (item.value.name || '').charAt(0))) || '艺'
)

/* 富文本正文对象：包含 history、steps、cards 等分区数据，保证始终返回对象 */
const body = computed(() => {
  const b = item.value && item.value.body
  return b && typeof b === 'object' ? b : {}
})
/* 附件列表：仅当 attachments 是数组时才使用，避免脏数据导致渲染报错 */
const docAtts = computed(() =>
  Array.isArray(item.value?.attachments) ? item.value.attachments : []
)
/* 根据文件扩展名返回附件图标文字 */
function fileIco(name) {
  const n = (name || '').toLowerCase()
  if (n.match(/\.(png|jpe?g|gif|webp|bmp)$/)) return '图'
  if (n.endsWith('.pdf')) return 'PDF'
  if (n.match(/\.docx?$/)) return 'DOC'
  if (n.match(/\.xlsx?$/)) return 'XLS'
  if (n.match(/\.pptx?$/)) return 'PPT'
  if (n.endsWith('.zip') || n.endsWith('.rar')) return '包'
  return '文'
}
/* 安全读取正文中的某个分区数组，不存在时返回空数组 */
const bodyArr = (k) => (Array.isArray(body.value[k]) ? body.value[k] : [])
/* 是否为富文本数据：history / steps / cards 任一有内容即视为新结构 */
const richMode = computed(() =>
  bodyArr('history').length || bodyArr('steps').length || bodyArr('cards').length
)

/* 章节中文序号，以及两种数据格式下章节的显示顺序 */
const CN = ['壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌']
const ORDER_RICH = ['history', 'process', 'essentials', 'cards', 'works', 'master', 'courses']
const ORDER_LEGACY = ['overview', 'process', 'essentials', 'works', 'master', 'courses']

/* 判断某个章节是否有内容可显示 */
function visible(key) {
  const i = item.value
  if (!i) return false
  switch (key) {
    case 'history': return richMode.value && bodyArr('history').length > 0
    case 'process': return richMode.value ? bodyArr('steps').length > 0 : parseList(i.steps).length > 0
    case 'cards': return richMode.value && bodyArr('cards').length > 0
    case 'essentials':
      return !!(i.raw_materials || i.rawMaterials || i.tools || i.hard_points || i.hardPoints || i.cautions)
    case 'overview': return !richMode.value && !!(i.abstract || i.desc)
    case 'works': return productWorks.value.length > 0 || parseList(i.works).length > 0
    case 'master': return !!i.ownerName
    case 'courses': return parseList(i.courses).length > 0
    default: return false
  }
}

/* 计算章节序号：只统计真正会显示的章节，避免序号出现空档 */
function secNo(key) {
  const order = richMode.value ? ORDER_RICH : ORDER_LEGACY
  const shown = order.filter((k) => visible(k))
  const idx = shown.indexOf(key)
  return idx >= 0 ? CN[idx] : ''
}

/* 关联作品：把 worksProductIds 转成数字后，筛出已审核通过的作品 */
const productWorks = computed(() => {
  if (!item.value) return []
  const ids = (Array.isArray(item.value.worksProductIds) ? item.value.worksProductIds : [])
    .map(Number).filter(Boolean)
  if (!ids.length) return []
  return heritageProducts.filter(
    (p) => p.status === 'approved' && ids.includes(Number(p.id))
  )
})

/* 传承人主页数据：按 ownerName 在传承人列表中匹配 */
const masterProfile = computed(() => {
  if (!item.value || !item.value.ownerName) return null
  return inheritors.find((m) => m.name === item.value.ownerName) || null
})

/* 把以「｜」分隔的旧版字符串拆成数组，去掉空白项 */
function parseList(str) {
  return (str || '').split('｜').map((x) => x.trim()).filter(Boolean)
}

/* 取名称首字，作为无图片时的占位字形 */
function glyphOf(w) {
  return (w || '').charAt(0)
}

/* 把用顿号、逗号、分号、空格或斜杠分隔的字符串拆成词条数组 */
function chips(str) {
  return (str || '').split(/、|，|,|；|;|\s+|\//).map((x) => x.trim()).filter(Boolean)
}

/* 把步骤编号补成两位数，如 1 → 01 */
function pad(n) {
  return String(n).padStart(2, '0')
}

/* 级别名称到 CSS 类名后缀的映射 */
function levelClass(level) {
  return level === '国家级' ? 'national' : level === '省级' ? 'province' : 'city'
}

/* 有封面时生成背景图样式，否则返回空样式 */
function productCover(p) {
  return p.cover ? { backgroundImage: 'url(' + p.cover + ')' } : {}
}
function goProduct(id) {
  router.push('/product/' + id)
}
function goMaster(id) {
  router.push('/inheritor/' + id)
}
function goCourse(id) {
  router.push('/course/' + id)
}
/* 按课程名称查找课程 id；找不到返回 null，此时不显示跳转交互 */
function courseIdOf(name) {
  const c = courses.find((x) => x.name === name)
  return c ? c.id : null
}
</script>

<style src="./ArchiveDetail.css"></style>
