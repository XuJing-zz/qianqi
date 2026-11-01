<!-- 留言管理页：查看「联系我们」留言，支持筛选、填写回复、标记已处理与删除 -->
<template>
  <AdminLayout>
    <div class="amsg-wrap">
      <!-- 页头区：标题与页面说明 -->
      <div class="amsg-head">
        <div class="amsg-head-left">
          <h2 class="amsg-title">留言管理</h2>
          <p class="amsg-sub">来自「联系我们」页的留言，可在处理后填写回复</p>
        </div>
      </div>

      <!-- 筛选区：按称呼/联系方式/事项/内容搜索，并按处理状态过滤 -->
      <div class="amsg-filter">
        <el-input v-model="keyword" placeholder="搜索称呼 / 联系方式 / 事项 / 内容" clearable style="width: 280px" />
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 130px">
          <el-option label="待处理" value="new" />
          <el-option label="已处理" value="handled" />
        </el-select>
      </div>

      <!-- 列表区：每条留言展示状态、主题、来信人、时间、内容与已有回复 -->
      <div v-if="loading" class="amsg-loading">加载中…</div>
      <div v-else-if="rows.length" class="amsg-list">
        <div v-for="m in rows" :key="m.id" class="amsg-card" :class="{ 'amsg-card-handled': m.status === 'handled' }">
          <div class="amsg-top">
            <span
              class="amsg-status"
              :style="{ color: messageStatusMap[m.status].color, borderColor: messageStatusMap[m.status].color }"
            >
              {{ messageStatusMap[m.status].label }}
            </span>
            <span v-if="m.subject" class="amsg-subject">{{ m.subject }}</span>
            <span class="amsg-from">
              <span class="amsg-name">{{ m.name }}</span>
              <span class="amsg-contact">{{ m.contact }}</span>
            </span>
            <span class="amsg-time">{{ m.createdAt }}</span>
            <!-- 行内操作：进入处理/编辑回复状态，或直接删除该留言 -->
            <span class="amsg-actions">
              <button v-if="editingId !== m.id" class="amsg-btn" @click="startEdit(m)">
                {{ m.status === 'handled' ? '编辑回复' : '处理' }}
              </button>
              <button class="amsg-btn amsg-btn-del" @click="removeMsg(m)">删除</button>
            </span>
          </div>

          <p class="amsg-message">{{ m.message }}</p>

          <!-- 已处理留言的回复展示区 -->
          <div v-if="m.status === 'handled' && m.reply && editingId !== m.id" class="amsg-reply">
            <span class="amsg-reply-tag">回复</span>
            <span class="amsg-reply-text">{{ m.reply }}</span>
          </div>

          <!-- 回复编辑区：填写回复后保存，同时把留言标记为已处理 -->
          <div v-if="editingId === m.id" class="amsg-editor">
            <el-input
              v-model="draftReply"
              type="textarea"
              :rows="2"
              maxlength="500"
              show-word-limit
              placeholder="填写回复（选填，可直接标记已处理）"
            />
            <div class="amsg-editor-actions">
              <button class="amsg-btn amsg-btn-solid" :disabled="saving" @click="saveEdit(m)">
                {{ saving ? '保存中...' : '标记已处理并保存' }}
              </button>
              <button class="amsg-btn" :disabled="saving" @click="cancelEdit">取消</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态：没有符合筛选条件的留言时显示 -->
      <div v-else class="amsg-empty">
        <span class="amsg-empty-glyph">信</span>
        <p class="amsg-empty-text">暂无留言</p>
      </div>

      <!-- 分页区：总条数超过每页数量时显示分页器 -->
      <div v-if="total > pageSize" class="amsg-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import {
  messageStatusMap,
  handleMessageAction,
  removeMessageAction,
  addLog,
  authState,
} from '@/store'
import { usePagedList } from '@/composables/usePagedList'
import { listContactMessages } from '@/api/contact'

// 筛选条件：关键字（称呼/联系方式/事项/内容）与处理状态
const keyword = ref('')
const statusFilter = ref('')


/* 整理一条留言：缺失字段兜底为空串，状态默认按待处理（new）展示，
   创建时间兼容后端的 created_at 字段。 */
function mapMsgRow(m) {
  return { id: m.id, name: m.name || '', contact: m.contact || '', subject: m.subject || '', message: m.message || '', status: m.status || 'new', reply: m.reply || '', createdAt: m.created_at || '' }
}

/* 分页加载留言：每次按页码、每页条数、关键字与状态组装查询参数，
   由 usePagedList 统一维护列表、总数与加载状态。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 8,
  map: mapMsgRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: keyword.value.trim() }
    if (statusFilter.value) params.status = statusFilter.value
    return listContactMessages(params)
  },
})

// 页面首次进入时加载第一页留言
onMounted(loadRows)
// 状态筛选变化后立即回到第一页重新加载
watch(statusFilter, onFilter)
// 关键字输入做 300ms 防抖，减少请求次数
let kwTimer = null
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300)
})

// 回复编辑状态：正在编辑哪条留言、回复草稿以及是否正在保存
const editingId = ref(null)
const draftReply = ref('')
const saving = ref(false)

// 当前操作人：取登录管理员姓名，缺省为“管理员”
function operator() {
  return authState.user?.name || '管理员'
}

// 进入某条留言的回复编辑状态，并回填已有回复
function startEdit(m) {
  editingId.value = m.id
  draftReply.value = m.reply || ''
}

// 取消编辑：退出编辑状态并清空草稿
function cancelEdit() {
  editingId.value = null
  draftReply.value = ''
}

/* 保存处理结果：
   校验回复长度，调用接口把留言状态改为 handled 并保存回复；
   成功后写操作日志、退出编辑并刷新列表，最后恢复保存按钮状态。 */
async function saveEdit(m) {
  const reply = draftReply.value.trim()
  if (reply.length > 500) {
    ElMessage.warning('回复不能超过 500 字')
    return
  }
  saving.value = true
  try {
    await handleMessageAction(m, { status: 'handled', reply })
    addLog('update', operator(), '处理联系留言', `留言来自「${m.name}」${reply ? '，已填写回复' : '，已标记为已处理'}`)
    ElMessage.success('已处理')
    cancelEdit()
    await loadRows()
  } catch (e) {
    ElMessage.error((e && e.message) || '保存失败')
  } finally {
    saving.value = false
  }
}

/* 删除留言：先弹确认框，确认后调用删除接口、写日志并刷新列表。 */
function removeMsg(m) {
  ElMessageBox.confirm(`确定删除「${m.name}」的这条留言吗？`, '删除留言', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await removeMessageAction(m)
        addLog('delete', operator(), '删除联系留言', `已删除「${m.name}」的留言`)
        ElMessage.success('已删除')
        await loadRows()
      } catch (e) {
        ElMessage.error((e && e.message) || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style src="./AdminMessages.css"></style>

<style scoped>
/* 加载提示：居中显示并留出上下间距 */
.amsg-loading { padding: 40px 0; text-align: center; color: #8a93a3; }
/* 分页条：右对齐，与列表拉开距离 */
.amsg-pager { display: flex; justify-content: flex-end; margin-top: 18px; }
</style>
