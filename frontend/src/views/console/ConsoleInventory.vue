<!-- 库存管理页：展示传承人的作品库存，支持入库、出库、损耗登记、预警值设置与出入库台账查看 -->
<template>
  <ConsoleLayout>
    <!-- 库存管理主内容区 -->
    <div class="cin-wrap">
      <div class="cin-head">
        <div class="cin-head-left">
          <h2 class="cin-title">库存管理</h2>
          <p class="cin-sub">我的作品 · 入库 / 出库 / 损耗登记与出入库台账</p>
        </div>
      </div>

      <!-- 库存预警提示区：列出低于预警值的在售作品，点击作品名可快捷入库 -->
      <div v-if="alertWorks.length" class="cin-alert">
        <span class="cin-alert-glyph">!</span>
        <p class="cin-alert-text">
          <strong>{{ alertWorks.length }} 件作品库存告急</strong>，低于预警值请及时补货：
          <template v-for="(w, i) in alertWorks" :key="w.id">
            <a class="cin-alert-link" @click="quickStockIn(w)">{{ w.name }}</a><template v-if="i < alertWorks.length - 1">、</template>
          </template>
        </p>
      </div>
      <div v-else-if="saleCount" class="cin-alert cin-alert-ok">
        <span class="cin-alert-glyph">✓</span>
        <p class="cin-alert-text">在售作品库存均充足，暂无补货提醒。</p>
      </div>

      <!-- 库存统计区：全部作品、库存充足、库存告急、已缺货的数量 -->
      <div class="cin-stats">
        <div class="cin-stat">
          <span class="cin-stat-num">{{ works.length }}</span>
          <span class="cin-stat-label">全部作品</span>
        </div>
        <div class="cin-stat">
          <span class="cin-stat-num" style="color:#2e7d32">{{ stockCount('ok') }}</span>
          <span class="cin-stat-label">库存充足</span>
        </div>
        <div class="cin-stat">
          <span class="cin-stat-num" style="color:#b8860b">{{ stockCount('low') }}</span>
          <span class="cin-stat-label">库存告急</span>
        </div>
        <div class="cin-stat">
          <span class="cin-stat-num" style="color:#c62828">{{ stockCount('empty') }}</span>
          <span class="cin-stat-label">已缺货</span>
        </div>
      </div>

      <!-- 筛选区：按作品名 / 工艺搜索，可切换为仅看库存告急 -->
      <div class="cin-filter">
        <el-input v-model="keyword" placeholder="搜索作品名 / 工艺" clearable style="width: 240px" />
        <button class="cin-low-btn" :class="{ 'cin-low-btn-active': lowOnly }" @click="lowOnly = !lowOnly">
          仅看库存告急{{ lowOnly ? ' ×' : '' }}
        </button>
        <span class="cin-filter-total">共 {{ shown.length }} 件</span>
      </div>

      <!-- 作品库存列表：按加载中 / 有数据 / 空状态三种情况切换 -->
      <div v-if="loading" class="cin-loading">加载中…</div>
      <div v-else-if="shown.length" class="cin-list">
        <div v-for="w in shown" :key="w.id" class="cin-card">
          <!-- 作品封面；没有图片时用作品名首字作为占位 -->
          <div class="cin-cover">
            <img v-if="w.cover" :src="w.cover" class="cin-cover-img" alt="" />
            <span v-else class="cin-cover-glyph">{{ w.glyph || w.name.charAt(0) }}</span>
          </div>
          <div class="cin-body">
            <div class="cin-body-top">
              <h3 class="cin-name">{{ w.name }}</h3>
              <span class="cin-badge" :style="{ color: productStatusMap[w.status].color, borderColor: productStatusMap[w.status].color }">
                {{ productStatusMap[w.status].label }}
              </span>
            </div>
            <div class="cin-meta">
              <span class="cin-meta-item">{{ w.craft }}</span>
              <span class="cin-meta-item">{{ w.category }}</span>
              <span v-if="w.saleable" class="cin-meta-item">售价 ¥{{ w.price }}</span>
              <span v-else class="cin-meta-item">非卖品</span>
            </div>
            <div class="cin-stock">
              <span class="cin-stock-label">库存</span>
              <span class="cin-stock-num" :style="{ color: stockState(w).color }">{{ w.stock }}</span>
              <span class="cin-stock-state" :style="{ color: stockState(w).color }">{{ stockState(w).label }}</span>
              <span class="cin-stock-threshold">预警值 {{ w.alertThreshold ?? 5 }}</span>
              <button class="cin-threshold-btn" @click="openThreshold(w)">改预警值</button>
            </div>
            <!-- 库存操作按钮：入库、出库、损耗、查看台账 -->
            <div class="cin-actions">
              <button class="cin-btn cin-btn-pass" @click="openStock(w, 'in')">入库</button>
              <button class="cin-btn" @click="openStock(w, 'out')">出库</button>
              <button class="cin-btn" @click="openStock(w, 'loss')">损耗</button>
              <button class="cin-btn cin-btn-ghost" @click="openLedger(w)">台账</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="cin-empty">
        <span class="cin-empty-glyph">存</span>
        <p class="cin-empty-text">暂无相关作品</p>
      </div>
    </div>

    <!-- 入库 / 出库 / 损耗登记弹窗 -->
    <el-dialog v-model="stockDialog" :title="stockDialogTitle" width="480px" :close-on-click-modal="false">
      <p class="cin-dialog-tip">
        作品：<strong>{{ stockTarget?.name }}</strong>（当前库存 {{ stockTarget ? stockTarget.stock : 0 }}）
        <template v-if="stockType === 'in'">，入库后实时更新库存并记入台账</template>
      </p>
      <div class="cin-form">
        <div class="cin-form-row">
          <span class="cin-form-label">数量 *</span>
          <el-input-number v-model="stockQty" :min="1" :max="9999" style="width: 100%" />
        </div>
        <div class="cin-form-row">
          <span class="cin-form-label">说明</span>
          <el-input v-model="stockNote" :placeholder="stockType === 'in' ? '如：新品入库 / 补货' : stockType === 'loss' ? '如：破损报废 / 丢失' : '如：线下定制 / 领用'" />
        </div>
      </div>
      <template #footer>
        <el-button @click="stockDialog = false">取消</el-button>
        <el-button type="primary" :loading="stockBusy" @click="confirmStock">确认{{ stockType === 'in' ? '入库' : stockType === 'loss' ? '损耗' : '出库' }}</el-button>
      </template>
    </el-dialog>

    <!-- 库存预警值设置弹窗 -->
    <el-dialog v-model="thresholdDialog" title="设置库存预警值" width="420px" :close-on-click-modal="false">
      <p class="cin-dialog-tip">
        作品：<strong>{{ thresholdTarget?.name }}</strong>（当前库存 {{ thresholdTarget ? thresholdTarget.stock : 0 }}）
      </p>
      <div class="cin-form">
        <div class="cin-form-row">
          <span class="cin-form-label">预警值 *</span>
          <el-input-number v-model="thresholdValue" :min="0" :max="9999" style="width: 100%" />
        </div>
      </div>
      <p class="cin-dialog-note">
        库存 ≤ 预警值时，本页顶部、传承人工作台与管理员首页都会提示补货；
        0 表示只看缺货，不再提前提醒。
      </p>
      <template #footer>
        <el-button @click="thresholdDialog = false">取消</el-button>
        <el-button type="primary" :loading="thresholdBusy" @click="confirmThreshold">保存</el-button>
      </template>
    </el-dialog>

    <!-- 出入库台账弹窗：按时间列出该作品的每一次库存变动 -->
    <el-dialog v-model="ledgerDialog" :title="`出入库台账 · ${ledgerTarget?.name || ''}`" width="640px" :close-on-click-modal="false">
      <div v-if="ledgerLoading" class="cin-loading">加载中…</div>
      <div v-else-if="ledgerRows.length" class="cin-ledger">
        <div class="cin-ledger-row cin-ledger-head">
          <span class="cin-ledger-col cin-ledger-type">类型</span>
          <span class="cin-ledger-col">数量</span>
          <span class="cin-ledger-col cin-ledger-note">说明</span>
          <span class="cin-ledger-col">操作人</span>
          <span class="cin-ledger-col cin-ledger-time">时间</span>
        </div>
        <div v-for="r in ledgerRows" :key="r.id" class="cin-ledger-row">
          <span class="cin-ledger-col cin-ledger-type" :style="{ color: stockRecordTypeMap[r.type].color }">{{ stockRecordTypeMap[r.type].label }}</span>
          <span class="cin-ledger-col" :style="{ color: (r.type === 'in') ? '#2e7d32' : '#c62828' }">{{ r.type === 'in' ? '+' : '-' }}{{ r.qty }}</span>
          <span class="cin-ledger-col cin-ledger-note">{{ r.note || '—' }}</span>
          <span class="cin-ledger-col">{{ r.operator }}</span>
          <span class="cin-ledger-col cin-ledger-time">{{ r.time }}</span>
        </div>
      </div>
      <div v-else class="cin-empty cin-empty-sm">
        <span class="cin-empty-glyph">账</span>
        <p class="cin-empty-text">暂无出入库记录</p>
      </div>
    </el-dialog>
  </ConsoleLayout>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、消息提示、工作台布局、状态层数据与库存/产品接口
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import { heritageProducts, productStatusMap, productStockState, stockRecordTypeMap, loadProducts, stockInOut, updateProductAction, addLog, authState } from '@/store'
import { listStockRecords } from '@/api/products'
import { mapKeys } from '@/api/utils'

// works 直接指向全局作品列表，库存变动后会同步反映到本页
const works = heritageProducts

// 页面状态：是否加载中、搜索关键字、是否仅看库存告急
const loading = ref(false)
const keyword = ref('')
const lowOnly = ref(false)

/* 页面挂载时拉取作品数据；失败时提示网络问题，结束后关闭加载态 */
onMounted(async () => {
  loading.value = true
  try {
    await loadProducts()
  } catch (e) {
    ElMessage.error('加载库存失败，请检查网络')
  } finally {
    loading.value = false
  }
})

/* 返回库存状态（标签和颜色）：非卖品单独标注，其余交给全局库存状态函数 */
function stockState(w) {
  if (!w.saleable) return { label: '非卖', color: '#9e9e9e' }
  return productStockState(w)
}

/* 判断库存是否告急：非卖品不参与；库存 ≤ 预警值（默认 5）即告急 */
function isLow(w) {
  if (!w.saleable) return false
  const s = Number(w.stock ?? 0)
  return s <= Number(w.alertThreshold ?? 5)
}

/* 判断库存是否充足：非卖品不参与；库存 > 预警值即充足 */
function isOk(w) {
  if (!w.saleable) return false
  return Number(w.stock ?? 0) > Number(w.alertThreshold ?? 5)
}

/* 统计各库存等级的作品数：ok 充足、low 告急且仍有货、empty 已缺货 */
function stockCount(level) {
  if (level === 'ok') return works.filter(isOk).length
  if (level === 'low') return works.filter((w) => isLow(w) && Number(w.stock ?? 0) > 0).length
  return works.filter((w) => w.saleable && Number(w.stock ?? 0) <= 0).length
}

// 在售作品数，用于决定是否展示“库存均充足”的提示
const saleCount = computed(() => works.filter((w) => w.saleable).length)

// 所有库存告急的作品，驱动顶部提醒条
const alertWorks = computed(() => works.filter(isLow))

/* 列表筛选：关键字匹配作品名或工艺名，lowOnly 为真时只保留库存告急作品 */
const shown = computed(() => {
  let list = works
  const kw = keyword.value.trim().toLowerCase()
  if (kw) {
    list = list.filter((w) => (w.name || '').toLowerCase().includes(kw) || (w.craft || '').toLowerCase().includes(kw))
  }
  if (lowOnly.value) list = list.filter(isLow)
  return list
})

// 出入库弹窗状态：是否显示、提交中、操作类型（in/out/loss）、数量、说明和目标作品
const stockDialog = ref(false)
const stockBusy = ref(false)
const stockType = ref('in')
const stockQty = ref(1)
const stockNote = ref('')
let stockTarget = null

// 根据操作类型动态生成弹窗标题
const stockDialogTitle = computed(() =>
  stockType.value === 'in' ? '入库（补货）' : stockType.value === 'loss' ? '报损耗' : '出库'
)

// 点击预警作品名时，快捷打开“入库”弹窗
function quickStockIn(w) {
  openStock(w, 'in')
}

/* 打开出入库弹窗：记录目标作品，并重置数量、说明等表单值 */
function openStock(w, type) {
  stockTarget = w
  stockType.value = type
  stockQty.value = 1
  stockNote.value = ''
  stockDialog.value = true
}

/* 当前操作人名称，用于写操作日志和台账的操作人字段 */
function operator() {
  return authState.user?.name || '传承人'
}

/* 提交库存变更：校验数量 → 调用 stockInOut → 成功后写日志并关闭弹窗 */
async function confirmStock() {
  if (!stockTarget) return
  const qty = Number(stockQty.value)
  if (!Number.isFinite(qty) || qty < 1) {
    ElMessage.warning('数量必须大于 0')
    return
  }
  stockBusy.value = true
  try {
    const res = await stockInOut(stockTarget, stockType.value, qty, stockNote.value.trim(), operator())
    if (!res.ok) {
      ElMessage.error(res.msg)
      return
    }
    const label = stockType.value === 'in' ? '入库' : stockType.value === 'loss' ? '损耗' : '出库'
    addLog(stockType.value === 'in' ? 'create' : 'update', operator(), `作品${label}`, `「${stockTarget.name}」${label} ${qty} 件`)
    ElMessage.success(`${label}成功`)
    stockDialog.value = false
    stockTarget = null
  } catch (e) {
    ElMessage.error((e && e.message) || '操作失败')
  } finally {
    stockBusy.value = false
  }
}

// 预警值弹窗状态：是否显示、保存中、预警值和目标作品
const thresholdDialog = ref(false)
const thresholdBusy = ref(false)
const thresholdValue = ref(5)
const thresholdTarget = ref(null)

/* 打开预警值弹窗，并回填当前作品的预警值（默认 5） */
function openThreshold(w) {
  thresholdTarget.value = w
  thresholdValue.value = Number(w.alertThreshold ?? 5)
  thresholdDialog.value = true
}

/* 保存预警值：校验非负后调用更新接口，并写操作日志 */
async function confirmThreshold() {
  const target = thresholdTarget.value
  if (!target) return
  const val = Number(thresholdValue.value)
  if (!Number.isFinite(val) || val < 0) {
    ElMessage.warning('预警值不能小于 0')
    return
  }
  thresholdBusy.value = true
  try {
    await updateProductAction(target.id, { alertThreshold: val })
    addLog('update', operator(), '修改库存预警值', `「${target.name}」预警值改为 ${val} 件`)
    ElMessage.success(`「${target.name}」预警值已设为 ${val} 件`)
    thresholdDialog.value = false
    thresholdTarget.value = null
  } catch (e) {
    ElMessage.error((e && e.message) || '保存失败')
  } finally {
    thresholdBusy.value = false
  }
}

// 台账弹窗状态：是否显示、加载中、记录列表和目标作品
const ledgerDialog = ref(false)
const ledgerLoading = ref(false)
const ledgerRows = ref([])
const ledgerTarget = ref(null)

/* 打开台账弹窗并按作品 ID 拉取出入库记录，统一字段后渲染表格 */
async function openLedger(w) {
  ledgerTarget.value = w
  ledgerDialog.value = true
  ledgerLoading.value = true
  ledgerRows.value = []
  try {
    // 接口可能返回数组或分页对象，这里兼容两种结构
    const data = await listStockRecords({ product_id: w.id })
    const arr = Array.isArray(data) ? data : data.results || []
    // mapKeys 把后端下划线命名字段转成前端驼峰字段，便于模板直接读取
    ledgerRows.value = arr.map((r) => {
      const m = mapKeys(r)
      return {
        id: m.id,
        type: m.type || 'in',
        qty: m.qty ?? 0,
        note: m.note || '',
        operator: m.operator || '',
        time: m.time || m.createdAt || '',
      }
    })
  } catch (e) {
    ElMessage.error('加载台账失败')
  } finally {
    ledgerLoading.value = false
  }
}
</script>

<style src="./ConsoleInventory.css"></style>
