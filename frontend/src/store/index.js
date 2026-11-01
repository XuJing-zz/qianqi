
/*全局状态管理（轻量版 store）：集中管理登录用户、收藏、报名、订单，并汇总导出各业务模块的状态与操作*/
// reactive：reactive(对象) 是 Vue 3 的响应式 API：把普通对象变成“深层响应式对象”，读取或修改属性时依赖它的视图会自动更新。
// 与 ref 不同，reactive 直接操作对象属性、不需要 .value，适合管理一组相关状态；解构它会让属性失去响应性，通常整体使用。
import { reactive } from 'vue'
// 收藏、报名、订单、字段命名转换相关的接口
import {
  listFavorites, addFavorite, removeFavorite,
} from '@/api/products'
import { listStudents, createStudent, updateStudent } from '@/api/students'   // 学员（报名）相关接口
import { listOrders, createOrder, buyProductOrder, payOrder, completeOrder, cancelOrder } from '@/api/orders'   // 订单相关接口
import { mapKeys, mapToSnake } from '@/api/utils'   // 后端下划线命名 <-> 前端驼峰命名的转换工具

// 把各业务子模块（课程、作品、技能、订单、库存、账号等）的状态和操作统一从这里再导出，页面只需从 '@/store' 导入
export { courses, loadCourses, ensureCourses, fetchCourseDetail } from './courses'
export { heritageCourses, courseStatusMap, videoStatusMap, durationToLessonCount, loadCourses as loadHeritageCourses, addCourse, reviewCourseAction, updateCourseAction, submitCourseAction, offlineCourseAction, reviewVideoAction } from './heritageCourses'
export { heritageProducts, productStatusMap, loadProducts, addProduct, updateProductAction, removeProduct, submitProductAction, reviewProductAction } from './heritageProducts'
export { heritageSkills, skillLevels, skillSchools, skillStatusMap, loadSkills, addSkill, updateSkillAction, removeSkill, submitSkillAction, reviewSkillAction, toggleOfflineSkill } from './heritageSkills'
export { heritageOrders, orderStatusMap, loadOrders as loadHeritageOrders, shipOrderAction, completeOrderAction, cancelOrderAction } from './heritageOrders'
export { heritageStudents, studentStatusMap, loadStudents, updateStudentAction, markStudentDoneAction, saveStudentMaterialPlan } from './heritageStudents'
export { trainingRecords, loadTrainingRecords, addTrainingRecord, updateTrainingRecordAction, removeTrainingRecord } from './heritageTrainingRecords'
export { heritageProfile, levelOptions, craftOptions, loadHeritageProfile, saveHeritageProfile } from './heritageProfile'
export {
  inventoryMaterials, materialTypeMap, materialState,
  materialRecordTypeMap,
  loadMaterials,
  materialStockInOut,
  shipments, shipmentStatusMap, derivedShipments,
  loadShipments, createShipmentAction, shipOut, signShipmentAction,
  checkStock, getStudentMaterialPlan, setStudentMaterialPlan,
} from './heritageInventory'
export { addresses, loadAddresses, addAddress, updateAddressAction, removeAddress } from './userAddresses'
export { accounts, accountRoleMap, addAccount, toggleAccountStatus, updateAccountAction, resetPassword, removeAccount, issueHeritageAccount } from './heritageAccounts'
export { inheritors, inheritorLevels, inheritorCrafts, inheritorStatusMap, loadInheritors, addInheritor, updateInheritor, removeInheritor, toggleInheritorStatus } from './heritageInheritors'
export { systemConfig, brandLogo, brandGlyph, brandShort, homeConfig, logTypeMap, addLog, loadConfig, saveConfigRemote, uploadSystemLogo, clearSystemLogo, uploadLimitMb, uploadLimitCount, videoUploadAllowed, checkUploadFile } from './heritageSystem'
export { contactMessages, messageStatusMap, loadContactMessages, handleMessageAction, removeMessageAction } from './contactMessages'
export { stockOf, productStockState, stockRecordTypeMap, stockInOut } from './heritageProductInventory'

/*收藏状态块：list 保存当前用户收藏的商品摘要，供商品列表/详情页显示收藏按钮和“我的收藏”页使用*/
const favoriteState = reactive({ list: [] })   // list：收藏商品数组

/*加载收藏列表：无参数；返回 Promise<void>（完成后更新 favoriteState.list）。
   流程：未登录则清空列表并结束；否则请求后端收藏接口，把每条记录的下划线字段转成驼峰并只保留页面需要的字段。*/
async function loadFavorites() {
  if (!isLoggedIn()) { favoriteState.list = []; return }   // 未登录时不请求接口
  const data = await listFavorites()   // 对应后端 GET /api/products/favorites/
  favoriteState.list = data.map((f) => {
    const m = mapKeys(f)   // 后端字段如 product_id 转成 productId
    return { productId: m.productId, glyph: m.glyph, name: m.name, inheritor: m.inheritor, craft: m.craft, cover: m.cover || '' }
  })
}

/*判断某个商品是否已收藏：参数 productId 商品 id；返回布尔值，true 表示已收藏。*/
function isFavorite(productId) {
  return favoriteState.list.some((f) => f.productId === productId)
}

/*取消收藏并同步本地列表：参数 productId 商品 id；返回 Promise<void>。
   先调用后端删除接口，成功后再从本地列表移除对应项（findIndex 找不到时返回 -1，此时不做处理）。*/
async function unfavoriteProduct(productId) {
  await removeFavorite(productId)   // 删除接口成功后才更新本地状态
  const idx = favoriteState.list.findIndex((f) => f.productId === productId)
  if (idx >= 0) favoriteState.list.splice(idx, 1)   // splice(idx, 1) 删除一个元素
}

/*切换收藏状态（商品卡片/详情页的收藏按钮）：参数 p 是商品对象（至少包含 id、name）；返回布尔值，true 表示切换后为“已收藏”。
   已收藏 -> 先从本地列表移除，再异步调用删除接口（失败也先保证界面操作流畅）；
   未收藏 -> 先用商品信息组装一条记录插入列表头部，再异步调用新增接口。*/
function toggleFavorite(p) {
  const idx = favoriteState.list.findIndex((f) => f.productId === p.id)
  if (idx >= 0) {
    // 当前已收藏：立即取消
    favoriteState.list.splice(idx, 1)
    removeFavorite(p.id).catch(() => {})   // 异步删除，失败不打断用户操作
    return false
  }
  // 当前未收藏：立即插入到列表最前面
  favoriteState.list.unshift({
    productId: p.id,
    glyph: p.glyph || p.name.charAt(0),   // 没有图标时用商品名首字代替
    name: p.name,
    inheritor: p.inheritor,
    craft: p.craft,
    cover: p.cover || '',
  })
  addFavorite(p.id).catch(() => {})   // 异步新增
  return true
}

/*报名状态块：list 保存当前用户的所有报名记录（课程、审核状态、学习进度等），供“我的报名/我的学习”使用*/
const enrollmentState = reactive({ list: [] })   // list：报名记录数组

/*加载我的报名：无参数；返回 Promise<void>（完成后更新 enrollmentState.list）。
   流程：未登录则清空；否则请求学员列表，并把后端字段转驼峰后整理成页面统一使用的结构（缺失字段给默认值）。*/
async function loadEnrollments() {
  if (!isLoggedIn()) { enrollmentState.list = []; return }   // 未登录时不请求
  const data = await listStudents()   // 对应后端 GET /api/students/students/
  enrollmentState.list = data.map((s) => {
    const m = mapKeys(s)
    return {
      id: m.id,
      courseId: m.courseId ?? 0,   // 课程 id（缺失时记为 0）
      name: m.courseName || m.name || '',
      learner: m.name || '',
      courseName: m.courseName || '',
      teacher: m.teacher || '',
      craft: m.craft || '',
      stage: m.stage || '',
      price: Number(m.price ?? 0),
      status: m.status || 'review',   // 默认“待审核”
      reviewComment: m.reviewComment || '',
      enrollTime: m.enrollTime || '',
      progress: Number(m.progress ?? 0),
      // 已完成课节统一转成字符串数组，避免数字/字符串比较不一致
      completed: Array.isArray(m.completed) ? m.completed.map(String) : [],
    }
  })
}

/*提交报名（课程详情页点击“立即报名”）：参数 payload 包含 courseId、courseName/name、teacher、craft、price 等。
   返回 Promise<boolean>：成功后 resolve true，失败时先回滚本地记录再抛出错误。
   流程：先用临时 id 把报名记录插入本地列表（乐观更新，界面立即有反馈）-> 调用创建学员接口 ->
   成功则用后端返回的数据替换临时记录，失败则删除临时记录。*/
function addEnrollment(payload) {
  const title = payload.courseName || payload.name || ''   // 课程名称
  const learner = (authState.user && (authState.user.name || authState.user.nick || authState.user.username)) || ''   // 学员名取当前用户
  const local = {
    id: Date.now(),   // 用当前时间戳作为临时 id
    courseId: payload.courseId,
    name: title,
    courseName: title,
    learner,
    teacher: payload.teacher || '',
    craft: payload.craft || '',
    stage: payload.stage || '',
    price: payload.price || 0,
    status: 'review',   // 新报名默认待审核
    reviewComment: '',
    enrollTime: payload.enrollTime || new Date().toLocaleString('zh-CN', { hour12: false }),
  }
  enrollmentState.list.unshift(local)   // 乐观更新：先显示在列表中

  return createStudent(mapToSnake({   // 前端驼峰字段转成后端需要的下划线字段
    name: learner,
    courseId: payload.courseId,
    courseName: title,
    teacher: payload.teacher || '',
    craft: payload.craft || '',
    price: payload.price || 0,
  }))
    .then((created) => {
      // 用后端返回的真实记录替换临时记录
      const idx = enrollmentState.list.findIndex((e) => e.id === local.id)
      if (idx >= 0) {
        enrollmentState.list[idx] = {
          ...local,
          ...mapKeys(created),
          name: created.course_name || title,
          courseName: created.course_name || title,
        }
      }
      return true
    })
    .catch((e) => {
      // 请求失败：删除乐观插入的临时记录，保持界面与后端一致，再把错误抛给调用方
      const idx = enrollmentState.list.findIndex((x) => x.id === local.id)
      if (idx >= 0) enrollmentState.list.splice(idx, 1)
      console.error('报名失败', e)
      throw e
    })
}

/*查找某门课程的报名记录：参数 courseId 课程 id；返回匹配的报名对象，找不到返回 null。*/
function enrollmentOf(courseId) {
  return enrollmentState.list.find((e) => Number(e.courseId) === Number(courseId)) || null
}

/*判断是否已成功报名某课程：只有状态为 ongoing（学习中）或 done（已完成）才算报名成功；
   参数 courseId；返回布尔值。*/
function isEnrolled(courseId) {
  const e = enrollmentOf(courseId)
  return !!e && (e.status === 'ongoing' || e.status === 'done')
}

/*更新我的学习进度：参数 id 报名记录 id，completed 是已完成课节列表；返回后端更新后的原始对象。
   流程：调用 PATCH 接口 -> 返回字段转驼峰 -> 在本地列表中找到对应项并替换，同步已完成列表、进度和状态。*/
async function updateMyEnrollmentCompleted(id, completed) {
  const updated = await updateStudent(id, { completed })   // 对应后端 PATCH /api/students/students/{id}/
  const m = mapKeys(updated)
  const idx = enrollmentState.list.findIndex((e) => e.id === id)
  if (idx >= 0) {
    const it = enrollmentState.list[idx]
    enrollmentState.list[idx] = {
      ...it,
      completed: Array.isArray(m.completed) ? m.completed.map(String) : [],
      progress: Number(m.progress ?? it.progress ?? 0),   // 后端没返回进度时沿用旧值
      status: m.status || it.status,
    }
  }
  return updated
}

/*订单状态块：list 保存当前用户的课程订单和商品订单，供“我的订单”、支付、确认收货等页面使用*/
const orderState = reactive({ list: [] })   // list：订单数组

/*加载我的订单：无参数；返回 Promise<void>（完成后更新 orderState.list）。
   流程：未登录则清空；否则请求订单列表，转驼峰后统一课程订单/商品订单的字段（缺失值给默认值）。*/
async function loadOrders() {
  if (!isLoggedIn()) { orderState.list = []; return }   // 未登录时不请求
  const data = await listOrders()   // 对应后端 GET /api/orders/orders/
  orderState.list = data.map((o) => {
    const m = mapKeys(o)
    return {
      id: m.id,
      courseId: m.courseId ?? 0,
      courseName: m.itemName || '',   // 课程订单沿用 itemName 字段
      itemName: m.itemName || '',
      name: m.itemName || '',
      price: Number(m.price ?? 0),
      payMethod: m.payMethod || '',
      payTime: m.payTime || '',
      orderTime: m.orderTime || '',
      status: m.status || 'review',
      type: m.type || 'course',   // course=课程订单，product=商品订单
      glyph: m.glyph || '',
      company: m.company || '',   // 物流公司
      trackingNo: m.trackingNo || '',   // 快递单号
      shipTime: m.shipTime || '',
      address: m.address || '',
      receiver: m.receiver || '',
      phone: m.phone || '',
      remark: m.remark || '',
    }
  })
}

/*创建课程订单并立即支付：参数 payload 包含 courseId、courseName、price、payMethod 等；返回 Promise<boolean>。
   流程：先插入一条临时订单（乐观更新）-> 调用创建订单接口 -> 用返回 id 调用支付接口 ->
   成功后用后端数据替换临时订单；任一步失败则删除临时订单并抛出错误。*/
function addOrder(payload) {
  const ts = payload.orderTime || payload.payTime || new Date().toLocaleString('zh-CN', { hour12: false })   // 下单时间
  const local = {
    id: Date.now(),   // 临时 id
    courseId: payload.courseId,
    type: 'course',
    courseName: payload.courseName,
    itemName: payload.courseName,
    glyph: payload.glyph || '课',
    price: payload.price,
    payMethod: payload.payMethod || '',
    payTime: '',
    orderTime: ts,
    status: 'pending',   // 待支付
  }
  orderState.list.unshift(local)   // 乐观更新

  return createOrder(mapToSnake({   // 创建订单接口：POST /api/orders/orders/
    type: 'course',
    itemName: payload.courseName,
    glyph: payload.glyph || '课',
    buyer: authState.user?.name || authState.user?.username || '',
    price: payload.price,
    payMethod: payload.payMethod || '',
    orderTime: local.orderTime,
  }))
    .then((created) => payOrder(created.id, { pay_method: payload.payMethod || '' }))   // 支付接口：POST /api/orders/orders/{id}/pay/
    .then((paid) => {
      // 支付成功：用后端返回的完整订单替换临时订单
      const idx = orderState.list.findIndex((o) => o.id === local.id)
      if (idx >= 0) {
        orderState.list[idx] = { ...local, ...mapKeys(paid) }
      }
      return true
    })
    .catch((e) => {
      // 下单或支付失败：回滚临时订单，并把错误抛给调用方
      const idx = orderState.list.findIndex((x) => x.id === local.id)
      if (idx >= 0) orderState.list.splice(idx, 1)
      console.error('课程下单失败', e)
      throw e
    })
}

/*购买商品并生成订单：参数 payload 是商品订单信息（商品 id、数量、收货地址、支付方式等）；
   返回 Promise<订单对象>（已转换为前端字段结构），并插入 orderState.list 顶部。
   对应后端 POST /api/orders/orders/buy_product/。*/
async function addProductOrder(payload) {
  const created = await buyProductOrder(mapToSnake(payload))
  const m = mapKeys(created)
  const item = {
    id: m.id,
    courseId: 0,   // 商品订单没有课程 id
    type: 'product',
    courseName: m.itemName || '',
    itemName: m.itemName || '',
    name: m.itemName || '',
    price: Number(m.price ?? 0),
    payMethod: m.payMethod || '',
    payTime: m.payTime || '',
    orderTime: m.orderTime || '',
    status: m.status || 'pending',
    glyph: m.glyph || '',
    company: m.company || '',
    trackingNo: m.trackingNo || '',
    shipTime: m.shipTime || '',
    address: m.address || '',
    receiver: m.receiver || '',
    phone: m.phone || '',
    remark: m.remark || '',
  }
  orderState.list.unshift(item)
  return item
}

/*支付我的订单：参数 id 订单 id，payMethod 支付方式；返回转换后的订单对象。
   调用 POST /api/orders/orders/{id}/pay/，成功后同步本地订单的状态、支付方式和支付时间。*/
async function payMyOrder(id, payMethod) {
  const paid = await payOrder(id, { pay_method: payMethod || '' })
  const m = mapKeys(paid)
  const idx = orderState.list.findIndex((o) => o.id === id)
  if (idx >= 0) {
    const it = orderState.list[idx]
    orderState.list[idx] = {
      ...it,
      status: m.status || it.status,
      payMethod: m.payMethod || '',
      payTime: m.payTime || '',
    }
  }
  return m
}

/*确认收货/完成订单：参数 id 订单 id；返回转换后的订单对象。
   调用 POST /api/orders/orders/{id}/complete/，成功后把本地订单状态改为完成。*/
async function confirmMyOrder(id) {
  const done = await completeOrder(id)
  const m = mapKeys(done)
  const idx = orderState.list.findIndex((o) => o.id === id)
  if (idx >= 0) orderState.list[idx] = { ...orderState.list[idx], status: m.status || 'done' }
  return m
}

/*取消订单：参数 id 订单 id；返回转换后的订单对象。
   调用 POST /api/orders/orders/{id}/cancel/，成功后把本地状态改为 cancelled，并保存后端的审核备注。*/
async function cancelMyOrder(id) {
  const c = await cancelOrder(id)
  const m = mapKeys(c)
  const idx = orderState.list.findIndex((o) => o.id === id)
  if (idx >= 0) orderState.list[idx] = {
    ...orderState.list[idx],
    status: m.status || 'cancelled',
    reviewComment: m.reviewComment || '',
  }
  return m
}

// ---- 登录状态与用户信息 ----
import { apiLogin, apiLogout } from '@/api/auth'

const AUTH_KEY = 'qianqi_auth'   // 在本地持久化用户信息时使用的键名

/*从本地读取登录用户信息：无参数；返回解析后的用户对象，没有记录或解析失败时返回 null。
   作用：刷新页面后仍能恢复登录状态（真正的接口鉴权仍依赖 token）。*/
function loadAuth() {
  try {
    const raw = localStorage.getItem(AUTH_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null   // 本地数据损坏时按未登录处理
  }
}

/*登录状态块：user 为当前登录用户对象（含 id、username、name、role 等），null 表示未登录*/
const authState = reactive({
  user: loadAuth(),   // 启动时尝试从本地恢复
})

/*登录后统一拉取用户数据：无参数；返回 Promise<void>。
   同时加载收藏、报名、订单；allSettled 会等全部请求结束，某个失败不影响其它数据。*/
async function loadUserData() {
  if (!isLoggedIn()) return
  await Promise.allSettled([loadFavorites(), loadEnrollments(), loadOrders()])
}

/*登录：参数 username 用户名、password 密码；返回 Promise<{ ok: true, role } | { ok: false, msg }>。
   流程：调用登录接口 -> 保存用户到响应式状态和本地存储 -> 后台加载用户数据 -> 返回成功和角色；
   捕获异常时把错误转换成友好提示并返回失败结果（不向外抛错）。*/
async function login(username, password) {
  try {
    const user = await apiLogin(username, password)   // POST /api/accounts/auth/login/，内部会保存 token
    authState.user = user
    localStorage.setItem(AUTH_KEY, JSON.stringify(user))   // 持久化用户信息
    loadUserData().catch(() => {})   // 不阻塞登录流程
    return { ok: true, role: user.role }
  } catch (e) {
    return { ok: false, msg: loginErrorMsg(e) }
  }
}

/*退出登录：无参数；返回 Promise<void>。
   先清空内存状态和本地用户信息（界面立即变为未登录），再通知后端注销 token。*/
async function logout() {
  authState.user = null
  localStorage.removeItem(AUTH_KEY)
  favoriteState.list = []
  enrollmentState.list = []
  orderState.list = []
  await apiLogout()   // POST /api/accounts/auth/logout/，并清除本地 token
}

/*判断是否已登录：返回布尔值（authState.user 是否存在）。*/
function isLoggedIn() {
  return !!authState.user
}

/*根据角色返回首页路径：heritage -> /console，admin -> /admin，其他（普通用户/未登录）-> /。
   参数 role 角色字符串；返回路径字符串。*/
function homeOf(role) {
  if (role === 'heritage') return '/console'
  if (role === 'admin') return '/admin'
  return '/'
}

/*登录后决定最终跳转地址：参数 role 角色、redirect 登录前想去的地址；返回最终路径。
   只有当 redirect 与该角色允许的区域匹配时才使用它，否则回到角色首页，防止越权跳转。*/
function resolveLanding(role, redirect) {
  if (typeof redirect === 'string' && redirect.length > 0) {
    if (role === 'admin' && redirect.startsWith('/admin')) return redirect
    if (role === 'heritage' && redirect.startsWith('/console')) return redirect
    if (role === 'user' && !redirect.startsWith('/admin') && !redirect.startsWith('/console')) return redirect
  }
  return homeOf(role)
}

/*把登录异常转换成用户看得懂的提示：参数 e 错误对象；返回提示字符串。
   优先使用后端返回的 detail/msg；其次识别网络错误和 4xx/5xx 状态；最后才使用原始错误信息。*/
function loginErrorMsg(e) {
  const dataMsg = e && e.data && (e.data.detail || e.data.msg)
  if (dataMsg) return dataMsg
  const m = (e && e.message) || ''
  if (m === 'Failed to fetch') return '无法连接服务器，请确认后端服务已启动'
  if (/请求失败\(5\d\d\)/.test(m)) return '服务器开小差了，请稍后再试'
  if (/请求失败\(4\d\d\)/.test(m)) return '账号或密码错误'
  return m || '账号或密码错误'
}

// 对外暴露的状态与操作：其他文件通过 import { ... } from '@/store' 使用
export {
  favoriteState,
  isFavorite,
  toggleFavorite,
  unfavoriteProduct,
  loadFavorites,
  enrollmentState,
  addEnrollment,
  enrollmentOf,
  isEnrolled,
  loadEnrollments,
  updateMyEnrollmentCompleted,
  orderState,
  addOrder,
  addProductOrder,
  payMyOrder,
  confirmMyOrder,
  cancelMyOrder,
  loadOrders,
  loadUserData,
  authState,
  login,
  logout,
  isLoggedIn,
  homeOf,
  resolveLanding,
}
