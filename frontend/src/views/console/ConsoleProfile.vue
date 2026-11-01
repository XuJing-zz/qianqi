<!-- 个人主页维护页：左侧实时预览传承人主页，右侧编辑资料、头像与荣誉证书 -->
<template>
  <ConsoleLayout>
    <div class="cpf-wrap">
      <!-- 页面标题区 -->
      <div class="cpf-head">
        <div class="cpf-head-left">
          <h2 class="cpf-title">个人主页</h2>
          <p class="cpf-sub">维护您对外展示的传承人主页信息</p>
        </div>
      </div>

      <!-- 左侧预览 + 右侧编辑表单的两栏布局 -->
      <div class="cpf-layout">
        <!-- 主页预览区：姓名、级别、技艺、简介、地区等信息随表单数据实时更新 -->
        <div class="cpf-preview">
          <div class="cpf-preview-label">主页预览</div>
          <div class="cpf-card">
            <div class="cpf-card-head">
              <div class="cpf-avatar" :style="avatarStyle">
                <span v-if="!profile.avatar" class="cpf-avatar-glyph">{{ profile.name.charAt(0) || '漆' }}</span>
                <img v-else :src="profile.avatar" class="cpf-avatar-img" alt="头像" />
              </div>
              <div class="cpf-card-info">
                <div class="cpf-seal">匠 心 传 人</div>
                <h1 class="cpf-name">{{ profile.name || '未填写姓名' }}</h1>
                <p class="cpf-level">✓ {{ profile.level }}非遗传承人 · {{ profile.craft }}技艺</p>
                <p v-if="profile.intro" class="cpf-intro">{{ profile.intro }}</p>
              </div>
            </div>
            <p class="cpf-bio">{{ profile.bio || '还没有填写简介' }}</p>
            <div class="cpf-meta">
              <span v-if="profile.region" class="cpf-meta-item">📍 {{ profile.region }}</span>
              <span v-if="profile.years" class="cpf-meta-item">🎨 从艺 {{ profile.years }} 年</span>
              <span v-if="profile.mentor" class="cpf-meta-item">👤 师承：{{ profile.mentor }}</span>
              <span v-if="profile.honor" class="cpf-meta-item">🏅 {{ profile.honor }}</span>
            </div>
          </div>
        </div>

        <!-- 资料编辑表单区 -->
        <div class="cpf-form-block">
          <el-form label-width="90px" class="cpf-form">
            <!-- 头像上传：选择图片后读取为 DataURL 并立即保存 -->
            <el-form-item label="头像">
              <div class="cpf-upload">
                <div class="cpf-upload-preview">
                  <img v-if="profile.avatar" :src="profile.avatar" class="cpf-upload-img" alt="头像" />
                  <span v-else class="cpf-upload-glyph">{{ profile.name.charAt(0) || '漆' }}</span>
                </div>
                <el-upload :show-file-list="false" :before-upload="onAvatarUpload" accept="image/*">
                  <el-button>上传头像</el-button>
                </el-upload>
                <el-button v-if="profile.avatar" text type="danger" @click="removeAvatar">移除</el-button>
              </div>
            </el-form-item>

            <el-form-item label="姓名">
              <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" />
            </el-form-item>

            <el-form-item label="传承级别">
              <el-select v-model="form.level" style="width: 100%">
                <el-option v-for="lv in levelOptions" :key="lv" :label="lv" :value="lv" />
              </el-select>
            </el-form-item>

            <el-form-item label="技艺方向">
              <el-select v-model="form.craft" style="width: 100%" filterable allow-create placeholder="可多选或用·分隔" multiple>
                <el-option v-for="c in craftOptions" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>

            <el-form-item label="所在地区">
              <el-input v-model="form.region" placeholder="如：四川成都" maxlength="50" />
            </el-form-item>

            <el-form-item label="师承关系">
              <el-input
                v-model="form.mentor"
                placeholder="如：师承漆艺大师王老"
                maxlength="100"
                show-word-limit
                :disabled="!profile.profileId"
              />
              <span class="cpf-field-tip">
                {{ profile.profileId ? '展示在主页「传承档案 · 师承关系」' : '尚未开通公开主页，需管理员建档后才能维护' }}
              </span>
            </el-form-item>

            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="数字，可用 - 或 * 脱敏" maxlength="20" />
            </el-form-item>

            <el-form-item label="从艺年限">
              <el-input-number v-model="form.years" :min="0" :max="80" />
            </el-form-item>

            <el-form-item label="一句话签名">
              <el-input v-model="form.intro" placeholder="如：以漆载道，一髹入心" maxlength="30" show-word-limit />
            </el-form-item>

            <el-form-item label="荣誉">
              <el-input v-model="form.honor" type="textarea" :rows="2" placeholder="如：作品入藏国家博物馆" maxlength="200" show-word-limit />
            </el-form-item>

            <!-- 荣誉证书：上传 / 移除附件；需先由管理员开通公开主页 -->
            <el-form-item label="荣誉证书">
              <div v-if="!profile.profileId" class="cpf-cert-tip">尚未开通公开主页，暂无法上传证书附件，请联系管理员。</div>
              <template v-else>
                <div class="cpf-cert-list">
                  <div v-for="(c, i) in profile.certs" :key="i" class="cpf-cert-item">
                    <span class="cpf-cert-icon">📄</span>
                    <a class="cpf-cert-name" :href="c.url" target="_blank" rel="noopener">{{ c.name }}</a>
                    <el-button text size="small" type="danger" @click="removeCert(i)">移除</el-button>
                  </div>
                  <el-upload
                    class="cpf-cert-upload"
                    :show-file-list="false"
                    :before-upload="onCertUpload"
                    accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip"
                  >
                    <el-button size="small" plain>＋ 上传证书附件</el-button>
                  </el-upload>
                </div>
                <p class="cpf-cert-hint">支持图片、PDF、Word、Excel 等，单文件 ≤ {{ docMaxMb }}MB</p>
              </template>
            </el-form-item>

            <el-form-item label="个人简介">
              <el-input v-model="form.bio" type="textarea" :rows="4" placeholder="介绍您的从艺经历、代表作等" maxlength="300" show-word-limit />
            </el-form-item>
          </el-form>

          <!-- 底部操作：还原为已保存内容 / 保存主页 -->
          <div class="cpf-actions">
            <el-button @click="resetForm">重置</el-button>
            <el-button type="primary" @click="save">保存主页</el-button>
          </div>
        </div>
      </div>
    </div>
  </ConsoleLayout>
</template>

<script setup>
// 页面依赖：Vue 响应式 API、消息提示、工作台布局、传承人接口与状态层资料
import { reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConsoleLayout from './ConsoleLayout.vue'
import { apiUploadCert, apiUpdateInheritor } from '@/api/heritage'
import { heritageProfile, levelOptions, craftOptions, loadHeritageProfile, saveHeritageProfile, addLog, authState, checkUploadFile, uploadLimitMb } from '@/store'

// profile 直接指向全局传承人资料，预览区因此能实时反映修改
const profile = heritageProfile

// 编辑表单：craft 在表单中用数组保存，提交时再拼回以“·”分隔的字符串
const form = reactive({
  name: profile.name,
  level: profile.level,
  craft: profile.craft ? profile.craft.split('·') : [],
  region: profile.region,
  phone: profile.phone,
  mentor: profile.mentor,
  years: profile.years,
  intro: profile.intro,
  honor: profile.honor,
  bio: profile.bio,
})

// 预览头像的背景样式：有头像时用图片填充，否则返回空对象显示占位文字
const avatarStyle = computed(() => (profile.avatar ? { backgroundImage: 'url(' + profile.avatar + ')' } : {}))

// 证书附件允许的大小上限（MB），取系统上传配置与 20MB 的较小值
const docMaxMb = computed(() => uploadLimitMb(20))

/* 头像上传流程：校验文件 → 读取为 DataURL → 先更新预览 → 保存失败则回滚 */
async function onAvatarUpload(file) {
  const err = checkUploadFile(file, { name: '头像', fallbackMb: 5 })
  if (err) {
    ElMessage.error(err)
    return false
  }
  let dataUrl = ''
  try {
    dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = () => reject(new Error('图片读取失败'))
      reader.readAsDataURL(file)
    })
  } catch (e) {
    ElMessage.error(e.message || '图片读取失败')
    return false
  }
  const prev = profile.avatar
  profile.avatar = dataUrl
  const res = await saveHeritageProfile({ avatar: dataUrl })
  if (res.ok) {
    ElMessage.success('头像已更新')
  } else {
    profile.avatar = prev
    ElMessage.error(res.msg || '头像保存失败')
  }
  return false
}

/* 移除头像：先清空预览，保存失败时恢复原来的头像 */
async function removeAvatar() {
  const prev = profile.avatar
  profile.avatar = ''
  const res = await saveHeritageProfile({ avatar: '' })
  if (res.ok) {
    ElMessage.success('已移除头像')
  } else {
    profile.avatar = prev
    ElMessage.error(res.msg || '移除失败')
  }
}

/* 当前操作人名称，用于写操作日志 */
function operator() {
  return authState.user?.name || '传承人'
}

/* 把证书列表持久化到传承人档案；未开通公开主页时提示并返回 false */
async function persistCerts(list) {
  if (!heritageProfile.profileId) {
    ElMessage.warning('尚未开通公开主页，无法保存证书附件')
    return false
  }
  try {
    await apiUpdateInheritor(heritageProfile.profileId, { cert_files: list })
    return true
  } catch (e) {
    ElMessage.error('保存失败：' + ((e && e.message) || '网络错误'))
    return false
  }
}

/* 证书上传流程：校验 → 上传附件 → 合并到现有列表 → 持久化并写日志 */
async function onCertUpload(file) {
  const err = checkUploadFile(file, { name: '证书附件', fallbackMb: 20 })
  if (err) {
    ElMessage.error(err)
    return false
  }
  try {
    const res = await apiUploadCert(file)
    const next = heritageProfile.certs.concat([{ name: res.name || file.name, url: res.url }])
    if (await persistCerts(next)) {
      heritageProfile.certs = next
      addLog('update', operator(), '更新荣誉证书', `上传证书附件「${res.name || file.name}」`)
      ElMessage.success('证书已上传')
    }
  } catch (e) {
    ElMessage.error('上传失败：' + ((e && e.message) || '网络错误'))
  }
  return false
}

/* 移除指定下标的证书：复制列表后删除一项，持久化成功才更新页面 */
async function removeCert(i) {
  const next = heritageProfile.certs.slice()
  next.splice(i, 1)
  if (await persistCerts(next)) {
    heritageProfile.certs = next
    addLog('update', operator(), '更新荣誉证书', '移除了证书附件')
    ElMessage.success('已移除')
  }
}

/* 保存主页：校验姓名与电话格式 → 组装提交数据 → 成功后同步全局资料并写日志 */
async function save() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写姓名')
    return
  }
  const phone = (form.phone || '').trim()
  if (phone && !/^[0-9\-\*]{7,20}$/.test(phone)) {
    ElMessage.warning('联系电话格式不正确（仅支持数字，可用 - 或 * 脱敏）')
    return
  }
  const payload = {
    name: form.name.trim(),
    level: form.level,
    craft: form.craft.join('·'),
    region: form.region.trim(),
    phone: form.phone.trim(),
    mentor: (form.mentor || '').trim(),
    years: form.years,
    intro: form.intro.trim(),
    honor: form.honor.trim(),
    bio: form.bio.trim(),
    avatar: profile.avatar,
  }
  const res = await saveHeritageProfile(payload)
  if (res.ok) {
    profile.name = payload.name
    profile.level = payload.level
    profile.craft = payload.craft
    profile.region = payload.region
    profile.phone = payload.phone
    profile.mentor = payload.mentor
    profile.years = payload.years
    profile.intro = payload.intro
    profile.honor = payload.honor
    profile.bio = payload.bio
    addLog('update', operator(), '修改个人主页', `更新了「${payload.name || '传承人'}」的主页资料`)
    ElMessage.success('主页已保存')
  } else {
    ElMessage.error(res.msg || '保存失败')
  }
}

/* 页面挂载时加载最新主页资料，并回填到编辑表单 */
onMounted(async () => {
  await loadHeritageProfile()
  form.name = profile.name
  form.level = profile.level
  form.craft = profile.craft ? profile.craft.split('·') : []
  form.region = profile.region
  form.phone = profile.phone
  form.mentor = profile.mentor
  form.years = profile.years
  form.intro = profile.intro
  form.honor = profile.honor
  form.bio = profile.bio
})

/* 重置表单：从当前已保存的 profile 重新填充所有字段 */
function resetForm() {
  form.name = profile.name
  form.level = profile.level
  form.craft = profile.craft ? profile.craft.split('·') : []
  form.region = profile.region
  form.phone = profile.phone
  form.mentor = profile.mentor
  form.years = profile.years
  form.intro = profile.intro
  form.honor = profile.honor
  form.bio = profile.bio
  ElMessage.info('已还原为当前保存内容')
}
</script>

<style src="./ConsoleProfile.css"></style>
