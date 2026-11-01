<!-- 管理员传承人管理页面：维护传承人人才库，支持筛选、新增/编辑资料、上传证书、在职/离岗切换与删除。 -->
<template>
  <AdminLayout>
    <div class="aih-wrap">
      <div class="aih-head">
        <div class="aih-head-left">
          <h2 class="aih-title">传承人管理</h2>
          <p class="aih-sub">共 {{ total }} 名传承人，维护传承人人才库</p>
        </div>
        <button class="aih-add-btn" @click="openAdd">＋ 新增传承人</button>
      </div>

      <!-- 筛选区：按姓名/技艺/师承搜索，并按传承等级与在职状态过滤 -->
      <div class="aih-filter">
        <el-input v-model="keyword" placeholder="搜索姓名 / 技艺 / 师承" clearable style="width: 220px" />
        <el-select v-model="levelFilter" placeholder="传承等级" clearable style="width: 140px">
          <el-option v-for="l in inheritorLevels" :key="l" :label="l" :value="l" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px">
          <el-option label="在职" value="active" />
          <el-option label="离岗" value="leave" />
        </el-select>
      </div>

      <!-- 传承人列表区：卡片展示基本信息、账号开通状态、师承荣誉与操作按钮 -->
      <div v-if="loading" class="aih-loading">加载中…</div>
      <div v-else-if="rows.length" class="aih-list">
        <div v-for="p in rows" :key="p.id" class="aih-card">
          <div class="aih-avatar">{{ p.name.charAt(0) }}</div>
          <div class="aih-body">
            <div class="aih-body-top">
              <h3 class="aih-name">{{ p.name }}</h3>
              <span class="aih-badge" :style="{ color: statusMap[p.status].color, borderColor: statusMap[p.status].color }">
                {{ statusMap[p.status].label }}
              </span>
            </div>
            <div class="aih-meta">
              <span class="aih-meta-item">{{ p.gender }} · {{ p.age }}岁</span>
              <span class="aih-meta-item">{{ p.level }}</span>
              <span class="aih-meta-item">擅长 {{ p.craft }}</span>
              <span class="aih-meta-item">从艺 {{ p.years }} 年</span>
              <span v-if="accountOf(p)" class="aih-account-tag" :style="{ color: '#1e6fb8', borderColor: '#8fb8d8' }">@{{ accountOf(p) }}</span>
              <span v-else class="aih-account-tag" :style="{ color: '#a8937a', borderColor: '#cbb594' }">未开通账号</span>
            </div>
            <div class="aih-meta">
              <span class="aih-meta-item">师承：{{ p.mentor || '—' }}</span>
              <span class="aih-meta-item">{{ p.phone }}</span>
            </div>
            <p class="aih-intro">{{ p.intro }}</p>
            <div v-if="p.honors" class="aih-honors">
              <span class="aih-honors-label">荣誉：</span>{{ p.honors }}
            </div>
            <div v-if="Array.isArray(p.cert_files) && p.cert_files.length" class="aih-honors aih-certs-count">
              <span class="aih-honors-label">证书：</span>{{ p.cert_files.length }} 份附件
            </div>
            <div class="aih-actions">
              <button class="aih-btn" @click="openEdit(p)">编辑资料</button>
              <button class="aih-btn" @click="toggleStatus(p)">{{ p.status === 'active' ? '设为离岗' : '设为在职' }}</button>
              <button class="aih-btn aih-btn-del" @click="remove(p)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="aih-empty">
        <span class="aih-empty-glyph">人</span>
        <p class="aih-empty-text">暂无传承人</p>
      </div>

      <!-- 分页区：传承人数量超过一页时显示 -->
      <div v-if="total > pageSize" class="aih-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>

    <!-- 弹窗区：新增 / 编辑传承人资料，包含基本资料、技艺师承、荣誉证书附件与简介 -->
    <el-dialog v-model="dialog" :title="editingId ? '编辑传承人' : '新增传承人'" width="min(640px, calc(100vw - 32px))" :close-on-click-modal="false">
      <div class="aih-form">
        <div class="aih-form-grid">
          <label class="aih-form-field">
            <span class="aih-form-label">姓名 *</span>
            <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" />
          </label>
          <label class="aih-form-field">
            <span class="aih-form-label">性别</span>
            <el-select v-model="form.gender" style="width: 100%">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </label>
          <label class="aih-form-field">
            <span class="aih-form-label">年龄</span>
            <el-input-number v-model="form.age" :min="16" :max="100" style="width: 100%" />
          </label>
          <label class="aih-form-field">
            <span class="aih-form-label">联系方式</span>
            <el-input v-model="form.phone" placeholder="手机号（选填）" maxlength="20" />
          </label>
          <label class="aih-form-field">
            <span class="aih-form-label">传承等级</span>
            <el-select v-model="form.level" style="width: 100%">
              <el-option v-for="l in inheritorLevels" :key="l" :label="l" :value="l" />
            </el-select>
          </label>
          <label class="aih-form-field">
            <span class="aih-form-label">从艺年限</span>
            <el-input-number v-model="form.years" :min="0" :max="80" style="width: 100%" />
          </label>
          <label class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">代表技艺</span>
            <el-select v-model="form.craft" multiple filterable allow-create style="width: 100%" placeholder="可多选或输入">
              <el-option v-for="c in inheritorCrafts" :key="c" :label="c" :value="c" />
            </el-select>
          </label>
          <label class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">师承关系</span>
            <el-input v-model="form.mentor" placeholder="如：师承漆艺大师王老" />
          </label>
          <label class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">教学资质</span>
            <el-input v-model="form.qual" placeholder="如：省级非遗代表性传承人" />
          </label>
          <label class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">所获荣誉（｜分隔）</span>
            <el-input v-model="form.honors" placeholder="如：作品入藏国家博物馆｜非遗金奖" />
          </label>
          <div class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">荣誉证书附件</span>
            <div class="aih-certs">
              <div v-for="(c, i) in form.certs" :key="i" class="aih-cert">
                <span class="aih-cert-icon">📄</span>
                <span class="aih-cert-name">{{ c.name }}</span>
                <el-button text size="small" type="danger" @click="removeCert(i)">移除</el-button>
              </div>
              <el-upload
                class="aih-cert-upload"
                :show-file-list="false"
                :before-upload="onCertUpload"
                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip"
              >
                <el-button size="small" plain>＋ 上传证书</el-button>
              </el-upload>
            </div>
            <p class="aih-cert-hint">支持图片、PDF、Word、Excel 等，单文件 ≤ 20MB；保存后随档案一同入库</p>
          </div>
          <label class="aih-form-field aih-form-field-full">
            <span class="aih-form-label">个人简介</span>
            <el-input v-model="form.intro" type="textarea" :rows="3" placeholder="个人简介" />
          </label>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="confirm">保存</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { apiListInheritors, apiUploadCert } from '@/api/heritage'
import {
  inheritorLevels,
  inheritorCrafts,
  inheritorStatusMap,
  addInheritor,
  updateInheritor,
  removeInheritor,
  toggleInheritorStatus,
  addLog,
  authState,
  checkUploadFile,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 传承人状态配置（在职/离岗的标签与颜色），来自 store
const statusMap = inheritorStatusMap

const keyword = ref('') // 搜索关键字（姓名 / 技艺 / 师承）
const levelFilter = ref('') // 传承等级筛选，空串表示不限
const statusFilter = ref('') // 在职状态筛选：active 在职、leave 离岗


// 兼容后端 snake_case 与前端 camelCase 两种账号字段命名
function mapProfileRow(p) {
  return { ...p, accountId: p.account_id ?? (p.accountId ?? null), accountUsername: p.account_username ?? (p.accountUsername ?? '') }
}

/* 分页列表：usePagedList 统一管理分页状态；
   fetchPage 按关键字请求传承人，等级与状态仅在已选择时才加入查询参数。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapProfileRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: keyword.value.trim() }
    if (levelFilter.value) params.level = levelFilter.value
    if (statusFilter.value) params.status = statusFilter.value
    return apiListInheritors(params)
  },
})

// 首次进入页面时加载传承人列表
onMounted(loadRows)
// 等级或状态变化时立即回到第一页重新查询
watch([levelFilter, statusFilter], onFilter)
let kwTimer = null // 关键字防抖定时器
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300) // 停止输入 300ms 后再查询
})

// 操作人名称：写入操作日志时使用，取不到登录用户时兜底为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 返回该传承人已绑定的账号名，未开通账号时返回 null
function accountOf(p) {
  return p.accountUsername || null
}

const dialog = ref(false) // 资料弹窗是否显示
const editingId = ref(null) // 编辑中的传承人 id，null 表示新增
// 表单数据：craft 用数组保存多选技艺，cert_files 保存已上传的证书附件
const form = reactive({
  name: '', gender: '男', age: 40, phone: '', level: '市级', years: 10,
  craft: [], mentor: '', qual: '', honors: '', intro: '', certs: [],
})

// 清空表单，恢复为新增传承人的默认值
function resetForm() {
  Object.assign(form, {
    name: '', gender: '男', age: 40, phone: '', level: '市级', years: 10,
    craft: [], mentor: '', qual: '', honors: '', intro: '', certs: [],
  })
}

// 把后端用“·”拼接的技艺字符串还原为数组，供多选下拉框回显
function craftToArray(v) {
  if (Array.isArray(v)) return v.slice()
  return String(v || '').split('·').map((s) => s.trim()).filter(Boolean)
}

/* 证书附件上传：先做大小/类型校验，再上传到服务器并暂存到表单，
   保存档案时附件随资料一起提交。before-upload 返回 false 可阻止组件自动上传。 */
async function onCertUpload(file) {
  const err = checkUploadFile(file, { name: '证书附件', fallbackMb: 20 })
  if (err) {
    ElMessage.error(err)
    return false
  }
  try {
    const res = await apiUploadCert(file)
    form.certs.push({ name: res.name || file.name, url: res.url })
    ElMessage.success('已上传，保存档案后生效')
  } catch (e) {
    ElMessage.error('上传失败：' + (e.message || '网络错误'))
  }
  return false
}

// 从待保存列表中移除一份证书附件
function removeCert(i) {
  form.certs.splice(i, 1)
}

// 打开“新增传承人”弹窗
function openAdd() {
  editingId.value = null
  resetForm()
  dialog.value = true
}

// 打开“编辑传承人”弹窗：把当前传承人资料回填到表单
function openEdit(p) {
  editingId.value = p.id
  Object.assign(form, {
    name: p.name || '',
    gender: p.gender || '男',
    age: p.age || 0,
    phone: p.phone || '',
    level: p.level || '市级',
    years: p.years || 0,
    craft: craftToArray(p.craft),
    mentor: p.mentor || '',
    qual: p.qual || '',
    honors: p.honors || '',
    intro: p.intro || '',
    certs: Array.isArray(p.cert_files) ? p.cert_files.slice() : [],
  })
  dialog.value = true
}

/* 保存传承人资料：校验姓名与手机号后组装 payload，
   有 editingId 走更新，否则走新增；成功后记录日志、关闭弹窗并刷新列表。 */
async function confirm() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写姓名')
    return
  }
  if (form.name.trim().length > 50) {
    ElMessage.warning('姓名不能超过 50 个字符')
    return
  }
  const phone = (form.phone || '').trim()
  if (phone && !/^[0-9\-\*]{7,20}$/.test(phone)) {
    ElMessage.warning('手机号格式不正确（仅支持数字，可用 - 或 * 脱敏）')
    return
  }
  // 多选技艺用“·”拼接成一个字符串，与后端存储格式保持一致
  const craftStr = Array.isArray(form.craft) ? form.craft.join('·') : form.craft
  const payload = {
    name: form.name.trim(), gender: form.gender, age: form.age, phone: form.phone,
    level: form.level, years: form.years, craft: craftStr,
    mentor: form.mentor, qual: form.qual, honors: form.honors, intro: form.intro,
    cert_files: form.certs.slice(),
  }
  const isEdit = !!editingId.value
  try {
    if (isEdit) {
      await updateInheritor(editingId.value, payload)
      addLog('update', operator(), '编辑传承人资料', `更新「${payload.name}」档案`)
      ElMessage.success('已保存')
    } else {
      await addInheritor(payload)
      addLog('create', operator(), '新增传承人', `「${payload.name}」已录入人才库`)
      ElMessage.success('已新增')
    }
    dialog.value = false
    editingId.value = null
    await loadRows()
  } catch (e) {
    ElMessage.error((isEdit ? '保存失败：' : '新增失败：') + (e.message || '网络错误'))
  }
}

/* 在职 / 离岗切换：变更前二次确认，成功后刷新列表。 */
function toggleStatus(p) {
  // 根据当前状态计算目标状态文案
  const target = p.status === 'active' ? '离岗' : '在职'
  ElMessageBox.confirm(`确定将「${p.name}」设为${target}吗？`, '状态变更', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await toggleInheritorStatus(p.id)
        addLog('update', operator(), '传承人状态变更', `「${p.name}」设为${target}`)
        ElMessage.success(`已设为${target}`)
        await loadRows()
      } catch (e) {
        ElMessage.error('操作失败：' + (e.message || '网络错误'))
      }
    })
    .catch(() => {})
}

/* 删除传承人：不可恢复，需二次确认。 */
function remove(p) {
  ElMessageBox.confirm(`确定删除传承人「${p.name}」吗？此操作不可恢复。`, '删除传承人', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'error',
  })
    .then(async () => {
      try {
        await removeInheritor(p.id)
        addLog('delete', operator(), '删除传承人', `「${p.name}」已删除`)
        ElMessage.success('已删除')
        await loadRows()
      } catch (e) {
        ElMessage.error('删除失败：' + (e.message || '网络错误'))
      }
    })
    .catch(() => {})
}
</script>

<style src="./AdminInheritors.css"></style>

<style scoped>
/* 加载提示、分页条与证书附件列表的基础布局 */
.aih-loading { padding: 40px 0; text-align: center; color: #8a93a3; }
.aih-pager { display: flex; justify-content: flex-end; margin-top: 18px; }
.aih-certs { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.aih-cert { display: flex; align-items: center; gap: 8px; background: #f7f0e4; border: 1px solid #e6d9c2; border-radius: 6px; padding: 6px 10px; }
.aih-cert-icon { font-size: 14px; }
.aih-cert-name { flex: 1; min-width: 0; font-size: 13px; color: #4a3b2a; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.aih-cert-hint { font-size: 12px; color: #a8937a; margin: 6px 0 0; }
.aih-certs-count { font-size: 13px; }
</style>
