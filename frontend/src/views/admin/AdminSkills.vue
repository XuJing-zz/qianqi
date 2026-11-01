<!-- AdminSkills.vue 技艺档案审核页：按状态分页查看传承人提交的档案，支持筛选、详情预览、通过、驳回与下架。 -->
<template>
  <AdminLayout>
    <div class="ask-wrap">
      <!-- 页头区：显示待审核总数，并提供「待审核/已通过/已驳回/已下架」状态页签 -->
      <div class="ask-head">
        <div class="ask-head-left">
          <h2 class="ask-title">技艺档案审核</h2>
          <p class="ask-sub">共 {{ pendingList.length }} 条待审核技艺档案</p>
        </div>
        <div class="ask-head-tabs">
          <button
            v-for="t in tabs"
            :key="t.value"
            class="ask-tab"
            :class="{ 'ask-tab-active': activeTab === t.value }"
            @click="switchTab(t.value)"
          >
            {{ t.label }}<span class="ask-tab-count">{{ countOf(t.value) }}</span>
          </button>
        </div>
      </div>

      <!-- 筛选区：级别、类别、难度、流派、地区与关键字；条件变化后从第 1 页重查 -->
      <div class="ask-filter">
        <el-select v-model="fLevel" placeholder="级别" clearable style="width: 116px" @change="applyFilter">
          <el-option v-for="v in levelOptions" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="fCategory" placeholder="技艺类别" clearable style="width: 140px" @change="applyFilter">
          <el-option v-for="v in categoryOptions" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="fDifficulty" placeholder="难度等级" clearable style="width: 124px" @change="applyFilter">
          <el-option v-for="v in difficultyOptions" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="fSchool" placeholder="工艺流派" clearable style="width: 136px" @change="applyFilter">
          <el-option v-for="v in schoolOptions" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="fRegion" placeholder="地区" clearable style="width: 124px" @change="applyFilter">
          <el-option v-for="v in regionOptions" :key="v" :label="v" :value="v" />
        </el-select>
        <el-input
          v-model="keyword"
          placeholder="搜档案名 / 类别 / 传承人"
          clearable
          style="width: 220px"
          @input="applyFilter"
          @clear="applyFilter"
        />
        <button v-if="hasFilter" class="ask-filter-reset" @click="resetFilters">重置筛选</button>
      </div>

      <!-- 列表区：卡片展示档案摘要；待审核可操作通过/驳回，已通过可下架 -->
      <div v-if="loading" class="ask-loading">加载中…</div>
      <div v-else-if="rows.length" class="ask-list">
        <div v-for="s in rows" :key="s.id" class="ask-card">
          <div class="ask-body">
            <div class="ask-body-top">
              <h3 class="ask-name">{{ s.name }}</h3>
              <span class="ask-badge" :style="{ color: statusMap[s.status].color, borderColor: statusMap[s.status].color }">
                {{ statusMap[s.status].label }}
              </span>
            </div>
            <div class="ask-meta">
              <span class="ask-meta-item">级别：{{ s.level }}</span>
              <span class="ask-meta-item">分类：{{ s.category }}</span>
              <span v-if="s.school" class="ask-meta-item">流派：{{ s.school }}</span>
              <span v-if="s.difficulty" class="ask-meta-item">难度：{{ s.difficulty }}</span>
              <span class="ask-meta-item">从艺 {{ s.years }} 年</span>
              <span v-if="s.submitTime" class="ask-meta-item">提交于 {{ s.submitTime }}</span>
            </div>
            <p class="ask-desc">{{ s.desc }}</p>

            <div v-if="s.status === 'rejected' && s.reviewComment" class="ask-reject">
              <span class="ask-reject-label">已驳回：</span>{{ s.reviewComment }}
            </div>

            <div class="ask-actions">
              <button class="ask-btn ask-btn-view" @click="openDetail(s)">查看详情</button>
              <template v-if="s.status === 'pending'">
                <button class="ask-btn ask-btn-pass" @click="approve(s)">通过</button>
                <button class="ask-btn ask-btn-reject" @click="openReject(s)">驳回</button>
              </template>
              <template v-else-if="s.status === 'approved'">
                <button class="ask-btn ask-btn-offline" @click="offline(s)">下架</button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="ask-empty">
        <span class="ask-empty-glyph">档</span>
        <p class="ask-empty-text">暂无{{ activeTabLabel }}技艺档案<template v-if="hasFilter">（当前筛选条件下）</template></p>
        <button v-if="hasFilter" class="ask-filter-reset" @click="resetFilters">清空筛选条件</button>
      </div>

      <!-- 分页区：由 usePagedList 维护的 total / page 驱动 -->
      <div v-if="total > pageSize" class="ask-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>

    <!-- 详情抽屉：完整展示申报信息、图文正文与素材，底部提供审核操作 -->
    <el-drawer v-model="detailVisible" title="技艺档案审核" size="min(680px, 94vw)" :close-on-click-modal="false" destroy-on-close>
      <div v-if="detail" class="ask-detail-body">
        <div class="ask-detail-head">
          <img v-if="detail.image" :src="detail.image" class="ask-detail-cover" alt="技艺图" />
          <span v-else class="ask-detail-glyph">{{ glyphOf(detail.name) }}</span>
          <div class="ask-detail-headinfo">
            <div class="ask-detail-title">
              <h3 class="ask-detail-name">{{ detail.name }}</h3>
              <span class="ask-badge" :style="{ color: statusMap[detail.status].color, borderColor: statusMap[detail.status].color }">
                {{ statusMap[detail.status].label }}
              </span>
            </div>
            <p class="ask-detail-owner">申报传承人：{{ detail.ownerName || '—' }}</p>
          </div>
        </div>

        <div class="ask-meta ask-detail-meta">
          <span class="ask-meta-item">级别：{{ detail.level }}</span>
          <span class="ask-meta-item">分类：{{ detail.category }}</span>
          <span v-if="detail.school" class="ask-meta-item">流派：{{ detail.school }}</span>
          <span v-if="detail.difficulty" class="ask-meta-item">难度：{{ detail.difficulty }}</span>
          <span v-if="detail.region" class="ask-meta-item">地区：{{ detail.region }}</span>
          <span v-if="detail.origin" class="ask-meta-item">发源：{{ detail.origin }}</span>
          <span class="ask-meta-item">从艺 {{ detail.years }} 年</span>
          <span v-if="detail.submitTime" class="ask-meta-item">提交于 {{ detail.submitTime }}</span>
        </div>

        <p v-if="detail.desc" class="ask-desc ask-detail-desc">{{ detail.desc }}</p>

        <!-- 图文正文区：按「历史背景 / 工艺流程 / 工艺纪实」三段渲染传承人填写的富文本数据 -->
        <div v-if="richBody()" class="ask-rich">
          <div class="ask-rich-tip">以下为传承人端填写的图文正文，审核通过后即照此发布：</div>

          <section v-if="bArr('history').length" class="ask-rich-sec">
            <div class="ask-rich-sec-head">
              <b>壹 · 历史背景</b><span class="ask-rich-count">{{ bArr('history').length }} 段</span>
            </div>
            <p v-for="(p, i) in bArr('history')" :key="'h' + i" class="ask-rich-para">{{ p.text }}</p>
          </section>

          <section v-if="bArr('steps').length" class="ask-rich-sec">
            <div class="ask-rich-sec-head">
              <b>贰 · 工艺流程</b><span class="ask-rich-count">{{ bArr('steps').length }} 道工序</span>
            </div>
            <article v-for="(s, i) in bArr('steps')" :key="'s' + i" class="ask-rich-step">
              <div class="ask-rich-step-head">
                <span class="ask-rich-step-no">{{ pad(i + 1) }}</span>
                <b class="ask-rich-step-name">{{ s.name || ('工序 ' + pad(i + 1)) }}</b>
                <span v-if="s.image" class="ask-rich-flag">有工序图</span>
              </div>
              <div v-if="chips(s.tools).length" class="ask-rich-row">
                <span class="ask-rich-label">工具</span>
                <span v-for="(t, ti) in chips(s.tools)" :key="'t' + ti" class="ask-detail-tag">{{ t }}</span>
              </div>
              <div v-if="chips(s.materials).length" class="ask-rich-row">
                <span class="ask-rich-label">材料</span>
                <span v-for="(m, mi) in chips(s.materials)" :key="'m' + mi" class="ask-detail-tag ask-detail-tag-alt">{{ m }}</span>
              </div>
              <p v-if="s.method" class="ask-rich-method">{{ s.method }}</p>
              <figure v-if="s.image" class="ask-rich-fig">
                <img :src="s.image" :alt="s.name || ''" />
                <figcaption v-if="s.caption">{{ s.caption }}</figcaption>
              </figure>
            </article>
          </section>

          <section v-if="bArr('cards').length" class="ask-rich-sec">
            <div class="ask-rich-sec-head">
              <b>叁 · 工艺纪实</b><span class="ask-rich-count">{{ bArr('cards').length }} 块</span>
            </div>
            <article v-for="(c, i) in bArr('cards')" :key="'c' + i" class="ask-rich-card">
              <div class="ask-rich-card-head">
                <b class="ask-rich-card-title">{{ c.title }}</b>
                <span v-if="c.image" class="ask-rich-flag">有配图</span>
              </div>
              <p v-if="c.text" class="ask-rich-text">{{ c.text }}</p>
              <figure v-if="c.image" class="ask-rich-fig">
                <img :src="c.image" :alt="c.title || ''" />
                <figcaption v-if="c.caption">{{ c.caption }}</figcaption>
              </figure>
            </article>
          </section>
        </div>

        <div v-else class="ask-detail-field ask-detail-block">
          <span class="ask-detail-label">工艺概述</span>
          <span v-if="detail.abstract && detail.abstract !== detail.desc" class="ask-detail-value ask-detail-story">{{ detail.abstract }}</span>
          <span v-else class="ask-detail-value ask-detail-story">{{ detail.desc || '—' }}</span>
        </div>
        <div v-if="!richBody()" class="ask-detail-field ask-detail-block">
          <span class="ask-detail-label">工序步骤</span>
          <div class="ask-detail-tags">
            <span v-for="(st, i) in parseList(detail.steps)" :key="i" class="ask-detail-tag">{{ st }}</span>
            <span v-if="!parseList(detail.steps).length" class="ask-detail-value">—</span>
          </div>
        </div>

        <!-- 素材与要点区：展示原材料、专用工具、制作难点与注意事项 -->
        <div v-if="hasEssentials" class="ask-detail-field ask-detail-block">
          <span class="ask-detail-label">素材与要点</span>
          <div class="ask-ess">
            <div v-if="essRaw" class="ask-ess-row">
              <span class="ask-ess-title">原材料清单</span>
              <div class="ask-detail-tags">
                <span v-for="(m, i) in chips(essRaw)" :key="'rm' + i" class="ask-detail-tag">{{ m }}</span>
              </div>
            </div>
            <div v-if="essTools" class="ask-ess-row">
              <span class="ask-ess-title">专用工具</span>
              <div class="ask-detail-tags">
                <span v-for="(t, i) in chips(essTools)" :key="'tl' + i" class="ask-detail-tag">{{ t }}</span>
              </div>
            </div>
            <div v-if="essHard" class="ask-ess-row">
              <span class="ask-ess-title">制作难点</span>
              <span class="ask-detail-value">{{ essHard }}</span>
            </div>
            <div v-if="essCaution" class="ask-ess-row">
              <span class="ask-ess-title">注意事项</span>
              <span class="ask-detail-value">{{ essCaution }}</span>
            </div>
          </div>
        </div>

        <!-- 关联信息区：代表作品优先按作品 ID 关联，旧数据回退为文本列表 -->
        <div class="ask-detail-field ask-detail-block">
          <span class="ask-detail-label">代表作品</span>
          <div v-if="boundWorks.length" class="ask-detail-tags">
            <span v-for="w in boundWorks" :key="w.id" class="ask-detail-tag ask-detail-tag-alt">
              {{ w.name }}<template v-if="w.status !== 'approved'">（{{ (productStatusMap[w.status] || {}).label || w.status }}）</template>
            </span>
          </div>
          <div v-else-if="parseList(detail.works).length" class="ask-detail-tags">
            <span v-for="(w, i) in parseList(detail.works)" :key="i" class="ask-detail-tag ask-detail-tag-alt">{{ w }}</span>
          </div>
          <span v-else class="ask-detail-value">—</span>
        </div>

        <div class="ask-detail-field ask-detail-block">
          <span class="ask-detail-label">关联课程</span>
          <div class="ask-detail-tags">
            <span v-for="(c, i) in parseList(detail.courses)" :key="i" class="ask-detail-tag ask-detail-tag-course">{{ c }}</span>
            <span v-if="!parseList(detail.courses).length" class="ask-detail-value">—</span>
          </div>
        </div>

        <div v-if="detail.status === 'rejected' && detail.reviewComment" class="ask-reject">
          <span class="ask-reject-label">驳回意见：</span>{{ detail.reviewComment }}
        </div>
      </div>

      <template v-if="detail" #footer>
        <div class="ask-detail-footer">
          <el-button @click="openPreview">预览前台页面</el-button>
          <template v-if="detail.status === 'pending'">
            <el-button type="primary" @click="approve(detail)">通过</el-button>
            <el-button type="danger" plain @click="openReject(detail)">驳回</el-button>
          </template>
          <template v-else-if="detail.status === 'approved'">
            <el-button @click="offline(detail)">下架</el-button>
          </template>
          <template v-else>
            <span class="ask-done">该档案已处理完毕</span>
          </template>
        </div>
      </template>
    </el-drawer>

    <!-- 前台预览层：复用学员端的 SkillDetailPage，按审核通过后的效果展示 -->
    <div v-if="previewVisible && detail" class="ask-preview-mask" @click.self="previewVisible = false">
      <div class="ask-preview-head">
        <span class="ask-preview-title">前台页面预览 · {{ detail.name || '未命名技艺' }}</span>
        <span class="ask-preview-tag">审核通过后学员端即见此效果</span>
        <button class="ask-preview-close" @click="previewVisible = false">返回审核 ×</button>
      </div>
      <div class="ask-preview-scroll">
        <SkillDetailPage :skill="detail" preview />
      </div>
    </div>

    <!-- 驳回弹窗：驳回原因必填，提交后会反馈给传承人 -->
    <el-dialog v-model="rejectDialog" title="驳回技艺档案" width="520px" :close-on-click-modal="false">
      <p class="ask-dialog-tip">请填写驳回原因，将反馈给传承人修改：</p>
      <el-input
        v-model="rejectComment"
        type="textarea"
        :rows="4"
        placeholder="如：缺少工序步骤图或原材料清单，请补充完整"
      />
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
/* 技艺档案审核组件：列表按状态页签 + 筛选条件分页加载；
   通过/驳回/下架都会调用审核接口、写入操作日志，并在成功后刷新当前列表。 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import SkillDetailPage from '@/views/user/archive/SkillDetailPage.vue'
import { listSkills } from '@/api/skills'
import { mapKeys } from '@/api/utils'
import {
  heritageSkills, skillStatusMap,
  heritageProducts, productStatusMap, loadProducts,
  reviewSkillAction, updateSkillAction, addLog, authState,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 档案状态到「中文标签 + 颜色」的映射，供列表与详情中的状态徽标使用
const statusMap = skillStatusMap

// 四个状态页签；value 与后端 status 字段保持一致
const tabs = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
  { label: '已下架', value: 'offline' },
]
// 当前状态页签，默认显示待审核
const activeTab = ref('pending')

// 当前页签的中文名，用于空状态文案
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')

// 待审核档案数量：直接基于全局档案缓存统计，用于页头提示
const pendingList = computed(() => heritageSkills.filter((s) => s.status === 'pending'))

// 统计各状态页签上的档案条数（基于已加载的全局缓存）
function countOf(v) {
  return heritageSkills.filter((s) => s.status === v).length
}



// 把后端档案字段整理成列表行结构，缺失字段补空字符串
function mapSkillRow(s) {
  const m = mapKeys(s)
  return { ...m, submitTime: m.submitTime || '', reviewComment: m.reviewComment || '' }
}

/* 分页列表加载（usePagedList）：
   - pageSize 指定每页 8 条；map 在渲染前统一整理行字段；
   - fetchPage 每次收到页码与每页条数，再叠加当前页签 status 和五个筛选条件，
     调用 listSkills 请求后端分页数据；
   - 解构出的 rows/total/page/loading 用于模板，onFilter 会先回到第 1 页，onPage 用于翻页。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapSkillRow,
  fetchPage: ({ page, page_size }) => {
    const params = { status: activeTab.value, page, page_size }
    if (fLevel.value) params.level = fLevel.value
    if (fCategory.value) params.category = fCategory.value
    if (fDifficulty.value) params.difficulty = fDifficulty.value
    if (fSchool.value) params.school = fSchool.value
    if (fRegion.value) params.region = fRegion.value
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    return listSkills(params)
  },
})

// 切换状态页签后从第 1 页重新加载（onFilter 内部会重置页码）
function switchTab(v) {
  activeTab.value = v
  onFilter()
}

// 五个筛选条件：级别、类别、难度、流派、地区，以及关键字
const fLevel = ref('')
const fCategory = ref('')
const fDifficulty = ref('')
const fSchool = ref('')
const fRegion = ref('')
const keyword = ref('')

// 从已加载档案中提取某个字段的去重候选值，并排序供下拉框使用
function distinctValues(field) {
  return Array.from(
    new Set(heritageSkills.map((s) => (s[field] || '').trim()).filter(Boolean)),
  ).sort()
}
// 各筛选下拉框的候选值，随档案缓存变化自动更新
const levelOptions = computed(() => distinctValues('level'))
const categoryOptions = computed(() => distinctValues('category'))
const difficultyOptions = computed(() => distinctValues('difficulty'))
const schoolOptions = computed(() => distinctValues('school'))
const regionOptions = computed(() => distinctValues('region'))

// 是否存在任一筛选条件，用于显示「重置筛选」和空状态提示
const hasFilter = computed(() => !!(
  fLevel.value || fCategory.value || fDifficulty.value
  || fSchool.value || fRegion.value || keyword.value.trim()
))

// 应用筛选：回到第 1 页并重新请求列表
function applyFilter() {
  page.value = 1
  loadRows()
}

// 清空全部筛选项后重新查询
function resetFilters() {
  fLevel.value = ''
  fCategory.value = ''
  fDifficulty.value = ''
  fSchool.value = ''
  fRegion.value = ''
  keyword.value = ''
  applyFilter()
}

// 页面初始化：加载当前页签列表，同时预加载作品数据（详情中展示关联作品需要）
onMounted(() => {
  loadRows()
  loadProducts().catch(() => {})
})

// 取当前登录管理员姓名，写入审核操作日志
function operator() {
  return authState.user?.name || '管理员'
}

// 把「｜」分隔的旧版文本字段拆成数组，用于工序、作品、课程等兼容展示
function parseList(str) {
  return (str || '').split('｜').map((x) => x.trim()).filter(Boolean)
}
// 序号补零到两位（1 → 01），用于工序编号
function pad(n) {
  return String(n).padStart(2, '0')
}
// 没有封面图时取档案名首字作为文字占位图
function glyphOf(name) {
  return (name || '').charAt(0) || '艺'
}
// 把顿号、逗号、分号、斜杠或空白分隔的文本拆成标签数组
function chips(str) {
  return (str || '').split(/、|，|,|；|;|\s+|\//).map((x) => x.trim()).filter(Boolean)
}

// 取档案的富文本正文对象；非对象或缺失时返回空对象，避免后续取值报错
function bodyOf() {
  const b = detail.value && detail.value.body
  return b && typeof b === 'object' ? b : {}
}
// 安全读取正文中的指定数组字段（history / steps / cards）
function bArr(k) {
  return Array.isArray(bodyOf()[k]) ? bodyOf()[k] : []
}
// 判断是否存在任一富文本区块；没有则回退到旧的纯文本展示
function richBody() {
  return bArr('history').length > 0 || bArr('steps').length > 0 || bArr('cards').length > 0
}

// 详情抽屉状态：detail 保存当前查看的档案对象
const detailVisible = ref(false)
const detail = ref(null)

// 素材要点：兼容驼峰与下划线两种后端字段命名
const essRaw = computed(() => (detail.value && (detail.value.rawMaterials || detail.value.raw_materials)) || '')
const essTools = computed(() => (detail.value && detail.value.tools) || '')
const essHard = computed(() => (detail.value && (detail.value.hardPoints || detail.value.hard_points)) || '')
const essCaution = computed(() => (detail.value && detail.value.cautions) || '')
// 只要任一项素材要点有值，就显示「素材与要点」区块
const hasEssentials = computed(() => !!(essRaw.value || essTools.value || essHard.value || essCaution.value))

// 把档案上的作品 ID 关联到全局作品列表，仅保留仍存在的作品
const boundWorks = computed(() => {
  const d = detail.value
  if (!d) return []
  const ids = (Array.isArray(d.worksProductIds) ? d.worksProductIds : []).map(Number).filter(Boolean)
  if (!ids.length) return []
  return heritageProducts.filter((p) => ids.includes(Number(p.id)))
})

// 打开详情抽屉，并确保作品数据已加载（用于关联作品展示）
function openDetail(s) {
  detail.value = s
  detailVisible.value = true
  loadProducts().catch(() => {})
}

// 审核/下架完成后的统一收尾：关闭预览与详情，并刷新当前页列表
async function afterAction() {
  previewVisible.value = false
  detailVisible.value = false
  await loadRows()
}

const previewVisible = ref(false)
// 打开前台预览层（需已选中一条档案）
function openPreview() {
  if (detail.value) previewVisible.value = true
}

// 通过审核：二次确认后调用审核接口，档案随即对外发布并可被学员查看
function approve(s) {
  ElMessageBox.confirm(`审核通过后「${s.name}」将对外发布，学员可查看学习。确定通过？`, '通过审核', {
    confirmButtonText: '通过',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await reviewSkillAction(s.id, 'approve', '')
      addLog('review', operator(), '通过技艺档案审核', `「${s.name}」`)
      ElMessage.success('已通过审核，档案已对外发布')
      await afterAction()
    })
    .catch(() => {})
}

// 下架已通过档案：确认后改为 offline，学员端不再可见
function offline(s) {
  ElMessageBox.confirm(`确定下架「${s.name}」吗？下架后学员将无法查看。`, '下架档案', {
    confirmButtonText: '下架',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await updateSkillAction(s.id, { status: 'offline' })
      addLog('review', operator(), '下架技艺档案', `「${s.name}」`)
      ElMessage.success('已下架')
      await afterAction()
    })
    .catch(() => {})
}

// 驳回弹窗状态：rejectTarget 记录待驳回的档案，rejectComment 保存驳回意见
const rejectDialog = ref(false)
const rejectComment = ref('')
let rejectTarget = null

// 打开驳回弹窗并清空上一次填写的原因
function openReject(s) {
  rejectTarget = s
  rejectComment.value = ''
  rejectDialog.value = true
}

// 确认驳回：原因不能为空；提交成功后记录日志并刷新列表
function confirmReject() {
  if (!rejectComment.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  if (rejectTarget) {
    const comment = rejectComment.value.trim()
    reviewSkillAction(rejectTarget.id, 'reject', comment)
      .then(async () => {
        addLog('review', operator(), '驳回技艺档案', `「${rejectTarget.name}」：${comment}`)
        ElMessage.success('已驳回，意见已反馈给传承人')
        await afterAction()
      })
      .catch(() => ElMessage.error('驳回失败'))
  }
  rejectDialog.value = false
  rejectTarget = null
}
</script>

<style src="./AdminSkills.css"></style>

<style scoped>

/* 列表加载中的占位样式 */
.ask-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
/* 分页器右对齐 */
.ask-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
/* 空状态下的「清空筛选」按钮与提示文字拉开距离 */
.ask-empty .ask-filter-reset {
  margin-top: 14px;
}
</style>
