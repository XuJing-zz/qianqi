<!-- 个人中心 · 个人资料页：展示登录用户资料，支持编辑资料与更换头像 -->
<template>
  <div class="profile-page">
    <Nav />

    <!-- 页面主体：左侧个人中心侧边栏 + 右侧资料内容 -->
    <div class="pf-wrap">
      <ProfileAside />

      <div class="pf-main">
        <!-- 未登录分支：显示占位说明和登录按钮 -->
        <template v-if="!loggedIn">
          <header class="pf-head">
            <h1 class="pf-title">个人中心</h1>
            <span class="pf-en">PROFILE</span>
          </header>
          <div class="pf-card pf-guest-card">
            <div class="pf-guest-seal">漆</div>
            <h2 class="pf-guest-title">您还未登录</h2>
            <p class="pf-guest-desc">登录后即可查看个人资料、管理报名与订单、收藏心仪作品。</p>
            <button class="pf-btn" @click="goLogin">立即登录</button>
          </div>
        </template>

        <template v-else>
        <!-- 已登录分支：展示头像、资料列表和编辑入口 -->
        <header class="pf-head">
          <h1 class="pf-title">个人资料</h1>
          <span class="pf-en">PROFILE</span>
        </header>

        <div class="pf-card">
          <!-- 头像区：点击“更换头像”选择图片后立即上传 -->
          <div class="pf-avatar-row">
            <div class="pf-avatar">
              <img v-if="avatarUrl" :src="avatarUrl" class="pf-avatar-img" alt="头像" />
              <span v-else class="pf-avatar-glyph">{{ form.nick.charAt(0) }}</span>
            </div>
            <div class="pf-avatar-tools">
              <button class="pf-btn pf-btn-ghost" @click="triggerUpload">更换头像</button>
              <input ref="fileInput" type="file" accept="image/*" class="pf-file-hidden" @change="onFileChange" />
            </div>
          </div>

          <!-- 资料展示列表：逐项显示昵称、姓名、联系方式、所在地等字段 -->
          <ul class="pf-list">
            <li class="pf-item">
              <span class="pf-label">昵称</span>
              <span class="pf-value">{{ form.nick }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">真实姓名</span>
              <span class="pf-value">{{ form.name || '未填写' }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">姓</span>
              <span class="pf-value">{{ form.last_name || '未填写' }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">名</span>
              <span class="pf-value">{{ form.first_name || '未填写' }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">手机号</span>
              <span class="pf-value">{{ form.phone }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">邮箱</span>
              <span class="pf-value">{{ form.email || '未填写' }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">性别</span>
              <span class="pf-value">{{ form.gender || '未填写' }}</span>
            </li>
            <li class="pf-item">
              <span class="pf-label">所在地</span>
              <span class="pf-value">{{ form.region || '未填写' }}</span>
            </li>
            <li class="pf-item pf-item-full">
              <span class="pf-label">个人简介</span>
              <span class="pf-value pf-bio">{{ form.bio || '这位漆友很低调，还没有留下简介。' }}</span>
            </li>
          </ul>

          <!-- 底部操作：打开编辑资料弹窗 -->
          <div class="pf-actions">
            <button class="pf-btn" @click="openEdit">编辑资料</button>
          </div>
        </div>
        </template>
      </div>
    </div>

    <!-- 编辑资料弹窗：包含昵称、姓名、性别、邮箱、所在地和简介表单 -->
    <el-dialog v-model="editVisible" title="编辑个人资料" width="480px" :append-to-body="true">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nick" placeholder="请输入昵称" maxlength="20" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="editForm.name" placeholder="请输入真实姓名" maxlength="20" />
        </el-form-item>
        <el-form-item label="姓">
          <el-input v-model="editForm.last_name" placeholder="请输入姓" maxlength="20" />
        </el-form-item>
        <el-form-item label="名">
          <el-input v-model="editForm.first_name" placeholder="请输入名" maxlength="20" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
            <el-radio label="保密">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" maxlength="50" />
        </el-form-item>
        <el-form-item label="所在地">
          <el-cascader
            v-model="editForm.regionArr"
            :options="chinaRegions"
            :props="{ value: 'label', label: 'label', children: 'children', expandTrigger: 'hover' }"
            placeholder="请选择省份/城市"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="editForm.bio" type="textarea" :rows="4" placeholder="介绍一下自己吧" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <!-- 弹窗底部：取消或保存 -->
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import ProfileAside from './ProfileAside.vue'
import { isLoggedIn, authState, checkUploadFile } from '@/store'
import { apiMe, apiUpdateProfile } from '@/api/auth'
import { chinaRegions } from '@/assets/china-regions'

// 路由对象：用于跳转登录页
const router = useRouter()
// 登录状态：来自全局 store 的判断函数
const loggedIn = computed(() => isLoggedIn())

// 未登录时跳转到登录页，登录成功后回到个人中心
function goLogin() {
  router.push({ path: '/login', query: { redirect: '/profile' } })
}

// 页面展示用的资料对象，字段与后端返回保持一致
const loading = ref(false)
const form = reactive({
  nick: '',
  name: '',
  first_name: '',
  last_name: '',
  phone: '',
  email: '',
  gender: '',
  region: '',
  bio: '',
  avatar: '',
})

// 拉取当前用户资料并填充到展示对象；失败时提示错误
async function loadProfile() {
  loading.value = true
  try {
    const data = await apiMe()
    form.nick = data.nick || ''
    form.name = data.name || ''
    form.first_name = data.first_name || ''
    form.last_name = data.last_name || ''
    form.phone = data.phone || ''
    form.email = data.email || ''
    form.gender = data.gender || ''
    form.region = data.region || ''
    form.bio = data.bio || ''
    form.avatar = data.avatar || ''
    if (data.avatar) {
      avatarUrl.value = data.avatar
    }
  } catch (e) {
    ElMessage.error(e.message || '加载个人资料失败')
  } finally {
    loading.value = false
  }
}

// 编辑弹窗的显示状态与表单副本；regionArr 供级联选择器使用
const editVisible = ref(false)
const editForm = reactive({ nick: '', name: '', first_name: '', last_name: '', email: '', gender: '', region: '', regionArr: [], bio: '' })

// 打开编辑弹窗：把展示数据拷贝到表单，并把地区文本转成级联选择器数组
function openEdit() {
  editForm.nick = form.nick
  editForm.name = form.name
  editForm.first_name = form.first_name
  editForm.last_name = form.last_name
  editForm.email = form.email
  editForm.gender = form.gender
  editForm.region = form.region
  editForm.regionArr = regionToArr(form.region)
  editForm.bio = form.bio
  editVisible.value = true
}

/* 保存资料：
   1. 把地区数组拼成文本，优先用“姓+名”组合出真实姓名；
   2. 校验昵称非空、昵称长度、邮箱格式、姓名长度；
   3. 调用更新接口，成功后同步本地展示数据和登录态缓存。 */
async function saveEdit() {
  const arr = editForm.regionArr
  const regionText = (Array.isArray(arr) && arr.length === 2)
    ? arr[0] + arr[1]
    : (editForm.region || '')
  const ln = (editForm.last_name || '').trim()
  const fn = (editForm.first_name || '').trim()
  const fullName = (ln && fn) ? (ln + fn) : (editForm.name || '').trim()
  const nick = (editForm.nick || '').trim()
  if (!nick) {
    ElMessage.warning('昵称不能为空')
    return
  }
  if (nick.length > 20) {
    ElMessage.warning('昵称不能超过 20 个字符')
    return
  }
  const email = (editForm.email || '').trim()
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }
  if ((ln + fn).length > 50) {
    ElMessage.warning('姓名过长，姓和名合计不能超过 50 个字符')
    return
  }
  try {
    await apiUpdateProfile({
      nick,
      name: fullName,
      first_name: editForm.first_name,
      last_name: editForm.last_name,
      email: editForm.email,
      gender: editForm.gender,
      region: regionText,
      bio: editForm.bio,
      avatar: form.avatar || '',
    })
    form.nick = nick
    if (authState.user) {
      authState.user.nick = nick
      authState.user.name = fullName
      authState.user.first_name = editForm.first_name || authState.user.first_name
      authState.user.last_name = editForm.last_name || authState.user.last_name
      authState.user.email = editForm.email || authState.user.email
      authState.user.region = regionText
      authState.user.bio = editForm.bio
      localStorage.setItem('qianqi_auth', JSON.stringify(authState.user))
    }
    form.name = fullName
    form.first_name = editForm.first_name
    form.last_name = editForm.last_name
    form.email = editForm.email
    form.gender = editForm.gender
    form.region = regionText
    form.bio = editForm.bio
    editVisible.value = false
    ElMessage.success('资料已保存')
  } catch (e) {
    ElMessage.error(e.message || '保存失败，请重试')
  }
}

// 把“浙江省杭州市”这类地区文本拆成 [省, 市] 数组，便于级联选择器回显
function regionToArr(region) {
  if (!region) return []
  const trimmed = region.trim()
  const m = trimmed.match(/^(.+?[省市])(.+)$/)
  if (m) return [m[1], m[2]]
  return [trimmed]
}

// 头像相关状态：头像地址、隐藏的文件输入框、头像保存中标记
const avatarUrl = ref('')
const fileInput = ref(null)
const avatarSaving = ref(false)

// 触发隐藏的文件输入框，弹出系统文件选择窗口
function triggerUpload() {
  fileInput.value && fileInput.value.click()
}

/* 处理头像文件选择：
   先校验文件大小，再读取图片为数据 URL，立即回显预览并调用更新接口保存。 */
// FileReader：FileReader 是浏览器提供的文件读取接口，readAsDataURL 可把文件读成 Base64 数据 URL
async function onFileChange(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  const limitErr = checkUploadFile(file, { name: '图片', fallbackMb: 5 })
  if (limitErr) {
    ElMessage.warning(limitErr)
    return
  }
  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result
    avatarUrl.value = dataUrl
    e.target.value = ''
    avatarSaving.value = true
    try {
      await apiUpdateProfile({ avatar: dataUrl })
      form.avatar = dataUrl
      ElMessage.success('头像已更新')
    } catch (err) {
      ElMessage.error((err && err.message) || '头像保存失败，请重试')
    } finally {
      avatarSaving.value = false
    }
  }
  reader.readAsDataURL(file)
}

// 页面挂载后，已登录才请求个人资料
onMounted(() => {
  if (isLoggedIn()) {
    loadProfile()
  }
})
</script>

<style src="./Profile.css"></style>
