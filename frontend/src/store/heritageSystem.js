/*系统配置与日志状态：维护站点品牌/上传限制/首页配置，以及后台操作日志和文件校验工具*/
import { computed, reactive } from 'vue'
import { listLogs, createLog, getConfig, saveConfig, uploadLogo } from '@/api/system'


/*系统配置：系统名称、Logo、上传大小/数量限制、首页公告、ICP 备案号等；由 loadConfig 覆盖*/
export const systemConfig = reactive({
  systemName: '千漆 · 漆器非遗传承平台',
  logoText: '漆',
  logoUrl: '',
  uploadMaxSize: 50,
  uploadMaxCount: 9,
  allowVideo: true,
  allowDoc: true,
  homeNotice: '传承千年漆艺，让非遗走进生活。',
  icp: '蜀ICP备2026000000号',
})

/*品牌展示派生值：Logo 地址、Logo 文字、系统简称（取系统名“·”前的一段），随 systemConfig 自动更新*/
export const brandLogo = computed(() => systemConfig.logoUrl || '')
export const brandGlyph = computed(() => systemConfig.logoText || '漆')
export const brandShort = computed(() => {
  const full = (systemConfig.systemName || '').trim()
  if (!full) return '千漆'
  return (full.split('·')[0] || full).trim()
})

/*
 * 获取上传大小上限（MB）：读取 systemConfig.uploadMaxSize，配置无效时用 fallbackMb。
 * 参数 fallbackMb：兜底值，默认 20；返回值：数字。
 */
export function uploadLimitMb(fallbackMb = 20) {
  const n = Number(systemConfig.uploadMaxSize)
  return n > 0 ? n : fallbackMb
}
/*
 * 获取单次上传数量上限：读取 systemConfig.uploadMaxCount，配置无效时用 fallback。
 * 参数 fallback：兜底值，默认 9；返回值：数字。
 */
export function uploadLimitCount(fallback = 9) {
  const n = Number(systemConfig.uploadMaxCount)
  return n > 0 ? n : fallback
}
/*判断系统是否允许上传视频：配置项不为 false 即允许*/
export function videoUploadAllowed() {
  return systemConfig.allowVideo !== false
}
/*判断系统是否允许上传文档：配置项不为 false 即允许*/
export function docUploadAllowed() {
  return systemConfig.allowDoc !== false
}

/*允许的视频扩展名白名单（内部常量）*/
const _VIDEO_EXT = ['mp4', 'webm', 'mov', 'm4v']
/*允许的文档扩展名白名单（内部常量）*/
const _DOC_EXT = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'csv', 'zip', 'rar']

/*
 * 上传前校验文件：检查视频/文档上传开关是否开放，以及文件大小是否超过系统上限。
 * 参数 file：浏览器 File 对象；name：提示文案中的文件称呼；fallbackMb：大小上限兜底值。
 * 返回值：空字符串表示通过，否则返回错误提示文案。
 */
export function checkUploadFile(file, { name = '文件', fallbackMb = 20 } = {}) {
  const ext = (file.name.includes('.') ? file.name.split('.').pop() : '').toLowerCase()
  if (_VIDEO_EXT.includes(ext) && !videoUploadAllowed()) return '管理员已关闭视频上传（系统配置 → 允许上传）'
  if (_DOC_EXT.includes(ext) && !docUploadAllowed()) return '管理员已关闭文档上传（系统配置 → 允许上传）'
  const mb = uploadLimitMb(fallbackMb)
  if (file.size > mb * 1024 * 1024) return `${name}不能超过 ${mb}MB`
  return ''
}


/*技艺档案候选池（本地静态数据）：首页配置可从中勾选要展示的档案 ID*/
export const archivePool = [
  { id: 1, name: '髹漆', desc: '生漆髹饰', tag: '国家级' },
  { id: 2, name: '螺钿', desc: '贝华镶嵌', tag: '国家级' },
  { id: 3, name: '雕漆', desc: '刀行漆上', tag: '省级' },
  { id: 4, name: '描金', desc: '金漆勾绘', tag: '省级' },
  { id: 5, name: '犀皮', desc: '流云斑纹', tag: '省级' },
  { id: 6, name: '镏金', desc: '刻划填金', tag: '国家级' },
  { id: 7, name: '百宝嵌', desc: '众彩纷呈', tag: '省级' },
  { id: 8, name: '素髹', desc: '大道至简', tag: '国家级' },
  { id: 9, name: '堆漆', desc: '堆塑起纹', tag: '省级' },
  { id: 10, name: '填漆', desc: '填嵌磨平', tag: '国家级' },
  { id: 11, name: '款彩', desc: '刻灰填彩', tag: '省级' },
  { id: 12, name: '描彩', desc: '漆上作画', tag: '省级' },
]

/*传承人候选池（本地静态数据）：首页配置可从中勾选要展示的传承人 ID*/
export const masterPool = [
  { id: 1, name: '张守一', title: '国家级传承人' },
  { id: 2, name: '李髹', title: '省级传承人' },
  { id: 3, name: '王漆', title: '省级传承人' },
  { id: 4, name: '陈艺', title: '市级传承人' },
  { id: 5, name: '赵雕', title: '国家级传承人' },
  { id: 6, name: '钱螺', title: '省级传承人' },
  { id: 7, name: '孙素', title: '市级传承人' },
  { id: 8, name: '周金', title: '省级传承人' },
]

/*首页配置：保存选中的档案/传承人 ID、精选课程 ID 和精选作品 ID 列表，默认展示全部候选*/
export const homeConfig = reactive({
  archives: archivePool.map((a) => a.id),
  masters: masterPool.map((m) => m.id),
  featuredCourses: 1,
  featuredProducts: [1, 2],
})

/*操作日志类型映射表：登录、新增、修改、删除、审核、订单、发货，用于日志列表标签*/
export const logTypeMap = {
  login: { label: '登录', color: '#1e6fb8' },
  create: { label: '新增', color: '#2e7d32' },
  update: { label: '修改', color: '#b8860b' },
  delete: { label: '删除', color: '#c62828' },
  review: { label: '审核', color: '#8b2e1c' },
  order: { label: '订单', color: '#7b1fa2' },
  ship: { label: '发货', color: '#00695c' },
}

/*操作日志列表：下面几条是本地演示数据，页面调用 loadLogs 后会被后端日志整体替换*/
export const operationLogs = reactive([
  { id: 1, type: 'login', operator: '管理员', action: '登录系统', detail: 'IP 192.168.1.100', time: '2026-08-16 18:30' },
  { id: 2, type: 'review', operator: '平台管理员', action: '通过课程审核', detail: '「半日髹漆体验 · 素色茶碗」', time: '2026-08-16 17:12' },
  { id: 3, type: 'review', operator: '管理员', action: '驳回技艺档案', detail: '「镏金技艺」缺少工序步骤图', time: '2026-08-16 16:05' },
  { id: 4, type: 'order', operator: '平台管理员', action: '更新订单状态', detail: '订单 #3 已发货', time: '2026-08-15 16:40' },
  { id: 5, type: 'create', operator: '张守一', action: '新增课程', detail: '「半日髹漆体验 · 素色茶碗」', time: '2026-08-14 10:00' },
  { id: 6, type: 'ship', operator: '平台管理员', action: '发货', detail: '学员「吴青」材料包已寄出', time: '2026-08-15 16:20' },
  { id: 7, type: 'delete', operator: '平台管理员', action: '删除学员', detail: '学员「测试账号」', time: '2026-08-13 11:00' },
  { id: 8, type: 'update', operator: '张守一', action: '修改个人主页', detail: '更新了头像与简介', time: '2026-08-12 09:30' },
])

/*
 * 记录一条操作日志：先在本地生成新 id（当前最大 id + 1）并插入日志列表开头，
 * 同时异步调用 createLog 上报后端；上报失败会被静默忽略。
 * 参数 type/operator/action/detail 分别对应日志类型、操作人、动作、详情；无返回值。
 */
export function addLog(type, operator, action, detail) {
  const id = operationLogs.length ? Math.max(...operationLogs.map((l) => l.id)) + 1 : 1
  operationLogs.unshift({
    id,
    type,
    operator,
    action,
    detail: detail || '',
    time: new Date().toLocaleString('zh-CN', { hour12: false }),
  })
  createLog({ type, operator, action, detail: detail || '' }).catch(() => {})
}

/*
 * 加载操作日志：调用 listLogs(params)（如分页/筛选参数），
 * 映射后整体替换 operationLogs；返回值：更新后的日志列表。
 */
export async function loadLogs(params = {}) {
  const data = await listLogs(params)
  operationLogs.splice(0, operationLogs.length, ...data.map((l) => ({
    id: l.id,
    type: l.type,
    operator: l.operator || '',
    action: l.action || '',
    detail: l.detail || '',
    ip: l.ip || '',
    time: l.time || l.created_at || '',
  })))
  return operationLogs
}

/*
 * 加载系统配置：调用 getConfig()，把返回的 system 合并进 systemConfig，
 * 把返回的 home 中的档案/传承人/精选课程/精选作品复制进 homeConfig（数组要复制，避免直接引用接口数据）。
 * 返回值：后端原始配置数据。
 */
export async function loadConfig() {
  const data = await getConfig()
  if (data && data.system && typeof data.system === 'object') {
    Object.assign(systemConfig, data.system)
  }
  if (data && data.home && typeof data.home === 'object') {
    const h = data.home
    if (Array.isArray(h.archives)) homeConfig.archives = [...h.archives]
    if (Array.isArray(h.masters)) homeConfig.masters = [...h.masters]
    if (h.featuredCourses != null) homeConfig.featuredCourses = h.featuredCourses
    if (Array.isArray(h.featuredProducts)) homeConfig.featuredProducts = [...h.featuredProducts]
  }
  return data
}

/*
 * 上传系统 Logo：把文件装入 FormData 后调用 uploadLogo，成功后写入 systemConfig.logoUrl。
 * 参数 file：图片 File 对象；返回值：最新 Logo 地址。
 */
export async function uploadSystemLogo(file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await uploadLogo(fd)
  systemConfig.logoUrl = (res && res.url) || ''
  return systemConfig.logoUrl
}

/*清空本地 Logo 地址（只改前端状态，不调用后端；保存配置后才持久化）*/
export function clearSystemLogo() {
  systemConfig.logoUrl = ''
}

/*
 * 保存配置到后端：把 systemConfig 与 homeConfig 一起提交给 saveConfig，
 * 数组字段先复制再提交；返回值：后端保存结果。
 */
export async function saveConfigRemote() {
  const res = await saveConfig({
    system: { ...systemConfig },
    home: {
      archives: [...homeConfig.archives],
      masters: [...homeConfig.masters],
      featuredCourses: homeConfig.featuredCourses,
      featuredProducts: [...homeConfig.featuredProducts],
    },
  })
  return res
}
