<!-- 文创作品列表页：精选轮播、多条件筛选、馆藏精品拼贴、作品网格与分页 -->
<template>
  <div class="product-page">
    <!-- 页面首屏标题区 -->
    <header class="product-hero">
      <div class="pl-hero-seal">漆 · 物</div>
      <h1 class="pl-hero-title">文 创 作 品</h1>
      <span class="pl-hero-en">CULTURAL CRAFTS</span>
      <div class="pl-hero-line"></div>
      <p class="pl-hero-note">把千年漆艺，带进日常。</p>
    </header>

    <Nav />

    <div class="product-wrap">

      <!-- 精选轮播：每 4 秒自动切换，点击圆点可手动切换，点击幻灯片进入详情 -->
      <div v-if="featured.length" class="carousel">
        <div
          class="carousel-track"
          :style="{ transform: 'translateX(-' + carouselIndex * 100 + '%)' }"
        >
          <div
            v-for="f in featured"
            :key="f.id"
            class="carousel-slide"
            :style="coverStyle(f)"
            @click="goDetail(f.id)"
          >
            <div class="carousel-mask">
              <span class="carousel-flag">{{ f.flag || '精选' }}</span>
              <div class="carousel-info">
                <h3 class="carousel-name">{{ f.name }}</h3>
                <p class="carousel-maker">{{ f.inheritor }} · {{ f.craft }}</p>
              </div>
            </div>
            <span class="carousel-glyph">{{ f.glyph }}</span>
          </div>
        </div>
        <div class="carousel-dots">
          <span
            v-for="(f, i) in featured"
            :key="'d' + f.id"
            class="dot"
            :class="{ 'dot-active': i === carouselIndex }"
            @click="carouselIndex = i"
          ></span>
        </div>
      </div>

      <!-- 筛选工具栏：品类标签页 + 工艺/传承人/价格下拉框 + 关键词搜索 -->
      <div class="pl-toolbar">
        <div class="pl-toolbar-tabs">
          <button
            v-for="cat in categories"
            :key="cat"
            class="pl-tab"
            :class="{ 'pl-tab-active': category === cat }"
            @click="category = cat; page = 1"
          >
            {{ cat }}
          </button>
        </div>
        <div class="pl-toolbar-right">
          <select v-model="craft" class="pl-select" @change="page = 1">
            <option v-for="c in craftOptions" :key="c" :value="c">{{ c === '全部' ? '全部工艺' : c }}</option>
          </select>
          <select v-model="inheritor" class="pl-select" @change="page = 1">
            <option v-for="m in inheritorOptions" :key="m" :value="m">{{ m === '全部' ? '全部传承人' : m }}</option>
          </select>
          <select v-model="priceRange" class="pl-select" @change="page = 1">
            <option v-for="r in priceRanges" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
          <input v-model="keyword" class="pl-search-input" type="text" placeholder="搜作品名或传承人" />
        </div>
      </div>

      <!-- 馆藏精品拼贴：仅在没有任何筛选条件时展示，大小卡片交错排列 -->
      <section v-if="isAll && masterpieces.length" class="masonry-section">
        <div class="pl-section-head">
          <h2 class="pl-section-cn">精品 · 馆藏</h2>
          <span class="pl-section-en">MASTERPIECES</span>
        </div>
        <div class="masonry">
          <div
            v-for="(m, i) in masterpieces"
            :key="m.id"
            class="masonry-card"
            :class="masonryClass(i)"
            @click="goDetail(m.id)"
          >
            <div class="masonry-cover" :style="coverStyle(m)">
              <span class="masonry-glyph">{{ m.glyph }}</span>
              <span v-if="m.flag" class="masonry-flag">{{ m.flag }}</span>
            </div>
            <div class="masonry-body">
              <h3 class="masonry-name">{{ m.name }}</h3>
              <p class="masonry-maker">{{ m.inheritor }} · {{ m.craft }} 出品</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 作品网格：展示筛选后的作品，点击进入详情 -->
      <section class="grid-section">
        <div class="pl-section-head">
          <h2 class="pl-section-cn">{{ category === '全部' ? '全部作品' : category }}</h2>
          <span class="pl-section-en">COLLECTION</span>
        </div>
        <div class="product-grid">
          <div
            v-for="p in pagedProducts"
            :key="p.id"
            class="product-card"
            @click="goDetail(p.id)"
          >
            <div class="product-cover" :style="coverStyle(p)">
              <span class="product-glyph">{{ p.glyph }}</span>
              <span v-if="p.flag" class="product-flag">{{ p.flag }}</span>
            </div>
            <div class="product-body">
              <h3 class="product-name">{{ p.name }}</h3>
              <p class="product-maker">
                <span class="pl-verified">✓</span>{{ p.inheritor }} · {{ p.craft }} 出品
              </p>
              <p class="product-desc">{{ p.desc }}</p>
              <div class="product-meta">
                <span class="p-tag">{{ p.category }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 筛选结果为空时的提示 -->
      <div v-if="pagedProducts.length === 0" class="pl-empty">未找到相关作品</div>

      <!-- 分页器：总页数大于 1 时才显示 -->
      <div class="pl-pager" v-if="totalPage > 1">
        <button class="pl-page-btn" :disabled="page === 1" @click="page--">‹</button>
        <button
          v-for="pg in totalPage"
          :key="pg"
          class="pl-page-btn"
          :class="{ 'pl-page-active': pg === page }"
          @click="page = pg"
        >
          {{ pg }}
        </button>
        <button class="pl-page-btn" :disabled="page === totalPage" @click="page++">›</button>
      </div>

      <!-- 平台保障说明：手工、生漆、出品与包装 -->
      <section class="pl-assure">
        <div class="pl-assure-title">匠心出品 · 平台保障</div>
        <div class="pl-assure-grid">
          <div class="pl-assure-item">
            <span class="pl-assure-icon">手</span>
            <h4 class="pl-assure-name">手工髹制</h4>
            <p class="pl-assure-desc">每件作品均由非遗传承人手作，非工业化量产。</p>
          </div>
          <div class="pl-assure-item">
            <span class="pl-assure-icon">料</span>
            <h4 class="pl-assure-name">天然生漆</h4>
            <p class="pl-assure-desc">选用天然生漆与天然矿物颜料，健康无害。</p>
          </div>
          <div class="pl-assure-item">
            <span class="pl-assure-icon">鉴</span>
            <h4 class="pl-assure-name">传承人出品</h4>
            <p class="pl-assure-desc">作品均附传承人出品标识，可溯源可查询。</p>
          </div>
          <div class="pl-assure-item">
            <span class="pl-assure-icon">运</span>
            <h4 class="pl-assure-name">严实包装</h4>
            <p class="pl-assure-desc">漆器易损，采用定制缓冲包装，破损包赔。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
/* 作品列表：加载作品与首页配置，实现轮播、多条件筛选和前端分页 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import { heritageProducts, homeConfig, loadProducts, loadConfig } from '@/store'

const router = useRouter()

/* 品类筛选选项与当前筛选条件 */
const categories = ['全部', '茶器', '文房', '首饰', '摆件', '日用', '雅玩']
const category = ref('全部')
const keyword = ref('')

/* 工艺、传承人、价格区间筛选条件 */
const craft = ref('全部')
const inheritor = ref('全部')
const priceRange = ref('all')
const priceRanges = [
  { value: 'all', label: '全部价格' },
  { value: '0-200', label: '200 元以下' },
  { value: '200-500', label: '200 - 500 元' },
  { value: '500-1000', label: '500 - 1000 元' },
  { value: '1000-', label: '1000 元以上' },
]
/* 判断价格是否落在所选区间：区间字符串形如 "200-500"，"1000-" 表示不设上限 */
function inPriceRange(price, range) {
  if (range === 'all') return true
  const p = Number(price) || 0
  const [lo, hi] = range.split('-')
  const min = Number(lo) || 0
  if (hi === '') return p >= min
  return p >= min && p < Number(hi)
}

/* 可展示的作品：只保留已审核作品，并把 story 字段映射为列表用的 desc */
const products = computed(() =>
  heritageProducts
    .filter((p) => p.status === 'approved')
    .map((p) => ({ ...p, desc: p.story }))
)

/* 轮播作品：按首页配置取 id 对应的作品，最多 4 件 */
const featured = computed(() =>
  homeConfig.featuredProducts
    .map((id) => products.value.find((p) => p.id === id))
    .filter(Boolean)
    .slice(0, 4)
)
/* 当前轮播下标与定时器句柄 */
const carouselIndex = ref(0)
let carouselTimer = null

/* 启动自动轮播：每 4 秒切到下一张；只有一张时保持不动 */
function startCarousel() {
  stopCarousel()
  carouselTimer = setInterval(() => {
    const len = featured.value.length
    if (len < 2) { carouselIndex.value = 0; return }
    carouselIndex.value = (carouselIndex.value + 1) % len
  }, 4000)
}
/* 停止轮播并清空定时器 */
function stopCarousel() {
  if (carouselTimer) clearInterval(carouselTimer)
  carouselTimer = null
}
// 页面挂载后启动轮播，同时加载作品和首页配置
onMounted(async () => {
  startCarousel()
  try {
    await Promise.all([loadProducts(), loadConfig()])
  } catch (e) {
  }
})
// onUnmounted：onUnmounted 是组合式 API 的生命周期钩子，组件卸载后执行；这里用来停止轮播定时器，避免定时器在组件销毁后继续运行
onUnmounted(stopCarousel)

/* 馆藏精品：标记为「臻品」的作品 */
const masterpieces = computed(() => products.value.filter((p) => p.flag === '臻品'))
/* 是否处于「无任何筛选」状态，只有此时才显示精品拼贴区 */
const isAll = computed(() =>
  category.value === '全部' && !keyword.value.trim()
  && craft.value === '全部' && inheritor.value === '全部' && priceRange.value === 'all'
)

/* 拼贴大小：每三张出现一张大卡 */
function masonryClass(i) {
  return i % 3 === 0 ? 'masonry-large' : 'masonry-small'
}

/* 工艺与传承人下拉选项：从作品数据中去重并排序生成 */
const craftOptions = computed(() => ['全部', ...Array.from(new Set(products.value.map((p) => p.craft).filter(Boolean))).sort()])
const inheritorOptions = computed(() => ['全部', ...Array.from(new Set(products.value.map((p) => p.inheritor).filter(Boolean))).sort()])

/* 综合筛选：依次按品类、工艺、传承人、价格区间过滤，最后匹配关键词 */
const filtered = computed(() => {
  let list = products.value
  if (category.value !== '全部') {
    list = list.filter((p) => p.category === category.value)
  }
  if (craft.value !== '全部') {
    list = list.filter((p) => p.craft === craft.value)
  }
  if (inheritor.value !== '全部') {
    list = list.filter((p) => p.inheritor === inheritor.value)
  }
  if (priceRange.value !== 'all') {
    list = list.filter((p) => inPriceRange(p.price, priceRange.value))
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim()
    list = list.filter(
      (p) => p.name.includes(kw) || p.inheritor.includes(kw) || p.craft.includes(kw) || p.category.includes(kw)
    )
  }
  return list
})

/* 前端分页：每页 16 件作品 */
const pageSize = 16
const page = ref(1)
const totalPage = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
/* 截取当前页要显示的作品 */
const pagedProducts = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

/* 有封面时生成背景图样式，否则返回空样式 */
function coverStyle(p) {
  if (p.cover) {
    return { backgroundImage: 'url(' + p.cover + ')' }
  }
  return {}
}

/* 跳转到作品详情页 */
function goDetail(id) {
  router.push('/product/' + id)
}

// 轮播数量变化时修正下标，防止下标越界
watch(
  () => featured.value.length,
  (len) => {
    if (carouselIndex.value >= len) carouselIndex.value = 0
  }
)

// 关键词变化时回到第一页，避免结果变少后停在空页
watch(keyword, () => {
  page.value = 1
})
</script>

<style src="./ProductList.css"></style>
