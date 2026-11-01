<!-- 视频审核页：按课程课时的视频状态审核传承人上传的教学视频，支持通过与驳回 -->
<template>
  <AdminLayout>
    <div class="avr-wrap">
      <!-- 页头区：标题、待审核视频总数与状态切换标签 -->
      <div class="avr-head">
        <div class="avr-head-left">
          <h2 class="avr-title">视频审核</h2>
          <p class="avr-sub">共 {{ pendingList.length }} 条待审核视频</p>
        </div>
        <!-- 状态标签区：待审核 / 已通过 / 已驳回，标签后显示各自数量 -->
        <div class="avr-head-tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="avr-tab"
            :class="{ 'avr-tab-active': activeTab === t.value }"
            @click="switchTab(t.value)"
          >
            {{ t.label }}<span class="avr-tab-count">{{ countOf(t.value) }}</span>
          </button>
        </div>
      </div>

      <!-- 列表区：每条展示课时标题、所属课程、视频预览与审核操作 -->
      <div v-if="loading" class="avr-loading">加载中…</div>
      <div v-else-if="rows.length" class="avr-list">
        <div v-for="item in rows" :key="item.courseId + '-' + item.lessonIdx" class="avr-card">
          <div class="avr-body">
            <div class="avr-body-top">
              <div class="avr-title-line">
                <h3 class="avr-name">{{ item.lesson.title }}</h3>
                <span class="avr-badge" :style="{ color: statusMap[item.lesson.videoStatus].color, borderColor: statusMap[item.lesson.videoStatus].color }">
                  {{ statusMap[item.lesson.videoStatus].label }}
                </span>
              </div>
            </div>
            <div class="avr-meta">
              <span class="avr-meta-item">所属课程：{{ item.course.name }}</span>
              <span class="avr-meta-item">技艺：{{ item.course.craft }}</span>
              <span v-if="item.lesson.scheduleDate" class="avr-meta-item">🕘 {{ item.lesson.scheduleDate }} {{ item.lesson.scheduleTime }}</span>
              <span v-if="item.lesson.videoName" class="avr-meta-item">文件：{{ item.lesson.videoName }}</span>
            </div>
            <p v-if="item.lesson.desc" class="avr-desc">{{ item.lesson.desc }}</p>

            <div v-if="item.lesson.video" class="avr-video">
              <video :src="item.lesson.video" controls preload="metadata" class="avr-video-el"></video>
              <span class="avr-videoname">{{ item.lesson.videoName || '视频' }}</span>
            </div>

            <div v-if="item.lesson.videoStatus === 'rejected' && item.lesson.videoReviewComment" class="avr-reject">
              <span class="avr-reject-label">已驳回：</span>{{ item.lesson.videoReviewComment }}
            </div>

            <!-- 操作区：待审核的视频显示「通过/驳回」按钮 -->
            <div class="avr-actions">
              <button class="avr-btn avr-btn-view" @click="openDetail(item)">查看详情</button>
              <template v-if="item.lesson.videoStatus === 'pending'">
                <button class="avr-btn avr-btn-pass" @click="approve(item)">通过</button>
                <button class="avr-btn avr-btn-reject" @click="openReject(item)">驳回</button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态：当前状态下没有视频时显示 -->
      <div v-else class="avr-empty">
        <span class="avr-empty-glyph">视</span>
        <p class="avr-empty-text">暂无{{ activeTabLabel }}视频</p>
      </div>

      <!-- 分页区：总条数超过每页数量时显示分页器 -->
      <div v-if="total > pageSize" class="avr-pager">
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

    <!-- 详情抽屉区：展示课时信息、视频播放器和驳回意见 -->
    <el-drawer v-model="detailVisible" title="视频详情" size="600px" :close-on-click-modal="false" destroy-on-close>
      <div v-if="detail" class="avr-detail-body">
        <div class="avr-detail-title">
          <h3 class="avr-detail-name">{{ detail.lesson.title || '（未填写标题）' }}</h3>
          <span class="avr-badge" :style="{ color: statusMap[detail.lesson.videoStatus].color, borderColor: statusMap[detail.lesson.videoStatus].color }">
            {{ statusMap[detail.lesson.videoStatus].label }}
          </span>
        </div>

        <div class="avr-detail-field">
          <span class="avr-detail-label">所属课程</span>
          <span class="avr-detail-value">{{ detail.course.name }}</span>
        </div>
        <div class="avr-detail-field">
          <span class="avr-detail-label">技艺类型</span>
          <span class="avr-detail-value">{{ detail.course.craft }}</span>
        </div>
        <div class="avr-detail-field">
          <span class="avr-detail-label">课时标题</span>
          <span class="avr-detail-value">{{ detail.lesson.title || '—' }}</span>
        </div>
        <div class="avr-detail-field acr-detail-block" style="display: flex; flex-direction: column; gap: 6px;">
          <span class="avr-detail-label">课时简介</span>
          <span class="avr-detail-value avr-detail-story">{{ detail.lesson.desc || '—' }}</span>
        </div>
        <div class="avr-detail-field">
          <span class="avr-detail-label">上课时间</span>
          <span class="avr-detail-value">{{ (detail.lesson.scheduleDate ? detail.lesson.scheduleDate + ' ' + detail.lesson.scheduleTime : '—') }}</span>
        </div>
        <div class="avr-detail-field">
          <span class="avr-detail-label">视频文件</span>
          <span class="avr-detail-value">{{ detail.lesson.videoName || '—' }}</span>
        </div>

        <div v-if="detail.lesson.video" class="avr-detail-video">
          <video :src="detail.lesson.video" controls preload="metadata" class="avr-detail-video-el"></video>
        </div>
        <div v-else class="avr-detail-novideo">未上传视频</div>

        <div v-if="detail.lesson.videoStatus === 'rejected' && detail.lesson.videoReviewComment" class="avr-reject">
          <span class="avr-reject-label">驳回意见：</span>{{ detail.lesson.videoReviewComment }}
        </div>
      </div>

      <!-- 抽屉底部操作区：待审核视频可在此直接通过或驳回 -->
      <template v-if="detail" #footer>
        <div class="avr-detail-footer">
          <template v-if="detail.lesson.videoStatus === 'pending'">
            <el-button type="primary" @click="approve(detail)">通过</el-button>
            <el-button type="danger" plain @click="openReject(detail)">驳回</el-button>
          </template>
          <template v-else>
            <span class="avr-done">该视频已处理完毕</span>
          </template>
        </div>
      </template>
    </el-drawer>

    <!-- 驳回弹窗区：填写驳回原因，提交后反馈给传承人重新录制 -->
    <el-dialog v-model="rejectDialog" title="驳回视频" width="520px" :close-on-click-modal="false">
      <p class="avr-dialog-tip">请填写驳回原因，将反馈给传承人修改：</p>
      <el-input
        v-model="rejectComment"
        type="textarea"
        :rows="4"
        placeholder="如：视频画面抖动明显，声音不清晰，请重新录制后再次提交"
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
import { listVideoReviews } from '@/api/courses'
import { mapKeys } from '@/api/utils'
import { heritageCourses, videoStatusMap, reviewVideoAction, addLog, authState } from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 视频状态字典：把状态值映射为文案与颜色，供状态徽标使用
const statusMap = videoStatusMap

// 视频审核状态标签配置，决定页头可切换的三种列表
const tabs = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
]
// 当前选中的视频状态，默认展示待审核
const activeTab = ref('pending')
// 当前标签对应的中文名称，用于空状态文案
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')


/* 汇总所有课程下的课时视频：
   遍历每个课程及其 lessons，把课程、课时和下标组合成一条记录，
   供页头待审核数量统计使用。 */
const allVideos = computed(() => {
  const result = []
  heritageCourses.forEach((c) => {
    if (!c.lessons) return
    c.lessons.forEach((les, idx) => {
      result.push({ course: c, lesson: les, courseId: c.id, lessonIdx: idx })
    })
  })
  return result
})

// 待审核视频列表，用于页头总数展示
const pendingList = computed(() => allVideos.value.filter((v) => v.lesson.videoStatus === 'pending'))

// 统计某个视频状态下有多少条课时，显示在对应标签后面
function countOf(v) {
  return allVideos.value.filter((x) => x.lesson.videoStatus === v).length
}

/* 整理后端返回的视频审核行：
   拆成 course（所属课程）与 lesson（课时详情）两层结构，
   缺失字段统一兜底为空串，保证模板可以直接渲染。 */
function mapVideoRow(raw) {
  const m = mapKeys(raw)
  return {
    courseId: m.courseId,
    lessonIdx: m.lessonIndex,
    course: { id: m.courseId, name: m.courseName, craft: m.craft || '' },
    lesson: {
      num: m.num,
      title: m.title || '',
      desc: m.desc || '',
      scheduleDate: m.scheduleDate || '',
      scheduleTime: m.scheduleTime || '',
      video: m.video || '',
      videoName: m.videoName || '',
      videoStatus: m.videoStatus || '',
      videoReviewComment: m.videoReviewComment || '',
    },
  }
}

/* 分页加载视频审核列表：每次按当前状态、页码与每页条数请求，
   由 usePagedList 统一维护列表、总数与加载状态。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapVideoRow,
  fetchPage: ({ page, page_size }) => listVideoReviews({
    video_status: activeTab.value,
    page,
    page_size,
  }),
})

// 切换审核状态标签：更新状态后回到第一页重新加载
function switchTab(v) {
  activeTab.value = v
  onFilter()
}

// 页面首次进入时加载待审核列表第一页
onMounted(loadRows)

// 当前操作人：取登录管理员姓名，缺省为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 详情抽屉状态：是否显示，以及当前查看的视频记录
const detailVisible = ref(false)
const detail = ref(null)

// 打开视频详情抽屉
function openDetail(item) {
  detail.value = item
  detailVisible.value = true
}

// 审核操作完成后的统一收尾：关闭详情抽屉并刷新列表
async function afterAction() {
  detailVisible.value = false
  await loadRows()
}

/* 通过视频审核：确认后按课程 ID 与课时下标调用审核接口，
   成功后记录操作日志、提示并刷新列表。 */
function approve(item) {
  ElMessageBox.confirm(`审核通过后「${item.lesson.title}」视频将对学员开放。确定通过？`, '通过审核', {
    confirmButtonText: '通过',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await reviewVideoAction(item.courseId, item.lessonIdx, 'approve', '')
      addLog('review', operator(), '通过视频审核', `「${item.course.name}」${item.lesson.num || ''}课「${item.lesson.title}」`)
      ElMessage.success('已通过审核')
      await afterAction()
    })
    .catch(() => {})
}

// 驳回弹窗状态：是否显示、驳回原因输入值以及目标视频记录
const rejectDialog = ref(false)
const rejectComment = ref('')
let rejectTarget = null

// 打开驳回弹窗：记录目标视频并清空上一次的驳回原因
function openReject(item) {
  rejectTarget = item
  rejectComment.value = ''
  rejectDialog.value = true
}

/* 确认驳回：校验原因必填，按课程 ID 与课时下标提交 reject 与原因，
   成功后记录日志、提示并刷新列表；最后关闭弹窗并清空目标。 */
function confirmReject() {
  if (!rejectComment.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  if (rejectTarget) {
    const comment = rejectComment.value.trim()
    reviewVideoAction(rejectTarget.courseId, rejectTarget.lessonIdx, 'reject', comment)
      .then(async () => {
        addLog('review', operator(), '驳回视频', `「${rejectTarget.course.name}」${rejectTarget.lesson.num || ''}课：${comment}`)
        ElMessage.success('已驳回，意见已反馈给传承人')
        await afterAction()
      })
      .catch(() => ElMessage.error('驳回失败'))
  }
  rejectDialog.value = false
  rejectTarget = null
}
</script>

<style src="./AdminVideos.css"></style>

<style scoped>
/* 加载提示：居中显示并留出上下间距 */
.avr-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
/* 分页条：右对齐，与列表拉开距离 */
.avr-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
