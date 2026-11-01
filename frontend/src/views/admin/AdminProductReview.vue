<!-- 作品审核页：按状态查看传承人提交的作品，支持通过上架、驳回、下架与详情查看 -->
<template>
  <AdminLayout>
    <div class="aprv-wrap">
      <!-- 页头区：标题、待审核总数与状态切换标签 -->
      <div class="aprv-head">
        <div class="aprv-head-left">
          <h2 class="aprv-title">作品审核</h2>
          <p class="aprv-sub">共 {{ pendingList.length }} 条待审核上架申请</p>
        </div>
        <!-- 状态标签区：待审核 / 已通过 / 已驳回 / 已下架，标签后显示各自数量 -->
        <div class="aprv-head-tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="aprv-tab"
            :class="{ 'aprv-tab-active': activeTab === t.value }"
            @click="switchTab(t.value)"
          >
            {{ t.label }}<span class="aprv-tab-count">{{ countOf(t.value) }}</span>
          </button>
        </div>
      </div>

      <!-- 列表区：每张卡片展示作品封面、名称、状态、工艺信息与审核操作 -->
      <div v-if="loading" class="aprv-loading">加载中…</div>
      <div v-else-if="rows.length" class="aprv-list">
        <div v-for="p in rows" :key="p.id" class="aprv-card">
          <div class="aprv-cover">
            <img v-if="p.cover" :src="p.cover" class="aprv-cover-img" alt="" />
            <span v-else class="aprv-cover-glyph">{{ p.glyph || p.name.charAt(0) }}</span>
            <span v-if="p.images && p.images.length > 1" class="aprv-cover-count">+{{ p.images.length - 1 }}</span>
          </div>
          <div class="aprv-body">
            <div class="aprv-body-top">
              <h3 class="aprv-name">{{ p.name }}</h3>
              <span class="aprv-badge" :style="{ color: statusMap[p.status].color, borderColor: statusMap[p.status].color }">
                {{ statusMap[p.status].label }}
              </span>
            </div>
            <div class="aprv-meta">
              <span class="aprv-meta-item">工艺：{{ p.craft }}</span>
              <span class="aprv-meta-item">分类：{{ p.category }}</span>
              <span class="aprv-meta-item">传承人：{{ p.inheritor }} · {{ p.level }}</span>
              <span v-if="p.saleable" class="aprv-meta-item">售价 ¥{{ p.price }}</span>
              <span v-else class="aprv-meta-item">非卖品</span>
              <span v-if="p.images && p.images.length" class="aprv-meta-item">{{ p.images.length }} 张照片</span>
              <span v-if="p.submitTime" class="aprv-meta-item">提交于 {{ p.submitTime }}</span>
            </div>
            <p class="aprv-desc">{{ p.story }}</p>

            <div v-if="p.status === 'rejected' && p.reviewComment" class="aprv-reject">
              <span class="aprv-reject-label">已驳回：</span>{{ p.reviewComment }}
            </div>

            <!-- 操作区：待审核可「通过/驳回」，已通过可「下架」 -->
            <div class="aprv-actions">
              <button class="aprv-btn aprv-btn-view" @click="openDetail(p)">查看详情</button>
              <template v-if="p.status === 'pending'">
                <button class="aprv-btn aprv-btn-pass" @click="approve(p)">通过上架</button>
                <button class="aprv-btn aprv-btn-reject" @click="openReject(p)">驳回</button>
              </template>
              <template v-else-if="p.status === 'approved'">
                <button class="aprv-btn aprv-btn-offline" @click="offline(p)">下架</button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态：当前状态下没有作品时显示 -->
      <div v-else class="aprv-empty">
        <span class="aprv-empty-glyph">作</span>
        <p class="aprv-empty-text">暂无{{ activeTabLabel }}作品</p>
      </div>

      <!-- 分页区：总条数超过每页数量时显示分页器 -->
      <div v-if="total > pageSize" class="aprv-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>

    <!-- 详情抽屉区：展示作品照片、工艺参数、故事、亮点与当前审核状态 -->
    <el-drawer v-model="detailVisible" title="作品审核" size="min(600px, 94vw)" :close-on-click-modal="false" destroy-on-close>
      <div v-if="detail" class="aprv-detail-body">
        <div class="aprv-detail-photos">
          <div v-for="(img, i) in photoList" :key="i" class="aprv-detail-photo-item">
            <img :src="img" class="aprv-detail-photo" alt="" />
            <span v-if="i === 0 && detail.images && detail.images.length" class="aprv-detail-photo-tag">封面</span>
          </div>
          <div v-if="!photoList.length" class="aprv-detail-noimg">
            <span class="aprv-detail-noimg-glyph">{{ detail.glyph || detail.name.charAt(0) }}</span>
            <span class="aprv-detail-noimg-text">尚未上传照片</span>
          </div>
        </div>

        <div class="aprv-detail-title">
          <h3 class="aprv-detail-name">{{ detail.name }}</h3>
          <span class="aprv-badge" :style="{ color: statusMap[detail.status].color, borderColor: statusMap[detail.status].color }">
            {{ statusMap[detail.status].label }}
          </span>
        </div>

        <div class="aprv-detail-field">
          <span class="aprv-detail-label">作品名称</span>
          <span class="aprv-detail-value">{{ detail.name }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">技艺门类</span>
          <span class="aprv-detail-value">{{ detail.craft }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">品类</span>
          <span class="aprv-detail-value">{{ detail.category }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">材质</span>
          <span class="aprv-detail-value">{{ detail.material }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">尺寸</span>
          <span class="aprv-detail-value">{{ detail.size }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">是否可售</span>
          <span class="aprv-detail-value">
            <span class="aprv-sale-tag" :class="detail.saleable ? 'aprv-sale-on' : 'aprv-sale-off'">
              {{ detail.saleable ? '可售' : '非卖（仅展示）' }}
            </span>
          </span>
        </div>
        <div v-if="detail.saleable" class="aprv-detail-field">
          <span class="aprv-detail-label">售价</span>
          <span class="aprv-detail-value aprv-detail-price">¥{{ detail.price }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">标签</span>
          <span class="aprv-detail-value">{{ detail.flag || '—' }}</span>
        </div>
        <div class="aprv-detail-field">
          <span class="aprv-detail-label">作品故事</span>
          <span class="aprv-detail-value aprv-detail-story">{{ detail.story }}</span>
        </div>

        <div class="aprv-detail-field aprv-detail-block">
          <span class="aprv-detail-label">工艺亮点</span>
          <div class="aprv-detail-value">
            <ul v-if="detail.highlights && detail.highlights.length" class="aprv-detail-hls">
              <li v-for="(h, i) in detail.highlights" :key="i">{{ h }}</li>
            </ul>
            <span v-else>—</span>
          </div>
        </div>

        <div class="aprv-detail-field">
          <span class="aprv-detail-label">作者</span>
          <span class="aprv-detail-value">{{ detail.inheritor }}（{{ detail.level }}）</span>
        </div>
        <div v-if="detail.ownerName" class="aprv-detail-field">
          <span class="aprv-detail-label">申报账号</span>
          <span class="aprv-detail-value">{{ detail.ownerName }}</span>
        </div>
        <div v-if="detail.submitTime" class="aprv-detail-field">
          <span class="aprv-detail-label">提交时间</span>
          <span class="aprv-detail-value">{{ detail.submitTime }}</span>
        </div>

        <div v-if="detail.status === 'rejected' && detail.reviewComment" class="aprv-reject">
          <span class="aprv-reject-label">驳回意见：</span>{{ detail.reviewComment }}
        </div>
      </div>

      <!-- 抽屉底部操作区：根据当前状态显示通过/驳回/下架 -->
      <template v-if="detail" #footer>
        <div class="aprv-detail-footer">
          <template v-if="detail.status === 'pending'">
            <el-button type="primary" @click="approve(detail)">通过上架</el-button>
            <el-button type="danger" plain @click="openReject(detail)">驳回</el-button>
          </template>
          <template v-else-if="detail.status === 'approved'">
            <el-button @click="offline(detail)">下架</el-button>
          </template>
          <template v-else>
            <span class="aprv-done">该作品已处理完毕</span>
          </template>
        </div>
      </template>
    </el-drawer>

    <!-- 驳回弹窗区：填写驳回原因，提交后反馈给传承人修改 -->
    <el-dialog v-model="rejectDialog" title="驳回上架申请" width="520px" :close-on-click-modal="false">
      <p class="aprv-dialog-tip">请填写驳回原因，将反馈给传承人修改：</p>
      <el-input
        v-model="rejectComment"
        type="textarea"
        :rows="4"
        placeholder="如：缺少多角度照片，或故事描述过于简单，请补充工艺细节"
      />
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listProducts } from '@/api/products'
import { mapKeys } from '@/api/utils'
import { heritageProducts, productStatusMap, reviewProductAction, updateProductAction, addLog, authState } from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 状态字典：把后端状态值映射为文案与颜色，供状态徽标使用
const statusMap = productStatusMap

// 审核状态标签配置，决定页头可切换的四种列表
const tabs = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
  { label: '已下架', value: 'offline' },
]
// 当前选中的审核状态，默认展示待审核
const activeTab = ref('pending')

// 当前标签对应的中文名称，用于空状态文案
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')

// 待审核作品列表：由 store 中的作品数据统计，用于页头总数展示
const pendingList = computed(() => heritageProducts.filter((p) => p.status === 'pending'))

// 统计某个状态下有多少件作品，显示在对应标签后面
function countOf(v) {
  return heritageProducts.filter((p) => p.status === v).length
}

// 当前操作人：取登录管理员姓名，缺省为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}


/* 整理后端作品数据：价格转数字，照片与工艺亮点兜底为数组，
   提交时间、驳回意见缺失时给空串，避免模板渲染报错。 */
function mapProductRow(p) {
  const m = mapKeys(p)
  return { ...m, price: Number(m.price ?? 0), images: Array.isArray(m.images) ? m.images : [], highlights: Array.isArray(m.highlights) ? m.highlights : [], submitTime: m.submitTime || '', reviewComment: m.reviewComment || '' }
}

/* 分页加载作品列表：每次按当前标签状态、页码和每页条数请求，
   由 usePagedList 统一维护列表、总数与加载状态。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapProductRow,
  fetchPage: ({ page, page_size }) => listProducts({ status: activeTab.value, page, page_size }),
})

// 切换审核状态标签：更新状态后回到第一页重新加载
function switchTab(v) {
  activeTab.value = v
  onFilter()
}

// 页面首次进入时加载当前标签第一页数据
onMounted(loadRows)

// 审核操作完成后的统一收尾：关闭详情抽屉并刷新列表
async function afterAction() {
  detailVisible.value = false
  await loadRows()
}

// 详情抽屉状态：是否显示，以及当前查看的作品
const detailVisible = ref(false)
const detail = ref(null)

// 详情照片列表：优先用多图数组，没有多图时退回封面，都没有则为空
const photoList = computed(() => {
  if (!detail.value) return []
  if (detail.value.images && detail.value.images.length) return detail.value.images.slice()
  if (detail.value.cover) return [detail.value.cover]
  return []
})

// 打开作品详情抽屉
function openDetail(p) {
  detail.value = p
  detailVisible.value = true
}

/* 通过上架审核：确认后调用审核接口，记录操作日志并刷新列表。 */
function approve(p) {
  ElMessageBox.confirm(`审核通过后「${p.name}」将上架，前台「文创作品」页可购买查看。确定通过？`, '通过上架审核', {
    confirmButtonText: '通过',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await reviewProductAction(p.id, 'approve', '')
      addLog('review', operator(), '通过作品审核', `「${p.name}」已通过并上架`)
      ElMessage.success('已通过审核，作品已上架')
      await afterAction()
    })
    .catch(() => {})
}

/* 下架作品：确认后把状态更新为 offline，写日志并刷新列表。 */
function offline(p) {
  ElMessageBox.confirm(`确定下架「${p.name}」吗？下架后前台不再展示。`, '下架作品', {
    confirmButtonText: '下架',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await updateProductAction(p.id, { status: 'offline' })
      addLog('review', operator(), '下架作品', `「${p.name}」已下架`)
      ElMessage.success('已下架')
      await afterAction()
    })
    .catch(() => {})
}

// 驳回弹窗状态：是否显示、驳回原因输入值以及被驳回的作品
const rejectDialog = ref(false)
const rejectComment = ref('')
let rejectTarget = null

// 打开驳回弹窗：记录目标作品并清空上一次的驳回原因
function openReject(p) {
  rejectTarget = p
  rejectComment.value = ''
  rejectDialog.value = true
}

/* 确认驳回：校验原因必填，调用审核接口提交 reject 与原因，
   成功后记录日志、提示并刷新列表；无论成败最后都关闭弹窗。 */
function confirmReject() {
  if (!rejectComment.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  if (rejectTarget) {
    const comment = rejectComment.value.trim()
    reviewProductAction(rejectTarget.id, 'reject', comment)
      .then(async () => {
        addLog('review', operator(), '驳回作品', `「${rejectTarget.name}」：${comment}`)
        ElMessage.success('已驳回，意见已反馈给传承人')
        await afterAction()
      })
      .catch(() => ElMessage.error('驳回失败'))
  }
  rejectDialog.value = false
  rejectTarget = null
}
</script>

<style src="./AdminProductReview.css"></style>

<style scoped>

/* 加载提示：居中显示并留出上下间距 */
.aprv-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
/* 分页条：右对齐，与列表拉开距离 */
.aprv-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
