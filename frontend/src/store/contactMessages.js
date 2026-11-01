/*联系留言状态：维护后台收到的用户留言列表，并提供处理/回复和删除操作*/
import { reactive } from 'vue'
import { listContactMessages, handleContactMessage, removeContactMessage } from '@/api/contact'


/*留言列表：由 loadContactMessages 填充，后台布局用它统计待处理留言数量*/
export const contactMessages = reactive([])

/*留言状态映射表：new 待处理、handled 已处理*/
export const messageStatusMap = { 
  new: { label: '待处理', color: '#c62828' },
  handled: { label: '已处理', color: '#2e7d32' },
}

/*
 * 留言字段映射：统一成驼峰命名，补全标题、内容、状态、回复默认值；
 * 后端 createdAt 为下划线命名 created_at，这里转换成 createdAt。
 * 参数 m：后端留言；返回值：前端留言对象。
 */
function mapMsg(m) {
  return {   
    id: m.id,     
    name: m.name || '',
    contact: m.contact || '',
    subject: m.subject || '',
    message: m.message || '', 
    status: m.status || 'new',
    reply: m.reply || '',
    createdAt: m.created_at || '',
  }
}

/*
 * 加载联系留言：调用 listContactMessages(params)（可带状态等筛选条件），
 * 映射后整体替换 contactMessages；返回值：更新后的留言列表。
 */
export async function loadContactMessages(params = {}) {
  const data = await listContactMessages(params)
  contactMessages.splice(0, contactMessages.length, ...data.map(mapMsg))
  return contactMessages
}

/*
 * 处理/回复留言：参数可传留言对象或 ID；调用 handleContactMessage(id, { status, reply })，
 * 成功后按下标替换列表中的留言；返回值：更新后的留言（列表中没有该项时为 undefined）。
 */
export async function handleMessageAction(msgOrId, payload) {
  const id = typeof msgOrId === 'object' ? msgOrId.id : msgOrId
  const updated = await handleContactMessage(id, {
    status: payload.status,
    reply: payload.reply ?? '',
  })
  const idx = contactMessages.findIndex((x) => x.id === id)
  if (idx >= 0) contactMessages[idx] = mapMsg(updated)
  return contactMessages[idx]
}

/*
 * 删除留言：参数可传留言对象或 ID；调用 removeContactMessage(id)，
 * 成功后从 contactMessages 中移除；无返回值。
 */
export async function removeMessageAction(msgOrId) {
  const id = typeof msgOrId === 'object' ? msgOrId.id : msgOrId
  await removeContactMessage(id)
  const idx = contactMessages.findIndex((x) => x.id === id)
  if (idx >= 0) contactMessages.splice(idx, 1)
}
