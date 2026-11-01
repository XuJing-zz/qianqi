
/*HTTP 请求统一封装：拼接 /api 前缀、自动携带 token、401 时尝试刷新 token、统一解析响应和错误*/
/* localStorage 是浏览器提供的本地存储：数据以“键值对”形式保存在用户电脑上，
   关闭页面或浏览器后仍然存在（除非手动清除）；它只能保存字符串，所以保存对象时要先序列化。
   这里用它保存登录令牌和用户信息，刷新页面后仍能读取。*/
const TOKEN_KEY = 'qianqi_token'   // 访问令牌（access token）的存储键名
const REFRESH_KEY = 'qianqi_refresh'   // 刷新令牌（refresh token）的存储键名
const AUTH_KEY = 'qianqi_auth'   // 用户信息 JSON 字符串的存储键名

/*读取访问令牌：无参数；返回保存的 token 字符串，没有则返回 null。*/
function getAccess() {
  return localStorage.getItem(TOKEN_KEY)
}
/*读取刷新令牌：无参数；返回保存的 refresh token 字符串，没有则返回 null。*/
function getRefresh() {
  return localStorage.getItem(REFRESH_KEY)
}
/*保存令牌：参数 access 访问令牌、refresh 刷新令牌（都是可选）；只写入非空值；无返回值。*/
export function setTokens(access, refresh) {
  if (access) localStorage.setItem(TOKEN_KEY, access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}
/*清除登录凭证：无参数；无返回值。移除访问令牌、刷新令牌和本地用户信息。*/
export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(AUTH_KEY)
}

let redirecting = false   // 防止多个请求同时收到 401 时重复跳转登录页
/*跳转到登录页（token 失效时调用）：无参数；无返回值。
   把当前页面地址放进 redirect 参数，登录成功后可以回到原页面；redirecting 保证只跳一次。*/
function redirectToLogin() {
  if (redirecting) return
  redirecting = true
  const cur = window.location.pathname + window.location.search   // 当前页面地址
  if (cur.startsWith('/login')) return
  window.location.assign('/login?expired=1&redirect=' + encodeURIComponent(cur))   // assign 会直接跳转并刷新页面
}

/*发送 HTTP 请求的统一入口：
   参数 path 是 /api 之后的接口路径（如 /orders/orders/）；options 可包含 method（默认 GET）、body（对象或 FormData）、headers（额外请求头）。
   返回值：Promise，成功时解析为响应 JSON 数据。
   失败时抛出 Error，错误对象额外带有 status（HTTP 状态码）和 data（后端返回的错误数据）。
   关键流程：拼接 URL -> 构造请求头和请求体 -> fetch 发送 -> 遇到 401 尝试刷新 token 并重试 ->
   读取 JSON 响应 -> 非 2xx 提取错误信息并抛错 -> 返回数据。*/
export async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const url = '/api' + path   // 所有后端接口都统一以 /api 开头（开发环境由 Vite 代理到后端）
  /* FormData 是浏览器提供的表单数据对象，用于构造 multipart/form-data 请求体，常见于文件上传。
     body instanceof FormData 用于判断本次请求体是不是表单数据；typeof 判断则是兼容不支持 FormData 的环境。*/
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData
  /*复制一份 FormData：参数 fd 是原表单对象；返回新的 FormData。
     逐项读取原表单的键值并 append 到新对象，供重试请求时重新构造请求体。*/
  const cloneForm = (fd) => {
    const c = new FormData()
    for (const [k, v] of fd.entries()) c.append(k, v)
    return c
  }
  /*构造 fetch 的配置对象：参数 token 用于拼接 Authorization 请求头；返回 { method, headers, body }。
     非表单请求会设置 JSON 的 Content-Type，并把 body 序列化为 JSON 字符串。*/
  const buildOpts = (token) => {
    const opts = {
      method,
      headers: { ...headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) },   // 有令牌时带上认证请求头
    }
    if (!isForm) opts.headers['Content-Type'] = 'application/json'
    if (body !== undefined) opts.body = isForm ? cloneForm(body) : JSON.stringify(body)
    return opts
  }

  /* fetch(url, options) 是浏览器内置的 HTTP 请求函数，返回 Promise<Response>。
     Response 的 status 是 HTTP 状态码，ok 表示状态码是否在 200-299 之间；
     json()/text()/blob() 用来读取响应体，但响应体只能读取一次。*/
  let res = await fetch(url, buildOpts(getAccess()))

  const isLoginCall = path.startsWith('/accounts/auth/login/') || path.startsWith('/accounts/auth/register/')   // 登录/注册本身不应触发刷新逻辑
  /* HTTP 401 Unauthorized 表示“未认证或令牌已过期”。
     这里的处理：如果是带 token 的普通请求且返回 401，先尝试用 refresh token 换新的 access token，再重发原请求；
     刷新后仍然是 401，则清除本地令牌并跳转登录页。登录/注册接口的 401 是账号密码错误，不在此处理。*/
  if (res.status === 401 && getAccess() && !isLoginCall) {
    const refresh = getRefresh()
    if (refresh) {
      try {
        const rr = await fetch('/api/token/refresh/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh }),   // 刷新接口要求提交 refresh token
        })
        const rd = await rr.json().catch(() => null)   // 解析失败时按 null 处理
        if (rr.ok && rd && rd.access) {
          setTokens(rd.access, rd.refresh || refresh)   // 后端可能同时返回新的 refresh token
          res = await fetch(url, buildOpts(rd.access))   // 用新 token 重发原请求
        }
      } catch (e) {
        // 刷新过程出错时继续走下面的 401 处理
      }
    }
    if (res.status === 401) {
      clearTokens()
      redirectToLogin()
    }
  }

  /* JSON.parse(字符串) 把 JSON 文本解析成 JavaScript 对象；JSON.stringify(对象) 则把对象序列化成 JSON 字符串。
     这里调用 res.json()，它相当于先读取响应文本再执行 JSON.parse；响应不是合法 JSON 时会被 catch 住并置为 null。*/
  let data = null
  try {
    data = await res.json()
  } catch (e) {
    data = null   // 204 无内容或非 JSON 响应
  }

  if (!res.ok) {
    // 从后端错误响应中尽量提取一条可展示的中文信息
    let msg = null
    if (data) {
      if (typeof data.detail === 'string') msg = data.detail
      else if (typeof data.msg === 'string') msg = data.msg
      else if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) msg = data.non_field_errors[0]
      else {
        // 常见 DRF 错误格式：{ 字段名: ["错误提示"] }，取第一个字符串作为提示
        for (const k of Object.keys(data)) {
          const v = data[k]
          if (Array.isArray(v) && v.length && typeof v[0] === 'string') { msg = v[0]; break }
          if (typeof v === 'string') { msg = v; break }
        }
      }
    }
    const err = new Error(msg || `请求失败(${res.status})`)   // 没有后端提示时使用状态码兜底
    err.status = res.status   // 调用方可据此判断 401/403/500 等
    err.data = data
    throw err
  }
  return data
}

/*对 request 的常用 HTTP 方法封装：各方法都返回 request 的 Promise。
   get(path) 查询；post(path, body) 新增；put/patch(path, body) 修改；del(path) 删除；upload(path, formData) 上传文件。*/
export const api = {
  get: (path) => request(path),   // GET：参数拼在 path 的查询串里
  post: (path, body) => request(path, { method: 'POST', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  patch: (path, body) => request(path, { method: 'PATCH', body }),
  del: (path) => request(path, { method: 'DELETE' }),
  upload: (path, formData) => request(path, { method: 'POST', body: formData }),   // 表单/文件上传，body 是 FormData
}
