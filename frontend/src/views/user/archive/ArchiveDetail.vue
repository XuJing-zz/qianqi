<!-- 技艺详情路由页：根据路由 id 找到技艺，复用 SkillDetailPage 展示 -->
<template>
  <div class="archive-detail-route">
    <!-- 详情主体；父组件通过 after-hero 具名插槽把导航栏插到首屏之后 -->
    <SkillDetailPage :skill="item">
      <template #after-hero><Nav /></template>
    </SkillDetailPage>
    <!-- 数据尚未加载到、详情主体不渲染时，单独显示导航栏 -->
    <Nav v-if="!item" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import SkillDetailPage from './SkillDetailPage.vue'
import { heritageSkills, loadSkills } from '@/store'

const route = useRoute()

// 进入页面时加载技艺档案；失败时静默处理，由 item 为空的分支给出提示
onMounted(() => {
  loadSkills().catch(() => {})
})

/* 从路由参数中取 id，在共享状态里查找对应技艺；找不到返回 null */
const item = computed(() => {
  const id = Number(route.params.id)
  return heritageSkills.find((s) => s.id === id) || null
})
</script>

<style scoped>
/* 让路由容器至少撑满一屏，避免内容不足时页脚上浮 */
.archive-detail-route {
  min-height: 100vh;
}
</style>
