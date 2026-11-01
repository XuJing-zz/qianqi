<!-- AdminProducts.vue 库存管理页：统一维护文创作品、基础材料/工具的库存，并查看出入库流水。 -->
<template>
  <AdminLayout>
    <div class="apr-wrap">
      <!-- 页面标题区：展示用途说明，并提供「录入作品」快捷入口 -->
      <div class="apr-head">
        <div class="apr-head-left">
          <h2 class="apr-title">库存管理</h2>
          <p class="apr-sub">文创作品 · 基础材料 · 工具，录入 / 编辑 / 入库出库 / 库存告警一屏掌握</p>
        </div>
        <div class="apr-head-actions">
          <button class="apr-add-btn" @click="openWorkCreate">＋ 录入作品</button>
        </div>
      </div>

      <!-- 顶部页签区：在「作品库存 / 基础工具材料 / 出入库流水」三个视图之间切换 -->
      <div class="apr-main-tabs">
        <button
          v-for="t in mainTabs"
          :key="t.value"
          class="apr-main-tab"
          :class="{ 'apr-main-tab-active': mainTab === t.value }"
          @click="mainTab = t.value"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- ===== 页签一：文创作品库存 ===== -->
      <div v-if="mainTab === 'products'">
        <!-- 筛选区：关键字、状态、工艺流派、传承人、价格区间、库存状态 -->
        <div class="apr-filter">
          <el-input v-model="productKeyword" placeholder="搜索作品名 / 传承人 / 工艺" clearable style="width: 240px" />
          <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 130px">
            <el-option v-for="(v, k) in productStatusMap" :key="k" :label="v.label" :value="k" />
          </el-select>
          <el-select v-model="craftFilter" placeholder="工艺流派" clearable filterable style="width: 150px">
            <el-option v-for="c in filterOptions.craft" :key="c" :label="c" :value="c" />
          </el-select>
          <el-select v-model="inheritorFilter" placeholder="创作传承人" clearable filterable style="width: 150px">
            <el-option v-for="m in filterOptions.inheritor" :key="m" :label="m" :value="m" />
          </el-select>
          <el-select v-model="priceFilter" placeholder="价格区间" clearable style="width: 150px">
            <el-option v-for="r in priceRangeOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
          <el-select v-model="stockFilter" placeholder="库存状态" clearable style="width: 140px">
            <el-option label="有货" value="in" />
            <el-option label="缺货" value="out" />
            <el-option label="库存告急" value="low" />
          </el-select>
          <span class="apr-filter-total">共 {{ invTotal }} 件作品</span>
        </div>

        <!-- 列表区：卡片形式展示作品信息、库存状态与操作按钮 -->
        <div v-if="invLoading" class="apr-loading">加载中…</div>
        <div v-else-if="invRows.length" class="apr-list">
          <div v-for="p in invRows" :key="p.id" class="apr-card">
            <div class="apr-cover"><span class="apr-cover-glyph">{{ p.glyph || p.name.charAt(0) }}</span></div>
            <div class="apr-body">
              <div class="apr-body-top">
                <h3 class="apr-name">{{ p.name }}</h3>
                <span class="apr-badge" :style="{ color: productStatusMap[p.status].color, borderColor: productStatusMap[p.status].color }">
                  {{ productStatusMap[p.status].label }}
                </span>
              </div>
              <div class="apr-meta">
                <span class="apr-meta-item">{{ p.craft }}</span>
                <span class="apr-meta-item">{{ p.category }}</span>
                <span class="apr-meta-item">{{ p.inheritor }}</span>
                <span v-if="p.saleable" class="apr-meta-item">售价 ¥{{ p.price }}</span>
                <span v-else class="apr-meta-item">非卖品</span>
              </div>
              <div class="apr-stock">
                <span class="apr-stock-label">库存：</span>
                <span class="apr-stock-num" :style="{ color: productStockState(p).color }">{{ p.stock }}</span>
                <span class="apr-stock-state" :style="{ color: productStockState(p).color }">{{ productStockState(p).label }}</span>
                <span v-if="p.alertThreshold" class="apr-stock-threshold">（预警值 {{ p.alertThreshold }}）</span>
              </div>
              <div class="apr-actions">
                <button class="apr-btn" @click="openWorkEdit(p)">编辑</button>
                <button v-if="p.status === 'approved'" class="apr-btn" @click="offline(p)">下架</button>
                <button v-else-if="p.status === 'offline'" class="apr-btn apr-btn-pass" @click="online(p)">上架</button>
                <button class="apr-btn" @click="openProductStock(p, 'in')">入库</button>
                <button class="apr-btn" @click="openProductStock(p, 'out')">出库</button>
                <button class="apr-btn apr-btn-loss" @click="openProductStock(p, 'loss')">损耗</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="apr-empty">
          <span class="apr-empty-glyph">作</span>
          <p class="apr-empty-text">暂无作品</p>
        </div>

        <!-- 分页区：按后端返回的总条数切换页码 -->
        <div v-if="invTotal > pageSize" class="apr-pager">
          <el-pagination
            background
            layout="prev, pager, next, total"
            :total="invTotal"
            :page-size="pageSize"
            :current-page="invPage"
            @current-change="onInvPage"
          />
        </div>
      </div>

      <!-- ===== 页签二：基础工具材料 ===== -->
      <div v-else-if="mainTab === 'materials'">
        <!-- 筛选区：按物料名称与类型过滤 -->
        <div class="apr-filter">
          <el-input v-model="materialKeyword" placeholder="搜索物料名" clearable style="width: 240px" />
          <el-select v-model="materialTypeFilter" placeholder="类型" clearable style="width: 130px">
            <el-option v-for="(v, k) in materialTypeMap" :key="k" :label="v.label" :value="k" />
          </el-select>
          <span class="apr-filter-total">共 {{ filteredMaterials.length }} 项物料</span>
        </div>

        <!-- 汇总区：统计当前筛选结果中的缺货与告急数量 -->
        <div class="apr-mat-summary">
          <span>共 <strong>{{ filteredMaterials.length }}</strong> 项物料</span>
          <span>缺货 <strong class="apr-sum-red">{{ shortageCount('danger') }}</strong></span>
          <span>告急 <strong class="apr-sum-warn">{{ shortageCount('warn') }}</strong></span>
        </div>

        <!-- 表格区：逐行展示物料规格、关联课程、库存与出入库操作 -->
        <div v-if="filteredMaterials.length" class="apr-mat-table">
          <div class="apr-mat-row apr-mat-head">
            <span>物料</span>
            <span>类型</span>
            <span>规格</span>
            <span>关联课程</span>
            <span>库存</span>
            <span>状态</span>
            <span>操作</span>
          </div>
          <div v-for="m in filteredMaterials" :key="m.id" class="apr-mat-row">
            <span class="apr-mat-name">{{ m.name }}</span>
            <span>
              <span class="apr-mat-type" :style="{ color: materialTypeMap[m.type].color, borderColor: materialTypeMap[m.type].color }">
                {{ materialTypeMap[m.type].label }}
              </span>
            </span>
            <span class="apr-mat-spec">{{ m.spec }}</span>
            <span class="apr-mat-link">{{ m.linkedCourseName || '—' }}</span>
            <span class="apr-mat-stock" :style="{ color: materialState(m).color }">{{ m.stock }}</span>
            <span class="apr-mat-state" :style="{ color: materialState(m).color }">{{ materialState(m).label }}</span>
            <span class="apr-mat-actions">
              <button class="apr-btn" @click="openMaterialStock(m, 'in')">入库</button>
              <button class="apr-btn" @click="openMaterialStock(m, 'out')">出库</button>
            </span>
          </div>
        </div>
        <div v-else class="apr-empty">
          <span class="apr-empty-glyph">料</span>
          <p class="apr-empty-text">暂无物料</p>
        </div>
      </div>

      <!-- ===== 页签三：出入库流水 ===== -->
      <div v-else>
        <!-- 作品出入库流水区：倒序展示每次入库/出库/损耗记录 -->
        <div class="apr-rec-block">
          <h3 class="apr-rec-title">作品出入库流水</h3>
          <div v-if="psrLoading" class="apr-rec-loading">加载中…</div>
          <div v-else-if="psrRows.length" class="apr-records">
            <div class="apr-rec-row apr-rec-head">
              <span>作品</span>
              <span>类型</span>
              <span>数量</span>
              <span>说明</span>
              <span>操作人</span>
              <span>时间</span>
            </div>
            <div v-for="r in psrRows" :key="r.id" class="apr-rec-row">
              <span class="apr-rec-name">{{ r.productName }}</span>
              <span>
                <span class="apr-rec-type" :style="{ color: stockRecordTypeMap[r.type].color, borderColor: stockRecordTypeMap[r.type].color }">
                  {{ stockRecordTypeMap[r.type].label }}
                </span>
              </span>
              <span class="apr-rec-qty" :style="{ color: (r.type === 'in') ? '#2e7d32' : '#c62828' }">
                {{ r.type === 'in' ? '+' : '-' }}{{ r.qty }}
              </span>
              <span class="apr-rec-note">{{ r.note || '—' }}</span>
              <span>{{ r.operator }}</span>
              <span class="apr-rec-time">{{ r.time }}</span>
            </div>
          </div>
          <div v-else class="apr-empty apr-empty-sm">
            <span class="apr-empty-glyph">账</span>
            <p class="apr-empty-text">暂无作品出入库记录</p>
          </div>
          <div v-if="psrTotal > psrPageSize" class="apr-rec-pager">
            <el-pagination
              background
              layout="prev, pager, next, total"
              :total="psrTotal"
              :page-size="psrPageSize"
              :current-page="psrPage"
              @current-change="onPsrPage"
            />
          </div>
        </div>

        <!-- 材料/工具出入库流水区：与上方结构一致，分页加载 -->
        <div class="apr-rec-block">
          <h3 class="apr-rec-title">材料 / 工具出入库流水</h3>
          <div v-if="msrLoading" class="apr-rec-loading">加载中…</div>
          <div v-else-if="msrRows.length" class="apr-records">
            <div class="apr-rec-row apr-rec-head">
              <span>物料</span>
              <span>类型</span>
              <span>数量</span>
              <span>说明</span>
              <span>操作人</span>
              <span>时间</span>
            </div>
            <div v-for="r in msrRows" :key="r.id" class="apr-rec-row">
              <span class="apr-rec-name">{{ r.materialName }}</span>
              <span>
                <span class="apr-rec-type" :style="{ color: materialRecordTypeMap[r.type].color, borderColor: materialRecordTypeMap[r.type].color }">
                  {{ materialRecordTypeMap[r.type].label }}
                </span>
              </span>
              <span class="apr-rec-qty" :style="{ color: (r.type === 'in') ? '#2e7d32' : '#c62828' }">
                {{ r.type === 'in' ? '+' : '-' }}{{ r.qty }}
              </span>
              <span class="apr-rec-note">{{ r.note || '—' }}</span>
              <span>{{ r.operator }}</span>
              <span class="apr-rec-time">{{ r.time }}</span>
            </div>
          </div>
          <div v-else class="apr-empty apr-empty-sm">
            <span class="apr-empty-glyph">账</span>
            <p class="apr-empty-text">暂无材料出入库记录</p>
          </div>
          <div v-if="msrTotal > msrPageSize" class="apr-rec-pager">
            <el-pagination
              background
              layout="prev, pager, next, total"
              :total="msrTotal"
              :page-size="msrPageSize"
              :current-page="msrPage"
              @current-change="onMsrPage"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 作品录入/编辑弹窗：同一表单通过 workForm.id 区分新增与编辑 -->
    <el-dialog
      v-model="workDialog"
      :title="workForm.id ? '编辑作品' : '录入作品'"
      width="min(620px, calc(100vw - 32px))"
      :close-on-click-modal="false"
    >
      <el-form :model="workForm" label-width="96px" class="apr-work-form">
        <el-form-item label="作品名称">
          <el-input v-model="workForm.name" placeholder="请输入作品名称" maxlength="200" />
        </el-form-item>
        <el-form-item label="技艺门类">
          <el-input v-model="workForm.craft" placeholder="如：髹漆 / 螺钿 / 描金 / 雕漆" maxlength="50" />
        </el-form-item>
        <el-form-item label="品类">
          <el-select v-model="workForm.category" placeholder="请选择" filterable allow-create style="width: 100%">
            <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="材质">
          <el-input v-model="workForm.material" placeholder="如：天然生漆 · 木胎" />
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="workForm.size" placeholder="如：口径 10cm · 高 6cm" />
        </el-form-item>
        <el-form-item label="作者/传承人">
          <el-select
            v-model="workForm.inheritor"
            placeholder="选择人才库传承人，或直接填写姓名"
            filterable
            allow-create
            clearable
            style="width: 100%"
          >
            <el-option v-for="m in filterOptions.inheritor" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否可售">
          <el-radio-group v-model="workForm.saleable">
            <el-radio :label="true">可售</el-radio>
            <el-radio :label="false">非卖（仅展示）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="workForm.saleable" label="售价（元）">
          <el-input-number v-model="workForm.price" :min="0" :step="10" />
        </el-form-item>
        <el-form-item label="成本价（元）">
          <el-input-number v-model="workForm.costPrice" :min="0" :step="10" />
        </el-form-item>
        <el-form-item label="库存 / 预警">
          <div class="apr-work-stock">
            <el-input-number v-model="workForm.stock" :min="0" :max="99999" />
            <span class="apr-work-stock-sep">预警值</span>
            <el-input-number v-model="workForm.alertThreshold" :min="0" :max="9999" />
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="workForm.status" style="width: 100%">
            <el-option v-for="(v, k) in productStatusMap" :key="k" :label="v.label" :value="k" />
          </el-select>
          <p class="apr-work-tip">管理员录入可直接选「已通过」上架；选「草稿」则仅后台可见。</p>
        </el-form-item>
        <el-form-item label="作品故事">
          <el-input v-model="workForm.story" type="textarea" :rows="3" placeholder="介绍作品背景与创作理念" />
        </el-form-item>
        <el-form-item label="工艺亮点">
          <el-input v-model="workHighlightsText" type="textarea" :rows="3" placeholder="每行一条亮点，如：犀皮打捻起纹" />
        </el-form-item>
        <!-- 图片上传：本地读取为 DataURL 预览，保存时随表单一起提交 -->
        <el-form-item label="作品照片">
          <div class="apr-upload">
            <div class="apr-upload-list">
              <div v-for="(img, i) in workImages" :key="i" class="apr-upload-item">
                <img :src="img" class="apr-upload-img" alt="" />
                <span v-if="i === 0" class="apr-upload-cover-tag">封面</span>
                <button class="apr-upload-remove" title="移除" @click="removeWorkImage(i)">×</button>
              </div>
              <button v-if="workImages.length < maxWorkImages" class="apr-upload-add" @click="triggerWorkUpload">
                <span class="apr-upload-add-glyph">＋</span>
                <span class="apr-upload-add-text">上传</span>
              </button>
            </div>
            <input ref="workFileInput" type="file" accept="image/*" multiple class="apr-file-hidden" @change="onWorkFileChange" />
            <p class="apr-upload-tip">第一张作为封面，最多 {{ maxWorkImages }} 张，单张不超过 {{ maxWorkImageMb }}MB（上传限制由「系统配置」设定）</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workDialog = false">取消</el-button>
        <el-button type="primary" :loading="workSaving" @click="saveWork">保存</el-button>
      </template>
    </el-dialog>

    <!-- 作品出入库弹窗：根据 stockMode 在入库/出库/损耗之间切换 -->
    <el-dialog v-model="productStockDialog" :title="stockTitle" width="480px" :close-on-click-modal="false">
      <p class="apr-dialog-tip">作品：<strong>{{ productStockTarget?.name }}</strong>（当前库存 {{ productStockTarget ? productStockTarget.stock : 0 }}）</p>
      <div class="apr-form">
        <label class="apr-form-row">
          <span class="apr-form-label">数量 *</span>
          <el-input-number v-model="stockQty" :min="1" :max="9999" style="width: 100%" />
        </label>
        <label class="apr-form-row">
          <span class="apr-form-label">说明</span>
          <el-input
            v-model="stockNote"
            :placeholder="stockMode === 'in' ? '如：新品入库 / 补货' : stockMode === 'loss' ? '如：破损报废 / 丢失' : '如：订单销售 / 领用'"
          />
        </label>
      </div>
      <template #footer>
        <el-button @click="productStockDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmProductStock">确认{{ stockActionLabel }}</el-button>
      </template>
    </el-dialog>

    <!-- 物料入库/出库弹窗：只允许正数数量，提交后刷新物料与流水 -->
    <el-dialog v-model="materialStockDialog" :title="materialMode === 'in' ? '物料入库' : '物料出库'" width="480px" :close-on-click-modal="false">
      <p class="apr-dialog-tip">物料：<strong>{{ materialStockTarget?.name }}</strong>（当前库存 {{ materialStockTarget ? materialStockTarget.stock : 0 }}）</p>
      <div class="apr-form">
        <label class="apr-form-row">
          <span class="apr-form-label">数量 *</span>
          <el-input-number v-model="materialQty" :min="1" :max="9999" style="width: 100%" />
        </label>
        <label class="apr-form-row">
          <span class="apr-form-label">说明</span>
          <el-input v-model="materialNote" :placeholder="materialMode === 'in' ? '如：采购入库' : '如：课程领用 / 损耗'" />
        </label>
      </div>
      <template #footer>
        <el-button @click="materialStockDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMaterialStock">确认{{ materialMode === 'in' ? '入库' : '出库' }}</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
/* 库存管理组件：三个页签分别对应作品库存、材料库存和出入库流水；
   作品支持录入/编辑/上下架/出入库，材料支持筛选与出入库，所有操作都会写入操作日志。 */
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listProducts, fetchProductFilters } from '@/api/products'
import { listStockRecords as listProductStockRecords } from '@/api/products'
import { listStockRecords as listMaterialStockRecords } from '@/api/inventory'
import { mapKeys } from '@/api/utils'
// 作品状态、物料类型、流水类型与库存状态的映射统一来自 store，模板据此显示中文标签和颜色
import {
  inventoryMaterials,
  productStatusMap,
  addProduct,
  updateProductAction,
  productStockState,
  stockRecordTypeMap,
  stockInOut,
  materialTypeMap,
  materialState,
  materialRecordTypeMap,
  materialStockInOut,
  loadMaterials,
  addLog,
  authState,
  uploadLimitMb,
  uploadLimitCount,
  checkUploadFile,
} from '@/store'

// 页面初始化：并行加载作品、筛选项、材料与两类流水；单个接口失败不影响其余区块
onMounted(() => {
  loadInvRows()
  loadFilterOptions()
  loadMaterials().catch(() => {})
  loadPsrRows()
  loadMsrRows()
})

// 三个库存视图页签，value 用于模板中的条件渲染
const mainTabs = [
  { label: '文创作品库存', value: 'products' },
  { label: '基础工具材料', value: 'materials' },
  { label: '出入库流水', value: 'records' },
]
const mainTab = ref('products')

// 取当前登录管理员姓名，作为出入库/操作日志的操作人
function operator() {
  return authState.user?.name || '管理员'
}


// 作品筛选条件：关键字与各下拉筛选项，任一变化都会回到第 1 页重新查询
const productKeyword = ref('')
const statusFilter = ref('')
const stockFilter = ref('')
const craftFilter = ref('')
const inheritorFilter = ref('')
const priceFilter = ref('')
// 价格区间选项：min/max 会转换成后端需要的 price_min / price_max 参数
const priceRangeOptions = [
  { value: '0-200', label: '200 元以下', min: 0, max: 200 },
  { value: '200-500', label: '200 - 500 元', min: 200, max: 500 },
  { value: '500-1000', label: '500 - 1000 元', min: 500, max: 1000 },
  { value: '1000-', label: '1000 元以上', min: 1000, max: null },
]
// 筛选项候选值：由后端聚合已有作品的品类、工艺流派与传承人
const filterOptions = reactive({ category: [], craft: [], inheritor: [] })

// 拉取筛选下拉选项；失败时保持为空，不阻塞主列表
async function loadFilterOptions() {
  try {
    const res = await fetchProductFilters()
    filterOptions.craft = res.craft || []
    filterOptions.inheritor = res.inheritor || []
    filterOptions.category = res.category || []
  } catch (e) {
  }
}
// 作品分页状态：行数据、总数、当前页、每页条数与加载标记
const invRows = ref([])
const invTotal = ref(0)
const invPage = ref(1)
const pageSize = 8
const invLoading = ref(false)
let invSeq = 0

// 把后端作品字段整理成页面使用的结构，并为可能缺失的数组/字符串补默认值
function mapProductInvRow(p) {
  const m = mapKeys(p)
  return {
    ...m,
    price: Number(m.price ?? 0),
    images: Array.isArray(m.images) ? m.images : [],
    highlights: Array.isArray(m.highlights) ? m.highlights : [],
    submitTime: m.submitTime || '',
    reviewComment: m.reviewComment || '',
  }
}

/* 加载当前页作品：
   1. 按筛选条件拼装查询参数；2. 用 invSeq 序号防止旧请求覆盖新结果；
   3. 兼容后端直接返回数组或 { results, count } 两种分页格式。 */
async function loadInvRows() {
  const my = ++invSeq
  invLoading.value = true
  try {
    // 只把已填写的筛选条件加入请求参数，空值不传
    const params = { page: invPage.value, page_size: pageSize, keyword: productKeyword.value.trim() }
    if (statusFilter.value) params.status = statusFilter.value
    if (stockFilter.value) params.stock_status = stockFilter.value
    if (craftFilter.value) params.craft = craftFilter.value
    if (inheritorFilter.value) params.inheritor = inheritorFilter.value
    const range = priceRangeOptions.find((r) => r.value === priceFilter.value)
    if (range) {
      params.price_min = range.min
      if (range.max != null) params.price_max = range.max
    }
    const res = await listProducts(params)
    if (my !== invSeq) return
    if (Array.isArray(res)) {
      invRows.value = res.map(mapProductInvRow)
      invTotal.value = res.length
    } else {
      invRows.value = (res.results || []).map(mapProductInvRow)
      invTotal.value = res.count || 0
    }
    // 当前页为空但总数不为零（如删除末页最后一条）时，回退到第 1 页重载
    if (!invRows.value.length && invPage.value > 1 && invTotal.value > 0) {
      invPage.value = 1
      return loadInvRows()
    }
  } catch (e) {
    if (my !== invSeq) return
    ElMessage.error((e && e.message) || '加载失败')
  } finally {
    if (my === invSeq) invLoading.value = false
  }
}

// 筛选条件变化：重置到第 1 页后重新查询
function onInvFilter() {
  invPage.value = 1
  loadInvRows()
}

// 点击分页器切换作品页码
function onInvPage(p) {
  invPage.value = p
  loadInvRows()
}

// 下拉筛选立即生效；关键字输入做 300ms 防抖，避免每敲一个字都请求
watch(statusFilter, onInvFilter)
watch(stockFilter, onInvFilter)
watch(craftFilter, onInvFilter)
watch(inheritorFilter, onInvFilter)
watch(priceFilter, onInvFilter)
let invKwTimer = null
watch(productKeyword, () => {
  clearTimeout(invKwTimer)
  invKwTimer = setTimeout(onInvFilter, 300)
})

// 下架作品：二次确认后把状态改为 offline，并记入操作日志
function offline(p) {
  ElMessageBox.confirm(`确定下架「${p.name}」吗？下架后前台不再展示。`, '下架作品', {
    confirmButtonText: '下架',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await updateProductAction(p.id, { status: 'offline' })
      addLog('update', operator(), '下架作品', `「${p.name}」已下架`)
      ElMessage.success('已下架')
      await loadInvRows()
    })
    .catch(() => {})
}

// 上架作品：把状态改为 approved，使前台重新可见
function online(p) {
  updateProductAction(p.id, { status: 'approved' })
    .then(async () => {
      addLog('update', operator(), '上架作品', `「${p.name}」已上架`)
      ElMessage.success('已上架')
      await loadInvRows()
    })
    .catch(() => ElMessage.error('上架失败'))
}

// 作品弹窗状态：workDialog 控制显隐，workSaving 控制保存按钮 loading
const workDialog = ref(false)
const workSaving = ref(false)
// 工艺亮点用多行文本编辑，保存时按行拆分；workImages 保存图片 DataURL 列表
const workHighlightsText = ref('')
const workImages = ref([])
const workFileInput = ref(null)
// 上传张数/大小限制来自「系统配置」，未配置时分别回退为 9 张、50MB
const maxWorkImages = computed(() => uploadLimitCount(9))
const maxWorkImageMb = computed(() => uploadLimitMb(50))

// 品类候选：内置常用品类与后端已有品类合并去重，允许用户自行输入新品类
const CATEGORY_PRESET = ['茶器', '文房', '首饰', '摆件', '日用', '雅玩']
const categoryOptions = computed(() => Array.from(new Set([...filterOptions.category, ...CATEGORY_PRESET])))

// 新增作品时的表单初始值；编辑时会用 openWorkEdit 覆盖这些字段
const emptyWork = () => ({
  id: null,
  name: '',
  craft: '',
  category: '茶器',
  material: '',
  size: '',
  inheritor: '',
  saleable: true,
  price: 0,
  costPrice: 0,
  stock: 0,
  alertThreshold: 5,
  status: 'approved',
  story: '',
})
// 表单对象保持同一个引用，新增/编辑都通过 Object.assign 复用
const workForm = reactive(emptyWork())

// 打开「录入作品」：先重置表单、亮点与图片，再显示弹窗
function openWorkCreate() {
  Object.assign(workForm, emptyWork())
  workHighlightsText.value = ''
  workImages.value = []
  workDialog.value = true
}

// 打开「编辑作品」：把列表行数据回填到表单，图片优先用 images，旧数据回退到 cover
function openWorkEdit(p) {
  Object.assign(workForm, {
    id: p.id,
    name: p.name || '',
    craft: p.craft || '',
    category: p.category || '茶器',
    material: p.material || '',
    size: p.size || '',
    inheritor: p.inheritor || '',
    saleable: p.saleable !== false,
    price: Number(p.price ?? 0),
    costPrice: Number(p.costPrice ?? 0),
    stock: Number(p.stock ?? 0),
    alertThreshold: Number(p.alertThreshold ?? 5),
    status: p.status || 'draft',
    story: p.story || '',
  })
  workHighlightsText.value = (p.highlights || []).join('\n')
  workImages.value = (p.images && p.images.length ? p.images : (p.cover ? [p.cover] : [])).slice()
  workDialog.value = true
}

/* 保存作品：
   先校验名称与技艺门类，再把亮点文本拆成数组、组装封面/图片等字段；
   有 id 调用更新接口，无 id 调用新增接口，成功后关闭弹窗并刷新列表与筛选项。 */
async function saveWork() {
  // 名称与技艺门类是必填项，未填写时直接提示并中断保存
  const name = workForm.name.trim()
  const craft = workForm.craft.trim()
  if (!name) {
    ElMessage.warning('请填写作品名称')
    return
  }
  if (!craft) {
    ElMessage.warning('请填写技艺门类')
    return
  }
  const highlights = workHighlightsText.value
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)
  // 亮点按行拆分并去掉空行；第一张图片同时作为封面
  const payload = {
    name,
    craft,
    category: workForm.category || '',
    material: workForm.material,
    size: workForm.size,
    inheritor: (workForm.inheritor || '').trim(),
    saleable: workForm.saleable,
    price: workForm.saleable ? workForm.price : 0,
    costPrice: workForm.costPrice,
    stock: workForm.stock,
    alertThreshold: workForm.alertThreshold,
    status: workForm.status,
    story: workForm.story,
    glyph: name.charAt(0),
    highlights,
    images: workImages.value.slice(),
    cover: workImages.value[0] || '',
  }
  // 保存期间禁用按钮，避免重复提交
  workSaving.value = true
  try {
    if (workForm.id) {
      await updateProductAction(workForm.id, payload)
      addLog('update', operator(), '编辑作品', `作品「${name}」信息已更新`)
      ElMessage.success('已保存')
    } else {
      await addProduct(payload)
      addLog('create', operator(), '录入作品', `作品「${name}」已录入`)
      ElMessage.success('作品已录入')
    }
    workDialog.value = false
    await loadInvRows()
    loadFilterOptions()
  } catch (e) {
    ElMessage.error((e.data && (e.data.detail || e.data.msg)) || (e && e.message) || '保存失败')
  } finally {
    workSaving.value = false
  }
}

// 点击自定义上传按钮时，转去触发隐藏的 file input
function triggerWorkUpload() {
  workFileInput.value && workFileInput.value.click()
}

/* 选择图片后的处理：
   先按剩余可上传张数截断，再逐个检查文件类型/大小（checkUploadFile），
   通过校验的文件用 FileReader 读成 DataURL 供本地预览。 */
function onWorkFileChange(e) {
  const files = e.target.files
  if (!files || !files.length) return
  const remaining = maxWorkImages.value - workImages.value.length
  const toRead = Array.from(files).slice(0, remaining)
  if (toRead.length < files.length) {
    ElMessage.warning(`最多上传 ${maxWorkImages.value} 张照片，已自动截取前几张`)
  }
  toRead.forEach((file) => {
    const err = checkUploadFile(file, { name: `「${file.name}」`, fallbackMb: 50 })
    if (err) {
      ElMessage.warning(`${err}，已跳过`)
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      workImages.value.push(reader.result)
    }
    reader.readAsDataURL(file)
  })
  e.target.value = ''
}

// 从预览列表移除指定图片，后续索引会自动前移
function removeWorkImage(i) {
  workImages.value.splice(i, 1)
}

// 材料筛选条件：名称关键字与物料类型
const materialKeyword = ref('')
const materialTypeFilter = ref('')

// 前端过滤材料列表：类型精确匹配，名称忽略大小写做包含匹配
const filteredMaterials = computed(() => {
  const kw = materialKeyword.value.trim().toLowerCase()
  let list = materialTypeFilter.value
    ? inventoryMaterials.filter((m) => m.type === materialTypeFilter.value)
    : inventoryMaterials
  if (kw) {
    list = list.filter((m) => (m.name || '').toLowerCase().includes(kw))
  }
  return list
})

// 统计缺货（库存 <= 0）或告急（0 < 库存 <= 预警值）的物料数量
function shortageCount(level) {
  return filteredMaterials.value.filter((m) => {
    if (level === 'danger') return m.stock <= 0
    return m.stock > 0 && m.stock <= m.alertThreshold
  }).length
}

// 作品出入库弹窗状态：stockMode 取 in/out/loss，stockQty 为本次数量
const productStockDialog = ref(false)
const stockMode = ref('in')
const stockQty = ref(1)
const stockNote = ref('')
let productStockTarget = null

// 根据操作模式生成按钮/标题文案（入库 / 出库 / 损耗）
const stockActionLabel = computed(() => (stockMode.value === 'in' ? '入库' : stockMode.value === 'loss' ? '损耗' : '出库'))
const stockTitle = computed(() => `作品${stockActionLabel.value}`)

// 打开作品出入库弹窗，并记录目标作品与操作模式
function openProductStock(p, mode) {
  productStockTarget = p
  stockMode.value = mode
  stockQty.value = 1
  stockNote.value = ''
  productStockDialog.value = true
}

/* 确认作品出入库：
   stockInOut 返回 { ok, msg }；失败时展示原因并保留弹窗，
   成功后写操作日志、关闭弹窗，并同时刷新作品列表与作品流水。 */
async function confirmProductStock() {
  if (!productStockTarget) return
  const label = stockActionLabel.value
  const res = await stockInOut(productStockTarget, stockMode.value, stockQty.value, stockNote.value.trim(), operator())
  if (!res.ok) {
    ElMessage.error(res.msg)
    return
  }
  addLog(stockMode.value === 'in' ? 'create' : 'update', operator(),
    `作品${label}`,
    `「${productStockTarget.name}」${stockMode.value === 'in' ? '+' : '-'}${stockQty.value}`)
  ElMessage.success(`${label}成功`)
  productStockDialog.value = false
  productStockTarget = null
  loadInvRows()
  loadPsrRows()
}

// 物料出入库弹窗状态：materialMode 只区分 in/out
const materialStockDialog = ref(false)
const materialMode = ref('in')
const materialQty = ref(1)
const materialNote = ref('')
let materialStockTarget = null

// 打开物料入库/出库弹窗，并记录目标物料与模式
function openMaterialStock(m, mode) {
  materialStockTarget = m
  materialMode.value = mode
  materialQty.value = 1
  materialNote.value = ''
  materialStockDialog.value = true
}

// 确认物料出入库：成功后刷新材料列表与材料流水
async function confirmMaterialStock() {
  if (!materialStockTarget) return
  const mode = materialMode.value
  const type = mode === 'in' ? 'in' : 'out'
  const res = await materialStockInOut(materialStockTarget, type, materialQty.value, materialNote.value.trim(), operator())
  if (!res.ok) {
    ElMessage.error(res.msg)
    return
  }
  addLog(mode === 'in' ? 'create' : 'update', operator(),
    mode === 'in' ? '物料入库' : '物料出库',
    `「${materialStockTarget.name}」${mode === 'in' ? '+' : '-'}${materialQty.value}`)
  ElMessage.success(mode === 'in' ? '入库成功' : '出库成功')
  materialStockDialog.value = false
  materialStockTarget = null
  loadMaterials().catch(() => {})
  loadMsrRows()
}

// 作品出入库流水分页状态（psr = product stock records）
const psrRows = ref([])
const psrTotal = ref(0)
const psrPage = ref(1)
const psrPageSize = 8
const psrLoading = ref(false)
let psrSeq = 0

// 统一流水记录的字段名，兼容 time / createdAt 两种时间字段
function mapProductStockRecord(r) {
  const m = mapKeys(r)
  return {
    id: m.id,
    productName: m.productName || '',
    type: m.type || 'in',
    qty: m.qty ?? 0,
    note: m.note || '',
    operator: m.operator || '管理员',
    time: m.time || m.createdAt || '',
  }
}

// 分页加载作品出入库流水，并用 psrSeq 防止旧请求覆盖新结果
async function loadPsrRows() {
  const my = ++psrSeq
  psrLoading.value = true
  try {
    const res = await listProductStockRecords({ page: psrPage.value, page_size: psrPageSize })
    if (my !== psrSeq) return
    if (Array.isArray(res)) {
      psrRows.value = res.map(mapProductStockRecord)
      psrTotal.value = res.length
    } else {
      psrRows.value = (res.results || []).map(mapProductStockRecord)
      psrTotal.value = res.count || 0
    }
    if (!psrRows.value.length && psrPage.value > 1 && psrTotal.value > 0) {
      psrPage.value = 1
      return loadPsrRows()
    }
  } catch (e) {
    if (my !== psrSeq) return
    ElMessage.error((e && e.message) || '加载失败')
  } finally {
    if (my === psrSeq) psrLoading.value = false
  }
}

// 切换作品流水页码
function onPsrPage(p) {
  psrPage.value = p
  loadPsrRows()
}

// 材料出入库流水分页状态（msr = material stock records）
const msrRows = ref([])
const msrTotal = ref(0)
const msrPage = ref(1)
const msrPageSize = 8
const msrLoading = ref(false)
let msrSeq = 0

// 统一材料流水字段，缺失字段给出默认值
function mapMaterialStockRecord(r) {
  const m = mapKeys(r)
  return {
    id: m.id,
    materialName: m.materialName || '',
    type: m.type || 'in',
    qty: m.qty ?? 0,
    note: m.note || '',
    operator: m.operator || '管理员',
    time: m.time || m.createdAt || '',
  }
}

// 分页加载材料出入库流水，并用 msrSeq 防止竞态覆盖
async function loadMsrRows() {
  const my = ++msrSeq
  msrLoading.value = true
  try {
    const res = await listMaterialStockRecords({ page: msrPage.value, page_size: msrPageSize })
    if (my !== msrSeq) return
    if (Array.isArray(res)) {
      msrRows.value = res.map(mapMaterialStockRecord)
      msrTotal.value = res.length
    } else {
      msrRows.value = (res.results || []).map(mapMaterialStockRecord)
      msrTotal.value = res.count || 0
    }
    if (!msrRows.value.length && msrPage.value > 1 && msrTotal.value > 0) {
      msrPage.value = 1
      return loadMsrRows()
    }
  } catch (e) {
    if (my !== msrSeq) return
    ElMessage.error((e && e.message) || '加载失败')
  } finally {
    if (my === msrSeq) msrLoading.value = false
  }
}

// 切换材料流水页码
function onMsrPage(p) {
  msrPage.value = p
  loadMsrRows()
}
</script>

<style src="./AdminProducts.css"></style>

<style scoped>
/* 页头右侧操作按钮布局 */
.apr-head-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.apr-add-btn {
  background: #1e6fb8;
  border: 1px solid #1e6fb8;
  color: #fff;
  border-radius: 8px;
  padding: 9px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.apr-add-btn:hover {
  background: #175a97;
  border-color: #175a97;
}
/* 库存数量与预警值并排输入 */
.apr-work-stock {
  display: flex;
  align-items: center;
  gap: 10px;
}
.apr-work-stock-sep {
  color: #8a93a3;
  font-size: 13px;
}
.apr-work-tip {
  margin: 4px 0 0;
  color: #8a93a3;
  font-size: 12px;
  line-height: 1.5;
}
.apr-upload {
  width: 100%;
}
/* 图片预览列表：自动换行排列 */
.apr-upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
/* 单张图片缩略图容器，封面标签与删除按钮绝对定位其上 */
.apr-upload-item {
  position: relative;
  width: 84px;
  height: 84px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e6ea;
}
.apr-upload-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.apr-upload-cover-tag {
  position: absolute;
  left: 0;
  bottom: 0;
  background: rgba(30, 111, 184, 0.85);
  color: #fff;
  font-size: 11px;
  padding: 1px 6px;
  border-top-right-radius: 6px;
}
.apr-upload-remove {
  position: absolute;
  right: 2px;
  top: 2px;
  width: 18px;
  height: 18px;
  line-height: 16px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  cursor: pointer;
  font-size: 13px;
}
/* 虚线「上传」占位块，尺寸与缩略图保持一致 */
.apr-upload-add {
  width: 84px;
  height: 84px;
  border: 1px dashed #c9d2dc;
  border-radius: 8px;
  background: #fafbfc;
  color: #8a93a3;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}
.apr-upload-add:hover {
  border-color: #1e6fb8;
  color: #1e6fb8;
}
.apr-upload-add-glyph {
  font-size: 20px;
  line-height: 1;
}
.apr-upload-add-text {
  font-size: 12px;
}
/* 隐藏原生 file input，由自定义按钮代为触发 */
.apr-file-hidden {
  display: none;
}
.apr-upload-tip {
  margin: 8px 0 0;
  color: #8a93a3;
  font-size: 12px;
}
.apr-filter-total {
  margin-left: 12px;
  color: #8a93a3;
  font-size: 13px;
}
.apr-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
/* 分页器右对齐 */
.apr-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
.apr-rec-loading {
  padding: 24px 0;
  text-align: center;
  color: #8a93a3;
}
.apr-rec-pager {
  display: flex;
  justify-content: flex-end;
  margin: 10px 0 4px;
}
</style>
