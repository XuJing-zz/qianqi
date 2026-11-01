/*认证接口：登录、退出、获取当前用户、修改个人资料、注册*/
import { api, setTokens, clearTokens } from './client'

/*登录：参数 username 用户名、password 密码；返回登录用户对象（含角色 role）。
   流程：调用后端登录接口 -> 保存返回的 access/refresh 令牌到本地 -> 只把 user 返回给调用方。
   后端接口：POST /api/accounts/auth/login/。*/
export async function apiLogin(username, password) {
  const data = await api.post('/accounts/auth/login/', { username, password })
  setTokens(data.access, data.refresh)   // 令牌由 client 统一持久化
  return data.user
}

/*退出登录：无参数；返回 Promise<void>。
   先请求后端注销（把 refresh 令牌加入黑名单等），即使请求失败也继续清除本地令牌。*/
export async function apiLogout() {
  try {
    await api.post('/accounts/auth/logout/', { refresh: localStorage.getItem('qianqi_refresh') })
  } catch (e) {
    // 网络失败不阻止本地退出
  }
  clearTokens()
}

/*获取当前登录用户信息：无参数；返回用户对象。
   后端接口：GET /api/accounts/auth/me/，可用于校验 token 是否仍有效。*/
export async function apiMe() {
  return api.get('/accounts/auth/me/')
}

/*修改个人资料：参数 payload 包含昵称、头像、手机号等可修改字段；返回更新后的用户信息。
   后端接口：POST /api/accounts/auth/update-profile/。*/
export async function apiUpdateProfile(payload) {
  return api.post('/accounts/auth/update-profile/', payload)
}

/*注册新用户：参数 payload 包含用户名、密码、昵称等注册信息；返回注册结果。
   后端接口：POST /api/accounts/auth/register/。*/
export async function apiRegister(payload) {
  return api.post('/accounts/auth/register/', payload)
}
