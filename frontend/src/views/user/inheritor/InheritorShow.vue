<!-- 传承人列表页：按级别筛选、按姓名或技艺搜索，并分页展示 -->
<template>
  <div class="inheritor-page">
    <!-- 页面首屏标题区 -->
    <header class="inheritor-hero">
      <div class="is-hero-seal">匠 心 传 人</div>
      <h1 class="is-hero-title">非 遗 传 承 人</h1>
      <span class="is-hero-en">HERITAGE MASTERS</span>
      <div class="is-hero-line"></div>
      <p class="is-hero-note">以手传心，以器载道。他们是千年漆艺的守护者。</p>
    </header>

    <Nav />

    <div class="inheritor-wrap">

      <!-- 筛选工具栏：级别标签页 + 关键词搜索 -->
      <div class="is-toolbar">
        <div class="is-toolbar-tabs">
          <button
            v-for="l in levels"
            :key="l"
            class="is-tab"
            :class="{ 'is-tab-active': level === l }"
            @click="level = l"
          >
            {{ l }}
          </button>
        </div>
        <input v-model="keyword" class="is-search-input" type="text" placeholder="搜传承人或技艺" />
      </div>

      <!-- 传承人卡片网格：头像、级别、技艺、简介与从艺信息 -->
      <div class="inheritor-grid">
        <div
          v-for="m in paged"
          :key="m.id"
          class="m-card"
          @click="goDetail(m.id)"
        >
          <div class="m-avatar">
            <span class="m-glyph">{{ glyphOf(m) }}</span>
          </div>
          <div class="m-body">
            <div class="m-top">
              <h3 class="m-name">{{ m.name }}</h3>
              <span class="m-level" :class="'lvl-' + levelClass(m.level)">{{ m.level }}</span>
            </div>
            <p class="m-craft">
              <span class="is-verified">✓</span>{{ m.level }}非遗传承人 · {{ m.craft }}技艺
            </p>
            <p class="m-bio">{{ m.intro }}</p>
            <div class="m-meta">
              <span class="m-tag">从艺 {{ m.years }} 年</span>
              <span v-if="m.qual" class="m-tag">{{ m.qual }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选结果为空时的提示 -->
      <div v-if="paged.length === 0" class="is-empty">未找到相关传承人</div>

      <!-- 分页器：总页数大于 1 时才显示 -->
      <div class="is-pager" v-if="totalPage > 1">
        <button class="is-page-btn" :disabled="page === 1" @click="page--">‹</button>
        <button
          v-for="p in totalPage"
          :key="p"
          class="is-page-btn"
          :class="{ 'is-page-active': p === page }"
          @click="page = p"
        >
          {{ p }}
        </button>
        <button class="is-page-btn" :disabled="page === totalPage" @click="page++">›</button>
      </div>
    </div>
  </div>
</template>

<script setup>
/* 传承人列表：加载传承人数据，按级别和关键词筛选后做前端分页 */
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import { inheritors, loadInheritors } from '@/store'

const router = useRouter()

// 进入页面时加载传承人数据；失败时静默处理，页面显示空结果
onMounted(() => {
  loadInheritors().catch(() => {})
})

/* 级别筛选选项与当前筛选条件 */
const levels = ['全部', '国家级', '省级', '市级']
const level = ref('全部')
const keyword = ref('')

/* 只展示处于启用状态的传承人 */
const activeInheritors = computed(() => inheritors.filter((m) => m.status === 'active'))

/* 按级别和关键词筛选；关键词匹配姓名或技艺 */
const filtered = computed(() => {
  let list = activeInheritors.value
  if (level.value !== '全部') {
    list = list.filter((m) => m.level === level.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim()
    list = list.filter((m) => (m.name || '').includes(kw) || (m.craft || '').includes(kw))
  }
  return list
})

/* 前端分页：每页 12 位传承人 */
const pageSize = 12
const page = ref(1)
const totalPage = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
/* 截取当前页要显示的传承人 */
const paged = computed(() => {
  const start = (page.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

// 级别或关键词变化时回到第一页，避免结果变少后停在空页
watch([level, keyword], () => {
  page.value = 1
})

/* 头像占位字：优先取技艺首字，其次姓名首字，最后用「匠」兜底 */
function glyphOf(m) {
  return (m.craft || m.name || '匠').charAt(0)
}

/* 级别名称到 CSS 类名后缀的映射 */
function levelClass(l) {
  return l === '国家级' ? 'national' : l === '省级' ? 'province' : 'city'
}

/* 跳转到传承人详情页 */
function goDetail(id) {
  router.push('/inheritor/' + id)
}
</script>

<style src="./InheritorShow.css"></style>
