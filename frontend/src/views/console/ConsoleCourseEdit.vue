<!-- 传承人工作台 · 课程新建/编辑：维护课程基础信息、课时排期与课时视频，并根据审核状态切换保存/提交动作 -->
<template>
  <!-- 工作台统一布局；ready 为 false 时先显示加载或未找到提示 -->
  <ConsoleLayout>
    <div class="cce-wrap" v-if="ready">
      <!-- 返回「我的课程」列表 -->
      <button class="cce-back" @click="goBack">‹ 返回我的课程</button>

      <!-- 课程头部：封面、课程名、技艺/难度/时长与审核状态；新建时显示表单中的课程名 -->
      <div class="cce-head">
        <div class="cce-head-left">
          <div class="cce-cover">
            <img v-if="f.cover" :src="f.cover" class="cce-cover-img" alt="课程封面" />
            <span v-else>{{ f.name.charAt(0) || '课' }}</span>
          </div>
          <div class="cce-head-info">
            <span class="cce-stage">{{ isNew ? '新建课程' : course.stage }}</span>
            <h2 class="cce-name">{{ isNew ? (f.name || '新建课程') : course.name }}</h2>
            <p class="cce-meta">
              {{ isNew ? '' : course.craft + ' · ' + course.difficulty + ' · ' + course.duration }}
            </p>
            <p v-if="!isNew" class="cce-badge" :style="{ color: statusMap[course.status].color, borderColor: statusMap[course.status].color }">
              {{ statusMap[course.status].label }}
            </p>
          </div>
        </div>
      </div>

      <!-- 已通过课程的修改提示：只改课时保持已通过，改基础信息会重新审核 -->
      <div v-if="!isNew && course.status === 'approved'" class="cce-notice">
        已通过课程：修改课时内容（含上传课时视频）将保持“已通过”；一旦修改基础信息，将重新提交管理员审核，通过前不公开。
      </div>

      <!-- 区块一：课程基本信息表单 -->
      <div class="cce-section">
        <div class="cce-section-head">
          <h3 class="cce-section-title">课程基本信息</h3>
          <p class="cce-section-sub">封面图与课程起止日期为必填，用于对外展示与课时排期</p>
        </div>

        <div class="cce-grid">
          <!-- 课程封面：必填，上传后用于课程卡片与详情页 -->
          <div class="cce-field cce-field-full">
            <label class="cce-label"><b class="cce-req">*</b>课程封面图</label>
            <div class="cce-cover-upload">
              <div class="cce-cover-preview">
                <img v-if="f.cover" :src="f.cover" class="cce-cover-preview-img" alt="课程封面" />
                <span v-else class="cce-cover-preview-glyph">封</span>
              </div>
              <div class="cce-cover-side">
                <el-upload :show-file-list="false" :before-upload="onCoverUpload" accept="image/*">
                  <button type="button" class="cce-upload-btn">{{ f.cover ? '更换封面' : '上传封面' }}</button>
                </el-upload>
                <p class="cce-tip">支持 jpg/png/webp/gif 等，单文件 ≤ {{ coverMaxMb }}MB；上传后用于课程卡片与详情页封面</p>
              </div>
            </div>
          </div>

          <!-- 课程名称与技艺类型：技艺类型可从技艺档案分类中选择，也可手动输入 -->
          <div class="cce-field">
            <label class="cce-label"><b class="cce-req">*</b>课程名称</label>
            <el-input v-model="f.name" placeholder="如：髹漆工艺系统课" maxlength="60" />
          </div>
          <div class="cce-field">
            <label class="cce-label"><b class="cce-req">*</b>技艺类型</label>
            <el-select
              v-model="f.craft"
              filterable
              allow-create
              default-first-option
              :reserve-keyword="false"
              placeholder="从技艺分类中选择，没有可输入新增"
              style="width: 100%"
            >
              <el-option v-for="c in craftOptions" :key="c" :label="c" :value="c" />
            </el-select>
            <p class="cce-tip">优先从技艺档案分类中选择；对应技艺未建档时可手动输入</p>
          </div>

          <!-- 课程类型与难度等级 -->
          <div class="cce-field">
            <label class="cce-label"><b class="cce-req">*</b>课程类型</label>
            <el-select v-model="f.stage" style="width: 100%">
              <el-option v-for="o in stageOptions" :key="o" :label="o" :value="o" />
            </el-select>
          </div>
          <div class="cce-field">
            <label class="cce-label"><b class="cce-req">*</b>难度等级</label>
            <el-select v-model="f.difficulty" style="width: 100%">
              <el-option v-for="o in diffOptions" :key="o" :label="o" :value="o" />
            </el-select>
          </div>

          <!-- 课程起止日期与开课时间：结课日期和课时日期都受此区间限制 -->
          <div class="cce-field cce-field-full">
            <label class="cce-label"><b class="cce-req">*</b>课程起止日期</label>
            <div class="cce-date-range">
              <el-date-picker v-model="f.scheduleDate" type="date" value-format="YYYY-MM-DD"
                placeholder="开课日期" :disabled-date="disabledStart" style="width: 180px" @change="onStartDateChange" />
              <el-time-picker v-model="f.scheduleTime" format="HH:mm" value-format="HH:mm"
                placeholder="开课时间" style="width: 130px" />
              <span class="cce-range-to">至</span>
              <el-date-picker v-model="f.endDate" type="date" value-format="YYYY-MM-DD"
                placeholder="结课日期" :disabled-date="disabledEnd" style="width: 180px" />
            </div>
            <p class="cce-tip">开课时间即对外展示的主上课时间；各课时日期必须安排在这段起止日期之内</p>
          </div>

          <!-- 课时数、招生人数与费用；已上架/下架课程的容量锁定不可改 -->
          <div class="cce-field">
            <label class="cce-label"><b class="cce-req">*</b>课时数</label>
            <el-input-number v-model="f.lessonCount" :min="1" :max="40" @change="onCountChange" />
            <p class="cce-tip">对应下方课时列表数量，可增减（共 {{ f.lessonCount }} 课时）</p>
          </div>
          <div class="cce-field">
            <label class="cce-label">招生人数</label>
            <el-input-number v-model="f.capacity" :min="1" :max="100" :disabled="capacityLocked" />
            <p v-if="capacityLocked" class="cce-tip">已上架/下架课程容量不可改，需转草稿后再调整</p>
          </div>
          <div class="cce-field">
            <label class="cce-label">费用（元）</label>
            <el-input-number v-model="f.priceNum" :min="0" :step="10" />
          </div>

          <!-- 上课地点与课程简介（选填） -->
          <div class="cce-field cce-field-full">
            <label class="cce-label">上课地点</label>
            <el-input v-model="f.location" maxlength="100" placeholder="如：福建省福州市漆艺工坊 / 线上直播（腾讯会议）" />
            <p class="cce-tip">课程整体的上课地点；各课时可在下方单独填写当次线上授课平台</p>
          </div>

          <div class="cce-field cce-field-full">
            <label class="cce-label">课程简介</label>
            <el-input v-model="f.desc" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="简要介绍课程内容与适合人群" />
          </div>
        </div>
      </div>

      <!-- 区块二：课时内容与安排；每个课时维护标题、上课时间、线上平台、简介与视频 -->
      <div class="cce-section">
        <div class="cce-section-head cce-section-head-row">
          <div>
            <h3 class="cce-section-title">课时内容与安排</h3>
            <p class="cce-section-sub">
              每个课时需安排上课时间与必填的<b class="cce-sub-em">线上授课平台</b>（上课日期均在课程起止日期内）。
              <template v-if="courseApproved">课时视频可在此上传，提交后经管理员审核对学员开放。</template>
              <template v-else>课时视频需在<b class="cce-sub-em">课程通过审核后</b>才能上传。</template>
            </p>
          </div>
          <el-button class="cce-add-lesson" plain type="primary" @click="addLesson">＋ 增加一个课时</el-button>
        </div>

        <!-- 课时列表：数量与上方「课时数」联动 -->
        <div class="cce-lesson-list">
          <div v-for="(les, i) in f.lessons" :key="i" class="cce-lesson">
            <div class="cce-lesson-head">
              <span class="cce-lesson-num">{{ les.num }}课</span>
              <span class="cce-lesson-label">第 {{ i + 1 }} 课时</span>
              <el-button v-if="f.lessons.length > 1" text size="small" type="danger" @click="removeLesson(i)">删除本课时</el-button>
            </div>

            <!-- 单个课时表单：标题、上课日期时间、线上授课平台与简介 -->
            <div class="cce-lesson-form">
              <el-input v-model="les.title" class="cce-title-input" placeholder="课时标题（如：识漆 · 初识生漆）" maxlength="40" />

              <div class="cce-lesson-schedule">
                <el-date-picker v-model="les.scheduleDate" type="date" value-format="YYYY-MM-DD"
                  placeholder="上课日期" :disabled-date="disabledLessonDate" style="width: 170px" />
                <el-time-picker v-model="les.scheduleTime" format="HH:mm" value-format="HH:mm"
                  placeholder="上课时间" style="width: 120px" />
                <span v-if="les.scheduleDate" class="cce-schedule-show">{{ les.scheduleDate }} {{ les.scheduleTime || '' }}</span>
              </div>
              <div class="cce-lesson-addr">
                <span class="cce-addr-mark"><b class="cce-req">*</b></span>
                <el-select
                  v-model="les.address"
                  filterable
                  allow-create
                  default-first-option
                  :reserve-keyword="false"
                  placeholder="线上授课平台（选择或输入，如 腾讯会议/钉钉/飞书）"
                  style="width: 100%"
                >
                  <el-option v-for="v in ONLINE_VENUES" :key="v" :label="v" :value="v" />
                </el-select>
              </div>

              <el-input v-model="les.desc" type="textarea" :rows="2" maxlength="200" placeholder="课时简介（教学内容、要点）" />
            </div>

            <!-- 课时视频被驳回时显示管理员意见 -->
            <div v-if="les.videoStatus === 'rejected' && les.videoReviewComment" class="cce-reject">
              <span class="cce-reject-label">驳回意见：</span>{{ les.videoReviewComment }}
            </div>

            <!-- 课时视频区：课程通过审核后才开放上传，视频本身还需再次提交审核 -->
            <div v-if="courseApproved" class="cce-video">
              <div class="cce-video-box" v-if="les.video">
                <video :src="les.video" controls preload="metadata" class="cce-video-el"></video>
                <span class="cce-videoname">{{ les.videoName || '已上传视频' }}</span>
              </div>
              <div class="cce-video-empty" v-else>
                <span class="cce-video-empty-glyph">视</span>
                <p class="cce-video-empty-text">尚未上传课时视频</p>
              </div>

              <div class="cce-video-actions">
                <el-upload :show-file-list="false" :before-upload="(file) => onVideoUpload(file, les)" accept="video/*">
                  <button type="button" class="cce-btn-mini">{{ les.video ? '重新上传' : '上传课时视频' }}</button>
                </el-upload>
                <el-button v-if="les.video" type="danger" plain size="small" @click="removeVideo(les)">删除</el-button>
                <el-button
                  v-if="les.video && (les.videoStatus === 'draft' || les.videoStatus === 'rejected')"
                  type="primary" size="small" @click="submitVideoReview(les)">
                  {{ les.videoStatus === 'rejected' ? '重新提交审核' : '提交视频审核' }}
                </el-button>
                <el-button v-else-if="les.video && les.videoStatus === 'pending'" size="small" disabled>视频审核中</el-button>
                <span v-else-if="les.video && les.videoStatus === 'approved'" class="cce-approved">✓ 视频已通过审核</span>
              </div>
              <p class="cce-tip">支持 mp4/webm/mov/m4v，单文件 ≤ {{ videoMaxMb }}MB；<b>上传即自动提交审核</b>，管理员通过后学员方可观看；被驳回可修改后重新提交；已过审视频的替换/删除需先下架课程</p>
            </div>
            <!-- 课程未通过审核时的视频区占位提示 -->
            <div v-else class="cce-video-lock">
              🔒 课程尚未通过审核，暂时不能上传课时视频（课程审核通过后此区域开放）
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作区：按钮组合随课程状态变化（草稿可保存草稿/提交，已通过只保存，下架可重新上架） -->
      <div class="cce-footer">
        <span class="cce-footer-tip" v-if="footerTip">{{ footerTip }}</span>
        <div class="cce-footer-btns">
          <button class="cce-btn cce-btn-ghost" @click="goBack">取消</button>

          <template v-if="canDraftSubmit">
            <button class="cce-btn cce-btn-draft" @click="saveDraft">保存草稿</button>
            <button class="cce-btn cce-btn-submit" @click="saveAndSubmit">保存并提交审核</button>
          </template>

          <template v-else-if="status === 'offline'">
            <button class="cce-btn cce-btn-draft" @click="saveKeep">保存</button>
            <button class="cce-btn cce-btn-submit" @click="saveAndSubmit">提交重新上架</button>
          </template>

          <template v-else>
            <button class="cce-btn cce-btn-submit" @click="saveKeep">{{ status === 'approved' ? '保存修改' : '保存' }}</button>
          </template>
        </div>
      </div>
    </div>

    <!-- 加载中 / 课程不存在的兜底状态 -->
    <div v-else class="cce-empty">
      <p class="cce-empty-text">{{ notFound ? '未找到该课程' : '加载中…' }}</p>
      <button v-if="notFound" class="cce-btn cce-btn-ghost" @click="goBack">返回我的课程</button>
    </div>
  </ConsoleLayout>
</template>

<script setup>

/* 页面逻辑：读取路由参数判断新建/编辑，加载课程并回填表单，校验后保存/提交，处理课时增删与视频审核 */
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import { uploadCourseCover, uploadCourseVideo } from '@/api/courses'
import { listSkillCategories } from '@/api/skills'
import {
  heritageCourses, courseStatusMap, loadHeritageCourses,
  addCourse, updateCourseAction, submitCourseAction, durationToLessonCount,
  addLog, authState,
  checkUploadFile, uploadLimitMb, videoUploadAllowed,
} from '@/store'

const route = useRoute()
const router = useRouter()

// 课程状态 → 文案/颜色映射，用于头部状态徽标
const statusMap = courseStatusMap
// 课程类型与难度选项，需与后端约定保持一致
const stageOptions = ['体验工作坊', '系统课程', '大师亲授']
const diffOptions = ['零基础', '进阶', '高级']

/* 线上授课平台预设值；下拉框允许手动输入其他平台 */
const ONLINE_VENUES = [
  '线上授课',
  '线上授课 · 腾讯会议',
  '线上授课 · 钉钉',
  '线上授课 · 飞书',
  '线上授课 · 微信视频号',
  '线上授课 · 抖音直播',
  '线上授课 · 平台直播间',
]

// 技艺档案中的分类列表，用于「技艺类型」下拉选项
const craftCats = ref([])
/* 合并档案分类、当前已填写的技艺类型并去重，保证正在编辑的值不会从选项里消失 */
const craftOptions = computed(() => {
  const set = new Set(craftCats.value.map((c) => (c || '').trim()).filter(Boolean))
  const cur = (f.craft || '').trim()
  if (cur) set.add(cur)
  return [...set]
})

/* 预生成 1~40 课时的中文序号（壹、贰……拾、拾壹），避免每次渲染重复计算 */
const CN = '壹贰叁肆伍陆柒捌玖拾'
const ORDINALS = []
for (let i = 1; i <= 40; i++) {
  ORDINALS.push((i <= 10 ? CN[i - 1] : (CN[Math.floor(i / 10) - 1] || '拾') + CN[i % 10 - 1]))
}
/* 返回第 i 个课时的中文序号，超出预生成范围时退回数字 */
function ordinalOf(i) {
  return ORDINALS[i] || String(i + 1)
}

// 从路由参数取课程 id；没有 id 表示新建课程
const editingId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isNew = computed(() => editingId.value == null)

// ready 控制页面是否渲染完成；notFound 标记路由 id 对应的课程不存在
const ready = ref(false)
const notFound = ref(false)

/* 新增课时的默认结构；视频状态从 draft 开始，上传后变为 pending */
const emptyLesson = () => ({
  num: '',
  title: '',
  desc: '',
  address: '线上授课',
  video: '',
  videoName: '',
  videoStatus: 'draft',
  videoReviewComment: '',
  scheduleDate: '',
  scheduleTime: '',
})

/* 课程编辑表单：基础信息 + 课时数组；新建时带常用默认值 */
const f = reactive({
  name: '',
  craft: '',
  stage: '体验工作坊',
  difficulty: '零基础',
  scheduleDate: '',
  scheduleTime: '14:00',
  endDate: '',
  capacity: 12,
  priceNum: 198,
  location: '',
  desc: '',
  cover: '',
  lessonCount: 2,
  lessons: [],
})

// 从 store 中按 id 找到当前课程；新建时返回 null
const course = computed(() => {
  if (isNew.value) return null
  return heritageCourses.find((c) => c.id === editingId.value) || null
})
// 当前状态；新建课程按草稿处理
const status = computed(() => (course.value ? course.value.status : 'draft'))
// 只有已通过审核的课程才允许上传课时视频
const courseApproved = computed(() => status.value === 'approved')
// 已上架/已下架课程不允许修改招生人数，避免影响已报名学员
const capacityLocked = computed(() => {
  const c = course.value
  return !!c && !isNew.value && (c.status === 'approved' || c.status === 'offline')
})

// 可保存草稿并提交审核的状态：新建、草稿、已驳回
const canDraftSubmit = computed(() => isNew.value || status.value === 'draft' || status.value === 'rejected')

/* 底部提示文案：根据课程状态说明当前保存动作的后果 */
const footerTip = computed(() => {
  if (isNew.value) return '新建课程可选择保存为草稿，或填齐后直接提交管理员审核'
  if (status.value === 'draft' || status.value === 'rejected') return '可继续保存草稿；信息完整后提交管理员审核'
  if (status.value === 'pending') return '该课程正在审核中，修改保存后仍保持待审核'
  if (status.value === 'offline') return '课程已下架，修改保存后需重新提交审核才能公开'
  return '修改课时内容保持已通过；若改基础信息将重新进入审核'
})

/* 把基础信息序列化成字符串，用于比较保存前后是否改动 */
function basicFieldsSnap() {
  return JSON.stringify({
    name: f.name, craft: f.craft, stage: f.stage, difficulty: f.difficulty,
    scheduleDate: f.scheduleDate, scheduleTime: f.scheduleTime, endDate: f.endDate,
    capacity: f.capacity, priceNum: f.priceNum, desc: f.desc, cover: f.cover,
    location: f.location, lessonCount: f.lessonCount,
  })
}
/* 把课时数组序列化，用于检测未保存修改 */
function lessonsSnap() {
  return JSON.stringify(f.lessons)
}
// 最近一次成功保存时的快照；空字符串表示还没建立基准
let savedSnap = ''
/* 基础信息或课时与快照不一致时视为有未保存修改 */
function isDirty() {
  return savedSnap !== '' && (basicFieldsSnap() + '|' + lessonsSnap() !== savedSnap)
}
/* 保存成功后更新快照，作为下一次脏检查的基准 */
function markSaved() {
  savedSnap = basicFieldsSnap() + '|' + lessonsSnap()
}

// onBeforeRouteLeave：onBeforeRouteLeave 是 vue-router 的离开守卫，返回 false 或拒绝的 Promise 会阻止跳转
/* 离开页面前检查未保存修改，有改动时弹确认框 */
onBeforeRouteLeave(() => {
  if (!isDirty()) return true
  return ElMessageBox.confirm('还有未保存的修改，确定离开吗？', '未保存修改', {
    confirmButtonText: '离开',
    cancelButtonText: '继续编辑',
    type: 'warning',
  })
    .then(() => true)
    .catch(() => false)
})

/* 初始化：加载课程与技艺分类；编辑时把课程数据拆解回填表单，新建时生成默认课时 */
onMounted(async () => {
  try {
    await loadHeritageCourses()
  } catch (e) { }
  try {
    craftCats.value = (await listSkillCategories()) || []
  } catch (e) { }
  if (!isNew.value) {
    const c = course.value
    if (!c) {
      notFound.value = true
      ready.value = true
      return
    }
    // schedule 形如「YYYY-MM-DD HH:mm」，拆成开课日期与开课时间
    const parts = (c.schedule || '').split(' ')
    f.name = c.name || ''
    f.craft = c.craft || ''
    f.stage = c.stage || '体验工作坊'
    f.difficulty = c.difficulty || '零基础'
    f.scheduleDate = parts[0] || ''
    f.scheduleTime = parts[1] || '14:00'
    f.endDate = c.endDate || ''
    f.capacity = c.capacity || 1
    f.priceNum = c.priceNum ?? 0
    f.location = c.location || ''
    f.desc = c.desc || ''
    f.cover = c.cover || ''
    // 优先用实际课时数组长度；旧数据没有课时时从「N 课时」文本解析，最后兜底 1
    const legacy = (c.lessons || []).length
    f.lessonCount = legacy || durationToLessonCount(c.duration) || 1
    f.lessons = buildLessons(f.lessonCount, c.lessons || [])
  } else {
    f.lessons = buildLessons(f.lessonCount)
  }
  ready.value = true
  // 初始化完成后记录快照，避免一进页面就提示未保存
  markSaved()
  // 单独记录基础信息快照，用于判断已通过课程是否改了基础信息
  basicSavedSnap = basicFieldsSnap()
})

/* 按数量生成课时数组：已有课时按位置保留原内容，新增课时用默认值补齐 */
function buildLessons(count, old = []) {
  const next = []
  for (let i = 0; i < count; i++) {
    const p = old[i] || {}
    next.push({
      num: ordinalOf(i),
      title: p.title || '',
      desc: p.desc || '',
      address: p.address || '线上授课',
      video: p.video || '',
      videoName: p.videoName || '',
      videoStatus: p.videoStatus || 'draft',
      videoReviewComment: p.videoReviewComment || '',
      scheduleDate: p.scheduleDate || '',
      scheduleTime: p.scheduleTime || '',
    })
  }
  return next
}

/* 课时数输入变化时同步调整课时数组 */
function onCountChange(n) {
  resizeLessons(n)
}
/* 手动增加一个课时，最多 40 个 */
function addLesson() {
  if (f.lessons.length >= 40) return
  resizeLessons(f.lessons.length + 1)
}
/* 删除指定课时：若已填写内容先确认，避免误删 */
function removeLesson(i) {
  const t = f.lessons[i]
  if (t.title || t.desc || t.address || t.scheduleDate) {
    ElMessageBox.confirm(`确定删除第 ${i + 1} 课时吗？其内容将被移除。`, '删除课时', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => resizeLessons(f.lessons.length - 1, i)).catch(() => {})
    return
  }
  resizeLessons(f.lessons.length - 1, i)
}
/* 调整课时数量：removeIdx >= 0 表示删除指定项，否则按数量截断或补齐（减少时会二次确认） */
function resizeLessons(n, removeIdx = -1) {
  if (n < 1) n = 1
  const arr = f.lessons.slice()
  if (removeIdx >= 0) arr.splice(removeIdx, 1)
  if (n < arr.length) {
    if (arr.length - n > 0 && removeIdx < 0) {
      ElMessageBox.confirm('减少课时数将删除末尾课时，确定？', '减少课时', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(() => { arr.length = n; applyLessons(arr) }).catch(() => { f.lessonCount = arr.length })
      return
    }
    arr.length = n
  }
  applyLessons(arr, n)
}
/* 用调整后的数组重建课时列表，并同步课时数 */
function applyLessons(arr, n) {
  const count = n && n >= arr.length ? n : arr.length
  f.lessons = buildLessons(count, arr)
  f.lessonCount = count
}

/* 日期工具：统一归零到当天 0 点，避免时分秒影响日期比较 */
function dayStart(d) {
  const x = new Date(d); x.setHours(0, 0, 0, 0); return x
}
/* 把日期（或日期字符串）转成时间戳；空值返回 null */
function toTs(s) {
  return s ? dayStart(s).getTime() : null
}
/* 开课日期不能早于今天 */
function disabledStart(d) {
  return dayStart(d).getTime() < dayStart(new Date()).getTime()
}
/* 结课日期不能早于开课日期 */
function disabledEnd(d) {
  const s = toTs(f.scheduleDate)
  return s != null && dayStart(d).getTime() < s
}
/* 开课日期变化后，若原结课日期已早于新开课日期则清空 */
function onStartDateChange(v) {
  if (v && f.endDate && f.endDate < v) f.endDate = ''
}
/* 课时日期只能在课程起止日期区间内选择 */
function disabledLessonDate(d) {
  const t = dayStart(d).getTime()
  const s = toTs(f.scheduleDate)
  const e = toTs(f.endDate)
  if (s != null && t < s) return true
  if (e != null && t > e) return true
  return false
}

/* 当前操作人名称，写入培训/课程日志 */
function operator() {
  return authState.user?.name || '传承人'
}

// 封面和视频大小上限（MB），由系统配置决定，默认分别为 5MB / 200MB
const coverMaxMb = computed(() => uploadLimitMb(5))
const videoMaxMb = computed(() => uploadLimitMb(200))

/* 封面上传：先校验类型/大小，成功后写回表单 */
async function onCoverUpload(file) {
  const err = checkUploadFile(file, { name: '封面', fallbackMb: 5 })
  if (err) {
    ElMessage.error(err)
    return false
  }
  try {
    const res = await uploadCourseCover(file)
    f.cover = res.url
    return false
  } catch (e) {
    ElMessage.error((e && e.message) || '封面上传失败')
    return false
  }
}

/* 基础信息校验：返回第一条错误文案，全部通过返回空字符串 */
function basicError() {
  if (!f.cover) return '请上传课程封面图'
  if (!f.name.trim()) return '请填写课程名称'
  if (!f.craft.trim()) return '请填写技艺类型'
  if (!f.scheduleDate || !f.scheduleTime) return '请选择开课日期与开课时间'
  if (!f.endDate) return '请选择结课日期'
  if (f.endDate < f.scheduleDate) return '结课日期不能早于开课日期'
  return ''
}

/* 课时校验：requireAll 为 true 时每个课时都必须排期；否则只校验已填写的课时，返回 { msg } */
function lessonError(requireAll) {
  const err = { title: '', msg: '' }
  for (let i = 0; i < f.lessons.length; i++) {
    const les = f.lessons[i]
    const label = les.title || ('课时 ' + (i + 1))
    if (les.scheduleDate || les.scheduleTime || les.address || requireAll) {
      if (!les.scheduleDate || !les.scheduleTime) {
        return { msg: `「${label}」请安排上课日期与时间` }
      }
      const s = toTs(f.scheduleDate)
      const e = toTs(f.endDate)
      const t = toTs(les.scheduleDate)
      if (s != null && t < s) return { msg: `「${label}」的上课日期不能早于开课日期 ${f.scheduleDate}` }
      if (e != null && t > e) return { msg: `「${label}」的上课日期不能晚于结课日期 ${f.endDate}` }
      if (!les.address.trim()) return { msg: `「${label}」请选择线上授课平台` }
    } else if (requireAll) {
      return { msg: `「${label}」请安排上课日期与时间并选择线上授课平台` }
    }
  }
  return err
}

/* 组装提交给后端的课程数据：字段名转成后端约定的形式；容量锁定时不发送 capacity */
function payload() {
  return {
    name: f.name.trim(),
    craft: f.craft.trim(),
    stage: f.stage,
    difficulty: f.difficulty,
    duration: `${f.lessonCount} 课时`,
    schedule: (f.scheduleDate ? f.scheduleDate + ' ' + (f.scheduleTime || '') : '').trim(),
    end_date: f.endDate,
    ...(capacityLocked.value ? {} : { capacity: f.capacity }),
    price_num: f.priceNum,
    location: (f.location || '').trim(),
    desc: f.desc.trim(),
    cover: f.cover,
    lessons: f.lessons.map((l) => ({ ...l })),
  }
}

/* 从接口错误对象中提取后端返回的字段错误或提示，取不到时用兜底文案 */
function errText(e) {
  const d = e && e.data
  if (d && typeof d === 'object') {
    const first = Object.values(d)[0]
    if (Array.isArray(first)) return first[0]
    if (typeof first === 'string') return first
  }
  if (d && (d.msg || d.detail)) return d.msg || d.detail
  return (e && e.message) || '保存失败，请重试'
}

/* 统一保存入口：新建调用 addCourse（返回新课程），编辑调用 updateCourseAction */
async function persist(snakePayload) {
  if (isNew.value) {
    const created = await addCourse(snakePayload)
    return created
  }
  return updateCourseAction(editingId.value, snakePayload)
}

/* 保存成功后的统一处理：更新脏检查快照并提示 */
function afterSaved(msg) {
  markSaved()
  ElMessage.success(msg)
}

/* 保存草稿：基础信息必填但课时可暂不排期；新建保存后返回列表 */
async function saveDraft() {
  const berr = basicError()
  if (berr) { ElMessage.warning(berr); return }
  const lerr = lessonError(false)
  if (lerr.msg) { ElMessage.warning(lerr.msg); return }
  try {
    await persist(payload())
    addLog('update', operator(), isNew.value ? '创建课程草稿' : '保存课程草稿',
      `课程「${f.name}」已保存为草稿`)
    afterSaved(isNew.value ? '课程草稿已创建，可稍后继续完善' : '已保存草稿')
    if (isNew.value) goBack()
  } catch (e) {
    ElMessage.error(errText(e))
  }
}

/* 保存并提交审核：课时的日期/时间/线上平台全部必填，保存后调用提交接口再返回列表 */
async function saveAndSubmit() {
  const berr = basicError()
  if (berr) { ElMessage.warning(berr); return }
  const lerr = lessonError(true)
  if (lerr.msg) { ElMessage.warning(lerr.msg); return }
  try {
    const saved = await persist(payload())
    // 新建时用接口返回的新课程 id 提交审核
    const id = isNew.value ? saved.id : editingId.value
    await submitCourseAction(id)
    addLog('review', operator(), '提交课程审核',
      `课程「${f.name}」${status.value === 'offline' ? '重新' : ''}提交审核`)
    afterSaved('已提交审核，请等待管理员审核')
    goBack()
  } catch (e) {
    ElMessage.error(errText(e))
  }
}

/* 只保存不主动提交：已通过课程若改了基础信息，会确认后自动重新提交审核 */
async function saveKeep() {
  const berr = basicError()
  if (berr) { ElMessage.warning(berr); return }
  const lerr = lessonError(false)
  if (lerr.msg) { ElMessage.warning(lerr.msg); return }

  if (status.value === 'approved') {
    // 已通过课程：只有基础信息变化才需要重新审核，单纯改课时保持已通过
    const basicChanged = basicFieldsSnap() !== basicSavedSnap
    if (basicChanged) {
      try {
        await ElMessageBox.confirm(
          '修改基础信息后，本课程将重新提交管理员审核，审核通过前不公开显示。确定保存并提交审核？',
          '重新审核',
          { confirmButtonText: '保存并提交审核', cancelButtonText: '取消', type: 'warning' },
        )
      } catch (e) { return }
      try {
        await persist(payload())
        await submitCourseAction(editingId.value)
        addLog('review', operator(), '提交课程审核', `课程「${f.name}」基础信息变更后重新提交审核`)
        afterSaved('已保存并重新提交审核')
        goBack()
      } catch (e) { ElMessage.error(errText(e)) }
      return
    }
  }
  try {
    await persist(payload())
    addLog('update', operator(), '保存课程内容', `课程「${f.name}」内容已保存`)
    afterSaved('课程内容已保存')
  } catch (e) {
    ElMessage.error(errText(e))
  }
}

// 最近一次加载/保存时的基础信息快照，用于判断已通过课程是否改了基础信息
let basicSavedSnap = ''

/* 只保存课时数组（视频上传/删除/提交审核后调用），不影响基础信息 */
async function saveLessonsOnly() {
  if (!course.value) return
  await updateCourseAction(course.value.id, { lessons: f.lessons.map((l) => ({ ...l })) })
  markSaved()
}

/* 课时视频上传：检查上传开关与文件大小，上传成功后先写回本地，再单独保存课时；保存失败则回滚视频字段 */
async function onVideoUpload(file, les) {
  if (!videoUploadAllowed()) {
    ElMessage.error('管理员已在「系统配置」中关闭视频上传')
    return false
  }
  const verr = checkUploadFile(file, { name: '视频', fallbackMb: 200 })
  if (verr) {
    ElMessage.error(verr)
    return false
  }
  // 先备份视频字段，保存失败时用于回滚
  const prev = {
    video: les.video, videoName: les.videoName,
    videoStatus: les.videoStatus, videoReviewComment: les.videoReviewComment,
  }
  // duration: 0 表示不会自动关闭，上传结束后手动 loading.close()
  const loading = ElMessage({ type: 'info', message: '正在上传视频…', duration: 0 })
  try {
    const res = await uploadCourseVideo(file)
    les.video = res.url
    les.videoName = res.name || file.name
    les.videoStatus = res.videoStatus || res.video_status || 'pending'
    les.videoReviewComment = ''
    loading.close()
    try {
      await saveLessonsOnly()
      ElMessage.success('视频已上传并提交审核，管理员通过后学员即可观看')
    } catch (e) {
      Object.assign(les, prev)
      ElMessage.error(errText(e))
    }
  } catch (e) {
    loading.close()
    ElMessage.error(errText(e))
  }
  return false
}

/* 删除课时视频：确认后清空视频字段并保存课时，失败时回滚 */
function removeVideo(les) {
  const prev = {
    video: les.video, videoName: les.videoName,
    videoStatus: les.videoStatus, videoReviewComment: les.videoReviewComment,
  }
  ElMessageBox.confirm('确定删除该课时视频吗？', '删除视频', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      les.video = ''
      les.videoName = ''
      les.videoStatus = 'draft'
      les.videoReviewComment = ''
      try {
        await saveLessonsOnly()
        ElMessage.success('已删除视频')
      } catch (e) {
        Object.assign(les, prev)
        ElMessage.error(errText(e))
      }
    })
    .catch(() => {})
}

/* 提交视频审核：被驳回后再次提交时按钮文案改为「重新提交」 */
function submitVideoReview(les) {
  const again = les.videoStatus === 'rejected'
  ElMessageBox.confirm('提交后管理员将审核该视频，通过后学员即可观看。确定提交？', again ? '重新提交视频审核' : '提交视频审核', {
    confirmButtonText: again ? '重新提交' : '提交',
    cancelButtonText: '取消',
    type: 'info',
  })
    .then(async () => {
      const prev = { videoStatus: les.videoStatus, videoReviewComment: les.videoReviewComment }
      les.videoStatus = 'pending'
      les.videoReviewComment = ''
      try {
        await saveLessonsOnly()
        addLog('review', operator(), '提交课时视频审核', `课程「${f.name}」课时「${les.title || les.num}」`)
        ElMessage.success('已提交视频审核，请等待管理员审核')
      } catch (e) {
        Object.assign(les, prev)
        ElMessage.error(errText(e))
      }
    })
    .catch(() => {})
}

/* 返回「我的课程」列表 */
function goBack() {
  router.push('/console/courses')
}
</script>

<style src="./ConsoleCourseEdit.css"></style>
