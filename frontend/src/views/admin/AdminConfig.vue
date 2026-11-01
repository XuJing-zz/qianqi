<!-- AdminConfig.vue 系统配置页：维护平台基础信息、上传限制、首页展示内容，并提供数据初始化入口。 -->
<template>
  <AdminLayout>
    <div class="acf-wrap">
      <!-- 页头区：页面标题与说明 -->
      <div class="acf-head">
        <div class="acf-head-left">
          <h2 class="acf-title">系统配置</h2>
          <p class="acf-sub">管理员 · 平台基础运行参数</p>
        </div>
      </div>

      <!-- 基础信息区：系统名称、LOGO、公告与备案号 -->
      <div class="acf-card">
        <div class="acf-card-head">
          <h3 class="acf-card-title">基础信息</h3>
        </div>
        <div class="acf-form">
          <label class="acf-form-row">
            <span class="acf-form-label">系统名称</span>
            <el-input v-model="form.systemName" placeholder="系统名称" />
          </label>
          <div class="acf-form-row">
            <span class="acf-form-label">系统 LOGO</span>
            <!-- LOGO 上传区：优先显示图片，未上传时回退为单字印章 -->
            <div class="acf-logo">
              <div class="acf-logo-preview">
                <img v-if="form.logoUrl" :src="form.logoUrl" alt="LOGO" class="acf-logo-img" />
                <span v-else class="acf-logo-fallback">{{ form.logoText || '漆' }}</span>
              </div>
              <div class="acf-logo-ops">
                <button class="acf-logo-btn" :disabled="logoUploading" @click="pickLogo">
                  {{ logoUploading ? '上传中…' : '上传 LOGO 图片' }}
                </button>
                <button v-if="form.logoUrl" class="acf-logo-btn acf-logo-btn-clear" @click="dropLogo">移除图片</button>
                <span class="acf-logo-tip">支持 jpg / png / webp 等，建议正方形，不超过 5MB；数据落 MEDIA，实时同步到用户端顶部、登录页与两端工作站</span>
              </div>
              <input ref="logoInput" type="file" accept="image/*" class="acf-file-hidden" @change="onLogoChange" />
            </div>
          </div>
          <label class="acf-form-row">
            <span class="acf-form-label">Logo 文字</span>
            <el-input v-model="form.logoText" placeholder="未上传图片时的单字印章，如「漆」" maxlength="2" style="width: 160px" />
          </label>
          <label class="acf-form-row">
            <span class="acf-form-label">首页公告</span>
            <el-input v-model="form.homeNotice" type="textarea" :rows="2" placeholder="首页顶部公告文案" />
          </label>
          <label class="acf-form-row">
            <span class="acf-form-label">备案号</span>
            <el-input v-model="form.icp" placeholder="ICP 备案号" />
          </label>
        </div>
      </div>

      <!-- 上传限制区：单文件大小、图片数量与视频/文档开关，保存后对全站生效 -->
      <div class="acf-card">
        <div class="acf-card-head">
          <h3 class="acf-card-title">上传限制</h3>
        </div>
        <div class="acf-form">
          <p class="acf-limit-note">
            以下参数对全站上传实时生效（课程视频、课程封面、技艺图片与附件、荣誉证书、作品照片、头像、系统 LOGO）：
            单文件上限由后端统一校验，图片数上限作用于各处选图入口；关闭「允许上传」后，对应类型的文件前后端都会拒绝。
          </p>
          <label class="acf-form-row">
            <span class="acf-form-label">单文件上限</span>
            <el-input-number v-model="form.uploadMaxSize" :min="1" :max="500" />
            <span class="acf-unit">MB</span>
          </label>
          <label class="acf-form-row">
            <span class="acf-form-label">图片数上限</span>
            <el-input-number v-model="form.uploadMaxCount" :min="1" :max="20" />
            <span class="acf-unit">张</span>
          </label>
          <div class="acf-form-row">
            <span class="acf-form-label">允许上传</span>
            <el-checkbox v-model="form.allowVideo">视频</el-checkbox>
            <el-checkbox v-model="form.allowDoc">文档</el-checkbox>
          </div>
        </div>
      </div>

      <!-- 首页内容配置区：勾选要在普通用户首页展示的技艺档案与传承人 -->
      <div class="acf-card">
        <div class="acf-card-head">
          <h3 class="acf-card-title">首页内容配置</h3>
          <p class="acf-card-tip">控制普通用户端首页展示哪些内容，勾选后保存立即生效</p>
        </div>
        <div class="acf-form">
          <div class="acf-form-row acf-form-col">
            <span class="acf-form-label">技艺档案</span>
            <div class="acf-options">
              <el-checkbox-group v-model="homeForm.archives">
                <el-checkbox v-for="s in approvedSkills" :key="s.id" :value="s.id">
                  {{ s.name }}<em class="acf-opt-sub">（{{ s.level }} · {{ s.region }}）</em>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
          <div class="acf-form-row acf-form-col">
            <span class="acf-form-label">匠心传人</span>
            <div class="acf-options">
              <el-checkbox-group v-model="homeForm.masters">
                <el-checkbox v-for="m in activeInheritors" :key="m.id" :value="m.id">
                  {{ m.name }}<em class="acf-opt-sub">（{{ m.level }} · {{ m.craft }}）</em>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程与作品展示区：配置「本周精选」课程与作品轮播图 -->
      <div class="acf-card">
        <div class="acf-card-head">
          <h3 class="acf-card-title">课程与作品展示</h3>
          <p class="acf-card-tip">控制培训课程页「本周精选」、文创作品页「轮播图」的内容</p>
        </div>
        <div class="acf-form">
          <div class="acf-form-row acf-form-col">
            <span class="acf-form-label">本周精选课程</span>
            <div class="acf-options">
              <el-select
                v-model="featuredCourseId"
                placeholder="选择一门课程作为本周精选"
                style="width: 100%"
              >
                <el-option
                  v-for="c in coursePool"
                  :key="c.id"
                  :label="c.name + '（' + c.craft + ' · ' + c.teacher + '）'"
                  :value="c.id"
                />
              </el-select>
            </div>
          </div>
          <div class="acf-form-row acf-form-col">
            <span class="acf-form-label">作品轮播图</span>
            <div class="acf-options">
              <el-checkbox-group v-model="homeForm.featuredProducts">
                <el-checkbox v-for="p in productPool" :key="p.id" :value="p.id">
                  {{ p.name }}<em class="acf-opt-sub">（{{ p.craft }} · {{ p.inheritor }}）</em>
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据初始化区（危险操作）：清空业务数据并按内置 seed 重建演示数据 -->
      <div class="acf-card acf-card-danger">
        <div class="acf-card-head">
          <h3 class="acf-card-title">数据初始化</h3>
          <p class="acf-card-tip">清空全部业务数据与账号，按内置 seed 重建初始演示数据</p>
        </div>
        <div class="acf-init-body">
          <p class="acf-init-warn">
            ⚠ 此操作将删除当前全部订单 / 报名 / 留言 / 日志 / 账号等数据并重建为出厂演示数据
            （admin / heritage01 / user01，密码均为 123456），完成后需重新登录。约需 1-2 分钟，期间请勿刷新。
          </p>
          <button class="acf-init-btn" @click="doInit">立即执行数据初始化</button>
        </div>
      </div>

      <!-- 底部操作区：保存会把配置同步到服务器；恢复默认只改本地表单，需再保存才生效 -->
      <div class="acf-actions">
        <button class="acf-btn acf-btn-save" @click="save">保存配置</button>
        <button class="acf-btn acf-btn-reset" @click="reset">恢复默认</button>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
/* 系统配置组件：本地表单与全局 systemConfig / homeConfig 双向同步；
   保存时先更新全局状态再提交服务器，LOGO 上传单独走文件接口，数据初始化会重建全部演示数据。 */
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { initData } from '@/api/system'
import { systemConfig, homeConfig, heritageSkills, loadSkills, inheritors, loadInheritors, courses, ensureCourses, heritageProducts, loadProducts, addLog, authState, loadConfig, saveConfigRemote, uploadSystemLogo, clearSystemLogo, checkUploadFile } from '@/store'

// 表单副本：form 供页面编辑，defaults 保存进入页面时的初始值供「恢复默认」使用
const form = reactive({ ...systemConfig })
const defaults = { ...systemConfig }

// 首页展示内容表单副本：数组复制一份，避免直接改动全局配置
const homeForm = reactive({
  archives: [...homeConfig.archives],
  masters: [...homeConfig.masters],
  featuredProducts: [...homeConfig.featuredProducts],
})
// 首页配置的初始快照，供「恢复默认」还原
const homeDefaults = {
  archives: [...homeConfig.archives],
  masters: [...homeConfig.masters],
  featuredProducts: [...homeConfig.featuredProducts],
}
// 恢复默认时使用的本周精选课程 ID
const defaultFeaturedCourse = 1

// 候选池：首页只能挑选已通过审核的档案、启用中的传承人、已通过的作品
const approvedSkills = computed(() => heritageSkills.filter((s) => s.status === 'approved'))
// 启用中的传承人候选
const activeInheritors = computed(() => inheritors.filter((m) => m.status === 'active'))
// 课程候选（全部课程）；作品候选仅保留已通过审核的作品
const coursePool = computed(() => courses)
const productPool = computed(() => heritageProducts.filter((p) => p.status === 'approved'))

// 本周精选课程：单独用 ref 绑定下拉框，保存时写回 homeConfig
const featuredCourseId = ref(homeConfig.featuredCourses)

// 取当前登录管理员姓名，写入配置变更日志
function operator() {
  return authState.user?.name || '管理员'
}

// LOGO 上传状态：logoInput 指向隐藏的 file input，logoUploading 控制按钮禁用
const logoInput = ref(null)
const logoUploading = ref(false)

// 点击自定义按钮时，触发隐藏的 file input 选择图片
function pickLogo() {
  logoInput.value && logoInput.value.click()
}

/* 选择 LOGO 后的处理：
   校验图片类型（image/*）与系统配置的大小上限，通过后立即上传；
   上传成功只更新表单中的 logoUrl，仍需点「保存配置」才全站生效。 */
async function onLogoChange(e) {
  const file = e.target.files && e.target.files[0]
  e.target.value = ''
  if (!file) return
  if (!/^image\//.test(file.type)) {
    ElMessage.warning('请选择图片文件（jpg / png / webp 等）')
    return
  }
  const limitErr = checkUploadFile(file, { name: 'LOGO 图片', fallbackMb: 5 })
  if (limitErr) {
    ElMessage.warning(limitErr)
    return
  }
  logoUploading.value = true
  try {
    const url = await uploadSystemLogo(file)
    form.logoUrl = url
    addLog('update', operator(), '上传系统LOGO', `LOGO 图片「${file.name}」已上传，点击保存后全站生效`)
    ElMessage.success('LOGO 已上传，点「保存配置」后全站生效')
  } catch (err) {
    ElMessage.error((err.data && (err.data.detail || err.data.msg)) || (err && err.message) || '上传失败')
  } finally {
    logoUploading.value = false
  }
}

// 移除 LOGO 图片，界面回退为 Logo 文字印章
function dropLogo() {
  clearSystemLogo()
  form.logoUrl = ''
  ElMessage.success('已移除 LOGO 图片，将回退显示 Logo 文字；点「保存配置」后全站生效')
}

/* 页面初始化：
   先并行预加载作品、课程、技艺档案与传承人（供各候选池使用），
   再从服务器读取配置，并用返回结果覆盖两张表单；读取失败时保留默认值。 */
onMounted(async () => {
  Promise.all([loadProducts().catch(() => {}), ensureCourses().catch(() => {}), loadSkills().catch(() => {}), loadInheritors().catch(() => {})])
  try {
    await loadConfig()
    Object.assign(form, systemConfig)
    homeForm.archives = [...homeConfig.archives]
    homeForm.masters = [...homeConfig.masters]
    homeForm.featuredProducts = [...homeConfig.featuredProducts]
    featuredCourseId.value = homeConfig.featuredCourses
  } catch (e) {
  }
})

/* 保存配置：
   先把表单值写回全局 systemConfig / homeConfig，再调用 saveConfigRemote 提交服务器；
   提交失败时提示「仅保存在本地」，成功才记录操作日志。 */
async function save() {
  Object.assign(systemConfig, form)
  homeConfig.archives = [...homeForm.archives]
  homeConfig.masters = [...homeForm.masters]
  homeConfig.featuredCourses = featuredCourseId.value
  homeConfig.featuredProducts = [...homeForm.featuredProducts]
  try {
    await saveConfigRemote()
  } catch (e) {
    ElMessage.error('配置保存到服务器失败，已保存在本地')
    return
  }
  addLog('update', operator(), '修改系统配置', '更新了系统运行参数与用户端展示内容')
  ElMessage.success('配置已保存')
}

/* 数据初始化（危险操作）：
   必须先通过确认框；执行期间展示不可自动关闭的提示，完成后弹窗告知新账号，
   跳转登录页重新登录。用户取消确认时直接返回，不发起请求。 */
async function doInit() {
  try {
    await ElMessageBox.confirm(
      '数据初始化将清空并重建全部演示数据（含账号），完成后需重新登录。确认执行吗？',
      '数据初始化',
      { confirmButtonText: '执行初始化', cancelButtonText: '取消', type: 'error', confirmButtonClass: 'el-button--danger' },
    )
  } catch (e) { return }
  try {
    ElMessage({ type: 'info', message: '正在初始化演示数据（约 1-2 分钟），请勿刷新…', duration: 0 })
    const res = await initData()
    ElMessage({ type: 'success', message: res.msg || '初始化完成', duration: 0 })
    ElMessageBox.alert(
      '演示数据已重建。账号已重置（admin / heritage01 / user01，密码均为 123456），请重新登录。',
      '初始化完成',
      { confirmButtonText: '去登录', type: 'success' },
    ).then(() => { location.href = '/login' }).catch(() => { location.href = '/login' })
  } catch (e) {
    ElMessage({ type: 'error', message: '初始化失败：' + ((e && e.message) || '未知错误') })
  }
}

// 恢复默认：把两张表单还原为进入页面时的快照，仅改本地，点「保存配置」后才生效
function reset() {
  ElMessageBox.confirm('确定恢复为默认配置吗？', '恢复默认', {
    confirmButtonText: '恢复',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      Object.assign(form, defaults)
      Object.assign(homeForm, {
        archives: [...homeDefaults.archives],
        masters: [...homeDefaults.masters],
        featuredProducts: [...homeDefaults.featuredProducts],
      })
      featuredCourseId.value = defaultFeaturedCourse
      ElMessage.success('已恢复默认（尚未保存，点击保存后生效）')
    })
    .catch(() => {})
}
</script>

<style src="./AdminConfig.css"></style>

<style scoped>
/* LOGO 预览与操作按钮横向排列，窄屏时自动换行 */
.acf-logo { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
/* 固定尺寸的 LOGO 预览框，图片按 contain 完整显示 */
.acf-logo-preview {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border: 1px solid #e6dccf;
  border-radius: 8px;
  background: #faf7f2;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.acf-logo-img { width: 100%; height: 100%; object-fit: contain; display: block; }
.acf-logo-fallback {
  font-size: 26px;
  color: #8b2e1c;
  letter-spacing: 0;
  font-family: 'STKaiti', 'KaiTi', serif;
}
.acf-logo-ops { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.acf-logo-btn {
  font-size: 13px;
  padding: 7px 14px;
  border: 1px solid #d9cdbb;
  background: #fff;
  color: #6b5a44;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.acf-logo-btn:hover:not(:disabled) { border-color: #8b2e1c; color: #8b2e1c; }
.acf-logo-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.acf-logo-btn-clear:hover { border-color: #c62828; color: #c62828; }
.acf-logo-tip { font-size: 12px; color: #a8937a; line-height: 1.6; flex: 1 1 240px; }
/* 隐藏原生 file input，由「上传 LOGO 图片」按钮代为触发 */
.acf-file-hidden { display: none; }
.acf-limit-note {
  margin: 0 0 4px;
  font-size: 12px;
  line-height: 1.7;
  color: #a8937a;
}
/* 危险操作卡片：红色边框与浅红背景，和普通配置区区分 */
.acf-card-danger { border: 1px solid #d8a0a0 !important; background: #fff8f6 !important; }
.acf-card-danger .acf-card-title { color: #c62828 !important; }
.acf-init-body { display: flex; flex-direction: column; gap: 14px; }
/* 初始化警告文案：虚框强调，提示操作影响范围 */
.acf-init-warn {
  margin: 0;
  font-size: 13px;
  line-height: 1.8;
  color: #8d4b4b;
  background: #fdf0ec;
  border: 1px dashed #e0b0a4;
  border-radius: 6px;
  padding: 10px 14px;
}
/* 初始化按钮：红色实心，悬停反白，强化危险操作提示 */
.acf-init-btn {
  align-self: flex-start;
  padding: 9px 22px;
  background: #c62828;
  border: 1px solid #c62828;
  color: #fff;
  font-size: 14px;
  letter-spacing: 2px;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s ease;
}
.acf-init-btn:hover { background: #fff; color: #c62828; }
</style>
