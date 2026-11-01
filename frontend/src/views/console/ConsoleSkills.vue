<!-- 传承人工作台 · 技艺管理：展示本人技艺档案，支持新增/编辑、提交审核、上下架与删除 -->
<template>
  <!-- 工作台统一布局：左侧导航 + 右侧内容区 -->
  <ConsoleLayout>
    <div class="csk-wrap">
      <!-- 页头：标题、技艺总数与新增入口 -->
      <div class="csk-head">
        <div class="csk-head-left">
          <h2 class="csk-title">我的技艺</h2>
          <p class="csk-sub">共 {{ skillList.length }} 项技艺</p>
        </div>
        <button class="csk-add-btn" @click="openCreate">＋ 新增技艺</button>
      </div>

      <!-- 状态标签：按审核状态筛选技艺，右侧显示各状态数量 -->
      <div class="csk-tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="csk-tab"
          :class="{ 'csk-tab-active': activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
          <span class="csk-tab-count">{{ countOf(t.value) }}</span>
        </button>
      </div>

      <!-- 技艺列表：每张卡片展示封面、基本信息、正文摘要与操作按钮 -->
      <div v-if="filtered.length" class="csk-list">
        <div v-for="s in filtered" :key="s.id" class="csk-card">
          <!-- 卡片头部：封面图/占位字、名称与级别信息、审核状态徽标 -->
          <div class="csk-card-head">
            <div class="csk-head-left">
              <img v-if="s.image" :src="s.image" class="csk-cover-img" alt="技艺图" />
              <span v-else class="csk-cover">{{ (s.category || '艺').charAt(0) }}</span>
              <div>
                <h3 class="csk-name">{{ s.name }}</h3>
                <p class="csk-meta">{{ s.level }} · {{ s.category }}<template v-if="s.school"> · {{ s.school }}</template><template v-if="s.difficulty"> · 难度 {{ s.difficulty }}</template> · 从艺 {{ s.years }} 年</p>
              </div>
            </div>
            <span class="csk-badge" :style="{ color: statusMap[s.status].color, borderColor: statusMap[s.status].color }">
              {{ statusMap[s.status].label }}
            </span>
          </div>

          <p class="csk-desc">{{ s.desc }}</p>

          <!-- 正文摘要：统计历史/工序/纪实各有多少段 -->
          <div v-if="bodySummary(s)" class="csk-block">
            <span class="csk-block-label">图文正文</span>
            <div class="csk-tags">
              <span class="csk-tag">{{ bodySummary(s) }}</span>
            </div>
          </div>
          <!-- 工序步骤标签：把「｜」分隔的工序名拆成标签 -->
          <div class="csk-block">
            <span class="csk-block-label">工序步骤</span>
            <div class="csk-tags">
              <span v-for="(st, i) in parseList(s.steps)" :key="i" class="csk-tag">{{ st }}</span>
            </div>
          </div>
          <!-- 代表作品：优先显示已上架作品的名称，无关联商品时退回文本 -->
          <div v-if="worksNamesOf(s).length" class="csk-block">
            <span class="csk-block-label">代表作品 · 已上架</span>
            <div class="csk-tags">
              <span v-for="(w, i) in worksNamesOf(s)" :key="i" class="csk-tag csk-tag-alt">{{ w }}</span>
            </div>
          </div>
          <div v-else-if="s.works" class="csk-block">
            <span class="csk-block-label">代表作品</span>
            <div class="csk-tags">
              <span v-for="(w, i) in parseList(s.works)" :key="i" class="csk-tag csk-tag-alt">{{ w }}</span>
            </div>
          </div>
          <!-- 关联课程标签 -->
          <div v-if="s.courses" class="csk-block">
            <span class="csk-block-label">关联课程</span>
            <div class="csk-tags">
              <span v-for="(c, i) in parseList(s.courses)" :key="i" class="csk-tag csk-tag-course">{{ c }}</span>
            </div>
          </div>

          <!-- 驳回原因：仅已驳回状态且管理员填写了意见时显示 -->
          <div v-if="s.status === 'rejected' && s.reviewComment" class="csk-reject">
            <span class="csk-reject-label">驳回意见：</span>{{ s.reviewComment }}
          </div>

          <!-- 操作区：按状态显示编辑、提交审核、下架/重新上架、删除 -->
          <div class="csk-actions">
            <button class="csk-btn" @click="openEdit(s)">编辑</button>
            <button v-if="s.status === 'draft' || s.status === 'rejected'" class="csk-btn csk-btn-primary" @click="submitReview(s)">提交审核</button>
            <button v-if="s.status === 'pending'" class="csk-btn csk-btn-plain" disabled>等待审核中</button>
            <button v-if="s.status === 'approved'" class="csk-btn csk-btn-warn" @click="toggleOffline(s)">下架</button>
            <button v-if="s.status === 'offline'" class="csk-btn csk-btn-primary" @click="toggleOffline(s)">重新上架</button>
            <button class="csk-btn csk-btn-danger" @click="removeSkill(s)">删除</button>
          </div>
        </div>
      </div>

      <!-- 空状态：当前筛选条件下没有技艺 -->
      <div v-else class="csk-empty">
        <span class="csk-empty-glyph">艺</span>
        <p class="csk-empty-text">暂无{{ activeTabLabel }}技艺</p>
      </div>
    </div>

    <!-- 新增/编辑技艺弹窗：表单内容较长，主体区域可滚动 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑技艺' : '新增技艺'"
      width="min(960px, calc(100vw - 40px))"
      top="3vh"
      :close-on-click-modal="false"
      class="csk-dialog"
    >
      <div class="csk-dlg-body">
        <!-- 区块一：基本信息（名称、级别、分类、流派、难度、地区、封面、简介、材料工具、附件） -->
        <div class="csk-sec">
          <div class="csk-sec-title"><b>基本信息</b><i>名称 / 级别 / 分类 / 封面，展示在技艺页题头</i></div>
          <div class="csk-grid csk-grid-2">
            <el-form-item label="技艺名称" class="csk-fi">
              <el-input v-model="form.name" placeholder="如：髹漆技艺" />
            </el-form-item>
            <el-form-item label="技艺级别" class="csk-fi">
              <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
                <el-option v-for="lv in skillLevels" :key="lv" :label="lv" :value="lv" />
              </el-select>
            </el-form-item>
            <el-form-item label="技艺分类" class="csk-fi">
              <el-input v-model="form.category" placeholder="如：髹漆 / 镏金 / 雕漆" />
            </el-form-item>
            <el-form-item label="工艺流派" class="csk-fi">
              <el-select
                v-model="form.school"
                placeholder="请选择，或直接输入流派名"
                filterable
                allow-create
                default-first-option
                clearable
                style="width: 100%"
              >
                <el-option v-for="sc in skillSchools" :key="sc" :label="sc" :value="sc" />
              </el-select>
            </el-form-item>
            <el-form-item label="难度等级" class="csk-fi">
              <el-select v-model="form.difficulty" placeholder="请选择" style="width: 100%">
                <el-option v-for="d in difficultyOptions" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
            <el-form-item label="从艺年限" class="csk-fi">
              <el-input-number v-model="form.years" :min="0" :max="80" style="width: 100%" />
            </el-form-item>
          </div>
          <div class="csk-grid csk-grid-2">
            <el-form-item label="所在地区（可选）" class="csk-fi">
              <el-input v-model="form.region" placeholder="如：广东省阳江市" />
            </el-form-item>
            <el-form-item label="技艺图片（题头大图）" class="csk-fi">
              <div class="csk-coverrow">
                <img v-if="form.image" :src="form.image" class="csk-coverpreview" alt="技艺图" />
                <span v-else class="csk-coverplaceholder">艺</span>
                <div class="csk-coverops">
                  <el-upload :show-file-list="false" :before-upload="onImagePick" accept="image/*">
                    <el-button size="small">{{ form.image ? '更换图片' : '上传图片' }}</el-button>
                  </el-upload>
                  <el-button v-if="form.image" size="small" text type="danger" @click="form.image = ''">移除</el-button>
                </div>
              </div>
            </el-form-item>
          </div>
          <el-form-item label="技艺简介（题头下方一句话介绍）" class="csk-fi">
            <el-input v-model="form.desc" type="textarea" :rows="2" maxlength="120" show-word-limit placeholder="简要介绍技艺特色，如：以腰果漆髹涂日用漆器见长，漆膜坚韧耐潮" />
          </el-form-item>
          <div class="csk-grid csk-grid-2">
            <el-form-item label="原材料清单（顿号分隔）" class="csk-fi">
              <el-input v-model="form.raw_materials" type="textarea" :rows="2" placeholder="如：天然生漆、夏布、瓦灰、金箔" />
            </el-form-item>
            <el-form-item label="专用工具（顿号分隔）" class="csk-fi">
              <el-input v-model="form.tools" type="textarea" :rows="2" placeholder="如：刻刀、刮刀、漆刷、磨石" />
            </el-form-item>
          </div>
          <el-form-item label="制作难点" class="csk-fi">
            <el-input v-model="form.hard_points" type="textarea" :rows="2" maxlength="200" show-word-limit placeholder="如：髹涂须薄而匀，厚一分即起皱；剔刻运刀深浅不匀则纹样呆板" />
          </el-form-item>
          <el-form-item label="注意事项" class="csk-fi">
            <el-input v-model="form.cautions" type="textarea" :rows="2" maxlength="200" show-word-limit placeholder="如：生漆易致敏，操作须戴手套；荫房温湿度控制在 25℃／75% 左右" />
          </el-form-item>
          <el-form-item label="附件文档（参考资料 / 图鉴 / 教材）" class="csk-fi">
            <div class="csk-files">
              <div v-for="(a, i) in form.attachments" :key="i" class="csk-file">
                <span class="csk-file-ico">📎</span>
                <a class="csk-file-link" :href="a.url" target="_blank" rel="noopener">{{ a.name }}</a>
                <el-button text size="small" type="danger" @click="removeAttachment(i)">移除</el-button>
              </div>
              <el-upload
                class="csk-file-upload"
                :show-file-list="false"
                :before-upload="onAttachmentPick"
                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip"
              >
                <el-button size="small" plain>＋ 添加附件</el-button>
              </el-upload>
            </div>
            <p class="csk-file-hint">支持图片、PDF、Word、Excel、PPT 等，单文件 ≤ {{ docMaxMb }}MB；审核通过后在技艺页底部提供下载</p>
          </el-form-item>
        </div>

        <!-- 区块二：历史背景，可增删段落并上下移动排序 -->
        <div class="csk-sec">
          <div class="csk-sec-title">
            <b>壹 · 历史背景</b>
            <i>逐段讲述源流与历史（每段在页面中作为独立自然段），保存时自动成为正文第一章节</i>
            <button class="csk-mini-add" @click="addHistory">＋ 添加一段</button>
          </div>
          <div class="csk-blocks">
            <div v-for="(p, i) in b.history" :key="'h' + i" class="csk-para">
              <span class="csk-idx">段{{ i + 1 }}</span>
              <el-input
                v-model="p.text"
                type="textarea"
                :rows="3"
                class="csk-para-input"
                placeholder="输入这一段的文字内容（建议一段讲清一件事：起源、地方特色、代表传承人……）"
              />
              <div class="csk-row-ops">
                <button class="csk-ico" :disabled="i === 0" @click="moveUp(b.history, i)">↑</button>
                <button class="csk-ico" :disabled="i === b.history.length - 1" @click="moveDown(b.history, i)">↓</button>
                <button class="csk-ico csk-ico-del" @click="removeAt(b.history, i)">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 区块三：工艺流程，每道工序含名称、工具材料、做法与工序图 -->
        <div class="csk-sec">
          <div class="csk-sec-title">
            <b>贰 · 工艺流程</b>
            <i>按实际制作顺序逐道填写；页面中每道工序是一张卡：名称 + 工具/材料标签 + 做法文字（+ 可选工序图）</i>
            <button class="csk-mini-add" @click="addStep">＋ 添加工序</button>
          </div>
          <div class="csk-blocks">
            <div v-for="(s, i) in b.steps" :key="'s' + i" class="csk-step">
              <div class="csk-step-head">
                <span class="csk-idx">工序 {{ pad(i + 1) }}</span>
                <el-input v-model="s.name" class="csk-step-name" placeholder="工序名，如：制胎成型" maxlength="30" />
                <div class="csk-row-ops">
                  <button class="csk-ico" :disabled="i === 0" @click="moveUp(b.steps, i)">↑</button>
                  <button class="csk-ico" :disabled="i === b.steps.length - 1" @click="moveDown(b.steps, i)">↓</button>
                  <button class="csk-ico csk-ico-del" @click="removeAt(b.steps, i)">删除工序</button>
                </div>
              </div>
              <div class="csk-grid csk-grid-2">
                <el-form-item label="工具（顿号分隔）" class="csk-fi">
                  <el-input v-model="s.tools" placeholder="如：牛角刮刀、漆刷、荫箱" />
                </el-form-item>
                <el-form-item label="材料（顿号分隔）" class="csk-fi">
                  <el-input v-model="s.materials" placeholder="如：天然大漆、瓦灰、夏布" />
                </el-form-item>
              </div>
              <el-form-item label="做法（具体怎么操作）" class="csk-fi">
                <el-input v-model="s.method" type="textarea" :rows="2" placeholder="写下这一步做什么、怎么动作、有什么要领，2~4 句话为佳" />
              </el-form-item>
              <div class="csk-grid csk-grid-2">
                <el-form-item label="工序图（可选，展示在做法下方）" class="csk-fi">
                  <div class="csk-bodyimg">
                    <img v-if="s.image" :src="s.image" class="csk-bodyimg-thumb" alt="工序图" />
                    <el-upload v-if="!s.image" :show-file-list="false" :before-upload="(f) => bodyImgPick(f, s)" accept="image/*">
                      <el-button size="small">上传工序图</el-button>
                    </el-upload>
                    <el-button v-if="s.image" size="small" text type="danger" @click="s.image = ''">移除</el-button>
                  </div>
                </el-form-item>
                <el-form-item label="图片说明（可选）" class="csk-fi">
                  <el-input v-model="s.caption" placeholder="图的配文，如：裱布后入荫阴干" maxlength="40" />
                </el-form-item>
              </div>
            </div>
            <p v-if="!b.steps.length" class="csk-hint">还没有工序。点右上「＋ 添加工序」逐道添加；没有工序图可以先留空，之后在正文页面再补图。</p>
          </div>
        </div>

        <!-- 区块四：工艺纪实（可选），标题+文字+配图卡片，可排序 -->
        <div class="csk-sec">
          <div class="csk-sec-title">
            <b>叁 · 工艺纪实（可选）</b>
            <i>补充特色 / 难点 / 传承故事，一段文字配一张图，左右交替排版</i>
            <button class="csk-mini-add" @click="addCard">＋ 添加一块</button>
          </div>
          <div class="csk-blocks">
            <div v-for="(c, i) in b.cards" :key="'c' + i" class="csk-card-block">
              <div class="csk-card-block-head">
                <span class="csk-idx">纪实 {{ i + 1 }}</span>
                <div class="csk-row-ops">
                  <button class="csk-ico" :disabled="i === 0" @click="moveUp(b.cards, i)">↑</button>
                  <button class="csk-ico" :disabled="i === b.cards.length - 1" @click="moveDown(b.cards, i)">↓</button>
                  <button class="csk-ico csk-ico-del" @click="removeAt(b.cards, i)">删除</button>
                </div>
              </div>
              <el-form-item label="小标题" class="csk-fi">
                <el-input v-model="c.title" placeholder="如：何谓平磨螺钿" maxlength="30" />
              </el-form-item>
              <el-form-item label="文字内容" class="csk-fi">
                <el-input v-model="c.text" type="textarea" :rows="3" placeholder="这一段要讲的内容，可配一张图" />
              </el-form-item>
              <div class="csk-grid csk-grid-2">
                <el-form-item label="配图（可选）" class="csk-fi">
                  <div class="csk-bodyimg">
                    <img v-if="c.image" :src="c.image" class="csk-bodyimg-thumb" alt="配图" />
                    <el-upload v-if="!c.image" :show-file-list="false" :before-upload="(f) => bodyImgPick(f, c)" accept="image/*">
                      <el-button size="small">上传配图</el-button>
                    </el-upload>
                    <el-button v-if="c.image" size="small" text type="danger" @click="c.image = ''">移除</el-button>
                  </div>
                </el-form-item>
                <el-form-item label="图片说明（可选）" class="csk-fi">
                  <el-input v-model="c.caption" placeholder="图的配文" maxlength="40" />
                </el-form-item>
              </div>
            </div>
            <p v-if="!b.cards.length" class="csk-hint">留空则该章节不出现在详情页；填了会以「标题 + 段落 + 图」的卡片展示。</p>
          </div>
        </div>

        <!-- 区块五：代表作与关联课程；代表作从本人已上架作品中多选 -->
        <div class="csk-sec">
          <div class="csk-sec-title"><b>代表作与课程</b><i>「代表作品」展示在正文之后；关联课程可留空</i></div>
          <el-form-item label="代表作品" class="csk-fi">
            <el-select
              v-model="form.worksProductIds"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="从你的已上架作品中勾选 1~N 件代表作"
              style="width: 100%"
            >
              <el-option v-for="p in ownApprovedProducts" :key="p.id" :label="productOptionLabel(p)" :value="p.id" />
            </el-select>
            <p v-if="ownApprovedProducts.length" class="csk-hint">
              勾选后，普通端「技艺详情 · 代表作品」将展示这些作品并可点进购买
            </p>
            <p v-else class="csk-hint">
              还没有已上架作品，先到
              <router-link to="/console/works" class="csk-link">商城作品</router-link>
              上架一件，才能勾选为该技艺的代表作
            </p>
          </el-form-item>
          <el-form-item label="关联课程" class="csk-fi">
            <el-input v-model="form.courses" type="textarea" :rows="1" placeholder="多个课程用｜分隔，可留空" />
          </el-form-item>
        </div>
      </div>

      <!-- 弹窗底部：取消、预览成稿、保存（编辑已通过/已下架技艺时保存会重新提交审核） -->
      <template #footer>
        <div class="csk-dlg-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button @click="openPreview">预览成稿效果</el-button>
          <el-button type="primary" @click="saveSkill">保存{{ editingId ? '并重新提交审核' : '' }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 成稿预览遮罩：复用普通端技艺详情组件渲染当前未保存草稿 -->
    <div v-if="previewVisible" class="csk-preview-mask" @click.self="previewVisible = false">
      <div class="csk-preview-head">
        <span class="csk-preview-title">成稿效果预览 · {{ form.name || '未命名技艺' }}</span>
        <span class="csk-preview-tag">未保存草稿 · 展示的是提交审核通过后的页面效果</span>
        <button class="csk-preview-close" @click="previewVisible = false">返回继续编辑 ×</button>
      </div>
      <div class="csk-preview-scroll">
        <SkillDetailPage :skill="previewSkill" preview />
      </div>
    </div>
  </ConsoleLayout>
</template>

<script setup>
/* 页面逻辑：列表筛选与状态统计、弹窗表单、分段正文编辑、上传、保存和审核操作 */
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import SkillDetailPage from '@/views/user/archive/SkillDetailPage.vue'
import { uploadSkillImage, uploadSkillDoc } from '@/api/skills'
import {
  heritageSkills, skillStatusMap, skillLevels, skillSchools, loadSkills,
  heritageProducts, loadProducts,
  addSkill, updateSkillAction, submitSkillAction,
  removeSkill as removeSkillRemote, toggleOfflineSkill,
  heritageProfile, loadHeritageProfile,
  checkUploadFile, uploadLimitMb,
} from '@/store'

// 附件上传大小上限（MB），由系统配置决定，默认 20MB
const docMaxMb = computed(() => uploadLimitMb(20))

/* 统一提取接口错误信息，取不到时返回兜底文案 */
function errMsg(e) {
  return (e && e.message) || '操作失败，请重试'
}

// 审核状态 → 文案/颜色的映射，卡片和状态标签共用
const statusMap = skillStatusMap

// 难度选项，与后端约定的三个等级
const difficultyOptions = ['零基础', '进阶', '高级']

// 进入页面时并行拉取技艺、作品和个人档案；作品用于「代表作」多选，档案用于默认作者
onMounted(() => {
  loadSkills().catch(() => {})
  loadProducts().catch(() => {})
  loadHeritageProfile().catch(() => {})
})
// 直接引用 store 中的响应式数组，加载完成后列表会自动刷新
const skillList = heritageSkills

/* 可勾选为代表作的作品：只保留审核通过（已上架）的作品 */
const ownApprovedProducts = computed(() =>
  heritageProducts.filter((p) => p.status === 'approved')
)

/* 作品下拉项的展示文案：名称 · 技艺（品类） */
function productOptionLabel(p) {
  const craft = p.craft ? ' · ' + p.craft : ''
  const cat = p.category ? '（' + p.category + '）' : ''
  return p.name + craft + cat
}

/* 根据作品 id 列表找出对应作品名称；id 统一转成数字后比较，过滤无效 id */
function worksNamesOf(s) {
  const ids = (Array.isArray(s.worksProductIds) ? s.worksProductIds : []).map(Number).filter(Boolean)
  if (!ids.length) return []
  return heritageProducts.filter((p) => ids.includes(Number(p.id))).map((p) => p.name)
}

/* 统计正文各区块的有效条目数，生成卡片上的「历史 N 段 · 工序 N 道」摘要 */
function bodySummary(s) {
  // 兼容 body 未存或格式异常的情况
  const bo = s.body && typeof s.body === 'object' ? s.body : {}
  // 只统计至少有一个非空字段的条目
  const n = (a) => (Array.isArray(a) ? a.filter((x) => x && Object.values(x).some((v) => v !== '')).length : 0)
  const h = n(bo.history)
  const st = n(bo.steps)
  const c = n(bo.cards)
  if (!h && !st && !c) return ''
  const parts = []
  if (h) parts.push('历史 ' + h + ' 段')
  if (st) parts.push('工序 ' + st + ' 道')
  if (c) parts.push('纪实 ' + c + ' 块')
  return parts.join(' · ')
}

/* 状态筛选标签配置；value 与后端 status 字段一致 */
const tabs = [
  { label: '全部', value: 'all' },
  { label: '草稿', value: 'draft' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已驳回', value: 'rejected' },
  { label: '已下架', value: 'offline' },
]
// 当前选中的状态标签
const activeTab = ref('all')
const activeTabLabel = computed(() => tabs.find((t) => t.value === activeTab.value)?.label || '')
// 根据当前标签过滤列表；「全部」直接返回原数组
const filtered = computed(() => {
  if (activeTab.value === 'all') return skillList
  return skillList.filter((s) => s.status === activeTab.value)
})
/* 统计某个状态的技艺数量，用于标签上的数字 */
function countOf(v) {
  if (v === 'all') return skillList.length
  return skillList.filter((s) => s.status === v).length
}

/* 把「｜」分隔的字符串拆成数组（代表作、关联课程、旧版工序字段都复用） */
function parseList(str) {
  return (str || '').split('｜').map((x) => x.trim()).filter(Boolean)
}
/* 数字补齐两位，用于工序序号显示（01、02……） */
function pad(n) {
  return String(n).padStart(2, '0')
}

// 弹窗与预览层开关；editingId 为 null 表示新增，否则为正在编辑的技艺 id
const dialogVisible = ref(false)
const editingId = ref(null)
const previewVisible = ref(false)

/* 新增技艺时的默认表单值，级别/难度/年限给常用默认值 */
const emptyForm = () => ({
  name: '',
  image: '',
  level: '省级',
  difficulty: '零基础',
  category: '',
  school: '',
  region: '',
  years: 20,
  desc: '',
  raw_materials: '',
  tools: '',
  hard_points: '',
  cautions: '',
  attachments: [],
  works: '',
  worksProductIds: [],
  courses: '',
  ownerName: '',
})
// 弹窗表单数据；用 reactive 包裹，模板中的 v-model 才能双向绑定
const form = reactive(emptyForm())

/* 正文各区块的空模板：新增段落/工序/纪实卡片时复用 */
const emptyPara = () => ({ text: '' })
const emptyStep = () => ({ name: '', tools: '', materials: '', method: '', image: '', caption: '' })
const emptyCard = () => ({ title: '', text: '', image: '', caption: '' })
// 正文编辑数据：历史段落、工序、纪实卡片分别维护，便于独立增删排序
const b = reactive({ history: [], steps: [], cards: [] })

/* 重置正文编辑区：历史默认留一个空段落，工序和纪实清空 */
function resetTemplate() {
  b.history.splice(0, b.history.length, emptyPara())
  b.steps.splice(0, b.steps.length)
  b.cards.splice(0, b.cards.length)
}

/* 正文分块的增删与排序操作：直接修改数组，界面随之更新 */
function addHistory() { b.history.push(emptyPara()) }
function addStep() { b.steps.push(emptyStep()) }
function addCard() { b.cards.push(emptyCard()) }
function moveUp(arr, i) { if (i > 0) { const t = arr[i - 1]; arr[i - 1] = arr[i]; arr[i] = t } }
function moveDown(arr, i) { if (i < arr.length - 1) { const t = arr[i + 1]; arr[i + 1] = arr[i]; arr[i] = t } }
function removeAt(arr, i) { arr.splice(i, 1) }

/* 校验图片类型和大小后上传，返回图片 URL；失败返回 null。封面、工序图、纪实配图共用 */
async function uploadBodyImage(file) {
  const nm = (file.name || '').toLowerCase()
  const ext = nm.includes('.') ? nm.split('.').pop() : ''
  const isImg = /^image\//.test(file.type || '') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)
  if (!isImg) { ElMessage.error('请选择图片文件（jpg/png/gif/webp/bmp）'); return null }
  const err = checkUploadFile(file, { name: '图片', fallbackMb: 15 })
  if (err) { ElMessage.error(err); return null }
  const res = await uploadSkillImage(file)
  return res.url || ''
}

/* 封面选择：el-upload 的 before-upload 回调，始终返回 false 阻止组件自动上传 */
async function onImagePick(file) {
  try {
    const url = await uploadBodyImage(file)
    if (url) { form.image = url; ElMessage.success('图片已上传') }
  } catch (e) { ElMessage.error(errMsg(e)) }
  return false
}

/* 附件选择：校验后上传到技能文档接口，成功后追加到 form.attachments */
async function onAttachmentPick(file) {
  const err = checkUploadFile(file, { name: '附件', fallbackMb: 20 })
  if (err) { ElMessage.error(err); return false }
  try {
    const res = await uploadSkillDoc(file)
    form.attachments.push({ name: res.name || file.name, url: res.url })
    ElMessage.success('附件已添加')
  } catch (e) { ElMessage.error(errMsg(e)) }
  return false
}

/* 从表单中移除指定附件 */
function removeAttachment(i) {
  form.attachments.splice(i, 1)
}

/* 工序图/纪实配图上传：把返回的 URL 写回对应的正文块 */
async function bodyImgPick(file, block) {
  try {
    const url = await uploadBodyImage(file)
    if (url) { block.image = url; ElMessage.success('图片已上传') }
  } catch (e) { ElMessage.error(errMsg(e)) }
  return false
}

/* 打开新增弹窗：清空表单、重置正文，并预填当前传承人姓名 */
function openCreate() {
  loadProducts().catch(() => {})
  editingId.value = null
  Object.assign(form, emptyForm(), { ownerName: heritageProfile.name || '' })
  resetTemplate()
  dialogVisible.value = true
  previewVisible.value = false
}

/* 打开编辑弹窗：把列表项字段回填到表单，并把正文数据转换成可编辑结构 */
function openEdit(s) {
  loadProducts().catch(() => {})
  editingId.value = s.id
  Object.assign(form, {
    name: s.name,
    image: s.image || '',
    level: s.level,
    difficulty: s.difficulty || '零基础',
    category: s.category,
    school: s.school || '',
    region: s.region || '',
    years: s.years,
    desc: s.desc,
    raw_materials: s.rawMaterials || s.raw_materials || '',
    tools: s.tools || '',
    hard_points: s.hardPoints || s.hard_points || '',
    cautions: s.cautions || '',
    attachments: Array.isArray(s.attachments) ? s.attachments.slice() : [],
    works: s.works,
    worksProductIds: Array.isArray(s.worksProductIds) ? s.worksProductIds.map(Number) : [],
    courses: s.courses,
    ownerName: s.ownerName || heritageProfile.name || '',
  })

  const bo = s.body && typeof s.body === 'object' ? s.body : {}
  // 历史段落优先取 body.history；旧数据没有时用摘要/简介兜底成一段
  const histSrc = (Array.isArray(bo.history) && bo.history.length)
    ? bo.history.map((p) => ({ text: (p && p.text) || '' }))
    : (s.abstract || s.desc)
      ? [{ text: s.abstract || s.desc || '' }]
      : []
  // 工序优先取 body.steps；旧数据只有「｜」分隔的工序名，用空模板占位
  const stepsSrc = (Array.isArray(bo.steps) && bo.steps.length)
    ? bo.steps.map((x) => ({ name: (x && x.name) || '', tools: (x && x.tools) || '', materials: (x && x.materials) || '', method: (x && x.method) || '', image: (x && x.image) || '', caption: (x && x.caption) || '' }))
    : parseList(s.steps).map((name) => emptyStep())
  // 纪实卡片只来自 body.cards，没有就留空
  const cardsSrc = (Array.isArray(bo.cards) && bo.cards.length)
    ? bo.cards.map((x) => ({ title: (x && x.title) || '', text: (x && x.text) || '', image: (x && x.image) || '', caption: (x && x.caption) || '' }))
    : []
  b.history.splice(0, b.history.length, ...(histSrc.length ? histSrc : [emptyPara()]))
  b.steps.splice(0, b.steps.length, ...(stepsSrc.length ? stepsSrc : []))
  b.cards.splice(0, b.cards.length, ...cardsSrc)
  dialogVisible.value = true
  previewVisible.value = false
}

/* 收集正文编辑区的有效内容：去空格、去掉空段落/空工序，供保存和预览使用 */
function bodyPayload() {
  const history = b.history
    .map((p) => ({ text: (p.text || '').trim() }))
    .filter((p) => p.text)
  const steps = b.steps
    .map((s) => ({ name: (s.name || '').trim(), tools: (s.tools || '').trim(), materials: (s.materials || '').trim(), method: (s.method || '').trim(), image: s.image || '', caption: (s.caption || '').trim() }))
    .filter((s) => s.name)
  const cards = b.cards
    .map((c) => ({ title: (c.title || '').trim(), text: (c.text || '').trim(), image: c.image || '', caption: (c.caption || '').trim() }))
    .filter((c) => c.text)
  return { history, steps, cards }
}

/* 用当前表单临时拼一个技艺对象，交给详情页组件做只读预览 */
const previewSkill = computed(() => {
  const payload = bodyPayload()
  return {
    id: editingId.value,
    name: form.name,
    glyph: form.name.charAt(0) || '艺',
    image: form.image,
    level: form.level,
    difficulty: form.difficulty,
    category: form.category,
    school: form.school,
    region: form.region,
    years: form.years,
    desc: form.desc,
    raw_materials: form.raw_materials,
    tools: form.tools,
    hard_points: form.hard_points,
    cautions: form.cautions,
    attachments: Array.isArray(form.attachments) ? form.attachments.slice() : [],
    body: payload,
    steps: payload.steps.map((s) => s.name).join('｜'),
    abstract: payload.history[0] ? payload.history[0].text : (form.desc || ''),
    works: '',
    worksProductIds: form.worksProductIds,
    courses: form.courses,
    ownerName: form.ownerName,
    status: 'draft',
    submitTime: '',
  }
})

/* 打开成稿预览（只渲染临时对象，不影响真实数据） */
function openPreview() {
  previewVisible.value = true
}

/* 保存技艺：先做前端必填校验，再按新增/编辑分别调用接口；已通过或已下架的技艺修改后重新提交审核 */
async function saveSkill() {
  if (!form.name.trim()) { ElMessage.warning('请填写技艺名称'); return }
  if (!form.category.trim()) { ElMessage.warning('请填写技艺分类'); return }
  if (ownApprovedProducts.length && !form.worksProductIds.length) {
    ElMessage.warning('请至少勾选一件已上架作品作为该技艺的代表作')
    return
  }
  const payload = bodyPayload()
  // 至少要有简介，或正文中有一段历史/工序/纪实，避免保存空内容
  if (!payload.history.length && !payload.steps.length && !payload.cards.length && !form.desc.trim()) {
    ElMessage.warning('请至少填写「技艺简介」或正文中的一段文字（历史 / 工序 / 纪实）')
    return
  }

  const formData = {
    ...form,
    body: payload,
    steps: payload.steps.map((s) => s.name).join('｜'),
    abstract: payload.history[0] ? payload.history[0].text : '',
  }

  try {
    if (editingId.value) {
      // 编辑：先记录原状态，保存后据此判断是否需要自动重新提交审核
      const target = skillList.find((s) => s.id === editingId.value)
      const oldStatus = target ? target.status : ''
      await updateSkillAction(editingId.value, formData)
      if (oldStatus === 'approved' || oldStatus === 'offline') {
        await submitSkillAction(editingId.value)
        ElMessage.success('已保存并重新提交审核')
      } else {
        ElMessage.success('已保存')
      }
    } else {
      await addSkill(formData)
      ElMessage.success('技艺已创建，当前为草稿状态')
    }
    dialogVisible.value = false
    previewVisible.value = false
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

/* 提交审核：先二次确认，再调用提交接口 */
async function submitReview(s) {
  try {
    await ElMessageBox.confirm('提交后管理员将进行审核，通过后技艺将公开显示。确定提交？', '提交审核', {
      confirmButtonText: '提交',
      cancelButtonText: '再想想',
      type: 'info',
    })
  } catch (e) { return }
  try {
    await submitSkillAction(s.id)
    ElMessage.success('已提交审核，请等待管理员审核')
  } catch (e) { ElMessage.error(errMsg(e)) }
}

/* 上架/下架切换：已通过 → 下架，已下架 → 重新上架 */
async function toggleOffline(s) {
  const goingDown = s.status === 'approved'
  try {
    await toggleOfflineSkill(s.id)
    ElMessage.success(goingDown ? '技艺已下架' : '技艺已重新上架')
  } catch (e) { ElMessage.error(errMsg(e)) }
}

/* 删除技艺：二次确认后调用删除接口，删除不可恢复 */
async function removeSkill(s) {
  try {
    await ElMessageBox.confirm(`确定删除技艺「${s.name}」吗？删除后不可恢复。`, '删除技艺', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch (e) { return }
  try {
    await removeSkillRemote(s.id)
    ElMessage.success('删除成功')
  } catch (e) { ElMessage.error(errMsg(e)) }
}
</script>

<style src="./ConsoleSkills.css"></style>

<style>

/* 列表卡片封面与正文链接 */
.csk-cover-img {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: 3px;
}
.csk-link {
  color: #8b2e1c;
  text-decoration: underline;
}

/* 弹窗：统一圆角，主体内容超高时在弹窗内部滚动 */
:deep(.csk-dialog) {
  --el-dialog-border-radius: 8px;
}
.csk-dlg-body {
  max-height: 72vh;
  overflow-y: auto;
  padding-right: 6px;
}
.csk-dlg-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  align-items: center;
}
.csk-dlg-footer .el-button--primary {
  background: #8b2e1c;
  border-color: #8b2e1c;
}

/* 弹窗内的分区卡片：虚线边框 + 米色背景，区分不同填写模块 */
.csk-sec {
  border: 1px dashed #e0d5c0;
  border-radius: 8px;
  padding: 16px 18px 6px;
  margin-bottom: 16px;
  background: #fffdf8;
}
.csk-sec-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.csk-sec-title b {
  font-size: 15px;
  color: #8b2e1c;
  letter-spacing: 1px;
  white-space: nowrap;
}
.csk-sec-title i {
  font-style: normal;
  font-size: 12px;
  color: #a8937a;
  flex: 1;
  line-height: 1.6;
}
.csk-mini-add {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 12px;
  padding: 6px 14px;
  border: 1px solid #8b2e1c;
  color: #8b2e1c;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
}
.csk-mini-add:hover { background: #8b2e1c; color: #f5efe4; }

/* 表单两列网格；窄屏媒体查询中会改成单列 */
.csk-grid { display: grid; gap: 0 16px; }
.csk-grid-2 { grid-template-columns: 1fr 1fr; }
.csk-fi { margin-bottom: 10px; }
.csk-fi .el-form-item__label { color: #6b5a44; font-size: 13px; }

.csk-coverrow { display: flex; align-items: center; gap: 12px; }
.csk-coverpreview { width: 72px; height: 72px; object-fit: cover; border-radius: 4px; border: 1px solid #e0d5c0; flex-shrink: 0; }
.csk-coverplaceholder { width: 72px; height: 72px; display: flex; align-items: center; justify-content: center; border-radius: 4px; background: #efe4d0; color: #8b2e1c; font-size: 26px; flex-shrink: 0; }
.csk-coverops { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }

.csk-file-link { flex: 1; min-width: 0; font-size: 13px; color: #8b2e1c; text-decoration: none; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.csk-file-link:hover { text-decoration: underline; }

.csk-blocks { display: flex; flex-direction: column; gap: 12px; margin-bottom: 12px; }
.csk-para { display: flex; gap: 10px; align-items: flex-start; background: #fdfaf2; border: 1px solid #eee3cd; border-radius: 6px; padding: 10px 12px; }
.csk-para-input { flex: 1; }
.csk-idx { flex-shrink: 0; font-size: 12px; color: #8b2e1c; background: #f6eedd; border: 1px solid #d8c6a6; border-radius: 3px; padding: 3px 8px; }
.csk-row-ops { display: flex; gap: 6px; flex-shrink: 0; }
.csk-ico { font-size: 12px; padding: 4px 10px; border: 1px solid #ddd2bb; background: #fff; color: #6b5a44; border-radius: 4px; cursor: pointer; font-family: inherit; }
.csk-ico:hover { border-color: #8b2e1c; color: #8b2e1c; }
.csk-ico:disabled { opacity: 0.4; cursor: not-allowed; }
.csk-ico-del { color: #c62828; border-color: #ecc6c6; }
.csk-ico-del:hover { background: #c62828; color: #fff; }

.csk-step { background: #fdfaf2; border: 1px solid #eee3cd; border-left: 3px solid #8b2e1c; border-radius: 6px; padding: 12px 14px; }
.csk-step-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.csk-step-name { flex: 1; max-width: 320px; }

.csk-card-block { background: #fdfaf2; border: 1px solid #eee3cd; border-radius: 6px; padding: 12px 14px; }
.csk-card-block-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }

.csk-bodyimg { display: flex; align-items: center; gap: 10px; }
.csk-bodyimg-thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #e0d5c0; }
.csk-hint:first-child { margin-top: 0; }

/* 全屏预览遮罩：固定定位并盖在弹窗之上，内部纵向排列头部和滚动内容 */
.csk-preview-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(30, 22, 14, 0.86);
  display: flex;
  flex-direction: column;
}
.csk-preview-head {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 24px;
  background: #2b2117;
  color: #f5efe4;
}
.csk-preview-title { font-size: 16px; letter-spacing: 2px; }
.csk-preview-close {
  margin-left: auto;
  font-size: 13px;
  padding: 6px 16px;
  border: 1px solid rgba(245, 239, 228, 0.6);
  color: #f5efe4;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  letter-spacing: 1px;
}
.csk-preview-close:hover { background: #f5efe4; color: #2b2117; }

@media (max-width: 860px) {
  .csk-grid-2 { grid-template-columns: 1fr; }

  .csk-sec-title { flex-wrap: wrap; row-gap: 6px; }
  .csk-sec-title b { white-space: normal; }
  .csk-sec-title i { flex: 1 1 100%; order: 3; margin-top: 2px; }
  .csk-mini-add { margin-left: auto; }

  .csk-para, .csk-step-head, .csk-card-block-head { flex-wrap: wrap; row-gap: 8px; }
  .csk-para { align-items: center; }
  .csk-para .csk-para-input { order: 3; flex: 1 1 100%; min-width: 0; }
  .csk-para .csk-row-ops { order: 2; margin-left: auto; }
  .csk-step-name { flex: 1 1 200px; max-width: none; min-width: 0; }

  .csk-coverrow, .csk-bodyimg { flex-wrap: wrap; }

  .csk-dlg-footer { flex-wrap: wrap; }

  .csk-preview-head { flex-wrap: wrap; row-gap: 8px; }
  .csk-preview-close { margin-left: auto; }
}
</style>
