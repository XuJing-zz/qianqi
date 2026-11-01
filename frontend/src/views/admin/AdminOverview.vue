<!-- 后台概览页：汇总待审核、待发货、学员与库存等关键数据，卡片可点击进入对应管理页 -->
<template>
  <AdminLayout>
    <div class="ado-wrap">
      <!-- 欢迎区：显示管理员称呼与当前各项待办数量 -->
      <div class="ado-hero">
        <h2 class="ado-title">管理后台</h2>
        <p class="ado-sub">欢迎，{{ userName }}。待处理审核 {{ totalPending }} 项、待审核订单 {{ reviewOrderCount }} 单、待发货订单 {{ paidOrderCount }} 单<template v-if="lowStockCount">、库存告急作品 {{ lowStockCount }} 件</template>。</p>
      </div>

      <!-- 数据卡片区：点击任意卡片跳转到对应的管理页面 -->
      <div class="ado-grid">
        <div class="ado-card" @click="go('/admin/courses')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': pendingCourseCount > 0 }">{{ pendingCourseCount }}</span>
          <span class="ado-card-label">待审核课程</span>
        </div>
        <div class="ado-card" @click="go('/admin/skills')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': pendingSkillCount > 0 }">{{ pendingSkillCount }}</span>
          <span class="ado-card-label">待审核技艺档案</span>
        </div>
        <div class="ado-card" @click="go('/admin/product-review')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': pendingProductCount > 0 }">{{ pendingProductCount }}</span>
          <span class="ado-card-label">待审核作品</span>
        </div>
        <div class="ado-card" @click="go('/admin/videos')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': pendingVideoCount > 0 }">{{ pendingVideoCount }}</span>
          <span class="ado-card-label">待审核视频</span>
        </div>
        <div class="ado-card" @click="go('/admin/orders')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': reviewOrderCount > 0 }">{{ reviewOrderCount }}</span>
          <span class="ado-card-label">待审核订单</span>
        </div>
        <div class="ado-card" @click="go('/admin/orders')">
          <span class="ado-card-num" :class="{ 'ado-card-num-warn': paidOrderCount > 0 }">{{ paidOrderCount }}</span>
          <span class="ado-card-label">待发货订单</span>
        </div>
        <div class="ado-card" @click="go('/admin/students')">
          <span class="ado-card-num">{{ studentCount }}</span>
          <span class="ado-card-label">学员总数</span>
        </div>
        <div class="ado-card" @click="go('/admin/products')">
          <span class="ado-card-num" :class="{ 'ado-card-num-amber': lowStockCount > 0 }">{{ lowStockCount }}</span>
          <span class="ado-card-label">低库存作品</span>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from './AdminLayout.vue'
import { heritageCourses, heritageSkills, heritageProducts, heritageOrders, heritageStudents, authState, loadHeritageCourses, loadSkills, loadProducts, loadHeritageOrders, loadStudents } from '@/store'

// 路由实例：卡片点击时用它跳转到目标管理页
const router = useRouter()

/* 进入概览页时并行加载课程、技艺、作品、订单与学员数据；
   allSettled 保证任一接口失败都不影响其余统计。 */
onMounted(() => {
  Promise.allSettled([loadHeritageCourses(), loadSkills(), loadProducts(), loadHeritageOrders(), loadStudents()])
})

// 当前登录管理员称呼，取不到时显示“管理员”
const userName = computed(() => authState.user?.name || '管理员')
/* 各类待办统计：
   课程、技艺档案、作品统计 status === 'pending' 的数量，
   视频统计所有课程课时中 videoStatus === 'pending' 的数量。 */
const pendingCourseCount = computed(() => heritageCourses.filter((c) => c.status === 'pending').length)
const pendingSkillCount = computed(() => heritageSkills.filter((s) => s.status === 'pending').length)
const pendingProductCount = computed(() => heritageProducts.filter((p) => p.status === 'pending').length)
const pendingVideoCount = computed(() => {
  let n = 0
  heritageCourses.forEach((c) => {
    ;(c.lessons || []).forEach((les) => {
      if (les.videoStatus === 'pending') n++
    })
  })
  return n
})
// 订单待办：review 为待审核，paid 为已支付待发货
const reviewOrderCount = computed(() => heritageOrders.filter((o) => o.status === 'review').length)
const paidOrderCount = computed(() => heritageOrders.filter((o) => o.status === 'paid').length)
// 学员总数
const studentCount = computed(() => heritageStudents.length)
// 所有内容类待审核数量之和，用于欢迎语中的总待办提示
const totalPending = computed(() => pendingCourseCount.value + pendingSkillCount.value + pendingProductCount.value + pendingVideoCount.value)
// 低库存作品：已上架、可售且库存不高于预警阈值的作品数量
const lowStockCount = computed(() =>
  heritageProducts.filter((p) => p.status === 'approved' && p.saleable && Number(p.stock ?? 0) <= Number(p.alertThreshold ?? 5)).length
)

// 卡片点击跳转到指定后台路由
function go(path) {
  router.push(path)
}
</script>

<style src="./AdminOverview.css"></style>
