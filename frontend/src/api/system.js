/*系统接口：操作日志查询/记录/导出，系统配置读取/保存、Logo 上传、初始化数据*/
import { api } from './client'
import { qs } from './utils'

/*查询操作日志：参数 params 可含分页、类型、操作人、时间范围等；返回日志数组或分页结果。
   后端接口：GET /api/system/logs/。*/
export function listLogs(params = {}) {
  return api.get('/system/logs/' + qs(params))
}
/*新增操作日志：参数 payload 包含日志类型、内容、操作人等；返回创建结果。
   后端接口：POST /api/system/logs/。*/
export function createLog(payload) {
  return api.post('/system/logs/', payload)
}
/*导出操作日志为 CSV 文件：参数 params 是筛选条件；返回 Promise<void>，完成后浏览器自动下载。
   流程：读取 token -> fetch 导出接口拿到 Blob -> 用 createObjectURL 生成临时地址 ->
   创建隐藏的 <a> 标签并触发 click 下载 -> 移除标签并释放临时地址。
   后端接口：GET /api/system/logs/export/。*/
export function exportLogs(params = {}) {
  const token = localStorage.getItem('qianqi_token')
  const query = qs(params)
  return fetch('/api/system/logs/export/' + query, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
    .then((res) => {
      if (!res.ok) throw new Error('导出失败')
      return res.blob()   // 把响应转成二进制文件内容
    })
    .then((blob) => {
      const url = URL.createObjectURL(blob)   // 为 Blob 创建一个临时可访问地址
      const a = document.createElement('a')   // 动态创建下载链接
      a.href = url
      a.download = 'operation_logs.csv'   // 指定下载文件名
      document.body.appendChild(a)
      a.click()   // 模拟点击触发下载
      a.remove()   // 下载后移除临时元素
      URL.revokeObjectURL(url)   // 释放临时地址，避免内存泄漏
    })
}
/*读取全部系统配置：无参数；返回配置对象（平台名称、Logo、首页配置、上传限制等）。
   后端接口：GET /api/system/config/all/。*/
export function getConfig() {
  return api.get('/system/config/all/')
}
/*保存系统配置：参数 payload 是配置键值对象；返回保存结果。
   后端接口：POST /api/system/config/save/。*/
export function saveConfig(payload) {
  return api.post('/system/config/save/', payload)
}
/*上传系统 Logo：参数 formData 是已经包装好文件的 FormData；返回 Logo 地址/配置信息。
   后端接口：POST /api/system/config/upload_logo/。*/
export function uploadLogo(formData) {
  return api.upload('/system/config/upload_logo/', formData)
}
/*初始化演示/基础数据：无参数；返回处理结果（通常只有管理员可用）。
   后端接口：POST /api/system/config/init/。*/
export function initData() {
  return api.post('/system/config/init/', {})
}
