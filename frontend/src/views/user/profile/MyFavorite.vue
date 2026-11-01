<!-- 个人中心 · 我的收藏页：展示收藏的文创作品，支持查看详情和取消收藏 -->
<template>
  <div class="favorite-page">
    <Nav />

    <!-- 页面主体：左侧个人中心侧边栏 + 右侧收藏网格 -->
    <div class="mf-wrap">
      <ProfileAside />

      <div class="mf-main">
        <header class="mf-head">
          <h1 class="mf-title">我的收藏</h1>
          <span class="mf-en">MY FAVORITES</span>
        </header>

        <!-- 工具栏：显示收藏数量 -->
        <div class="mf-toolbar">
          <span class="mf-count">共收藏 {{ favorites.length }} 件作品</span>
        </div>

        <!-- 收藏作品网格：点击卡片进入详情，右上角按钮取消收藏 -->
        <div class="mf-grid" v-if="favorites.length">
          <div
            v-for="f in favorites"
            :key="f.productId"
            class="mf-card"
            @click="goDetail(f)"
          >
            <div class="mf-cover" :style="coverStyle(f)">
              <span class="mf-glyph">{{ f.glyph }}</span>
              <button
                class="mf-unfav"
                title="取消收藏"
                @click.stop="unfavorite(f)"
              >
                ♥
              </button>
            </div>
            <div class="mf-body">
              <h3 class="mf-name">{{ f.name }}</h3>
              <p class="mf-maker">{{ f.inheritor }} · {{ f.craft }}</p>
            </div>
          </div>
        </div>

        <div v-else class="mf-empty">
          <!-- 空状态：没有收藏时引导去作品列表 -->
          <p class="mf-empty-text">还没有收藏任何作品</p>
          <button class="mf-btn mf-btn-solid" @click="goBrowse">去逛逛</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import ProfileAside from './ProfileAside.vue'
import { favoriteState, loadFavorites, unfavoriteProduct } from '@/store'

// 进入页面时加载收藏列表，失败时静默处理
onMounted(() => {
  loadFavorites().catch(() => {})
})

const router = useRouter()

// 收藏列表：直接读取全局 store 中的收藏状态
const favorites = computed(() => favoriteState.list)

// 有封面图时生成背景图样式，否则使用默认占位样式
function coverStyle(f) {
  if (f.cover) return { backgroundImage: 'url(' + f.cover + ')' }
  return {}
}

// 跳转到作品详情页
function goDetail(f) {
  router.push('/product/' + f.productId)
}

// 取消收藏：调用 store 方法移除收藏并提示结果
async function unfavorite(f) {
  try {
    await unfavoriteProduct(f.productId)
    ElMessage.success('已取消收藏')
  } catch (e) {
    ElMessage.error((e && e.message) || '取消收藏失败')
  }
}

// 空状态按钮：跳转到作品列表
function goBrowse() {
  router.push('/product')
}
</script>

<style src="./MyFavorite.css"></style>
