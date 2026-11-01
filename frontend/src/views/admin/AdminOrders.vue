<!-- 管理员订单管理页面：处理商品订单的审核/发货/完成/取消与状态流转，并处理学员材料包发货和签收。 -->
<template>
  <AdminLayout>
    <div class="aor-wrap">
      <div class="aor-head">
        <div class="aor-head-left">
          <h2 class="aor-title">订单管理</h2>
          <p class="aor-sub">处理商品订单与学员材料包发货</p>
        </div>
        <div class="aor-head-right">
          <button class="aor-add-btn" @click="openManual">＋ 手动录入订单</button>
        </div>
      </div>

      <!-- 主选项卡区：在“商品订单”和“材料发货”两个业务视图之间切换 -->
      <div class="aor-main-tabs">
        <button
          v-for="t in mainTabs"
          :key="t.value"
          class="aor-main-tab"
          :class="{ 'aor-main-tab-active': mainTab === t.value }"
          @click="mainTab = t.value"
        >
          {{ t.label }}<span class="aor-main-tab-count">{{ t.count }}</span>
        </button>
      </div>

      <!-- 商品订单视图 -->
      <div v-if="mainTab === 'orders'">
        <!-- 筛选区：关键字搜索 + 订单状态选项卡，切换状态后重新加载第一页 -->
        <div class="aor-filter">
          <el-input v-model="orderKeyword" placeholder="搜索订单号 / 客户 / 商品名" clearable style="width: 240px" />
          <div class="aor-status-tabs">
            <button
              v-for="t in orderTabs"
              :key="t.value"
              class="aor-tab"
              :class="{ 'aor-tab-active': orderTab === t.value }"
              @click="switchOrderTab(t.value)"
            >
              {{ t.label }}<span class="aor-tab-count">{{ orderCountOf(t.value) }}</span>
            </button>
          </div>
        </div>

        <!-- 订单列表区：卡片展示订单信息，并按当前状态给出审核/发货/完成/取消等操作 -->
        <div v-if="loading" class="aor-loading">加载中…</div>
        <div v-else-if="rows.length" class="aor-list">
          <div v-for="o in rows" :key="o.id" class="aor-card">
            <div class="aor-card-glyph">{{ o.glyph || o.itemName.charAt(0) }}</div>
            <div class="aor-card-body">
              <div class="aor-card-top">
                <h3 class="aor-card-name">{{ o.itemName }}</h3>
                <span class="aor-badge" :style="{ color: orderStatusMap[o.status].color, borderColor: orderStatusMap[o.status].color }">
                  {{ statusLabelOf(o) }}
                </span>
              </div>
              <div class="aor-card-meta">
                <span class="aor-card-meta-item">订单号 {{ o.orderNo }}</span>
                <span class="aor-card-meta-item">买家 {{ o.buyer }}（{{ o.buyerPhone }}）</span>
                <span class="aor-card-meta-item">¥{{ o.price }}</span>
                <span class="aor-card-meta-item">{{ o.type === 'course' ? '课程' : '作品' }}</span>
                <span v-if="o.source === 'manual'" class="aor-src-chip">手工单</span>
                <span v-if="o.payTime" class="aor-card-meta-item">支付 {{ o.payTime }}</span>
              </div>
              <div v-if="o.type === 'product'" class="aor-card-addr">
                <span class="aor-card-addr-label">收货：</span>{{ o.receiver }} · {{ o.address }} · {{ o.phone }}
              </div>
              <div v-if="o.reviewComment && o.status === 'rejected'" class="aor-card-remark aor-remark-reject">驳回原因：{{ o.reviewComment }}</div>
              <div v-if="o.remark" class="aor-card-remark">备注：{{ o.remark }}</div>

              <div v-if="o.status === 'shipped' || o.status === 'done'" class="aor-logistics">
                <span class="aor-logistics-item">{{ o.company || '未填物流' }}</span>
                <span v-if="o.trackingNo" class="aor-logistics-item">单号 {{ o.trackingNo }}</span>
              </div>

              <div class="aor-actions">
                <template v-if="o.status === 'review'">
                  <button class="aor-btn aor-btn-pass" @click="approveOrder(o)">通过审核</button>
                  <button class="aor-btn aor-btn-danger" @click="rejectOrder(o)">驳回订单</button>
                </template>
                <template v-else-if="o.status === 'paid'">
                  <template v-if="o.type === 'product'">
                    <button class="aor-btn aor-btn-pass" @click="openShip(o)">发货</button>
                  </template>
                  <span v-else class="aor-done">已支付 · 待上课</span>
                  <button class="aor-btn aor-btn-danger" @click="cancelOrder(o)">取消订单</button>
                </template>
                <template v-else-if="o.status === 'shipped'">
                  <button class="aor-btn" @click="markDone(o)">标记完成</button>
                </template>
                <template v-else-if="o.status === 'pending'">
                  <span class="aor-done">待买家付款</span>
                  <button class="aor-btn aor-btn-danger" @click="cancelOrder(o)">取消订单</button>
                </template>
                <template v-else>
                  <span class="aor-done">{{ statusLabelOf(o) || '已完成' }}</span>
                </template>
                <button class="aor-btn aor-btn-ghost" @click="openStatus(o)">变更状态</button>
                <button class="aor-btn aor-btn-ghost" @click="openFlow(o)">流转记录</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="aor-empty">
          <span class="aor-empty-glyph">单</span>
          <p class="aor-empty-text">暂无相关订单</p>
        </div>

        <!-- 分页区：订单总数超过一页时显示 -->
        <div v-if="total > pageSize" class="aor-pager">
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

      <!-- 材料发货视图：上方为待寄材料包，下方为历史邮寄记录 -->
      <div v-else>
        <!-- 待寄材料包：由已录取学员及其课程材料配置推导而来 -->
        <div v-if="derivedShipments.length" class="aor-list">
          <div v-for="s in derivedShipments" :key="s.studentId" class="aor-card">
            <div class="aor-card-glyph">{{ s.studentName.charAt(0) }}</div>
            <div class="aor-card-body">
              <div class="aor-card-top">
                <h3 class="aor-card-name">{{ s.studentName }}</h3>
                <span class="aor-badge" :style="{ color: '#b8860b', borderColor: '#b8860b' }">待寄</span>
              </div>
              <div class="aor-card-meta">
                <span class="aor-card-meta-item">{{ s.courseName }}</span>
              </div>
              <div class="aor-card-items">
                <span class="aor-card-items-label">传承人配置：</span>
                <span v-for="(it, j) in s.items" :key="j" class="aor-item-tag">
                  {{ it.materialName }} ×{{ it.qty }}
                  <span class="aor-item-stock">(库存 {{ stockOf(it.materialId) }})</span>
                </span>
              </div>
              <div class="aor-actions">
                <button class="aor-btn aor-btn-pass" @click="shipMaterials(s)">发货（扣库存）</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="aor-empty">
          <span class="aor-empty-glyph">寄</span>
          <p class="aor-empty-text">暂无待寄材料包（传承人尚未配置或已全部寄出）</p>
        </div>

        <!-- 邮寄记录区：展示已创建的材料包发货单，可标记签收 -->
        <div v-if="shipments.length" class="aor-records">
          <h3 class="aor-records-title">邮寄记录</h3>
          <div v-for="s in shipments" :key="s.id" class="aor-record-card">
            <div class="aor-card-top">
              <h4 class="aor-card-name">{{ s.studentName }} · {{ s.courseName }}</h4>
              <span class="aor-badge" :style="{ color: shipmentStatusMap[s.status].color, borderColor: shipmentStatusMap[s.status].color }">
                {{ shipmentStatusMap[s.status].label }}
              </span>
            </div>
            <div class="aor-card-items">
              <span class="aor-card-items-label">寄出材料：</span>
              <span v-for="(it, j) in s.items" :key="j" class="aor-item-tag">{{ it.materialName }} ×{{ it.qty }}</span>
            </div>
            <div class="aor-logistics">
              <span v-if="s.company" class="aor-logistics-item">{{ s.company }}</span>
              <span v-if="s.trackingNo" class="aor-logistics-item">单号 {{ s.trackingNo }}</span>
              <span v-if="s.shipTime" class="aor-logistics-item">{{ s.shipTime }}</span>
            </div>
            <div v-if="s.status === 'shipped'" class="aor-actions">
              <button class="aor-btn" @click="markSigned(s)">标记已签收</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗区：手动录入线下/电话订单，录入后进入待审核 -->
    <el-dialog v-model="manualDialog" title="手动录入订单" width="640px" :close-on-click-modal="false" @open="openManual">
      <p class="aor-dialog-tip">线下/电话订单先录为「待审核」，审核通过后计入待发货；选择订购作品时金额以系统售价为准。</p>
      <div class="aor-form">
        <div class="aor-form-row">
          <span class="aor-form-label">录入方式</span>
          <el-select v-model="mf.mode" style="width: 100%">
            <el-option label="从在售作品中选择" value="product-pick" />
            <el-option label="自定义商品 / 课程" value="free" />
          </el-select>
        </div>

        <template v-if="mf.mode === 'product-pick'">
          <div class="aor-form-row">
            <span class="aor-form-label">作品</span>
            <el-select v-model="mf.productId" filterable placeholder="搜索并选择文创作品" style="width: 100%">
              <el-option v-for="p in productOptions" :key="p.id" :label="`${p.name}（¥${p.price} · 库存 ${p.stock}）`" :value="p.id" />
            </el-select>
          </div>
          <div class="aor-form-row">
            <span class="aor-form-label">数量</span>
            <el-input-number v-model="mf.qty" :min="1" :max="999" />
          </div>
        </template>
        <template v-else>
          <div class="aor-form-row">
            <span class="aor-form-label">商品类型</span>
            <el-select v-model="mf.type" style="width: 100%">
              <el-option label="文创作品" value="product" />
              <el-option label="课程" value="course" />
            </el-select>
          </div>
          <div class="aor-form-row">
            <span class="aor-form-label">商品名称</span>
            <el-input v-model="mf.itemName" placeholder="请输入商品名称" />
          </div>
          <div class="aor-form-row">
            <span class="aor-form-label">金额 / 数量</span>
            <el-input-number v-model="mf.price" :min="0" :precision="2" style="width: 160px" />
            <el-input-number v-model="mf.qty" :min="1" :max="999" />
          </div>
        </template>

        <div class="aor-form-row">
          <span class="aor-form-label">买家</span>
          <el-input v-model="mf.buyer" placeholder="买家姓名（选填）" style="width: 220px" />
          <el-input v-model="mf.buyerPhone" placeholder="联系电话" style="width: 200px" />
        </div>
        <div class="aor-form-row">
          <span class="aor-form-label">收货信息</span>
          <el-input v-model="mf.receiver" placeholder="收货人（选填）" style="width: 180px" />
          <el-input v-model="mf.phone" placeholder="收货电话" style="width: 180px" />
        </div>
        <div class="aor-form-row">
          <span class="aor-form-label">收货地址</span>
          <el-input v-model="mf.address" placeholder="省市区 + 详细地址（选填）" />
        </div>
        <div class="aor-form-row">
          <span class="aor-form-label">备注</span>
          <el-input v-model="mf.remark" placeholder="备注信息（选填）" />
        </div>
      </div>
      <template #footer>
        <el-button @click="manualDialog = false">取消</el-button>
        <el-button type="primary" :loading="manualBusy" @click="confirmManual">确认录入</el-button>
      </template>
    </el-dialog>

    <!-- 发货弹窗区：商品订单填写物流公司与运单号 -->
    <el-dialog v-model="shipDialog" title="发货" width="520px" :close-on-click-modal="false">
      <p class="aor-dialog-tip">请选择物流公司并填写运单号（学员端「我的订单」会展示，故均必填）：</p>
      <div class="aor-form">
        <label class="aor-form-row">
          <span class="aor-form-label">物流公司</span>
          <el-select v-model="shipForm.company" placeholder="请选择物流公司" style="width: 100%">
            <el-option v-for="c in logisticsCompanies" :key="c" :label="c" :value="c" />
          </el-select>
        </label>
        <label class="aor-form-row">
          <span class="aor-form-label">物流单号</span>
          <el-input v-model="shipForm.trackingNo" placeholder="请输入物流单号" />
        </label>
      </div>
      <template #footer>
        <el-button @click="shipDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmShip">确认发货</el-button>
      </template>
    </el-dialog>

    <!-- 材料包发货弹窗区：确认后扣减对应物料库存 -->
    <el-dialog v-model="materialShipDialog" title="材料包发货" width="520px" :close-on-click-modal="false">
      <p v-if="materialShipTarget" class="aor-dialog-tip">
        为学员「{{ materialShipTarget.studentName }}」寄出材料包（{{ materialShipTarget.courseName }}），
        确认后扣减对应物料库存：
      </p>
      <div class="aor-form">
        <label class="aor-form-row">
          <span class="aor-form-label">快递公司</span>
          <el-select v-model="materialShipForm.company" placeholder="请选择快递公司" style="width: 100%">
            <el-option v-for="c in logisticsCompanies" :key="c" :label="c" :value="c" />
          </el-select>
        </label>
        <label class="aor-form-row">
          <span class="aor-form-label">快递单号</span>
          <el-input v-model="materialShipForm.trackingNo" placeholder="请输入快递单号" />
        </label>
      </div>
      <template #footer>
        <el-button @click="materialShipDialog = false">取消</el-button>
        <el-button type="primary" :loading="materialShipBusy" @click="confirmShipMaterials">确认发货</el-button>
      </template>
    </el-dialog>

    <!-- 状态变更弹窗区：手动纠偏订单状态，作品订单会同步扣减/退回库存 -->
    <el-dialog v-model="statusDialog" title="变更订单状态" width="460px" :close-on-click-modal="false">
      <p v-if="statusTarget" class="aor-dialog-tip">
        订单 {{ statusTarget.orderNo }}「{{ statusTarget.itemName }}」当前状态：{{ statusLabelOf(statusTarget) }}
      </p>
      <div class="aor-form">
        <div class="aor-form-row">
          <span class="aor-form-label">目标状态</span>
          <el-select v-model="statusForm.status" placeholder="请选择目标状态" style="width: 100%">
            <el-option
              v-for="(v, k) in orderStatusMap"
              :key="k"
              :label="v.label"
              :value="k"
              :disabled="statusTarget && statusTarget.status === k"
            />
          </el-select>
        </div>
        <div class="aor-form-row">
          <span class="aor-form-label">变更备注</span>
          <el-input v-model="statusForm.note" placeholder="如：线下补单、异常单纠偏（选填）" />
        </div>
      </div>
      <p class="aor-dialog-tip">作品订单在「待发货及之后」与「之前」状态之间切换时，会同步扣减/退回库存。</p>
      <template #footer>
        <el-button @click="statusDialog = false">取消</el-button>
        <el-button type="primary" :loading="statusBusy" @click="confirmStatus">确认变更</el-button>
      </template>
    </el-dialog>

    <!-- 流转记录抽屉区：用时间线展示订单每一次状态变更、操作人与备注 -->
    <el-drawer v-model="flowDrawer" title="订单状态流转" size="420px">
      <div v-if="flowTarget" class="aor-flow">
        <p class="aor-flow-head">
          <span class="aor-flow-no">{{ flowTarget.orderNo }}</span>
          <span class="aor-flow-name">{{ flowTarget.itemName }}</span>
        </p>
        <el-timeline v-if="flowTarget.statusLogs.length">
          <el-timeline-item
            v-for="(l, i) in flowTarget.statusLogs"
            :key="i"
            :timestamp="l.time"
            placement="top"
            :color="statusColor(l.toStatus)"
          >
            <p class="aor-flow-title">{{ l.fromStatusLabel || '新建' }} → {{ l.toStatusLabel }}</p>
            <p v-if="l.operator" class="aor-flow-sub">操作人：{{ l.operator }}</p>
            <p v-if="l.note" class="aor-flow-sub">{{ l.note }}</p>
          </el-timeline-item>
        </el-timeline>
        <p v-else class="aor-flow-empty">暂无流转记录</p>
      </div>
    </el-drawer>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listOrders, auditOrder, manualCreateOrder, setOrderStatus } from '@/api/orders'
import { listProducts } from '@/api/products'
import { mapKeys } from '@/api/utils'
import {
  heritageOrders,
  orderStatusMap,
  loadHeritageOrders,
  shipOrderAction,
  completeOrderAction,
  cancelOrderAction,
  derivedShipments,
  shipments,
  shipmentStatusMap,
  inventoryMaterials,
  checkStock,
  shipOut as doShipOut,
  createShipmentAction,
  signShipmentAction,
  loadMaterials,
  loadShipments,
  loadStudents,
  addLog,
  authState,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 首次进入页面：并行加载订单、物料、邮寄与学员缓存，同时加载分页订单列表
onMounted(() => {
  Promise.allSettled([loadHeritageOrders(), loadMaterials(), loadShipments(), loadStudents()])
  loadRows()
})

// 主选项卡：商品订单显示待审核数量，材料发货显示待寄材料包数量
const mainTabs = computed(() => [
  { label: '商品订单', value: 'orders', count: heritageOrders.filter((o) => o.status === 'review').length },
  { label: '材料发货', value: 'materials', count: derivedShipments.length },
])
const mainTab = ref('orders') // 当前主视图：orders 商品订单、materials 材料发货

// 商品订单状态选项卡，value 与后端 status 参数对应
const orderTabs = [
  { label: '待审核', value: 'review' },
  { label: '待发货', value: 'paid' },
  { label: '待付款', value: 'pending' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'done' },
  { label: '已驳回', value: 'rejected' },
  { label: '已取消', value: 'cancelled' },
  { label: '全部', value: 'all' },
]

// 物流公司下拉选项，商品与材料包发货时使用
const logisticsCompanies = [
  '顺丰速运',
  '京东物流',
  '邮政EMS',
  '中通快递',
  '圆通速递',
  '申通快递',
  '韵达快递',
  '极兔速递',
  '德邦快递',
]
const orderTab = ref('review') // 当前订单状态筛选，默认待审核
const orderKeyword = ref('') // 订单搜索关键字（订单号 / 客户 / 商品名）

// 订单状态文案：课程订单的 paid 显示为“已支付 · 待上课”，其余取状态映射表
function statusLabelOf(o) {
  if (o.type === 'course' && o.status === 'paid') return '已支付 · 待上课'
  return (orderStatusMap[o.status] && orderStatusMap[o.status].label) || o.status
}

// 统计某个状态下的订单数量，供状态选项卡角标使用
function orderCountOf(v) {
  if (v === 'all') return heritageOrders.length
  return heritageOrders.filter((o) => o.status === v).length
}


// 规范化订单数据：补齐价格、订单号、流转记录、物流等字段的默认值
function mapOrderRow(o) {
  const m = mapKeys(o)
  return {
    ...m,
    price: Number(m.price ?? 0),
    orderNo: m.orderNo || ('QQ' + String(m.id ?? 0).padStart(8, '0')),
    statusLogs: Array.isArray(m.statusLogs) ? m.statusLogs : [],
    itemName: m.itemName || '',
    name: m.itemName || '',
    buyerPhone: m.buyerPhone || '',
    payMethod: m.payMethod || '',
    orderTime: m.orderTime || '',
    payTime: m.payTime || '',
    company: m.company || '',
    trackingNo: m.trackingNo || '',
    shipTime: m.shipTime || '',
  }
}

/* 商品订单分页列表：usePagedList 统一管理分页状态，
   fetchPage 按关键字与状态请求订单，“全部”状态不传 status 参数。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapOrderRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: orderKeyword.value.trim() }
    if (orderTab.value !== 'all') params.status = orderTab.value
    return listOrders(params)
  },
})

// 切换订单状态选项卡，并重新加载第一页
function switchOrderTab(v) {
  orderTab.value = v
  onFilter()
}

// 状态变化时立即回到第一页重新查询
watch(orderTab, onFilter)
let orderKwTimer = null // 关键字防抖定时器
watch(orderKeyword, () => {
  clearTimeout(orderKwTimer)
  orderKwTimer = setTimeout(onFilter, 300) // 停止输入 300ms 后再查询
})

// 操作人名称：写入操作日志时使用，取不到登录用户时兜底为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 查询某个物料 id 的当前库存，用于待寄材料包上的库存提示
function stockOf(materialId) {
  const m = inventoryMaterials.find((x) => x.id === materialId)
  return m ? m.stock : 0
}

const shipDialog = ref(false) // 商品发货弹窗是否显示
const shipForm = reactive({ company: '', trackingNo: '' }) // 发货表单：物流公司与运单号
let shipTarget = null // 当前要发货的订单

// 打开发货弹窗并清空上一次的物流信息
function openShip(o) {
  shipTarget = o
  shipForm.company = ''
  shipForm.trackingNo = ''
  shipDialog.value = true
}

/* 确认商品发货：物流公司与单号必填，成功后写日志、关闭弹窗并刷新订单列表。 */
async function confirmShip() {
  if (!shipTarget) return
  if (!shipForm.company.trim()) {
    ElMessage.warning('请填写物流公司')
    return
  }
  if (!shipForm.trackingNo.trim()) {
    ElMessage.warning('请填写物流单号')
    return
  }
  try {
    await shipOrderAction(shipTarget.id, { company: shipForm.company.trim(), trackingNo: shipForm.trackingNo.trim() })
    addLog('ship', operator(), '商品发货', `订单 ${orderNo(shipTarget)}「${shipTarget.itemName}」已发货`)
    ElMessage.success('已发货')
    shipDialog.value = false
    shipTarget = null
    await loadRows()
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '发货失败')
  }
}

/* 标记订单完成：已发货订单在买家确认收货后由管理员标记完成。 */
function markDone(o) {
  ElMessageBox.confirm(`确定将「${o.itemName}」标记为已完成吗？`, '完成订单', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      await completeOrderAction(o.id)
      addLog('order', operator(), '订单完成', `订单 ${orderNo(o)}`)
      ElMessage.success('订单已完成')
      await loadRows()
    })
    .catch(() => {})
}

/* 取消订单：待付款或已付款订单均可取消，操作前二次确认。 */
function cancelOrder(o) {
  ElMessageBox.confirm(`确定取消订单「${o.itemName}」吗？`, '取消订单', {
    confirmButtonText: '取消订单',
    cancelButtonText: '再想想',
    type: 'warning',
  })
    .then(async () => {
      await cancelOrderAction(o.id)
      addLog('order', operator(), '取消订单', `订单 ${orderNo(o)}「${o.itemName}」已取消`)
      ElMessage.success('订单已取消')
      await loadRows()
    })
    .catch(() => {})
}

const statusDialog = ref(false) // 状态变更弹窗是否显示
const statusBusy = ref(false) // 提交中标记，防止重复点击
const statusTarget = ref(null) // 当前要变更状态的订单
const statusForm = reactive({ status: '', note: '' }) // 目标状态与变更备注

// 打开状态变更弹窗并清空表单
function openStatus(o) {
  statusTarget.value = o
  statusForm.status = ''
  statusForm.note = ''
  statusDialog.value = true
}

/* 手动变更订单状态：提交后先用返回值更新当前页对应行，再刷新分页列表与全局订单缓存；
   作品订单在“待发货及之后”与“之前”之间切换时，库存由后端同步扣减/退回。 */
async function confirmStatus() {
  if (!statusTarget.value) return
  if (!statusForm.status) {
    ElMessage.warning('请选择目标状态')
    return
  }
  statusBusy.value = true
  try {
    const updated = mapOrderRow(await setOrderStatus(statusTarget.value.id, {
      status: statusForm.status,
      note: statusForm.note.trim(),
    }))
    // 若当前页存在该订单，先就地替换，减少等待刷新时的视觉跳变
    const idx = rows.value.findIndex((x) => x.id === updated.id)
    if (idx >= 0) rows.value[idx] = updated
    addLog('order', operator(), '订单状态调整',
      `订单 ${updated.orderNo}「${updated.itemName}」已变更为「${statusLabelOf(updated)}」`)
    ElMessage.success('状态已变更')
    statusDialog.value = false
    await loadRows()
    await loadHeritageOrders()
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || (e && e.message) || '变更失败')
  } finally {
    statusBusy.value = false
  }
}

const flowDrawer = ref(false) // 流转记录抽屉是否显示
const flowTarget = ref(null) // 当前查看流转记录的订单

// 打开订单状态流转记录抽屉
function openFlow(o) {
  flowTarget.value = o
  flowDrawer.value = true
}

// 根据目标状态取时间线节点颜色
function statusColor(s) {
  return (orderStatusMap[s] && orderStatusMap[s].color) || '#8a93a3'
}

// 订单号展示：优先用后端订单号，缺失时用 id 补零生成
function orderNo(o) {
  return o.orderNo || ('#' + String(o.id).padStart(4, '0'))
}

/* 审核通过：作品订单通过后会扣减库存，课程订单通过后进入待上课；
   成功后刷新分页列表与全局订单缓存。 */
function approveOrder(o) {
  const stockWarn = o.type === 'product' ? '作品订单通过后将从库存扣减对应数量。' : ''
  ElMessageBox.confirm(`审核通过订单 ${orderNo(o)}「${o.itemName}」吗？${stockWarn}`, '通过审核', {
    confirmButtonText: '确认通过',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      try {
        await auditOrder(o.id, { action: 'approve' })
        addLog('review', operator(), '订单审核通过', `订单 ${orderNo(o)}「${o.itemName}」已通过，进入待发货`)
        ElMessage.success('已通过审核，订单进入待发货')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '操作失败')
      }
      await loadRows()
      await loadHeritageOrders()
    })
    .catch(() => {})
}

/* 驳回订单：弹窗填写原因（可留空使用默认提示），提交后反馈给买家。 */
function rejectOrder(o) {
  ElMessageBox.prompt('请填写驳回原因（将反馈给买家），或留空使用默认提示', '驳回订单', {
    confirmButtonText: '确认驳回',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '例如：订单信息有误，请核对后重新下单',
    type: 'warning',
  })
    .then(async ({ value }) => {
      try {
        await auditOrder(o.id, { action: 'reject', review_comment: (value || '').trim() })
        addLog('review', operator(), '订单驳回', `订单 ${orderNo(o)}「${o.itemName}」被驳回`)
        ElMessage.success('已驳回该订单')
      } catch (e) {
        ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '操作失败')
      }
      await loadRows()
      await loadHeritageOrders()
    })
    .catch(() => {})
}

const manualDialog = ref(false) // 手动录入弹窗是否显示
const manualBusy = ref(false) // 提交中标记，防止重复录入
const productOptions = ref([]) // 在售作品下拉选项，首次打开弹窗时加载
// 手动录入表单：可从在售作品中选择，也可自定义商品 / 课程
const mf = reactive({
  mode: 'product-pick',
  type: 'product',
  productId: null,
  itemName: '',
  price: 0,
  qty: 1,
  buyer: '',
  buyerPhone: '',
  receiver: '',
  phone: '',
  address: '',
  remark: '',
})

/* 打入手动录入弹窗：重置表单；首次打开时加载在售作品，
   只保留已审核通过且可售的作品作为下拉选项。 */
async function openManual() {
  Object.assign(mf, {
    mode: 'product-pick', type: 'product', productId: null, itemName: '', price: 0,
    qty: 1, buyer: '', buyerPhone: '', receiver: '', phone: '', address: '', remark: '',
  })
  if (!productOptions.value.length) {
    try {
      const list = await listProducts({ page_size: 200 })
      const arr = Array.isArray(list) ? list : list.results || []
      productOptions.value = arr
        .map(mapKeys)
        .filter((p) => p.status === 'approved' && p.saleable)
        .map((p) => ({ id: p.id, name: p.name, price: Number(p.price || 0), stock: Number(p.stock || 0) }))
    } catch (e) {
      productOptions.value = []
    }
  }
}

/* 提交手动录入：两种录入方式分别校验，成功后进入待审核并刷新列表与订单缓存。 */
async function confirmManual() {
  if (mf.mode === 'product-pick') {
    if (!mf.productId) {
      ElMessage.warning('请选择订购作品')
      return
    }
  } else if (!mf.itemName.trim()) {
    ElMessage.warning('请填写商品名称')
    return
  }
  const qty = Number(mf.qty)
  if (!Number.isFinite(qty) || qty < 1) {
    ElMessage.warning('数量至少为 1')
    return
  }
  const payload = {
    qty,
    buyer: mf.buyer.trim(),
    buyer_phone: mf.buyerPhone.trim(),
    receiver: mf.receiver.trim(),
    phone: mf.phone.trim(),
    address: mf.address.trim(),
    remark: mf.remark.trim(),
  }
  if (mf.mode === 'product-pick') {
    payload.product_id = mf.productId
  } else {
    payload.type = mf.type
    payload.item_name = mf.itemName.trim()
    payload.price = Number(mf.price) || 0
  }
  manualBusy.value = true
  try {
    const created = await manualCreateOrder(payload)
    addLog('create', operator(), '手动录入订单', `录入订单 ${created.order_no || '#' + String(created.id).padStart(4, '0')}「${created.item_name || ''}」，待审核`)
    ElMessage.success('已录入，订单进入待审核')
    manualDialog.value = false
    await loadRows()
    await loadHeritageOrders()
  } catch (e) {
    ElMessage.error((e.data && (e.data.msg || e.data.detail)) || '录入失败')
  } finally {
    manualBusy.value = false
  }
}

const materialShipDialog = ref(false) // 材料包发货弹窗是否显示
const materialShipBusy = ref(false) // 提交中标记，防止重复发货
const materialShipForm = reactive({ company: '', trackingNo: '' }) // 快递公司与单号
let materialShipTarget = null // 当前要发货的材料包

/* 打开材料包发货弹窗之前先检查库存，库存不足时提示缺少的数量并终止。 */
function shipMaterials(s) {
  const shortage = checkStock(s)
  if (shortage.length) {
    const msg = shortage.map((x) => `${x.materialName}缺${x.need - x.have}`).join('、')
    ElMessageBox.alert(`库存不足，无法发货：${msg}`, '库存不足', { type: 'warning' })
    return
  }
  materialShipTarget = s
  materialShipForm.company = ''
  materialShipForm.trackingNo = ''
  materialShipDialog.value = true
}

/* 确认材料包发货：创建发货单并执行出库扣减库存，成功后刷新物料与邮寄记录。 */
async function confirmShipMaterials() {
  const s = materialShipTarget
  if (!s) return
  if (!materialShipForm.company.trim()) {
    ElMessage.warning('请选择快递公司')
    return
  }
  if (!materialShipForm.trackingNo.trim()) {
    ElMessage.warning('请填写快递单号')
    return
  }
  materialShipBusy.value = true
  try {
    const created = await createShipmentAction(s)
    const res = await doShipOut(
      created,
      materialShipForm.company.trim(),
      materialShipForm.trackingNo.trim(),
    )
    if (res.ok) {
      addLog('ship', operator(), '材料发货', `学员「${s.studentName}」材料包已寄出`)
      ElMessage.success('已发货，库存已扣减')
      materialShipDialog.value = false
      materialShipTarget = null
      loadMaterials().catch(() => {})
      loadShipments().catch(() => {})
    } else {
      ElMessage.error(res.msg || '发货失败，库存不足')
    }
  } catch (e) {
    ElMessage.error((e && e.message) || '发货失败')
  } finally {
    materialShipBusy.value = false
  }
}

/* 标记材料包已签收：仅已发货的邮寄记录可操作。 */
function markSigned(s) {
  ElMessageBox.confirm('确认学员已签收材料包吗？', '标记签收', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'success',
  })
    .then(async () => {
      try {
        await signShipmentAction(s.id)
        ElMessage.success('已标记签收')
      } catch (e) {
        ElMessage.error((e && e.message) || '操作失败')
      }
    })
    .catch(() => {})
}
</script>


<style src="./AdminOrders.css"></style>

<style scoped>
/* 加载提示与分页条的基础布局 */
.aor-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
.aor-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
.aor-btn-ghost {
  background: transparent;
  border-color: #e0d7c6;
  color: #8a7a63;
}
/* 流转抽屉头部：订单号与商品名纵向排列，并用底部分隔线区分时间线 */
.aor-flow-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0 0 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid #efe7d8;
}
.aor-flow-no {
  font-size: 13px;
  letter-spacing: 1px;
  color: #8a7a63;
}
.aor-flow-name {
  font-size: 15px;
  font-weight: 600;
  color: #2b2b2b;
}
.aor-flow-title {
  margin: 0;
  font-size: 13px;
  color: #2b2b2b;
}
.aor-flow-sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #8a93a3;
}
.aor-flow-empty {
  font-size: 13px;
  color: #8a93a3;
}
</style>
