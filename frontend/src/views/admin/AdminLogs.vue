<!-- 操作日志页：分页查看后台各类操作记录，支持关键字/类型筛选与 CSV 导出 -->
<template>
  <AdminLayout>
    <div class="alg-wrap">
      <!-- 页头区：标题、日志总数与导出按钮 -->
      <div class="alg-head">
        <div class="alg-head-left">
          <h2 class="alg-title">操作日志</h2>
          <p class="alg-sub">共 {{ total }} 条操作记录，实现全程可追溯</p>
        </div>
        <el-button class="alg-export" type="primary" @click="onExport">导出 CSV</el-button>
      </div>

      <!-- 筛选区：按操作人/内容关键字与日志类型过滤，变化后自动重新请求 -->
      <div class="alg-filter">
        <el-input v-model="keyword" placeholder="搜索操作人 / 内容" clearable style="width: 240px" />
        <el-select v-model="typeFilter" placeholder="类型" clearable style="width: 130px">
          <el-option v-for="(v, k) in logTypeMap" :key="k" :label="v.label" :value="k" />
        </el-select>
      </div>

      <!-- 列表区：每条日志展示类型、操作人、动作、IP、时间与详情 -->
      <div v-if="loading" class="alg-loading">加载中…</div>
      <div v-else-if="rows.length" class="alg-list">
        <div v-for="l in rows" :key="l.id" class="alg-card">
          <span class="alg-type" :style="{ color: logTypeMap[l.type].color, borderColor: logTypeMap[l.type].color }">
            {{ logTypeMap[l.type].label }}
          </span>
          <div class="alg-body">
            <div class="alg-body-top">
              <span class="alg-operator">{{ l.operator }}</span>
              <span class="alg-action">{{ l.action }}</span>
              <span class="alg-ip">IP {{ l.ip || '—' }}</span>
              <span class="alg-time">{{ l.time }}</span>
            </div>
            <div v-if="l.detail" class="alg-detail">{{ l.detail }}</div>
          </div>
        </div>
      </div>

      <!-- 空状态：没有符合筛选条件的日志时显示 -->
      <div v-else class="alg-empty">
        <span class="alg-empty-glyph">志</span>
        <p class="alg-empty-text">暂无日志</p>
      </div>

      <!-- 分页区：总条数超过每页数量时显示分页器 -->
      <div v-if="total > pageSize" class="alg-pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="pageSize" :current-page="page" @current-change="onPage" />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import AdminLayout from './AdminLayout.vue'
import { listLogs, exportLogs } from '@/api/system'
import { logTypeMap } from '@/store'
import { usePagedList } from '@/composables/usePagedList'

// 筛选条件：关键字（操作人/内容）与日志类型
const keyword = ref('')
const typeFilter = ref('')

/* 导出日志：按当前筛选条件请求后端生成 CSV，
   请求期间给出提示，成功或失败分别反馈。 */
async function onExport() {
  try {
    const params = { keyword: keyword.value.trim() }
    if (typeFilter.value) params.type = typeFilter.value
    ElMessage.info('正在生成导出文件…')
    await exportLogs(params)
    ElMessage.success('已导出')
  } catch (e) {
    ElMessage.error((e && e.message) || '导出失败')
  }
}


/* 整理一条日志：缺失字段兜底为空串；时间优先用 time，没有再退回 created_at。 */
function mapLogRow(l) {
  return { id: l.id, type: l.type, operator: l.operator || '', action: l.action || '', detail: l.detail || '', ip: l.ip || '', time: l.time || l.created_at || '' }
}

/* 分页加载日志：每次按页码、每页条数、关键字与类型组装查询参数，
   由 usePagedList 统一维护列表、总数与加载状态。 */
const { rows, total, page, pageSize, loading, loadRows, onFilter, onPage } = usePagedList({
  pageSize: 10,
  map: mapLogRow,
  fetchPage: ({ page, page_size }) => {
    const params = { page, page_size, keyword: keyword.value.trim() }
    if (typeFilter.value) params.type = typeFilter.value
    return listLogs(params)
  },
})

// 页面首次进入时加载第一页日志
onMounted(loadRows)
// 类型筛选变化后立即回到第一页重新加载
watch(typeFilter, onFilter)
// 关键字输入做 300ms 防抖，减少请求次数
let kwTimer = null
watch(keyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(onFilter, 300)
})
</script>

<style src="./AdminLogs.css"></style>

<style scoped>
/* 加载提示：居中显示并留出上下间距 */
.alg-loading { padding: 40px 0; text-align: center; color: #8a93a3; }
/* 分页条：右对齐，与列表拉开距离 */
.alg-pager { display: flex; justify-content: flex-end; margin-top: 18px; }
</style>
