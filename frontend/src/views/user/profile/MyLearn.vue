<!-- 个人中心 · 我的学习页：展示单门课程的报名状态、学习进度和课时列表 -->
<template>
  <div class="learn-page">
    <Nav />

    <!-- 加载完成后显示学习内容 -->
    <div class="ln-wrap" v-if="!loading">
      <button class="ln-back" @click="goBack">‹ 返回我的报名</button>

      <!-- 报名状态分支：未报名/审核中/已驳回/课程下架分别显示对应提示 -->
      <div v-if="state === 'no-enroll'" class="ln-empty">
        <p class="ln-empty-text">你还没有报名这门课程，报名后才能进入学习</p>
        <button class="ln-btn ln-btn-solid" @click="goCourse">查看课程并报名</button>
      </div>

      <div v-else-if="state === 'review'" class="ln-empty">
        <p class="ln-empty-text">报名正在等待管理员审核，录取后方可进入学习</p>
        <button class="ln-btn ln-btn-solid" @click="goBack">返回我的报名</button>
      </div>

      <div v-else-if="state === 'rejected'" class="ln-empty">
        <p class="ln-empty-text">
          报名未通过<template v-if="rejectReason">：{{ rejectReason }}</template>，可重新提交报名
        </p>
        <button class="ln-btn ln-btn-solid" @click="goPay">重新报名</button>
        <button class="ln-btn" @click="goBack">返回我的报名</button>
      </div>

      <div v-else-if="state === 'offline'" class="ln-empty">
        <p class="ln-empty-text">课程可能已下架，暂时无法观看学习内容</p>
        <button class="ln-btn" @click="goBack">返回我的报名</button>
      </div>

      <template v-else-if="course">
        <!-- 正常学习内容：课程信息、学习进度和课时列表 -->
        <header class="ln-head">
          <div class="ln-head-cover">
            <span class="ln-head-glyph">{{ course.glyph }}</span>
          </div>
          <div class="ln-head-body">
            <div class="ln-head-tags">
              <span class="ln-stage">{{ course.stage }}</span>
              <span class="ln-verified">✓ 已报名</span>
            </div>
            <h1 class="ln-title">{{ course.name }}</h1>
            <p class="ln-maker">{{ course.teacher }} · {{ course.craft }}</p>
          </div>
        </header>

        <!-- 学习进度：已完成课时数、百分比以及不同阶段的提示 -->
        <section class="ln-progress">
          <div class="ln-progress-head">
            <h3 class="ln-progress-title">{{ isDone ? '已结课' : (allDone ? '课时已全部学完' : '学习进度') }}</h3>
            <span class="ln-progress-num">已完成 {{ doneCount }} / {{ totalCount }} 课时 · {{ percent }}%</span>
          </div>
          <div class="ln-progress-bar"><i :style="{ width: percent + '%' }"></i></div>
          <p class="ln-progress-hint" v-if="isDone">这门课已结课，感谢你的参与！</p>
          <p class="ln-progress-hint" v-else-if="allDone">已学完全部课时，请等待传承人确认结课</p>
          <p class="ln-progress-hint ln-progress-sub" v-else>线下实操课时可点「标记完成」自行上报，传承人将在后台复核</p>
          <p class="ln-progress-schedule" v-if="course.schedule">开课 {{ course.schedule }}<template v-if="course.endDate"> ～ {{ course.endDate }} 结课</template> · 共 {{ totalCount }} 个课时</p>
        </section>

        <!-- 课时列表区块 -->
        <section class="ln-block">
          <div class="ln-section-head">
            <h2 class="ln-section-cn">课程进度</h2>
            <span class="ln-section-en">LESSONS</span>
          </div>

          <!-- 每个课时：序号、标题、时间地点，以及播放视频/标记完成操作 -->
          <div class="ln-lesson" v-for="(les, i) in lessonRows" :key="les.key">
            <span class="ln-lesson-num" :class="{ 'ln-lesson-num-done': isDoneKey(les.key) }">{{ numCn(i) }}</span>
            <div class="ln-lesson-body">
              <h4 class="ln-lesson-title">{{ les.title }}</h4>
              <p class="ln-lesson-desc" v-if="les.desc">{{ les.desc }}</p>
              <p class="ln-lesson-schedule" v-if="les.meta">{{ les.meta }}</p>
            </div>
            <div class="ln-lesson-side">
              <span class="ln-state" :class="{ 'ln-state-done': isDoneKey(les.key) }">{{ isDoneKey(les.key) ? '已完成' : '待学习' }}</span>
              <button
                v-if="les.playable"
                class="ln-btn ln-btn-sm"
                :class="{ 'ln-btn-solid': !isDoneKey(les.key) }"
                @click="openPlayer(les)"
              >播放视频</button>
              <button v-else class="ln-btn ln-btn-sm" :class="{ 'ln-btn-solid': !isDoneKey(les.key) }" @click="toggleDone(les.key)">
                {{ isDoneKey(les.key) ? '取消标记' : '标记完成' }}
              </button>
              <button v-if="isDoneKey(les.key) && les.playable" class="ln-btn ln-btn-sm ln-btn-cancel" @click="toggleDone(les.key)">撤销</button>
            </div>
          </div>

          <div v-if="!lessonRows.length" class="ln-lesson-empty">传承人尚未编排课时，请稍后再来</div>
        </section>
      </template>
    </div>

    <div v-else class="ln-wrap"><div class="ln-empty"><p class="ln-empty-text">加载中…</p></div></div>

    <!-- 视频播放弹窗：播放完整后自动标记该课时已完成 -->
    <el-dialog v-model="playerOpen" :title="playing?.title || '课时视频'" width="820px" :close-on-click-modal="false" @close="onPlayerClose">
      <video
        v-if="playing && playing.video"
        :src="playing.video"
        controls
        autoplay
        class="ln-player"
        @ended="onVideoEnded"
      ></video>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import { enrollmentState, loadEnrollments, updateMyEnrollmentCompleted, fetchCourseDetail } from '@/store'

// 从路由参数中读取当前课程 ID
const route = useRoute()
const router = useRouter()
const courseId = Number(route.params.courseId)

// 页面状态：loading 加载中 / no-enroll 未报名 / review 审核中 / rejected 已驳回 / offline 课程下架 / ok 正常
const loading = ref(true)
const state = ref('loading')
const detail = ref(null)
const rejectReason = ref('')
const completed = ref([])
let saving = false

/* 进入页面后的加载流程：
   1. 先加载报名记录，按 courseId 找到对应报名；
   2. 根据报名状态决定显示未报名、审核中、已驳回还是正常学习界面；
   3. 正常状态再拉取课程详情，拉取失败视为课程已下架。 */
onMounted(async () => {
  try {
    await loadEnrollments()
    const en = enrollmentState.list.find((e) => Number(e.courseId) === courseId)
    if (!en) {
      state.value = 'no-enroll'
      loading.value = false
      return
    }
    if (en.status === 'review') {
      state.value = 'review'
      loading.value = false
      return
    }
    if (en.status === 'rejected') {
      state.value = 'rejected'
      rejectReason.value = en.reviewComment || ''
      loading.value = false
      return
    }
    completed.value = Array.isArray(en.completed) ? en.completed.map(String) : []
    try {
      detail.value = await fetchCourseDetail(courseId)
      state.value = 'ok'
    } catch (e) {
      state.value = 'offline'
    }
  } catch (e) {
    state.value = 'offline'
  }
  loading.value = false
})

// 课程详情
const course = computed(() => detail.value)
// 报名状态是否为已结课
const isDone = computed(() => {
  const en = enrollmentState.list.find((e) => Number(e.courseId) === courseId)
  return en?.status === 'done'
})

/* 把课程详情中的课时转换成页面渲染需要的行数据：
   key 优先用课时编号，playable 表示该课时是否有已审核通过的视频。 */
const lessonRows = computed(() => {
  const list = detail.value?.lessons || []
  return list.map((l, i) => {
    const key = String((l.num != null && l.num !== '') ? l.num : (i + 1))
    const playable = !!(l.video && l.videoStatus === 'approved')
    return {
      key,
      title: l.title || '课时' + (i + 1),
      desc: l.desc || '',
      playable,
      video: l.video,
      meta: lessonMeta(l, playable),
    }
  })
})

// 生成课时的补充信息：上课时间、地点以及视频审核状态
function lessonMeta(les, playable) {
  const parts = []
  const schedule = les.scheduleDate ? les.scheduleDate + (les.scheduleTime ? ' ' + les.scheduleTime : '') : ''
  if (schedule) parts.push(schedule)
  if (les.address) parts.push(les.address)
  if (playable) parts.push('含线上演示视频')
  else if (les.videoStatus === 'pending') parts.push('演示视频待审核上线')
  else if (les.videoStatus === 'rejected') parts.push('演示视频未过审，请联系传承人')
  else parts.push('线下实操课时，完成后请自行标记')
  return parts.join(' · ')
}

// 判断某个课时是否已经在完成列表中
function isDoneKey(key) {
  return completed.value.includes(key)
}

// 进度统计：总课时、已完成课时、完成百分比和是否全部完成
const totalCount = computed(() => lessonRows.value.length)
const doneCount = computed(() => lessonRows.value.filter((r) => isDoneKey(r.key)).length)
const percent = computed(() => (totalCount.value ? Math.round((doneCount.value / totalCount.value) * 100) : 0))
const allDone = computed(() => totalCount.value > 0 && doneCount.value >= totalCount.value)

/* 保存学习进度：
   saving 防止重复提交；成功后用后端返回的 completed 列表刷新本地进度，
   失败时优先展示后端返回的错误信息。 */
async function pushCompleted(next) {
  if (saving) return
  const en = enrollmentState.list.find((e) => Number(e.courseId) === courseId)
  if (!en) return
  saving = true
  try {
    const upd = await updateMyEnrollmentCompleted(en.id, next)
    completed.value = (Array.isArray(upd.completed) ? upd.completed : []).map(String)
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '保存进度失败，请重试')
  } finally {
    saving = false
  }
}

// 切换课时完成状态：已完成则从列表移除，未完成则追加
async function toggleDone(key) {
  const next = isDoneKey(key) ? completed.value.filter((k) => k !== key) : [...completed.value, key]
  await pushCompleted(next)
}

// 视频弹窗状态；pendingKey 记录当前播放的课时，视频结束时用于标记完成
const playerOpen = ref(false)
const playing = ref(null)
let pendingKey = null

// 打开视频播放弹窗，并记住当前课时
function openPlayer(les) {
  playing.value = les
  pendingKey = les.key
  playerOpen.value = true
}

// 视频播放结束后，自动把当前课时标记为已完成
async function onVideoEnded() {
  const k = pendingKey
  pendingKey = null
  if (k && !isDoneKey(k)) {
    ElMessage.success('本课时已学完 ✓')
    await pushCompleted([...completed.value, k])
  }
}

// 关闭播放弹窗时清空待标记的课时
function onPlayerClose() {
  pendingKey = null
}

// 课时序号使用中文数字显示
const NUMS = '壹贰叁肆伍陆柒捌玖拾'
function numCn(i) {
  return i < NUMS.length ? NUMS[i] : String(i + 1)
}

// 页面跳转辅助函数：返回报名页、课程详情页或重新报名支付页
function goBack() {
  router.push('/profile/enroll')
}
function goCourse() {
  router.push('/course/' + courseId)
}
function goPay() {
  router.push('/pay/' + courseId)
}
</script>

<style src="./MyLearn.css"></style>
