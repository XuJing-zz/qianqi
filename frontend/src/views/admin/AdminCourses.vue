<!-- 管理员课程审核页面：按状态选项卡分页查看课程，支持查看详情、通过、驳回与下架。 -->
<template>
  <AdminLayout>
    <div class="acr-wrap">
      <div class="acr-head">
        <div class="acr-head-left">
          <h2 class="acr-title">课程审核</h2>
          <p class="acr-sub">共 {{ pendingList.length }} 条待审核课程</p>
        </div>
        <!-- 状态选项卡：待审核 / 已通过 / 已驳回 / 已下架，右侧数字来自全局课程缓存 -->
        <div class="acr-head-tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="acr-tab"
            :class="{ 'acr-tab-active': activeTab === t.value }"
            @click="switchTab(t.value)"
          >
            {{ t.label }}<span class="acr-tab-count">{{ countOf(t.value) }}</span>
          </button>
        </div>
      </div>

      <!-- 课程列表区：卡片展示课程关键信息，按状态显示通过/驳回/下架按钮 -->
      <div v-if="loading" class="acr-loading">加载中…</div>
      <div v-else-if="rows.length" class="acr-list">
        <div v-for="c in rows" :key="c.id" class="acr-card">
          <div class="acr-cover">
            <span class="acr-cover-glyph">{{ c.craft.charAt(0) }}</span>
          </div>
          <div class="acr-body">
            <div class="acr-body-top">
              <h3 class="acr-name">{{ c.name }}</h3>
              <span class="acr-badge" :style="{ color: statusMap[c.status].color, borderColor: statusMap[c.status].color }">
                {{ statusMap[c.status].label }}
              </span>
            </div>
            <div class="acr-meta">
              <span class="acr-meta-item">技艺：{{ c.craft }}</span>
              <span class="acr-meta-item">类型：{{ c.stage }}</span>
              <span class="acr-meta-item">难度：{{ c.difficulty }}</span>
              <span class="acr-meta-item">课时：{{ c.duration }}</span>
              <span v-if="c.schedule" class="acr-meta-item">🕘 {{ c.schedule }}<template v-if="c.endDate"> ～ {{ c.endDate }}</template></span>
            </div>
            <div class="acr-meta">
              <span class="acr-meta-item">费用 ¥{{ c.priceNum }}</span>
              <span class="acr-meta-item">招生 {{ c.capacity }} 人</span>
              <span class="acr-meta-item">共 {{ (c.lessons || []).length }} 课时</span>
              <span v-if="c.submitTime" class="acr-meta-item">提交于 {{ c.submitTime }}</span>
            </div>
            <p class="acr-desc">{{ c.desc }}</p>

            <div v-if="c.status === 'rejected' && c.reviewComment" class="acr-reject">
              <span class="acr-reject-label">已驳回：</span>{{ c.reviewComment }}
            </div>

            <div class="acr-actions">
              <button class="acr-btn acr-btn-view" @click="openDetail(c)">查看详情</button>
              <template v-if="c.status === 'pending'">
                <button class="acr-btn acr-btn-pass" @click="approve(c)">通过</button>
                <button class="acr-btn acr-btn-reject" @click="openReject(c)">驳回</button>
              </template>
              <template v-else-if="c.status === 'approved'">
                <button class="acr-btn acr-btn-offline" @click="offline(c)">下架</button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="acr-empty">
        <span class="acr-empty-glyph">课</span>
        <p class="acr-empty-text">暂无{{ activeTabLabel }}课程</p>
      </div>

      <!-- 分页区：课程数量超过一页时显示 -->
      <div v-if="total > pageSize" class="acr-pager">
        <el-pagination
          background
          layout="prev, pager, next, total"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="onPage"
        />
      </div>
    </div>

    <!-- 详情抽屉区：展示课程完整信息与课时大纲，底部按状态提供审核操作 -->
    <el-drawer v-model="detailVisible" title="课程审核" size="min(720px, 94vw)" :close-on-click-modal="false" destroy-on-close>
      <div v-if="detail" class="acr-detail-body">
        <div class="acr-detail-head">
          <img v-if="detail.cover" :src="detail.cover" class="acr-detail-cover" alt="课程封面" />
          <span v-else class="acr-detail-glyph">{{ glyphOf(detail.craft) }}</span>
          <div class="acr-detail-headinfo">
            <div class="acr-detail-title">
              <h3 class="acr-detail-name">{{ detail.name }}</h3>
              <span class="acr-badge" :style="{ color: statusMap[detail.status].color, borderColor: statusMap[detail.status].color }">
                {{ statusMap[detail.status].label }}
              </span>
            </div>
            <p class="acr-detail-owner">授课传承人：{{ detail.ownerName || '—' }}<template v-if="detail.level"> · {{ detail.level }}<template v-if="detail.region"> · {{ detail.region }}</template></template></p>
          </div>
        </div>

        <div class="acr-detail-field">
          <span class="acr-detail-label">课程名称</span>
          <span class="acr-detail-value">{{ detail.name }}</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">技艺类型</span>
          <span class="acr-detail-value">{{ detail.craft }}</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">课程类型</span>
          <span class="acr-detail-value">{{ detail.stage }}</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">难度等级</span>
          <span class="acr-detail-value">{{ detail.difficulty }}</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">课时</span>
          <span class="acr-detail-value">{{ detail.duration }}</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">上课时间</span>
          <span class="acr-detail-value">{{ detail.schedule }}<template v-if="detail.endDate"> ～ {{ detail.endDate }} 结课</template></span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">招生人数</span>
          <span class="acr-detail-value">{{ detail.capacity }} 人</span>
        </div>
        <div class="acr-detail-field">
          <span class="acr-detail-label">费用</span>
          <span class="acr-detail-value acr-detail-price">¥{{ detail.priceNum }}</span>
        </div>
        <div class="acr-detail-field acr-detail-block">
          <span class="acr-detail-label">课程简介</span>
          <span class="acr-detail-value acr-detail-story">{{ detail.desc }}</span>
        </div>

        <div class="acr-detail-field">
          <span class="acr-detail-label">宣传视频</span>
          <span class="acr-detail-value">
            <a v-if="detail.video" :href="detail.video" target="_blank" rel="noopener" class="acr-link">{{ detail.video }}</a>
            <span v-else>—</span>
          </span>
        </div>

        <div v-if="detail.lessons && detail.lessons.length" class="acr-lessons">
          <div class="acr-lessons-head">
            <b>课时大纲</b>
            <span class="acr-lessons-count" title="名额以录取为准，待审核/已驳回的报名记录不占名额">{{ detail.lessons.length }} 课时 · 已录取 {{ detail.enrolled }} 人</span>
          </div>
          <div v-for="(l, i) in detail.lessons" :key="l.num || i" class="acr-lesson">
            <span class="acr-lesson-no">{{ pad(i + 1) }}</span>
            <div class="acr-lesson-main">
              <div class="acr-lesson-row">
                <b class="acr-lesson-title">{{ l.title || ('课时 ' + pad(i + 1)) }}</b>
                <span v-if="l.video || (l.videoStatus && l.videoStatus !== 'draft')" class="acr-lesson-state" :class="'acr-vs-' + l.videoStatus">{{ videoStateLabel(l.videoStatus) }}</span>
              </div>
              <p v-if="l.desc" class="acr-lesson-desc">{{ l.desc }}</p>
              <p v-if="l.scheduleDate || l.address" class="acr-lesson-time"><template v-if="l.scheduleDate">{{ l.scheduleDate }}<template v-if="l.scheduleTime"> {{ l.scheduleTime }}</template><template v-if="l.address"> · </template></template>{{ l.address }}</p>
              <p v-if="l.videoStatus === 'rejected' && l.videoReviewComment" class="acr-lesson-rej">视频驳回意见：{{ l.videoReviewComment }}</p>
              <a v-if="l.video" :href="l.video" target="_blank" rel="noopener" class="acr-lesson-play">播放已上传视频 ›</a>
            </div>
          </div>
        </div>
        <div v-else class="acr-detail-field acr-detail-block">
          <span class="acr-detail-label">课时大纲</span>
          <span class="acr-detail-value">尚未填写课时</span>
        </div>

        <div v-if="detail.submitTime" class="acr-detail-field">
          <span class="acr-detail-label">提交时间</span>
          <span class="acr-detail-value">{{ detail.submitTime }}</span>
        </div>

        <div v-if="detail.status === 'rejected' && detail.reviewComment" class="acr-reject">
          <span class="acr-reject-label">驳回意见：</span>{{ detail.reviewComment }}
        </div>
      </div>

      <template v-if="detail" #footer>
        <div class="acr-detail-footer">
          <template v-if="detail.status === 'pending'">
            <el-button type="primary" @click="approve(detail)">通过</el-button>
            <el-button type="danger" plain @click="openReject(detail)">驳回</el-button>
          </template>
          <template v-else-if="detail.status === 'approved'">
            <el-button @click="offline(detail)">下架</el-button>
          </template>
          <template v-else>
            <span class="acr-done">该课程已处理完毕</span>
          </template>
        </div>
      </template>
    </el-drawer>

    <!-- 驳回弹窗区：填写驳回原因，提交后反馈给传承人修改 -->
    <el-dialog v-model="rejectDialog" title="驳回课程" width="520px" :close-on-click-modal="false">
      <p class="acr-dialog-tip">请填写驳回原因，将反馈给传承人修改：</p>
      <el-input
        v-model="rejectComment"
        type="textarea"
        :rows="4"
        placeholder="如：课程大纲过于简单，请补充课时内容与材料清单"
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
import { listCourses } from '@/api/courses'
import { mapKeys } from '@/api/utils'
import { heritageCourses, courseStatusMap, reviewCourseAction, offlineCourseAction, addLog, authState } from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 课程状态配置（标签与颜色），来自 store，用于卡片和详情中的状态标签
const statusMap = courseStatusMap

// 审核状态选项卡配置，value 与后端课程 status 字段对应
const tabs = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
  { label: '已下架', value: 'offline' },
]
const activeTab = ref('pending') // 当前选中的审核状态，默认看待审核
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '') // 当前选项卡文案，用于空状态提示

// 全局缓存中待审核的课程，用于页面头部的待审核数量
const pendingList = computed(() => heritageCourses.filter((c) => c.status === 'pending'))

// 统计某个审核状态下的课程数量，供选项卡角标使用
function countOf(v) {
  return heritageCourses.filter((c) => c.status === v).length
}


// 把后端课程字段转成前端驼峰字段，并为价格、课时、报名人数等补齐默认值
function mapCourse(c) {
  const m = mapKeys(c)
  return {
    ...m,
    priceNum: m.priceNum ?? 0,
    submitTime: m.submitTime || '',
    reviewComment: m.reviewComment || '',
    enrolled: m.enrolled ?? 0,
    lessons: Array.isArray(m.lessons) ? m.lessons : [],
  }
}

/* 分页列表：usePagedList 统一管理分页状态，
   fetchPage 按当前审核状态向后端请求课程，切换选项卡时由 onFilter 重置到第一页。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapCourse,
  fetchPage: ({ page, page_size }) => listCourses({ status: activeTab.value, page, page_size }),
})

// 切换审核状态选项卡，并重新加载第一页课程
function switchTab(v) {
  activeTab.value = v
  onFilter()
}

// 首次进入页面时加载默认的待审核课程列表
onMounted(loadRows)

// 操作人名称：写入操作日志时使用，取不到登录用户时兜底为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 课时序号补零，例如 1 → 01
function pad(n) {
  return String(n).padStart(2, '0')
}
// 取技艺名称首字作为无封面时的占位字符
function glyphOf(name) {
  return (name || '').charAt(0) || '课'
}
// 课时视频审核状态转中文文案
function videoStateLabel(s) {
  return { draft: '未传视频', pending: '视频待审', approved: '视频已过审', rejected: '视频被驳回' }[s] || s || '未传视频'
}

const detailVisible = ref(false) // 详情抽屉是否显示
const detail = ref(null) // 当前查看的课程对象

// 打开课程详情抽屉
function openDetail(c) {
  detail.value = c
  detailVisible.value = true
}

// 审核动作完成后的收尾：关闭抽屉并刷新列表
async function afterAction() {
  detailVisible.value = false
  await loadRows()
}

/* 审核通过：课程将公开显示并允许学员报名，操作前二次确认。 */
function approve(c) {
  ElMessageBox.confirm(`审核通过后「${c.name}」将公开显示，学员可报名。确定通过？`, '通过审核', {
    confirmButtonText: '通过',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await reviewCourseAction(c.id, 'approve', '')
      addLog('review', operator(), '通过课程审核', `「${c.name}」`)
      ElMessage.success('已通过审核')
      await afterAction()
    })
    .catch(() => {})
}

/* 下架课程：下架后学员无法继续报名。 */
function offline(c) {
  ElMessageBox.confirm(`确定下架「${c.name}」吗？下架后学员将无法报名。`, '下架课程', {
    confirmButtonText: '下架',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await offlineCourseAction(c.id)
      addLog('review', operator(), '下架课程', `「${c.name}」`)
      ElMessage.success('已下架')
      await afterAction()
    })
    .catch(() => {})
}

const rejectDialog = ref(false) // 驳回弹窗是否显示
const rejectComment = ref('') // 驳回原因输入内容
let rejectTarget = null // 当前要驳回的课程（普通变量即可，不需要响应式）

// 打开驳回弹窗并清空上一次填写的原因
function openReject(c) {
  rejectTarget = c
  rejectComment.value = ''
  rejectDialog.value = true
}

/* 提交驳回：原因必填，成功后记录日志、关闭弹窗并刷新列表。 */
function confirmReject() {
  if (!rejectComment.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  if (rejectTarget) {
    const comment = rejectComment.value.trim()
    reviewCourseAction(rejectTarget.id, 'reject', comment)
      .then(async () => {
        addLog('review', operator(), '驳回课程', `「${rejectTarget.name}」：${comment}`)
        ElMessage.success('已驳回，意见已反馈给传承人')
        await afterAction()
      })
      .catch(() => ElMessage.error('驳回失败'))
  }
  rejectDialog.value = false
  rejectTarget = null
}
</script>

<style src="./AdminCourses.css"></style>

<style scoped>
/* 加载提示与分页条：居中/右对齐的基础布局 */
.acr-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
.acr-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
