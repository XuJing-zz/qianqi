<!-- 个人中心 · 收货地址页：展示地址列表，支持新增、编辑、删除和设为默认 -->
<template>
  <div class="address-page">
    <Nav />

    <!-- 页面主体：左侧个人中心侧边栏 + 右侧地址列表 -->
    <div class="ma-wrap">
      <ProfileAside />

      <div class="ma-main">
        <header class="ma-head">
          <h1 class="ma-title">收货地址</h1>
          <span class="ma-en">SHIPPING ADDRESS</span>
        </header>

        <!-- 工具栏：地址总数与新增按钮 -->
        <div class="ma-toolbar">
          <span class="ma-count">共 {{ addresses.length }} 个地址</span>
          <button class="ma-btn ma-btn-solid" @click="openAdd">+ 新增地址</button>
        </div>

        <!-- 地址列表：每张卡片显示收货人、电话、完整地址和操作按钮 -->
        <div class="ma-list" v-if="addresses.length">
          <div v-for="a in addresses" :key="a.id" class="ma-card" :class="{ 'ma-card-default': a.isDefault }">
            <div class="ma-top">
              <span class="ma-name">{{ a.name }}</span>
              <span class="ma-phone">{{ a.phone }}</span>
              <span v-if="a.isDefault" class="ma-default">默认</span>
            </div>
            <p class="ma-detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</p>
            <div class="ma-actions">
              <button class="ma-link" @click="openEdit(a)">编辑</button>
              <button v-if="!a.isDefault" class="ma-link" @click="setDefault(a)">设为默认</button>
              <button class="ma-link ma-link-danger" @click="removeAddress(a)">删除</button>
            </div>
          </div>
        </div>

        <div v-else class="ma-empty">
          <!-- 空状态：没有地址时给出新增入口 -->
          <p class="ma-empty-text">还没有收货地址</p>
          <button class="ma-btn ma-btn-solid" @click="openAdd">新增地址</button>
        </div>
      </div>
    </div>

    <!-- 新增/编辑地址弹窗：editingId 为空表示新增，否则表示编辑 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑地址' : '新增地址'" width="480px" :append-to-body="true">
      <el-form :model="addrForm" label-width="80px">
        <el-form-item label="收货人">
          <el-input v-model="addrForm.name" placeholder="请输入收货人姓名" maxlength="20" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="addrForm.phone" placeholder="11 位手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="省/市/区">
          <div class="ma-region-row">
            <el-input v-model="addrForm.province" placeholder="省" maxlength="20" />
            <el-input v-model="addrForm.city" placeholder="市" maxlength="20" />
            <el-input v-model="addrForm.district" placeholder="区/县" maxlength="20" />
          </div>
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="addrForm.detail" type="textarea" :rows="2" placeholder="街道、门牌号等" maxlength="100" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addrForm.isDefault" />
        </el-form-item>
      </el-form>
      <!-- 弹窗底部：取消或保存 -->
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Nav from '@/views/user/common/nav.vue'
import ProfileAside from './ProfileAside.vue'
import { addresses, loadAddresses, addAddress, updateAddressAction, removeAddress as removeAddressRemote } from '@/store'

// 进入页面时加载地址列表；失败时静默处理，由全局请求层负责提示
onMounted(() => {
  loadAddresses().catch(() => {})
})

// 弹窗状态：editingId 为 null 时是新增，否则是正在编辑的地址 ID
const dialogVisible = ref(false)
const editingId = ref(null)
const addrForm = reactive({ name: '', phone: '', province: '', city: '', district: '', detail: '', isDefault: false })

// 打开新增弹窗：清空表单并清除编辑标识
function openAdd() {
  editingId.value = null
  Object.assign(addrForm, { name: '', phone: '', province: '', city: '', district: '', detail: '', isDefault: false })
  dialogVisible.value = true
}

// 打开编辑弹窗：把选中地址的字段回填到表单
function openEdit(a) {
  editingId.value = a.id
  Object.assign(addrForm, {
    name: a.name, phone: a.phone, province: a.province, city: a.city,
    district: a.district, detail: a.detail, isDefault: a.isDefault,
  })
  dialogVisible.value = true
}

// 把表单字段转换成后端接口需要的字段名（页面用 name，接口用 receiver）
function toPayload() {
  return {
    receiver: addrForm.name.trim(),
    phone: addrForm.phone.trim(),
    province: addrForm.province.trim(),
    city: addrForm.city.trim(),
    district: addrForm.district.trim(),
    detail: addrForm.detail.trim(),
    isDefault: addrForm.isDefault,
  }
}

/* 保存地址：
   先校验收货人、手机号、省市区和详细地址是否填写完整，再校验手机号格式；
   通过后根据 editingId 判断调用更新接口还是新增接口。 */
async function saveAddress() {
  if (!addrForm.name.trim() || !addrForm.phone.trim() || !addrForm.province.trim() || !addrForm.city.trim() || !addrForm.detail.trim()) {
    ElMessage.warning('请填写完整的地址信息')
    return
  }
  if (!/^1\d{10}$/.test(addrForm.phone.trim())) {
    ElMessage.warning('请输入正确的 11 位手机号')
    return
  }
  try {
    if (editingId.value) {
      await updateAddressAction(editingId.value, toPayload())
      ElMessage.success('地址已更新')
    } else {
      await addAddress(toPayload())
      ElMessage.success('地址已新增')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error((e && e.message) || '保存失败，请重试')
  }
}

// 设为默认地址：复用更新接口，把该地址的 isDefault 置为 true
async function setDefault(a) {
  try {
    await updateAddressAction(a.id, {
      receiver: a.name, phone: a.phone, province: a.province,
      city: a.city, district: a.district, detail: a.detail,
      isDefault: true,
    })
    ElMessage.success('已将「' + a.province + a.city + '」设为默认地址')
  } catch (e) {
    ElMessage.error((e && e.message) || '操作失败，请重试')
  }
}

// 删除地址：先弹确认框，确认后再调用删除接口
function removeAddress(a) {
  ElMessageBox.confirm('确定删除该地址吗？', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await removeAddressRemote(a.id)
        ElMessage.success('已删除')
      } catch (e) {
        ElMessage.error((e && e.message) || '删除失败，请重试')
      }
    })
    .catch(() => {})
}
</script>

<style src="./MyAddress.css"></style>
