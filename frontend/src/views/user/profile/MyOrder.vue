<!-- 个人中心 · 我的订单页：按状态和关键字筛选订单，支持支付、取消、确认收货和查看流转记录 -->
<template>
  <div class="order-page">
    <Nav />

    <!-- 页面主体：左侧个人中心侧边栏 + 右侧订单列表 -->
    <div class="mo-wrap">
      <ProfileAside />

      <div class="mo-main">
        <header class="mo-head">
          <h1 class="mo-title">我的订单</h1>
          <span class="mo-en">MY ORDERS</span>
        </header>

        <!-- 工具栏：状态筛选标签、订单搜索框和数量统计 -->
        <div class="mo-toolbar">
          <div class="mo-tabs">
            <button
              v-for="s in statusLabels"
              :key="s.key"
              class="mo-tab"
              :class="{ 'mo-tab-active': status === s.key }"
              @click="status = s.key"
            >
              {{ s.label }}
            </button>
          </div>
          <div class="mo-toolbar-right">
            <input v-model="keyword" class="mo-search" type="text" placeholder="搜订单编号 / 商品名称" />
            <span class="mo-count">共 {{ filtered.length }} 笔</span>
          </div>
        </div>

        <!-- 订单卡片列表 -->
        <div class="mo-list" v-if="filtered.length">
          <div
            v-for="o in filtered"
            :key="o.id"
            class="mo-card"
          >
            <div class="mo-cover" :style="coverStyle(o)" @click="goDetail(o)">
              <span class="mo-glyph">{{ o.glyph || '单' }}</span>
            </div>
            <div class="mo-body">
              <div class="mo-top">
                <h3 class="mo-name" @click="goDetail(o)">{{ o.name }}</h3>
                <span class="mo-status" :class="'mo-status-' + o.status">{{ statusText(o) }}</span>
              </div>
              <p class="mo-maker">
                订单编号 <span class="mo-no">{{ o.orderNo }}</span>
                <span class="mo-sep">·</span>{{ typeText(o.type) }}
                <span class="mo-sep">·</span>{{ o.payMethod || '未支付' }}
              </p>
              <div v-if="o.type === 'product' && (o.receiver || o.address)" class="mo-addr">
                <span class="mo-addr-label">收货</span>{{ o.receiver || '' }}<template v-if="o.receiver && o.address"> · </template>{{ o.address || '' }}<template v-if="o.address && o.phone"> · </template>{{ o.phone || '' }}
              </div>
              <p v-if="o.company || o.trackingNo" class="mo-ship">
                <template v-if="o.company">物流：{{ o.company }}</template>
                <template v-if="o.trackingNo"><span v-if="o.company"> · </span>单号 {{ o.trackingNo }}</template>
                <span v-if="o.shipTime"> · {{ o.shipTime }} 发货</span>
              </p>

              <!-- 订单流转记录：展开后按时间显示状态变化 -->
              <div v-if="openFlowId === o.id" class="mo-flow">
                <div v-for="(l, i) in (o.statusLogs || [])" :key="i" class="mo-flow-item">
                  <span class="mo-flow-dot" :style="{ background: flowColor(l.toStatus) }"></span>
                  <div class="mo-flow-body">
                    <p class="mo-flow-title">{{ l.fromStatusLabel || '新建' }} → {{ l.toStatusLabel }}</p>
                    <p class="mo-flow-time">{{ l.time }}<template v-if="l.operator"> · {{ l.operator }}</template></p>
                    <p v-if="l.note" class="mo-flow-note">{{ l.note }}</p>
                  </div>
                </div>
                <p v-if="!(o.statusLogs || []).length" class="mo-flow-empty">暂无流转记录</p>
              </div>
              <!-- 订单底部：下单时间、金额和当前可执行的操作 -->
              <div class="mo-foot">
                <span class="mo-time">{{ o.orderTime }} 下单</span>
                <div class="mo-right">
                  <span class="mo-price"><em>¥</em>{{ o.price }}</span>
                  <button v-if="o.status === 'pending'" class="mo-act mo-act-solid" @click="openPay(o)">去支付</button>
                  <button v-if="canCancel(o)" class="mo-act mo-act-danger" @click="onCancel(o)">取消订单</button>
                  <button v-if="o.type === 'product' && o.status === 'shipped'" class="mo-act mo-act-solid" @click="onConfirm(o)">确认收货</button>
                  <span class="mo-btn" @click="goDetail(o)">查看详情</span>
                  <span class="mo-btn" @click="toggleFlow(o)">{{ openFlowId === o.id ? '收起流转' : '流转记录' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="mo-empty">
          <!-- 空状态：没有符合条件的订单时引导去商品列表 -->
          <p class="mo-empty-text">暂无相关订单</p>
          <button class="mo-btn mo-btn-solid" @click="goProducts">去逛逛</button>
        </div>
      </div>
    </div>

    <!-- 模拟收银台弹窗：选择支付方式并完成支付 -->
    <el-dialog v-model="payVisible" title="收银台 · 模拟支付" width="440px" :close-on-click-modal="false">
      <div v-if="payTarget" class="mo-cash">
        <p class="mo-cash-item">{{ payTarget.itemName }}<span class="mo-cash-type">{{ typeText(payTarget.type) }}</span></p>
        <p class="mo-cash-amount">应付金额 <em>¥</em>{{ payTarget.price }}</p>
      </div>
      <div class="mo-methods">
        <label v-for="m in methods" :key="m.key" class="mo-method" :class="{ 'mo-method-on': payMethod === m.name }">
          <input type="radio" :value="m.name" v-model="payMethod" />
          <span class="mo-method-icon">{{ m.icon }}</span>
          <span>{{ m.name }}</span>
        </label>
      </div>
      <p class="mo-cash-tip">本页面为演示，选择支付方式后点击「立即支付」即模拟支付成功</p>
      <template #footer>
        <el-button @click="payVisible = false">取消</el-button>
        <el-button type="primary" :loading="paying" @click="doPay">立即支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import ProfileAside from './ProfileAside.vue'
import { orderState, loadOrders, courses, ensureCourses, heritageProducts, loadProducts, payMyOrder, confirmMyOrder, cancelMyOrder } from '@/store'

const router = useRouter()

// 进入页面时并行加载订单、课程和商品数据；单项失败不影响其他数据
onMounted(() => {
  Promise.all([loadOrders().catch(() => {}), ensureCourses().catch(() => {}), loadProducts().catch(() => {})])
})

// 订单状态筛选配置：key 对应订单状态，all 表示全部
const statusLabels = [
  { key: 'all', label: '全部' },
  { key: 'review', label: '待审核' },
  { key: 'pending', label: '待付款' },
  { key: 'paid', label: '待发货' },
  { key: 'shipped', label: '已发货' },
  { key: 'done', label: '已完成' },
  { key: 'rejected', label: '已驳回' },
  { key: 'cancelled', label: '已取消' },
]

// 当前筛选状态，默认全部
const status = ref('all')

// 搜索关键字：匹配订单编号或商品/课程名称
const keyword = ref('')

// 先按状态过滤，再按关键字过滤订单编号/商品名称
const filtered = computed(() => {
  let list = status.value === 'all' ? orderState.list : orderState.list.filter((o) => o.status === status.value)
  const kw = keyword.value.trim()
  if (kw) {
    list = list.filter(
      (o) => (o.orderNo || '').includes(kw) || (o.itemName || '').includes(kw) || (o.name || '').includes(kw)
    )
  }
  return list
})

// 状态文案：课程已支付显示“待上课”，商品已支付显示“待发货”
function statusText(o) {
  const s = typeof o === 'string' ? o : o.status
  if (s === 'paid') {
    const isCourse = typeof o === 'string' ? false : o.type === 'course'
    return isCourse ? '已支付 · 待上课' : '待发货'
  }
  return {
    pending: '待付款',
    review: '待审核',
    rejected: '已驳回',
    shipped: '已发货',
    done: '已完成',
    cancelled: '已取消',
  }[s] || s
}

// 订单类型文案
function typeText(t) {
  return t === 'course' ? '培训课程' : '文创作品'
}


// 当前展开流转记录的订单 ID：再次点击同一订单则收起
const openFlowId = ref(null)
function toggleFlow(o) {
  openFlowId.value = openFlowId.value === o.id ? null : o.id
}
// 不同订单状态对应的流转节点颜色
function flowColor(s) {
  return {
    review: '#e6a23c',
    pending: '#b8860b',
    paid: '#1e6fb8',
    shipped: '#2e7d32',
    done: '#9e9e9e',
    cancelled: '#9e9e9e',
    rejected: '#c0392b',
  }[s] || '#8a93a3'
}

// 有封面图时生成背景图样式，否则使用默认占位样式
function coverStyle(o) {
  if (o.cover) return { backgroundImage: 'url(' + o.cover + ')' }
  return {}
}

// 查看详情：课程跳课程详情，商品跳商品详情；按名称找不到对应 ID 时回到列表页
function goDetail(o) {
  if (o.type === 'course') {
    const c = courses.find((x) => x.name === o.itemName)
    if (c) router.push('/course/' + c.id)
    else router.push('/course')
  } else {
    const p = heritageProducts.find((x) => x.name === o.itemName)
    if (p) router.push('/product/' + p.id)
    else router.push('/product')
  }
}
// 空状态按钮：跳转到商品列表
function goProducts() {
  router.push('/product')
}

// 支付方式配置：key 为内部标识，icon 为字形图标，name 为展示文案
const methods = [
  { key: 'wechat', icon: '微', name: '微信支付' },
  { key: 'alipay', icon: '支', name: '支付宝' },
  { key: 'bank', icon: '银', name: '银行卡' },
]
// 收银台弹窗状态：是否显示、是否支付中、待支付订单和选择的支付方式
const payVisible = ref(false)
const paying = ref(false)
const payTarget = ref(null)
const payMethod = ref('微信支付')

// 打开收银台：记录待支付订单并回显该订单已选的支付方式
function openPay(o) {
  payTarget.value = o
  payMethod.value = o.payMethod || '微信支付'
  payVisible.value = true
}

// 可取消的订单：待付款、待审核，以及已支付但尚未发货的商品订单
function canCancel(o) {
  return o.status === 'pending' || o.status === 'review' || (o.status === 'paid' && o.type === 'product')
}

// 模拟支付：调用 store 的支付方法，成功后关闭弹窗并按订单类型提示
async function doPay() {
  if (!payTarget.value) return
  const isCourse = payTarget.value.type === 'course'
  paying.value = true
  try {
    await payMyOrder(payTarget.value.id, payMethod.value)
    payVisible.value = false
    payTarget.value = null
    ElMessage.success(isCourse ? '支付成功' : '支付成功，订单进入待发货')
  } catch (e) {
    const msg = (e && e.data && (e.data.msg || e.data.detail)) || (e && e.message) || '支付失败，请重试'
    ElMessage.error(msg)
  } finally {
    paying.value = false
  }
}

// 取消订单：二次确认后调用取消接口；已支付商品会提示退款和库存返还
function onCancel(o) {
  ElMessageBox.confirm(
    `确定取消订单「${o.itemName || o.name}」吗？${o.status === 'paid' ? '已支付款项将退回，系统自动返还已扣库存。' : ''}`,
    '取消订单',
    { confirmButtonText: '取消订单', cancelButtonText: '再想想', type: 'warning' },
  )
    .then(async () => {
      try {
        await cancelMyOrder(o.id)
        ElMessage.success('订单已取消')
      } catch (e) {
        ElMessage.error((e && e.data && (e.data.msg || e.data.detail)) || (e && e.message) || '取消失败')
      }
    })
    .catch(() => {})
}

// 确认收货：二次确认后调用确认接口，订单随即完成
function onConfirm(o) {
  ElMessageBox.confirm('确认已收到商品了吗？确认后订单完成。', '确认收货', {
    confirmButtonText: '确认收货',
    cancelButtonText: '再等等',
    type: 'success',
  })
    .then(async () => {
      try {
        await confirmMyOrder(o.id)
        ElMessage.success('已确认收货，订单完成')
      } catch (e) {
        ElMessage.error((e && e.data && (e.data.msg || e.data.detail)) || (e && e.message) || '操作失败')
      }
    })
    .catch(() => {})
}
</script>

<style src="./MyOrder.css"></style>

<style>
/* 订单操作按钮：胶囊样式，区分普通、主要和危险操作 */
.mo-act {
  border: 1px solid #dfd0b8;
  background: #fff;
  color: #6b4a2b;
  border-radius: 999px;
  padding: 3px 12px;
  font-size: 12px;
  cursor: pointer;
  margin-left: 8px;
  line-height: 18px;
}
.mo-act:hover { border-color: #6b4a2b; }
.mo-act-solid { background: #6b4a2b; color: #fff; border-color: #6b4a2b; }
.mo-act-danger { color: #c0392b; border-color: #e2b4ab; }
.mo-act-danger:hover { border-color: #c0392b; }
/* 订单搜索框：圆角输入框，聚焦时高亮边框 */
.mo-search {
  border: 1px solid #e0d3bd;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  color: #5a4632;
  background: #fff;
  outline: none;
  width: 180px;
}
.mo-search:focus { border-color: #c9a86a; }
/* 订单流转记录面板：浅色背景、圆角和细边框 */
.mo-flow {
  margin: 10px 0 2px;
  padding: 10px 12px;
  background: #faf6ef;
  border: 1px solid #f0e6d6;
  border-radius: 6px;
}
.mo-flow-item + .mo-flow-item { margin-top: 10px; }
.mo-flow-dot {
  flex: none;
  width: 8px;
  height: 8px;
  margin-top: 5px;
  border-radius: 50%;
}
.mo-flow-title { margin: 0; font-size: 13px; color: #3a2a18; }
.mo-flow-time { margin: 2px 0 0; font-size: 12px; color: #9a8a73; }
.mo-flow-note { margin: 2px 0 0; font-size: 12px; color: #8a6d4f; }
.mo-flow-empty { margin: 0; font-size: 12px; color: #9a8a73; }
.mo-cash { padding: 2px 2px 8px; }
.mo-cash-item { font-size: 15px; color: #3a2a18; margin: 0; }
.mo-cash-type { margin-left: 8px; font-size: 12px; color: #8a6d4f; }
.mo-cash-amount { font-size: 13px; color: #5a4632; margin: 6px 0 0; }
.mo-cash-amount em { font-style: normal; color: #a3361f; font-weight: 700; font-size: 18px; }
.mo-cash-tip { margin: 12px 0 0; font-size: 12px; color: #9a8a73; }
/* 收银台支付方式：横向等分排列 */
.mo-methods { display: flex; gap: 8px; margin-top: 6px; }
.mo-method {
  flex: 1;
  position: relative;
  border: 1px solid #e0d3bd;
  border-radius: 6px;
  padding: 10px 4px;
  text-align: center;
  cursor: pointer;
  font-size: 13px;
  color: #5a4632;
}
.mo-method input { position: absolute; opacity: 0; pointer-events: none; }
/* 选中的支付方式：加深边框并使用浅色背景 */
.mo-method-on { border-color: #6b4a2b; background: #faf3e6; }
.mo-method-icon {
  display: block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  margin: 0 auto 4px;
  background: #c9a86a;
  color: #fff;
  border-radius: 50%;
  font-size: 13px;
}
</style>
