<!-- 培训课程列表页：学习路径、档位筛选、本周精选、课程网格与分页 -->
<template>
  <div class="course-page">
    <!-- 首屏：标语与课程/传承人/授课地统计 -->
    <header class="course-hero">
      <div class="course-hero-inner">
        <div class="cl-hero-seal">习 漆 · 传 艺</div>
        <h1 class="cl-hero-title">髹 一 把 属 于 你 的 漆 器</h1>
        <p class="hero-sub">非遗传承人 · 亲授 · 小班 · 限量开课</p>
        <div class="cl-hero-line"></div>
        <p class="cl-hero-note">从半日体验到大师亲授，一条髹漆之旅，由此入门。</p>
        <div class="hero-stats">
          <div class="hero-stat"><span class="hs-num">{{ statCourses }}</span><span class="hs-label">门在授课程</span></div>
          <div class="hero-stat"><span class="hs-num">{{ statTeachers }}</span><span class="hs-label">位授课传承人</span></div>
          <div class="hero-stat"><span class="hs-num">{{ statRegions }}</span><span class="hs-label">处授课地</span></div>
        </div>
      </div>
    </header>

    <Nav />

    <div class="course-wrap">

      <!-- 学习路径：体验工作坊 → 系统课程 → 大师亲授 -->
      <section class="path">
        <div class="path-title">
          <h2 class="path-cn">学 习 路 径</h2>
          <span class="path-en">LEARNING PATH</span>
        </div>
        <div class="path-line">
          <div class="path-node" v-for="s in stages" :key="s.name">
            <span class="path-dot"></span>
            <span class="path-node-name">{{ s.name }}</span>
            <span class="path-node-en">{{ s.en }}</span>
            <span class="path-node-desc">{{ s.desc }}</span>
          </div>
        </div>
      </section>

      <!-- 筛选工具栏：档位标签页 + 关键词搜索 -->
      <div class="cl-toolbar">
        <div class="cl-toolbar-tabs">
          <button
            v-for="cat in categories"
            :key="cat"
            class="cl-tab"
            :class="{ 'cl-tab-active': stage === cat }"
            @click="stage = cat; page = 1"
          >
            {{ cat }}
          </button>
        </div>
        <div class="cl-toolbar-right">
          <input v-model="keyword" class="cl-search-input" type="text" placeholder="搜课程或传承人姓名" />
        </div>
      </div>

      <!-- 本周精选课程：由后台配置的 featuredCourses 指定，点击进入详情 -->
      <div v-if="featured" class="featured" @click="goDetail(featured.id)">
        <div class="featured-cover" :style="coverStyle(featured)">
          <span class="featured-glyph">{{ featured.glyph }}</span>
        </div>
        <div class="featured-body">
          <div class="featured-badges">
            <span class="badge cl-badge-flag">本周精选</span>
            <span class="badge badge-limit">仅 {{ featured.capacity }} 席</span>
          </div>
          <h3 class="featured-name">{{ featured.name }}</h3>
          <p class="featured-teacher">
            <span class="cl-verified">✓ 已认证</span> 国家级非遗传承人 · {{ featured.teacher }}
          </p>
          <p class="featured-desc">{{ featured.desc }}</p>
          <div class="featured-meta">
            <span class="f-meta"><span class="f-label">时长</span>{{ featured.duration }}</span>
            <span class="f-meta"><span class="f-label">地点</span>{{ featured.region }}</span>
            <span class="f-meta"><span class="f-label">难度</span>{{ featured.difficulty }}</span>
          </div>
          <div class="featured-foot">
            <span class="featured-price">{{ featured.price }}</span>
            <span class="cl-btn featured-cta">查看详情</span>
          </div>
        </div>
      </div>

      <!-- 课程卡片网格：展示档位、授课人、时长、名额与价格 -->
      <div class="course-grid">
        <div v-for="c in pagedCourses" :key="c.id" class="cl-course-card" @click="goDetail(c.id)">
          <div class="course-cover" :style="coverStyle(c)">
            <span class="course-glyph">{{ c.glyph }}</span>
            <span class="course-stage-tag" :class="'cl-stage-' + stageClass(c.stage)">{{ c.stage }}</span>
          </div>
          <div class="course-body">
            <div class="course-top">
              <h3 class="cl-course-name">{{ c.name }}</h3>
              <span v-if="c.flag" class="course-flag">{{ c.flag }}</span>
            </div>
            <p class="course-teacher">
              <span class="cl-verified">✓</span>
              {{ teacherTitle(c) }} · {{ c.teacher }}
            </p>
            <p class="course-craft">所属技艺：{{ c.craft }} · {{ c.region }}</p>
            <p class="cl-course-desc">{{ c.desc }}</p>
            <div class="course-meta">
              <span class="meta-item"><span class="meta-label">时长</span>{{ c.duration }}</span>
              <span class="meta-item"><span class="meta-label">名额</span>仅 {{ c.capacity }} 席</span>
            </div>
          </div>
          <div class="course-side">
            <div class="course-price">{{ c.price }}</div>
            <button class="enroll-btn" @click.stop="goDetail(c.id)">查看</button>
          </div>
        </div>
      </div>

      <!-- 筛选结果为空时的提示 -->
      <div v-if="pagedCourses.length === 0" class="cl-empty">未找到相关课程</div>

      <!-- 分页器：总页数大于 1 时才显示 -->
      <div class="cl-pager" v-if="totalPage > 1">
        <button class="cl-page-btn" :disabled="page === 1" @click="page--">‹</button>
        <button
          v-for="p in totalPage"
          :key="p"
          class="cl-page-btn"
          :class="{ 'cl-page-active': p === page }"
          @click="page = p"
        >
          {{ p }}
        </button>
        <button class="cl-page-btn" :disabled="page === totalPage" @click="page++">›</button>
      </div>

      <!-- 平台保障说明：亲授、审核、材料、证书 -->
      <section class="cl-assure">
        <div class="cl-assure-title">报名须知 · 官方背书</div>
        <div class="cl-assure-grid">
          <div class="cl-assure-item">
            <span class="cl-assure-icon">印</span>
            <h4 class="cl-assure-name">传承人亲授</h4>
            <p class="cl-assure-desc">全部课程均由已认证非遗传承人亲自授课，无代课。</p>
          </div>
          <div class="cl-assure-item">
            <span class="cl-assure-icon">审</span>
            <h4 class="cl-assure-name">平台审核</h4>
            <p class="cl-assure-desc">课程内容经平台非遗顾问委员会审核后发布展示。</p>
          </div>
          <div class="cl-assure-item">
            <span class="cl-assure-icon">材</span>
            <h4 class="cl-assure-name">材料全含</h4>
            <p class="cl-assure-desc">授课所用生漆、胎体、工具等材料费用均已包含。</p>
          </div>
          <div class="cl-assure-item">
            <span class="cl-assure-icon">证</span>
            <h4 class="cl-assure-name">结业证书</h4>
            <p class="cl-assure-desc">完成长期课程可获平台与传承人联合签发的结业证书。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
/* 课程列表：加载课程与首页配置，提供筛选、精选展示和前端分页 */
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import { courses, homeConfig, ensureCourses, loadConfig } from '@/store'

const router = useRouter()

// 进入页面时加载课程和首页配置；任一请求失败都不影响页面其余部分
onMounted(() => {
  Promise.allSettled([ensureCourses(), loadConfig()])
})

/* 学习路径的三个阶段说明 */
const stages = [
  { name: '体验工作坊', en: 'WORKSHOP', desc: '半日 · 零基础 · 做一件小物' },
  { name: '系统课程', en: 'COURSE', desc: '长期 · 系统学一门技艺' },
  { name: '大师亲授', en: 'MASTER', desc: '限量 · 国家级传承人亲带' },
]

/* 档位筛选选项与当前筛选条件 */
const categories = ['全部', '体验工作坊', '系统课程', '大师亲授']
const stage = ref('全部')
const keyword = ref('')

/* 本周精选：按首页配置中的 featuredCourses 查找对应课程 */
const featured = computed(() => {
  return courses.find((c) => c.id === homeConfig.featuredCourses) || null
})

/* 首屏统计：课程数、去重后的授课人数与授课地数量 */
const statCourses = computed(() => courses.length)
const statTeachers = computed(() => new Set(courses.map((c) => c.teacher).filter(Boolean)).size)
const statRegions = computed(() => new Set(courses.map((c) => c.region).filter(Boolean)).size)

/* 按档位和关键词筛选课程；关键词会匹配课程名、传承人、技艺与地区 */
const filtered = computed(() => {
  let list = courses
  if (stage.value !== '全部') {
    list = list.filter((c) => c.stage === stage.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim()
    list = list.filter(
      (c) => c.name.includes(kw) || c.teacher.includes(kw) || c.craft.includes(kw) || c.region.includes(kw)
    )
  }
  return list
})

/* 前端分页：每页 6 门课程 */
const pageSize = 6
const page = ref(1)
const totalPage = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
/* 截取当前页要显示的课程 */
const pagedCourses = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

// 关键词变化时回到第一页，避免结果变少后停在空页
watch(keyword, () => {
  page.value = 1
})

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

/* 跳转到课程详情页 */
function goDetail(id) {
  router.push('/course/' + id)
}
</script>

<style src="./CourseList.css"></style>
