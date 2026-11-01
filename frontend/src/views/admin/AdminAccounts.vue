<!-- 管理员账号管理页面：按身份选项卡分页展示账号，支持筛选、新增/编辑、发放传承人账号、启用/停用、重置密码与删除。 -->
<template>
  <AdminLayout>
    <div class="aac-wrap">
      <div class="aac-head">
        <div class="aac-head-left">
          <h2 class="aac-title">账号管理</h2>
          <p class="aac-sub">按身份分页展示账号，可新增/编辑账号、发放传承人账号、停用启用、重置密码、删除账号</p>
        </div>
        <div class="aac-head-actions">
          <!-- @click：@click 是 Vue 的事件绑定指令，用户点击元素时执行等号后的方法或表达式。 -->
          <button class="aac-add-btn aac-add-btn-ghost" @click="openIssueHeritage">＋ 发放传承人账号</button>
          <button class="aac-add-btn" @click="openAdd">＋ 新增账号</button>
        </div>
      </div>

      <!-- 选项卡区：按身份（全部/管理员/传承人/学员）切换列表数据。 -->
      <div class="aac-tabs">
        <!-- v-for：v-for 是 Vue 的列表渲染指令，这里遍历 identTabs，为每种身份生成一个选项卡按钮。 -->
        <button
          v-for="t in identTabs"
          :key="t.key"
          class="aac-tab"
          :class="{ 'aac-tab-active': activeRole === t.key }"
          @click="activeRole = t.key"
        >
          {{ t.label }}<span v-if="tabCounts[t.key] != null" class="aac-tab-count">{{ tabCounts[t.key] }}</span>
        </button>
      </div>

      <!-- 筛选区：关键字与账号状态；条件变化后重新请求第一页数据。 -->
      <div class="aac-filter">
        <!-- v-model：v-model 是 Vue 的双向绑定指令，输入框的值与 keyword 变量实时同步（输入即更新变量，变量变化也会回显）。 -->
        <el-input v-model="keyword" placeholder="搜索用户名 / 姓名" clearable style="width: 220px" />
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px">
          <el-option label="正常" value="active" />
          <el-option label="停用" value="disabled" />
        </el-select>
        <span class="aac-filter-total">共 {{ total }} 条</span>
      </div>

      <!-- 表格区：表头 + 账号行；角色与状态用不同颜色标签区分。 -->
      <div v-if="loading" class="aac-loading">加载中…</div>
      <div v-else-if="rows.length" class="aac-table">
        <div class="aac-row aac-row-head">
          <span class="aac-col aac-col-name">账号</span>
          <span class="aac-col">姓名</span>
          <span class="aac-col">身份</span>
          <span class="aac-col">联系方式</span>
          <span class="aac-col">状态</span>
          <span class="aac-col">注册时间</span>
          <span class="aac-col aac-col-act">操作</span>
        </div>
        <div v-for="u in rows" :key="u.role + '-' + u.id" class="aac-row">
          <span class="aac-col aac-col-name">
            <span class="aac-avatar">{{ u.name.charAt(0) }}</span>
            <span class="aac-name-wrap">
              <span class="aac-name">{{ u.username }}</span>
              <span class="aac-id">ID {{ u.id }}</span>
            </span>
          </span>
          <span class="aac-col">{{ u.name }}</span>
          <span class="aac-col">
            <span class="aac-role" :style="{ color: roleMap[u.role].color, borderColor: roleMap[u.role].color }">
              {{ roleMap[u.role].label }}
            </span>
          </span>
          <span class="aac-col">{{ u.phone || '—' }}</span>
          <span class="aac-col">
            <span class="aac-status" :style="{ color: u.status === 'active' ? '#2e7d32' : '#9e9e9e' }">
              {{ u.status === 'active' ? '正常' : '停用' }}
            </span>
          </span>
          <span class="aac-col aac-col-time">{{ u.createdAt }}</span>
          <span class="aac-col aac-col-act">
            <button class="aac-btn" @click="openEdit(u)">编辑</button>
            <button class="aac-btn" @click="resetPwd(u)">重置密码</button>
            <button class="aac-btn aac-btn-toggle" @click="toggleStatus(u)">{{ u.status === 'active' ? '停用' : '启用' }}</button>
            <button class="aac-btn aac-btn-del" @click="removeRow(u)">删除</button>
          </span>
        </div>
      </div>

      <div v-else class="aac-empty">
        <span class="aac-empty-glyph">号</span>
        <p class="aac-empty-text">暂无账号</p>
      </div>

      <!-- 分页区：总数超过一页时才显示，切页时调用 onPage 重新加载。 -->
      <div v-if="total > pageSize" class="aac-pager">
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

    <!-- 弹窗区：新增账号 / 编辑账号 / 发放传承人账号共用同一表单，按模式切换标题与可编辑字段。 -->
    <el-dialog v-model="dialog" :title="dialogTitle" width="520px" :close-on-click-modal="false">
      <div class="aac-form">
        <label class="aac-form-row">
          <span class="aac-form-label">用户名 *</span>
          <el-input v-model="form.username" placeholder="登录用户名（3~30 位）" maxlength="30" />
        </label>
        <label class="aac-form-row">
          <span class="aac-form-label">姓名 *</span>
          <el-input v-model="form.name" placeholder="真实姓名" maxlength="50" />
        </label>
        <label class="aac-form-row" v-if="!editKey">
          <span class="aac-form-label">初始密码 *</span>
          <el-input v-model="form.password" placeholder="6~32 位，默认留空为 123456" show-password maxlength="32" />
        </label>
        <label class="aac-form-row">
          <span class="aac-form-label">身份 *</span>
          <el-select v-model="form.role" style="width: 100%" :disabled="issueMode || !!editKey">
            <el-option v-if="form.role === 'admin'" label="管理员" value="admin" />
            <el-option label="传承人" value="heritage" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </label>
        <label class="aac-form-row">
          <span class="aac-form-label">联系方式</span>
          <el-input v-model="form.phone" placeholder="手机号（选填）" maxlength="20" />
        </label>
        <p v-if="issueMode" class="aac-issue-tip">传承人账号开通后，档案信息（性别/年龄/师承/技艺等）由传承人登录后自行到「个人主页」补全。</p>
        <p v-else-if="editKey" class="aac-issue-tip">账号身份由其所在账号表决定，不支持在此修改；如需变更请删除后按新身份新建账号。</p>
      </div>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="confirm">保存</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listAccounts } from '@/api/accounts'
import { mapKeys } from '@/api/utils'
import {
  accountRoleMap,
  addAccount,
  toggleAccountStatus,
  updateAccountAction,
  resetPassword,
  removeAccount,
  issueHeritageAccount,
  addLog,
  authState,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 角色展示配置（标签、颜色），来自 store，用于表格中的身份标签与新增时的日志文案
const roleMap = accountRoleMap

// 身份选项卡配置：key 与后端 role 参数对应，all 表示不按角色过滤
const identTabs = [
  { key: 'all', label: '全部' },
  { key: 'admin', label: '管理员' },
  { key: 'heritage', label: '传承人' },
  { key: 'user', label: '学员' },
]
const activeRole = ref('all') // 当前选中的身份选项卡
const keyword = ref('') // 搜索关键字（用户名 / 姓名）
const statusFilter = ref('') // 状态筛选：active 正常、disabled 停用，空串表示全部

// 各身份选项卡的账号数量；null 表示数量加载失败，前端不显示该数字
const tabCounts = reactive({ all: null, admin: null, heritage: null, user: null })

// 把后端返回的 snake_case 字段转成前端驼峰字段，并补齐缺失字段
function mapUser(u) {
  const m = mapKeys(u)
  return { ...m, createdAt: m.createdAt || '' }
}

/* 分页列表：usePagedList 统一管理 rows/total/page/loading，
   fetchPage 在翻页或筛选时携带当前身份、状态、关键字向后端请求账号数据。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapUser,
  fetchPage: ({ page, page_size }) => listAccounts({
    role: activeRole.value,
    status: statusFilter.value || '',
    keyword: keyword.value.trim(),
    page,
    page_size,
  }),
})

/* 并行统计各身份的账号数量：每个身份只取 1 条数据以读取总数，
   某个身份请求失败时把数量置为 null，避免影响其他选项卡。 */
async function refreshTabCounts() {
  const out = { all: 0, admin: 0, heritage: 0, user: 0 }
  await Promise.all(
    identTabs.map(async (t) => {
      try {
        const res = await listAccounts({ role: t.key, page_size: 1 })
        out[t.key] = Array.isArray(res) ? res.length : res.count || 0
      } catch (e) {
        out[t.key] = null
      }
    }),
  )
  Object.assign(tabCounts, out)
}

// onMounted：onMounted 是 Vue 的生命周期钩子，组件挂载到页面后执行一次，这里用于首次加载列表与选项卡数量。
onMounted(() => {
  loadRows() // 加载当前筛选条件下的第一页账号
  refreshTabCounts() // 统计各身份选项卡的账号数量
})
// 身份或状态变化时立即回到第一页并重新查询
watch(activeRole, onFilter)
watch(statusFilter, onFilter)
let kwTimer = null // 关键字防抖定时器，避免每输入一个字符都发请求
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300) // 停止输入 300ms 后再查询
})

// 操作人名称：写入操作日志时使用，取不到登录用户时兜底为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

const dialog = ref(false) // 表单弹窗是否显示
const editKey = ref('') // 编辑目标的唯一键（角色-id），空串表示新增
const editRole = ref('') // 编辑目标的角色
const editId = ref(null) // 编辑目标的账号 id
const issueMode = ref(false) // 是否处于“发放传承人账号”模式
const dialogTitle = computed(() => {
  if (issueMode.value) return '发放传承人账号'
  return editKey.value ? '编辑账号' : '新增账号'
})
// 表单数据：新增时密码可留空，提交时默认使用 123456
const form = reactive({ username: '', name: '', password: '', role: 'user', phone: '' })

// 清空表单，恢复为新增账号的默认值
function resetForm() {
  Object.assign(form, { username: '', name: '', password: '', role: 'user', phone: '' })
}

// 打开“新增账号”弹窗：清空编辑标记并重置表单
function openAdd() {
  editKey.value = ''
  editRole.value = ''
  editId.value = null
  issueMode.value = false
  resetForm()
  dialog.value = true
}

// 打开“发放传承人账号”弹窗：角色锁定为 heritage，档案由传承人登录后自行补全
function openIssueHeritage() {
  editKey.value = ''
  editRole.value = ''
  editId.value = null
  issueMode.value = true
  resetForm()
  form.role = 'heritage'
  dialog.value = true
}

// 打开“编辑账号”弹窗：回填当前行数据，密码留空表示不修改
function openEdit(u) {
  editKey.value = u.role + '-' + u.id
  editRole.value = u.role
  editId.value = u.id
  issueMode.value = false
  Object.assign(form, { username: u.username, name: u.name, password: '', role: u.role, phone: u.phone || '' })
  dialog.value = true
}

/* 保存表单：先做前端校验，再按“编辑 / 发放传承人 / 新增”三种模式调用对应 action，
   成功后写操作日志、关闭弹窗并刷新列表与选项卡数量。 */
async function confirm() {
  const username = form.username.trim()
  const name = form.name.trim()
  if (!username || !name) {
    ElMessage.warning('请填写用户名和姓名')
    return
  }
  if (username.length < 3 || username.length > 30) {
    ElMessage.warning('用户名长度需为 3~30 位')
    return
  }
  if (!/^[\p{L}\p{N}_.@+-]+$/u.test(username)) {
    ElMessage.warning('用户名仅可包含字母、数字、下划线、中划线、点与中文，不能包含空格')
    return
  }
  if (name.length > 50) {
    ElMessage.warning('姓名不能超过 50 个字符')
    return
  }
  const phone = form.phone.trim()
  if (phone && !/^[0-9\-\*]{7,20}$/.test(phone)) {
    ElMessage.warning('手机号格式不正确（仅支持数字，可用 - 或 * 脱敏）')
    return
  }
  if (!editKey.value) {
    const pwd = form.password || ''
    if (pwd && (pwd.length < 6 || pwd.length > 32)) {
      ElMessage.warning('初始密码需为 6~32 位')
      return
    }
    if (pwd && pwd !== pwd.trim()) {
      ElMessage.warning('密码不能以空格开头或结尾')
      return
    }
    if (!pwd) {
      form.password = '123456'
    }
  }
  try {
    if (editKey.value) {
      // 编辑模式：在当前页数据中找到原账号后更新，账号身份不允许在此修改
      const u = rows.value.find((x) => x.role === editRole.value && x.id === editId.value)
      if (!u) {
        ElMessage.warning('账号不存在，请刷新后重试')
        return
      }
      const res = await updateAccountAction(u, {
        username: form.username.trim(),
        name: form.name.trim(),
        phone: form.phone.trim(),
      })
      if (!res.ok) {
        ElMessage.warning(res.msg)
        return
      }
      addLog('update', operator(), '更新账号', `账号「${form.username.trim()}」信息已更新`)
      ElMessage.success('已保存')
    } else if (issueMode.value) {
      // 发放传承人账号：只创建登录账号，性别/师承/技艺等档案由传承人自行完善
      const res = await issueHeritageAccount({
        username: form.username.trim(),
        password: form.password || '123456',
        name: form.name.trim(),
        phone: form.phone.trim(),
      })
      if (!res.ok) {
        ElMessage.warning(res.msg)
        return
      }
      addLog('create', operator(), '发放传承人账号', `传承人「${form.name.trim()}」账号已注册开通，档案待其自行完善`)
      ElMessage.success('传承人账号已注册开通')
      refreshTabCounts()
    } else {
      // 新增账号：按表单选择的身份创建
      const res = await addAccount({
        username: form.username.trim(),
        name: form.name.trim(),
        password: form.password || '123456',
        role: form.role,
        phone: form.phone.trim(),
      })
      if (!res.ok) {
        ElMessage.warning(res.msg)
        return
      }
      addLog('create', operator(), '新增账号', `账号「${form.username.trim()}」（${roleMap[form.role].label}）已创建`)
      ElMessage.success('已新增账号')
      refreshTabCounts()
    }
    dialog.value = false
    await loadRows() // 保存成功后刷新当前页数据
  } catch (e) {
    ElMessage.error((e && e.message) || '保存失败')
  }
}

/* 重置密码：二次确认后把密码重置为 123456，并写入操作日志。 */
function resetPwd(u) {
  ElMessageBox.confirm(`确定重置账号「${u.username}」的密码吗？新密码将默认为 123456。`, '重置密码', {
    confirmButtonText: '重置',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      const res = await resetPassword(u)
      if (res && res.ok) {
        addLog('update', operator(), '重置密码', `账号「${u.username}」密码已重置`)
        ElMessage.success('密码已重置为 123456')
      } else {
        ElMessage.error((res && res.msg) || '重置失败')
      }
    })
    .catch(() => {})
}

/* 删除账号：先确认；若账号名下仍有关联数据，后端返回 needConfirm，
   再展示影响范围让管理员二次确认，最终带 confirm 参数强制执行。 */
function removeRow(u) {
  ElMessageBox.confirm(
    `确定删除账号「${u.username}」吗？删除后该账号将无法登录，且不可恢复。`,
    '删除账号',
    { confirmButtonText: '删除', cancelButtonText: '取消', type: 'error' },
  )
    .then(async () => {
      let res = await removeAccount(u)
      // 有关联数据时，先告知影响范围并要求再次确认
      if (!res.ok && res.needConfirm) {
        const detail = (res.impact || []).map((i) => `${i.label} ${i.count} 条`).join('、') || '关联数据'
        try {
          await ElMessageBox.confirm(
            `该账号名下仍有 ${detail}。删除后这些记录会失去归属（档案/课程/作品本身保留，但不再关联该账号）。`,
            '确认删除',
            { confirmButtonText: '仍然删除', cancelButtonText: '取消', type: 'warning' },
          )
        } catch (e) {
          return
        }
        res = await removeAccount(u, { confirm: true })
      }
      if (!res.ok) {
        ElMessage.error(res.msg || '删除失败')
        return
      }
      addLog('delete', operator(), '删除账号', `账号「${u.username}」已删除`)
      ElMessage.success(res.msg || '已删除')
      await loadRows()
      refreshTabCounts()
    })
    .catch(() => {})
}

/* 启用 / 停用账号：停用后账号将无法登录，操作前二次确认。 */
function toggleStatus(u) {
  // 根据当前状态计算目标动作文案
  const target = u.status === 'active' ? '停用' : '启用'
  ElMessageBox.confirm(`确定${target}账号「${u.username}」吗？`, `${target}账号`, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await toggleAccountStatus(u)
        addLog('update', operator(), `${target}账号`, `账号「${u.username}」已${target}`)
        ElMessage.success(`已${target}`)
        await loadRows()
      } catch (e) {
        ElMessage.error((e && e.message) || `${target}失败`)
      }
    })
    .catch(() => {})
}
</script>

<style src="./AdminAccounts.css"></style>

<style scoped>
/* scoped：scoped 表示下面的样式只作用于当前组件，不会影响其他页面中的同名类名。 */
/* 身份选项卡：横向排列并允许换行，空间不足时自动折行 */
.aac-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin: 18px 0 6px;
}
.aac-tab {
  border: 1px solid #e2e6ea;
  background: #fff;
  color: #5b6472;
  border-radius: 999px;
  padding: 7px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.aac-tab:hover {
  border-color: #1e6fb8;
  color: #1e6fb8;
}
.aac-tab-active {
  background: #1e6fb8;
  border-color: #1e6fb8;
  color: #fff;
}
.aac-tab-count {
  font-size: 12px;
  opacity: 0.85;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 999px;
  padding: 0 7px;
  line-height: 16px;
}
.aac-tab:not(.aac-tab-active) .aac-tab-count {
  background: #eef1f5;
  color: #7a8393;
}
/* 筛选区与分页区的基础间距 */
.aac-filter {
  margin: 12px 0 16px;
}
.aac-filter-total {
  margin-left: 14px;
  color: #8a93a3;
  font-size: 13px;
}
.aac-loading {
  padding: 40px 0;
  text-align: center;
  color: #8a93a3;
}
.aac-pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
.aac-btn-del {
  color: #c62828;
  border-color: #e6bcbc;
}
.aac-btn-del:hover {
  background: #fdf3f3;
  border-color: #c62828;
}
</style>
