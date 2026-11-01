<!-- 文创作品详情页：作品信息、收藏、购买下单弹窗、作品故事与同作者作品 -->
<template>
  <div class="product-detail-page">
    <!-- 首屏：作品封面、名称、传承人与技艺信息 -->
    <header v-if="product" class="pd-hero" :class="{ 'hero-plain': !product.cover }" :style="coverStyle(product)">
      <span class="pd-detail-glyph">{{ product.glyph }}</span>
      <div class="pd-hero-mask">
        <span v-if="product.flag" class="detail-flag">{{ product.flag }}</span>
        <div class="pd-detail-seal">漆 · 物</div>
        <h1 class="pd-detail-name">{{ product.name }}</h1>
        <p class="detail-maker">
          <span class="pd-verified">✓</span>{{ product.inheritor }} · {{ product.craft }} · {{ product.level }}非遗传承人
        </p>
        <button class="maker-link" @click="goInheritor">查看传承人主页 ›</button>
      </div>
    </header>

    <Nav />

    <div class="pd-detail-wrap" v-if="product">
      <!-- 返回作品列表 -->
      <button class="pd-back-btn" @click="goBack">‹ 返回作品</button>

      <div class="pd-detail-main">
        <!-- 作品信息区：收藏按钮、规格参数、购买或非卖品说明 -->
        <div class="detail-info">

          <!-- 收藏按钮：已收藏时显示实心爱心 -->
          <button class="pd-fav-btn" :class="{ 'pd-fav-active': favorited }" @click="toggleFav">
            <span class="pd-fav-heart">{{ favorited ? '♥' : '♡' }}</span>
            {{ favorited ? '已收藏' : '收藏' }}
          </button>

          <!-- 规格参数：技艺门类、品类、材质、尺寸 -->
          <div class="detail-spec">
            <div class="spec-row"><span class="spec-label">技艺门类</span><span class="spec-val">{{ product.craft }}</span></div>
            <div class="spec-row"><span class="spec-label">品类</span><span class="spec-val">{{ product.category }}</span></div>
            <div class="spec-row"><span class="spec-label">材质</span><span class="spec-val">{{ product.material }}</span></div>
            <div class="spec-row"><span class="spec-label">尺寸</span><span class="spec-val">{{ product.size }}</span></div>
          </div>

          <!-- 交易区：可售作品显示价格、库存和购买按钮；非卖品只作展示 -->
          <div class="detail-trade" :class="product.saleable ? 'trade-on' : 'trade-off'">
            <template v-if="product.saleable">
              <div class="trade-price">
                <span class="trade-price-label">售价</span>
                <span class="trade-price-num"><em>¥</em>{{ product.price }}</span>
              </div>
              <div class="trade-stock" :class="product.stock > 0 ? '' : 'trade-stock-none'">
                {{ product.stock > 0 ? '库存 ' + product.stock + ' 件' : '已售罄' }}
              </div>
              <button class="pd-btn" :disabled="product.stock <= 0" @click="openBuy">
                {{ product.stock > 0 ? '立即购买' : '已售罄' }}
              </button>
            </template>
            <template v-else>
              <div class="trade-offline">
                <span class="trade-offline-icon">藏</span>
                <div class="trade-offline-text">
                  <span class="trade-offline-title">非卖品 · 仅供欣赏</span>
                  <span class="trade-offline-note">{{ product.saleNote || '此作为传承人珍藏，仅作展示，暂不出售。' }}</span>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 作品故事 -->
      <section class="detail-story">
        <div class="pd-section-head">
          <h2 class="pd-section-cn">作品故事</h2>
          <span class="pd-section-en">THE STORY</span>
        </div>
        <p class="story-text">{{ product.story }}</p>
      </section>

      <!-- 工艺亮点：逐条编号展示 -->
      <section v-if="product.highlights && product.highlights.length" class="detail-craft">
        <div class="pd-section-head">
          <h2 class="pd-section-cn">工艺亮点</h2>
          <span class="pd-section-en">CRAFT</span>
        </div>
        <ul class="pd-craft-list">
          <li v-for="(h, i) in product.highlights" :key="i" class="pd-craft-item">
            <span class="pd-craft-num">{{ '零一二三四五六七八九'[i] || i + 1 }}</span>
            <span class="pd-craft-text">{{ h }}</span>
          </li>
        </ul>
      </section>

      <!-- 同作者作品：最多展示 4 件，点击进入对应详情 -->
      <section v-if="others.length" class="detail-others">
        <div class="pd-section-head">
          <h2 class="pd-section-cn">同作者作品</h2>
          <span class="pd-section-en">MORE WORKS</span>
        </div>
        <div class="others-grid">
          <div v-for="o in others" :key="o.id" class="other-card" @click="goDetail(o.id)">
            <div class="other-cover" :style="coverStyle(o)">
              <span class="other-glyph">{{ o.glyph }}</span>
            </div>
            <h4 class="other-name">{{ o.name }}</h4>
            <p class="other-maker">{{ o.craft }} · {{ o.category }}</p>
          </div>
        </div>
      </section>
    </div>

    <!-- 作品不存在时的空状态 -->
    <div v-else class="pd-detail-empty">
      <p class="pd-empty-text">未找到该作品</p>
      <button class="pd-btn" @click="goBack">返回作品列表</button>
    </div>

    <!-- 下单弹窗：作品摘要、购买数量、收货地址、备注与合计金额 -->
    <el-dialog v-model="buyVisible" title="确认订单" width="520px" :close-on-click-modal="false">
      <template v-if="product">
        <!-- 作品摘要：缩略字形、名称、技艺信息与单价 -->
        <div class="pd-buy-summary">
          <span class="pd-buy-glyph">{{ product.glyph }}</span>
          <div class="pd-buy-info">
            <h4>{{ product.name }}</h4>
            <p>{{ product.craft }} · {{ product.category }} · 传承人 {{ product.inheritor }}</p>
          </div>
          <span class="pd-buy-price"><em>¥</em>{{ product.price }}</span>
        </div>

        <el-form label-width="72px" class="pd-buy-form">
          <!-- 购买数量：最少 1 件，最多不超过库存 -->
          <el-form-item label="数量">
            <el-input-number v-model="qty" :min="1" :max="Math.max(1, product.stock)" />
            <span class="pd-buy-stock">库存 {{ product.stock }} 件</span>
          </el-form-item>

          <!-- 收货地址簿：点击某个地址即可选中，并自动填入订单信息 -->
          <div v-if="bookAddresses.length" class="pd-addr-book">
            <p class="pd-addr-book-title">收货地址</p>
            <div
              v-for="a in bookAddresses"
              :key="a.id"
              class="pd-addr-item"
              :class="{ 'pd-addr-item-on': selectedAddrId === a.id }"
              @click="chooseAddr(a)"
            >
              <span class="pd-addr-radio">{{ selectedAddrId === a.id ? '◉' : '○' }}</span>
              <div class="pd-addr-main">
                <p class="pd-addr-l1">
                  <b>{{ a.name }}</b><i>{{ a.phone }}</i><em v-if="a.isDefault">默认</em>
                </p>
                <p class="pd-addr-l2">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</p>
              </div>
            </div>
          </div>

          <!-- 新增地址开关：地址簿为空时默认展开 -->
          <div class="pd-addr-new-toggle">
            <button type="button" class="pd-addr-new-btn" @click="toggleAddrAdd">
              {{ showAddrAdd ? '− 收起新增' : '＋ ' + (bookAddresses.length ? '没有合适地址？新增一个' : '添加收货地址') }}
            </button>
          </div>
          <!-- 新增地址表单：保存后会自动选中并用于本次下单 -->
          <div v-if="showAddrAdd" class="pd-addr-new">
            <el-input v-model="addrForm.receiver" placeholder="收货人姓名" maxlength="20" />
            <el-input v-model="addrForm.phone" placeholder="11 位手机号" maxlength="11" />
            <div class="pd-addr-new-row">
              <el-input v-model="addrForm.province" placeholder="省" maxlength="20" />
              <el-input v-model="addrForm.city" placeholder="市" maxlength="20" />
              <el-input v-model="addrForm.district" placeholder="区/县" maxlength="20" />
            </div>
            <el-input v-model="addrForm.detail" placeholder="详细地址（街道、门牌号）" maxlength="100" />
            <div class="pd-addr-new-actions">
              <el-button size="small" type="primary" :loading="savingAddr" @click="saveNewAddr">保存该地址并使用</el-button>
            </div>
          </div>

          <!-- 订单备注与实时计算的合计金额 -->
          <el-form-item label="备注">
            <el-input v-model="buyForm.remark" placeholder="选填，如：工作日派送" />
          </el-form-item>
          <div class="pd-buy-total">
            合计：<span class="pd-buy-total-num"><em>¥</em>{{ (Number(product.price) * qty).toFixed(2) }}</span>
          </div>
        </el-form>
      </template>
      <!-- 弹窗底部操作：取消或提交订单 -->
      <template #footer>
        <el-button @click="buyVisible = false">取消</el-button>
        <el-button type="primary" :loading="buying" @click="confirmBuy">提交订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/* 作品详情：展示作品信息，处理收藏、收货地址与下单流程 */
import { computed, ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import { isFavorite, toggleFavorite, loadFavorites, heritageProducts, loadProducts, addProductOrder, isLoggedIn, authState, inheritors, loadInheritors, addresses as bookAddresses, loadAddresses, addAddress } from '@/store'

const route = useRoute()
const router = useRouter()

const products = heritageProducts

// 加载作品与传承人数据；已登录用户额外加载收藏记录，用于显示收藏状态
onMounted(() => {
  const jobs = [loadProducts(), loadInheritors()]
  if (isLoggedIn()) jobs.push(loadFavorites())
  Promise.allSettled(jobs)
})

/* 当前作品：按路由 id 查找已审核通过的作品，找不到返回 null */
const product = computed(() => {
  const id = Number(route.params.id)
  return products.find((p) => p.id === id && p.status === 'approved') || null
})

/* 同作者作品：同一位传承人下其他已审核作品，最多取 4 件 */
const others = computed(() => {
  if (!product.value) return []
  return products
    .filter((p) => p.status === 'approved' && p.inheritor === product.value.inheritor && p.id !== product.value.id)
    .slice(0, 4)
})

/* 有封面时生成背景图样式，否则返回空样式 */
function coverStyle(p) {
  if (p.cover) {
    return { backgroundImage: 'url(' + p.cover + ')' }
  }
  return {}
}

function goDetail(id) {
  router.push('/product/' + id)
}

function goBack() {
  router.push('/product')
}

/* 下单弹窗状态：是否显示、是否提交中、购买数量与订单表单 */
const buyVisible = ref(false)
const buying = ref(false)
const qty = ref(1)
const buyForm = reactive({ receiver: '', phone: '', address: '', remark: '' })

/* 地址相关状态：当前选中的地址、是否展开新增表单、是否保存中，以及新增地址表单 */
const selectedAddrId = ref(null)
const showAddrAdd = ref(false)
const savingAddr = ref(false)
const addrForm = reactive({ receiver: '', phone: '', province: '', city: '', district: '', detail: '' })

/* 把选中地址拆分后填入订单表单，省去用户重复输入 */
function fillBuyFrom(a) {
  buyForm.receiver = a.name
  buyForm.phone = a.phone
  buyForm.address = (a.province || '') + (a.city || '') + (a.district || '') + (a.detail || '')
}

/* 选择地址：记录选中项、收起新增表单并同步订单信息 */
function chooseAddr(a) {
  selectedAddrId.value = a.id
  showAddrAdd.value = false
  fillBuyFrom(a)
}

/* 展开或收起新增地址表单 */
function toggleAddrAdd() {
  showAddrAdd.value = !showAddrAdd.value
}

/* 清空新增地址表单 */
function resetAddrNew() {
  Object.assign(addrForm, { receiver: '', phone: '', province: '', city: '', district: '', detail: '' })
}

/* 保存新地址：先校验必填项和手机号格式，成功后自动选中该地址 */
async function saveNewAddr() {
  // 收货人、电话、省市区和详细地址都不能为空
  if (!addrForm.receiver.trim() || !addrForm.phone.trim() || !addrForm.province.trim() || !addrForm.city.trim() || !addrForm.detail.trim()) {
    ElMessage.warning('请完整填写收货人、电话与省市区/详细地址')
    return
  }
  // 手机号必须是 1 开头的 11 位数字
  if (!/^1\d{10}$/.test(addrForm.phone.trim())) {
    ElMessage.warning('请输入正确的 11 位手机号')
    return
  }
  savingAddr.value = true
  try {
    const created = await addAddress({
      receiver: addrForm.receiver.trim(),
      phone: addrForm.phone.trim(),
      province: addrForm.province.trim(),
      city: addrForm.city.trim(),
      district: addrForm.district.trim(),
      detail: addrForm.detail.trim(),
      isDefault: !bookAddresses.length,
    })
    // 新地址保存成功：选中它、收起表单、填入订单并清空新增表单
    const a = created
    selectedAddrId.value = a.id
    showAddrAdd.value = false
    fillBuyFrom(a)
    resetAddrNew()
    ElMessage.success('地址已保存并使用')
  } catch (e) {
    ElMessage.error((e && e.message) || '保存地址失败，请重试')
  } finally {
    savingAddr.value = false
  }
}

/* 打开下单弹窗：先检查登录与角色，再加载地址簿并给出默认地址 */
async function openBuy() {
  if (!product.value) return
  // 未登录先跳转登录页，登录后回到当前作品页
  if (!isLoggedIn()) {
    router.push('/login?redirect=' + encodeURIComponent(route.fullPath))
    return
  }
  // 只有普通学员账号可以购买
  if (authState.user?.role !== 'user') {
    ElMessage.warning('仅普通用户账号可购买作品，请用学员账号登录')
    return
  }
  // 每次打开都重置弹窗状态
  selectedAddrId.value = null
  showAddrAdd.value = false
  buyForm.remark = ''
  qty.value = 1
  try {
    await loadAddresses()
  } catch (e) {
  }
  // 有地址时优先选默认地址，否则选第一条；完全没有地址则展开新增表单
  const def = bookAddresses.find((a) => a.isDefault) || bookAddresses[0]
  if (def) {
    chooseAddr(def)
  } else {
    // 用当前账号信息预填收货人，减少输入
    buyForm.receiver = authState.user?.name || authState.user?.username || ''
    buyForm.phone = authState.user?.phone || ''
    buyForm.address = ''
    resetAddrNew()
    showAddrAdd.value = true
  }
  buyVisible.value = true
}

/* 提交订单：校验收货信息后调用下单接口，成功则跳到我的订单页 */
async function confirmBuy() {
  if (!product.value) return
  // 收货人、电话、地址三项必填
  if (!buyForm.receiver.trim()) {
    ElMessage.warning('请填写收件人')
    return
  }
  if (!buyForm.phone.trim()) {
    ElMessage.warning('请填写联系电话')
    return
  }
  if (!buyForm.address.trim()) {
    ElMessage.warning('请填写收货地址')
    return
  }
  buying.value = true
  try {
    const p = product.value
    await addProductOrder({
      productId: p.id,
      qty: qty.value,
      receiver: buyForm.receiver.trim(),
      phone: buyForm.phone.trim(),
      address: buyForm.address.trim(),
      remark: buyForm.remark.trim(),
    })
    // 下单成功：关闭弹窗，提示用户去付款，稍后自动跳转订单页
    buyVisible.value = false
    ElMessage.success('订单已提交，待付款，请前往「我的订单」完成支付')
    setTimeout(() => router.push('/profile/order'), 600)
  } catch (e) {
    ElMessage.error((e && e.message) || '下单失败，请重试')
  } finally {
    buying.value = false
  }
}

/* 按作品上的传承人姓名查找主页，找到后跳转，否则回到传承人列表 */
function goInheritor() {
  if (!product.value) return
  const master = inheritors.find((m) => m.name === product.value.inheritor)
  if (master) {
    router.push('/inheritor/' + master.id)
  } else {
    router.push('/inheritor')
  }
}

/* 当前作品是否已被收藏 */
const favorited = computed(() => {
  return product.value ? isFavorite(product.value.id) : false
})

/* 切换收藏状态，并根据结果给出提示 */
function toggleFav() {
  if (!product.value) return
  const nowFav = toggleFavorite(product.value)
  if (nowFav) {
    ElMessage.success('已收藏，可在「我的收藏」查看')
  } else {
    ElMessage.success('已取消收藏')
  }
}
</script>

<style src="./ProductDetail.css"></style>

<style scoped>
/* 库存提示：有货用棕色，售罄用红色 */
.trade-stock {
  margin: 6px 0 10px;
  font-size: 13px;
  color: #8a6d4f;
}
.trade-stock-none {
  color: #c0392b;
}
.pd-btn[disabled] {
  opacity: 0.55;
  cursor: not-allowed;
}
/* 下单弹窗中的作品摘要：横向排列缩略图、文字和价格 */
.pd-buy-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 6px;
  background: #faf6ef;
  border-radius: 6px;
}
.pd-buy-glyph {
  width: 42px;
  height: 42px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
  background: #6b4a2b;
  border-radius: 4px;
}
.pd-buy-info {
  flex: 1;
  min-width: 0;
}
.pd-buy-info h4 {
  margin: 0 0 2px;
  font-size: 15px;
  color: #3a2a18;
}
.pd-buy-info p {
  margin: 0;
  font-size: 12px;
  color: #8a6d4f;
}
.pd-buy-price {
  color: #a3361f;
  font-weight: 700;
  font-size: 16px;
}
.pd-buy-stock {
  margin-left: 10px;
  font-size: 12px;
  color: #8a6d4f;
}
.pd-buy-total {
  text-align: right;
  padding-right: 6px;
  font-size: 13px;
  color: #5a4632;
}
.pd-buy-total-num {
  color: #a3361f;
  font-weight: 700;
  font-size: 18px;
}

/* 地址簿：限制最大高度，地址较多时在内部滚动 */
.pd-addr-book {
  margin: 0 0 6px;
  padding: 0 2px;
  max-height: 172px;
  overflow: auto;
}
.pd-addr-book-title {
  margin: 0 0 6px;
  font-size: 13px;
  color: #5a4632;
}
/* 单条地址：整块可点击，悬停时边框变色 */
.pd-addr-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  margin-bottom: 6px;
  border: 1px solid #e6dccb;
  border-radius: 6px;
  cursor: pointer;
  background: #fff;
  transition: all 0.15s;
}
.pd-addr-item:hover {
  border-color: #c9a86a;
}
/* 当前选中的地址：深色边框 + 浅色背景 */
.pd-addr-item-on {
  border-color: #6b4a2b;
  background: #faf3e6;
}
.pd-addr-radio {
  color: #6b4a2b;
  font-size: 14px;
  line-height: 20px;
}
.pd-addr-main {
  flex: 1;
  min-width: 0;
}
.pd-addr-l1 {
  margin: 0 0 2px;
  font-size: 13px;
  color: #3a2a18;
}
.pd-addr-l1 b {
  margin-right: 8px;
}
.pd-addr-l1 i {
  font-style: normal;
  color: #8a6d4f;
  margin-right: 8px;
}
.pd-addr-l1 em {
  font-style: normal;
  font-size: 11px;
  color: #fff;
  background: #b8860b;
  border-radius: 3px;
  padding: 1px 4px;
}
.pd-addr-l2 {
  margin: 0;
  font-size: 12px;
  color: #8a6d4f;
}
.pd-addr-new-toggle {
  margin: 2px 0 10px;
}
.pd-addr-new-btn {
  border: none;
  background: none;
  padding: 0;
  font-size: 13px;
  color: #6b4a2b;
  cursor: pointer;
}
.pd-addr-new-btn:hover {
  color: #a3361f;
}
/* 新增地址表单：虚线边框与浅色底，和地址列表区分开 */
.pd-addr-new {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  margin: 0 0 12px;
  border: 1px dashed #c9a86a;
  border-radius: 6px;
  background: #fdfbf6;
}
.pd-addr-new-row {
  display: flex;
  gap: 8px;
}
.pd-addr-new-actions {
  text-align: right;
}
</style>
