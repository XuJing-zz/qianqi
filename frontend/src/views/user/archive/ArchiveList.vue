<!-- 技艺档案列表页：支持级别、门类、难度、流派、地区筛选与关键词搜索、分页 -->
<template>
  <div class="archive-page">
    <!-- 页面首屏标题区 -->
    <header class="archive-hero">
      <div class="archive-hero-inner">
        <span class="head-seal">技 艺</span>
        <h1 class="head-title">技艺档案</h1>
        <span class="head-en">CRAFT ARCHIVES</span>
        <div class="head-line"></div>
        <p class="head-note">髹漆成器，历七千年而不朽；錾纹雕饰，藏一室而尽览。</p>
      </div>
    </header>

    <Nav />

    <div class="archive-list">

      <!-- 筛选工具栏：级别标签页 + 门类/难度/流派/地区下拉框 + 搜索框 -->
      <div class="al-toolbar">
        <div class="al-toolbar-tabs">
          <button
            v-for="cat in categories"
            :key="cat"
            class="al-tab"
            :class="{ 'al-tab-active': category === cat }"
            @click="category = cat; resetPage()"
          >
            {{ cat }}
          </button>
        </div>
        <div class="al-toolbar-right">
          <select v-model="craftCategory" class="region-select" @change="resetPage">
            <option v-for="c in craftCategories" :key="c" :value="c">{{ c === '全部' ? '全部类别' : c }}</option>
          </select>
          <select v-model="difficulty" class="region-select" @change="resetPage">
            <option v-for="d in difficulties" :key="d" :value="d">{{ d === '全部' ? '全部难度' : d }}</option>
          </select>
          <select v-model="school" class="region-select" @change="resetPage">
            <option v-for="sc in schools" :key="sc" :value="sc">{{ sc === '全部' ? '全部流派' : sc }}</option>
          </select>
          <select v-model="region" class="region-select" @change="resetPage">
            <option v-for="r in regions" :key="r" :value="r">{{ r === '全部' ? '全部地区' : r }}</option>
          </select>
          <div class="toolbar-search">
            <input v-model="keyword" class="al-search-input" type="text" placeholder="搜技艺名称，如「髹漆」" @input="resetPage" />
          </div>
        </div>
      </div>

      <!-- 档案卡片网格：每张卡片链接到对应详情页，有图显示图片，无图显示字形 -->
      <div class="archive-grid">
        <router-link
          v-for="a in pagedArchives"
          :key="a.id"
          :to="'/archive/' + a.id"
          class="archive-card"
        >
          <img v-if="a.image" :src="a.image" class="card-glyph card-glyph-img" alt="技艺图" />
          <div v-else class="card-glyph">{{ a.glyph }}</div>
          <div class="card-body">
            <h3 class="card-name">{{ a.name }}</h3>
            <p class="card-desc">{{ a.desc }}</p>
            <div class="card-meta">
              <span class="card-tag" :class="'al-tag-' + levelClass(a.level)">{{ a.level }}</span>
              <span v-if="a.category" class="card-origin">{{ a.category }}</span>
              <span v-if="a.school" class="card-origin">流派 · {{ a.school }}</span>
              <span v-if="a.difficulty" class="card-origin">难度 · {{ a.difficulty }}</span>
              <span class="card-origin">{{ a.origin }}</span>
            </div>
            <p class="card-abstract">{{ a.abstract }}</p>
          </div>
          <span class="card-arrow">入 卷 ›</span>
        </router-link>
      </div>

      <!-- 筛选结果为空时的提示 -->
      <div v-if="filtered.length === 0" class="al-empty">未找到相关技艺档案</div>

      <!-- 分页器：上一页、页码、下一页 -->
      <div class="al-pager">
        <button class="al-page-btn" :disabled="page === 1" @click="page--">‹</button>
        <button
          v-for="p in totalPage"
          :key="p"
          class="al-page-btn"
          :class="{ 'al-page-active': p === page }"
          @click="page = p"
        >
          {{ p }}
        </button>
        <button class="al-page-btn" :disabled="page === totalPage" @click="page++">›</button>
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import Nav from '@/views/user/common/nav.vue'
import { heritageSkills, loadSkills } from '@/store'

// 进入页面时加载技艺数据；失败时静默处理，页面显示空结果
onMounted(() => {
  loadSkills().catch(() => {})
})

/* 只展示审核通过的技艺档案 */
const archives = computed(() => heritageSkills.filter((s) => s.status === 'approved'))

/* 级别标签页固定为「全部 / 国家级 / 省级」 */
const categories = ['全部', '国家级', '省级']
const category = ref('全部')
/* 以下四个选项列表从已加载档案中去重生成，数据变化时会自动更新 */
const regions = computed(() => ['全部', ...Array.from(new Set(archives.value.map((a) => a.region).filter(Boolean)))])
const craftCategories = computed(() => ['全部', ...Array.from(new Set(archives.value.map((a) => a.category).filter(Boolean))).sort()])
const difficulties = computed(() => ['全部', ...Array.from(new Set(archives.value.map((a) => a.difficulty).filter(Boolean)))])
const schools = computed(() => ['全部', ...Array.from(new Set(archives.value.map((a) => a.school).filter(Boolean))).sort()])
const craftCategory = ref('全部')
const difficulty = ref('全部')
const school = ref('全部')
const region = ref('全部')
const keyword = ref('')

/* 综合筛选：依次按级别、门类、难度、流派、地区过滤，最后叠加关键词匹配 */
const filtered = computed(() => {
  let list = archives.value
  if (category.value !== '全部') {
    list = list.filter((a) => a.level === category.value)
  }
  if (craftCategory.value !== '全部') {
    list = list.filter((a) => a.category === craftCategory.value)
  }
  if (difficulty.value !== '全部') {
    list = list.filter((a) => a.difficulty === difficulty.value)
  }
  if (school.value !== '全部') {
    list = list.filter((a) => a.school === school.value)
  }
  if (region.value !== '全部') {
    list = list.filter((a) => a.region === region.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim()
    list = list.filter(
      (a) => (a.name || '').includes(kw) || (a.desc || '').includes(kw)
        || (a.origin || '').includes(kw) || (a.category || '').includes(kw)
        || (a.school || '').includes(kw)
        || (a.tools || '').includes(kw) || (a.raw_materials || '').includes(kw)
    )
  }
  return list
})

/* 前端分页：每页 12 条，总页数至少为 1 */
const pageSize = 12
const page = ref(1)
const totalPage = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))

/* 用 slice 截取当前页对应的数据片段 */
const pagedArchives = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

/* 筛选条件变化后回到第一页，避免停留在超出范围的页码 */
function resetPage() {
  page.value = 1
}

/* 把级别名称映射成对应的 CSS 类名后缀 */
function levelClass(level) {
  return level === '国家级' ? 'national' : 'province'
}
</script>

<style src="./ArchiveList.css"></style>

<style scoped>
/* 卡片图片：铺满卡片上方区域并按比例裁切，避免变形 */
.card-glyph-img {
  display: block;
  object-fit: cover;
  vertical-align: top;
}
</style>
