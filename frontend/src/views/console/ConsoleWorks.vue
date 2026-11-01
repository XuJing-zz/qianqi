<!-- 传承人工作台 · 作品管理：展示本人作品，支持新建/编辑、多图上传、提交审核、上下架与删除 -->
<template>
  <!-- 工作台统一布局 -->
  <ConsoleLayout>
    <div class="cwk-wrap">
      <!-- 页头：标题、作品总数与新建入口 -->
      <div class="cwk-head">
        <div class="cwk-head-left">
          <h2 class="cwk-title">我的作品</h2>
          <p class="cwk-sub">共 {{ workList.length }} 件作品</p>
        </div>
        <button class="cwk-add-btn" @click="openCreate">＋ 新建作品</button>
      </div>

      <!-- 状态标签：按审核状态筛选作品并显示数量 -->
      <div class="cwk-tabs">
        <button
          v-for="t in tabs"
          :key="t.value"
          class="cwk-tab"
          :class="{ 'cwk-tab-active': activeTab === t.value }"
          @click="activeTab = t.value"
        >
          {{ t.label }}
          <span class="cwk-tab-count">{{ countOf(t.value) }}</span>
        </button>
      </div>

      <!-- 作品列表：每张卡片展示封面、名称、作者/门类/材质/尺寸与操作按钮 -->
      <div v-if="filtered.length" class="cwk-list">
        <div v-for="w in filtered" :key="w.id" class="cwk-card">
          <!-- 封面区：无图时显示首字占位；多图时右上角显示额外图片数量 -->
          <div class="cwk-cover">
            <img v-if="w.cover" :src="w.cover" class="cwk-cover-img" alt="" />
            <span v-else class="cwk-cover-glyph">{{ w.glyph || w.name.charAt(0) }}</span>
            <template v-if="w.images && w.images.length > 1">
              <span class="cwk-cover-count">+{{ w.images.length - 1 }}</span>
            </template>
          </div>
          <div class="cwk-body">
            <!-- 作品名与审核状态徽标 -->
            <div class="cwk-body-top">
              <h3 class="cwk-name">{{ w.name }}</h3>
              <span class="cwk-badge" :style="{ color: statusMap[w.status].color, borderColor: statusMap[w.status].color }">
                {{ statusMap[w.status].label }}
              </span>
            </div>
            <!-- 作者、技艺门类、品类、材质、尺寸等基础信息 -->
            <div class="cwk-meta">
              <span class="cwk-meta-item">作者：{{ w.inheritor || '—' }}</span>
              <span class="cwk-meta-item">{{ w.craft }}</span>
              <span class="cwk-meta-item">{{ w.category }}</span>
              <span class="cwk-meta-item">{{ w.material }}</span>
              <span class="cwk-meta-item">{{ w.size }}</span>
            </div>
            <!-- 销售信息：可售/非卖、售价与自定义标签 -->
            <div class="cwk-meta cwk-meta-num">
              <span class="cwk-meta-item">
                <span class="cwk-sale-tag" :class="w.saleable ? 'cwk-sale-on' : 'cwk-sale-off'">
                  {{ w.saleable ? '可售' : '非卖' }}
                </span>
              </span>
              <span v-if="w.saleable" class="cwk-meta-item">售价 ¥{{ w.price }}</span>
              <span v-if="w.flag" class="cwk-meta-item">标签：{{ w.flag }}</span>
            </div>
            <!-- 被驳回时显示管理员意见 -->
            <div v-if="w.status === 'rejected' && w.reviewComment" class="cwk-reject">
              <span class="cwk-reject-label">驳回意见：</span>{{ w.reviewComment }}
            </div>
            <!-- 操作区：按状态显示编辑、提交审核、下架/重新上架与删除 -->
            <div class="cwk-actions">
              <button class="cwk-btn" @click="openEdit(w)">编辑</button>
              <button v-if="w.status === 'draft' || w.status === 'rejected'" class="cwk-btn cwk-btn-primary" @click="submitReview(w)">提交审核</button>
              <button v-if="w.status === 'pending'" class="cwk-btn cwk-btn-plain" disabled>等待审核中</button>
              <button v-if="w.status === 'approved'" class="cwk-btn cwk-btn-warn" @click="toggleOffline(w)">下架</button>
              <button v-if="w.status === 'offline'" class="cwk-btn cwk-btn-primary" @click="toggleOffline(w)">重新上架</button>
              <button class="cwk-btn cwk-btn-danger" @click="removeWork(w)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态：当前筛选条件下没有作品 -->
      <div v-else class="cwk-empty">
        <span class="cwk-empty-glyph">作</span>
        <p class="cwk-empty-text">暂无{{ activeTabLabel }}作品</p>
      </div>
    </div>

    <!-- 新建/编辑作品弹窗：基础信息、销售设置、作品故事、工艺亮点与多图上传 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑作品' : '新建作品'"
      width="min(600px, calc(100vw - 32px))"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="90px" class="cwk-form">
        <!-- 基础信息：名称、技艺门类、品类、材质、尺寸、作者 -->
        <el-form-item label="作品名称">
          <el-input v-model="form.name" placeholder="请输入作品名称" />
        </el-form-item>
        <el-form-item label="技艺门类">
          <el-input v-model="form.craft" placeholder="如：髹漆 / 螺钿 / 描金 / 雕漆" />
        </el-form-item>
        <el-form-item label="品类">
          <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
            <el-option label="茶器" value="茶器" />
            <el-option label="文房" value="文房" />
            <el-option label="首饰" value="首饰" />
            <el-option label="摆件" value="摆件" />
            <el-option label="日用" value="日用" />
            <el-option label="雅玩" value="雅玩" />
          </el-select>
        </el-form-item>
        <el-form-item label="材质">
          <el-input v-model="form.material" placeholder="如：天然生漆 · 木胎" />
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="form.size" placeholder="如：口径 10cm · 高 6cm" />
        </el-form-item>
        <el-form-item label="作者">
          <el-select
            v-model="form.inheritor"
            placeholder="默认本人，也可选择人才库其他传承人或直接填姓名"
            filterable
            allow-create
            clearable
            style="width: 100%"
          >
            <el-option v-for="m in authorOptions" :key="m" :label="m" :value="m" />
          </el-select>
          <span class="cwk-field-tip">默认填本人姓名；代录他人作品时请与人才库姓名一致，前台详情页才能跳转到其主页</span>
        </el-form-item>
        <!-- 销售设置：可售时才显示售价与库存预警值 -->
        <el-form-item label="是否可售">
          <el-radio-group v-model="form.saleable">
            <el-radio :label="true">可售</el-radio>
            <el-radio :label="false">非卖（仅展示）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.saleable" label="售价（元）">
          <el-input-number v-model="form.price" :min="0" :step="10" />
        </el-form-item>
        <el-form-item v-if="form.saleable" label="库存预警值">
          <el-input-number v-model="form.alertThreshold" :min="0" :max="9999" />
          <span class="cwk-field-tip">库存 ≤ 该值时提示补货，默认 5；「库存管理」页里也能随时改</span>
        </el-form-item>
        <!-- 作品故事与工艺亮点（亮点每行一条） -->
        <el-form-item label="作品故事">
          <el-input v-model="form.story" type="textarea" :rows="3" placeholder="介绍作品背景与创作理念" />
        </el-form-item>
        <el-form-item label="工艺亮点">
          <el-input
            v-model="highlightsText"
            type="textarea"
            :rows="3"
            placeholder="每行一条亮点，如：犀皮打捻起纹"
          />
        </el-form-item>
        <!-- 作品照片：第一张作封面，支持多选；受系统配置的数量/大小上限约束 -->
        <el-form-item label="作品照片">
          <div class="cwk-upload">
            <div class="cwk-upload-list">
              <div v-for="(img, i) in formImages" :key="i" class="cwk-upload-item">
                <img :src="img" class="cwk-upload-img" alt="" />
                <span v-if="i === 0" class="cwk-upload-cover-tag">封面</span>
                <button class="cwk-upload-remove" title="移除" @click="removeImage(i)">×</button>
              </div>
              <button v-if="formImages.length < maxImages" class="cwk-upload-add" @click="triggerUpload">
                <span class="cwk-upload-add-glyph">＋</span>
                <span class="cwk-upload-add-text">上传</span>
              </button>
            </div>
            <input ref="fileInput" type="file" accept="image/*" multiple class="cwk-file-hidden" @change="onFileChange" />
            <p class="cwk-upload-tip">第一张作为封面，最多 {{ maxImages }} 张，单张不超过 {{ maxImageMb }}MB（上传限制由管理员在「系统配置」中设定）</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWork">保存</el-button>
      </template>
    </el-dialog>
  </ConsoleLayout>
</template>

<script setup>
/* 页面逻辑：作品列表筛选、表单编辑、图片本地预览与提交、审核/上下架/删除操作 */
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import { heritageProducts, productStatusMap, loadProducts, addProduct, updateProductAction, removeProduct, submitProductAction, uploadLimitMb, uploadLimitCount, checkUploadFile, inheritors, loadInheritors, heritageProfile, loadHeritageProfile, authState } from '@/store'

// 作品状态 → 文案/颜色映射
const statusMap = productStatusMap

// 直接引用 store 中的响应式作品数组，加载完成后自动刷新
const workList = heritageProducts

// 进入页面时加载作品、个人档案（默认作者）和传承人名单（作者下拉）
onMounted(() => {
  loadProducts().catch(() => {
    ElMessage.error('加载作品失败，请检查网络')
  })
  loadHeritageProfile().catch(() => {})
  loadInheritors().catch(() => {})
})

/* 当前传承人姓名：优先取档案姓名，其次取登录账号的姓名/用户名 */
const selfName = computed(() => heritageProfile.name || (authState.user && (authState.user.name || authState.user.username)) || '')

/* 作者下拉选项：人才库姓名去重，并确保本人姓名排在最前 */
const authorOptions = computed(() => {
  const names = inheritors.map((m) => (m.name || '').trim()).filter(Boolean)
  if (selfName.value && !names.includes(selfName.value)) names.unshift(selfName.value)
  return [...new Set(names)]
})

/* 状态筛选标签配置，value 与后端 status 一致 */
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

// 按状态过滤作品；「全部」直接返回原数组
const filtered = computed(() => {
  if (activeTab.value === 'all') return workList
  return workList.filter((w) => w.status === activeTab.value)
})

/* 统计某个状态的作品数量 */
function countOf(v) {
  if (v === 'all') return workList.length
  return workList.filter((w) => w.status === v).length
}

// 弹窗状态：editingId 为 null 表示新建；formImages 保存图片的 base64 预览地址
const dialogVisible = ref(false)
const editingId = ref(null)
// 工艺亮点原始文本，每行一条，保存时拆成数组
const highlightsText = ref('')
const formImages = ref([])
// 隐藏的文件输入框，点击「上传」时由代码触发
const fileInput = ref(null)
// 图片数量与单张大小上限，由系统配置决定，默认 9 张 / 50MB
const maxImages = computed(() => uploadLimitCount(9))
const maxImageMb = computed(() => uploadLimitMb(50))

/* 新建作品时的默认表单值，作者默认为本人 */
const emptyForm = () => ({
  name: '',
  craft: '',
  category: '茶器',
  material: '',
  size: '',
  inheritor: selfName.value,
  saleable: true,
  price: 0,
  alertThreshold: 5,
  story: '',
})
// 弹窗表单数据；用 reactive 包裹，模板中的 v-model 才能双向绑定
const form = reactive(emptyForm())

/* 打开新建弹窗：重置表单、亮点文本和图片列表 */
function openCreate() {
  editingId.value = null
  Object.assign(form, emptyForm())
  highlightsText.value = ''
  formImages.value = []
  dialogVisible.value = true
}

/* 打开编辑弹窗：回填表单字段、亮点文本与已有图片（没有 images 时退回 cover） */
function openEdit(w) {
  editingId.value = w.id
  Object.assign(form, {
    name: w.name,
    craft: w.craft,
    category: w.category,
    material: w.material,
    size: w.size,
    inheritor: w.inheritor || selfName.value,
    saleable: w.saleable,
    price: w.price,
    alertThreshold: Number(w.alertThreshold ?? 5),
    story: w.story,
  })
  highlightsText.value = (w.highlights || []).join('\n')
  formImages.value = (w.images && w.images.length ? w.images : (w.cover ? [w.cover] : [])).slice()
  dialogVisible.value = true
}

/* 保存作品：校验名称/门类/作者，亮点按行拆分，第一张图作为封面；新增后为草稿状态 */
async function saveWork() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写作品名称')
    return
  }
  if (!form.craft.trim()) {
    ElMessage.warning('请填写技艺门类')
    return
  }
  const author = (form.inheritor || '').trim()
  if (!author) {
    ElMessage.warning('请填写作者')
    return
  }

  const highlights = highlightsText.value
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)

  const payload = {
    ...form,
    inheritor: author,
    glyph: form.name.charAt(0),
    highlights,
    images: formImages.value.slice(),
    cover: formImages.value[0] || '',
  }

  try {
    if (editingId.value) {
      // 编辑：只更新内容，审核状态由列表中的提交/下架操作控制
      await updateProductAction(editingId.value, payload)
      ElMessage.success('已保存')
    } else {
      await addProduct(payload)
      ElMessage.success('作品已创建，当前为草稿状态')
    }
  } catch (e) {
    ElMessage.error((e.data && (e.data.detail || e.data.msg)) || '保存失败')
  }
  dialogVisible.value = false
}

/* 触发隐藏的 file 输入框，打开系统文件选择框 */
function triggerUpload() {
  fileInput.value && fileInput.value.click()
}

/* 选择图片后：按剩余张数截取、逐个校验大小，再读成 base64 追加到 formImages */
function onFileChange(e) {
  const files = e.target.files
  if (!files || !files.length) return
  // 只读取剩余名额内的图片，超出的直接忽略并提示
  const remaining = maxImages.value - formImages.value.length
  const toRead = Array.from(files).slice(0, remaining)
  if (toRead.length < files.length) {
    ElMessage.warning(`最多上传 ${maxImages.value} 张照片，已自动截取前几张`)
  }
  toRead.forEach((file) => {
    const err = checkUploadFile(file, { name: `「${file.name}」`, fallbackMb: 50 })
    if (err) {
      ElMessage.warning(`${err}，已跳过`)
      return
    }
    const reader = new FileReader()
    // 读取完成后把 base64 结果加入预览列表
    reader.onload = () => {
      formImages.value.push(reader.result)
    }
    reader.readAsDataURL(file)
  })
  // 清空输入框，保证再次选择同一文件也能触发 change
  e.target.value = ''
}

/* 移除指定图片；移除封面后下一张自动成为封面 */
function removeImage(i) {
  formImages.value.splice(i, 1)
}

/* 提交审核：确认后调用提交接口，作品由草稿/已驳回进入待审核 */
function submitReview(w) {
  ElMessageBox.confirm('提交后管理员将进行审核，审核通过后作品将公开显示。确定提交？', '提交审核', {
    confirmButtonText: '提交',
    cancelButtonText: '再想想',
    type: 'info',
  })
    .then(() => {
      submitProductAction(w.id)
        .then(() => ElMessage.success('已提交审核，请等待管理员审核'))
        .catch(() => ElMessage.error('提交审核失败'))
    })
    .catch(() => {})
}

/* 上架/下架切换：已通过 → 下架，已下架 → 重新上架 */
async function toggleOffline(w) {
  const next = w.status === 'approved' ? 'offline' : 'approved'
  try {
    await updateProductAction(w.id, { status: next })
    ElMessage.success(next === 'offline' ? '作品已下架' : '作品已重新上架')
  } catch (e) {
    ElMessage.error((e.data && (e.data.detail || e.data.msg)) || '操作失败')
  }
}

/* 删除作品：二次确认后调用删除接口，删除不可恢复 */
function removeWork(w) {
  ElMessageBox.confirm(`确定删除「${w.name}」吗？删除后不可恢复。`, '删除作品', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await removeProduct(w.id)
        ElMessage.success('删除成功')
      } catch (e) {
        ElMessage.error((e.data && (e.data.detail || e.data.msg)) || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style src="./ConsoleWorks.css"></style>
