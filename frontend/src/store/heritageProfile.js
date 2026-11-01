/*传承人个人资料状态：合并账号资料与传承人档案，供传承端“个人主页”读取和保存*/
import { reactive } from 'vue'
import { apiMe, apiUpdateProfile } from '@/api/auth'
import { apiMyInheritor, apiUpdateInheritor } from '@/api/heritage'
import { isLoggedIn } from './index'


/*当前登录传承人的资料：profileId 为传承人档案 ID，0 表示还没有档案；其余字段来自账号+档案*/
export const heritageProfile = reactive({
  profileId: 0,
  name: '',
  level: '',
  craft: '',
  bio: '',
  avatar: '',
  region: '',
  phone: '',
  mentor: '',
  intro: '',
  years: null,
  honor: '',
  certs: [],
})

/*传承人等级下拉选项*/
export const levelOptions = ['国家级', '省级', '市级']

/*传承技艺下拉选项*/
export const craftOptions = ['髹漆', '镏金', '雕漆', '螺钿', '描金', '描彩', '犀皮', '素髹', '百宝嵌', '填漆', '款彩', '堆漆']

/*
 * 加载当前传承人资料，分两步：
 * 1. apiMe 取账号级信息（昵称、头像、地区、电话、简介）；
 * 2. apiMyInheritor 取本人传承人档案并合并（等级、技艺、师承、年限、荣誉、证书）。
 * 未登录返回 false；档案不存在时 profileId 置 0；否则返回 true。
 */
export async function loadHeritageProfile() {
  if (!isLoggedIn()) return false
  try {
    const data = await apiMe()
    Object.assign(heritageProfile, {
      name: data.name || data.nick || '',
      avatar: data.avatar || '',
      region: data.region || '',
      phone: data.phone || '',
      bio: data.bio || '',
    })
  } catch (e) {
    return false
  }
  try {
    // 第二步：读取本人传承人档案；没有档案时接口会报错，由下面的 catch 把 profileId 置 0
    const mine = await apiMyInheritor()
    heritageProfile.profileId = mine.id
    Object.assign(heritageProfile, {
      name: mine.name || heritageProfile.name,
      level: mine.level || '',
      craft: mine.craft || '',
      phone: mine.phone || heritageProfile.phone,
      mentor: mine.mentor || '',
      years: mine.years,
      intro: mine.intro || '',
      honor: mine.honors || '',
      // Array.prototype.slice：slice() 不传参数时复制整个数组，这里复制证书数组，避免直接引用接口返回的数组
      certs: Array.isArray(mine.cert_files) ? mine.cert_files.slice() : [],
    })
  } catch (e) {
    heritageProfile.profileId = 0
  }
  return true
}

/*
 * 保存当前传承人资料：
 * 1. 调用 apiUpdateProfile 保存账号级资料，并合入本地 heritageProfile；
 * 2. 若已有传承人档案（profileId 非 0），再调用 apiUpdateInheritor 同步公开档案字段，
 *    这一步失败会被吞掉，不阻塞账号资料保存；
 * 3. 同步证书数组到本地缓存。
 * 参数 payload：要保存的字段；返回值 { ok:true } 或 { ok:false, msg }。
 */
export async function saveHeritageProfile(payload) {
  if (!isLoggedIn()) return { ok: false, msg: '未登录' }
  try {
    await apiUpdateProfile(payload)
    Object.assign(heritageProfile, payload)
    if (heritageProfile.profileId) {
      const pub = {
        name: payload.name ?? heritageProfile.name,
        level: payload.level ?? heritageProfile.level,
        craft: payload.craft ?? heritageProfile.craft,
        phone: payload.phone ?? heritageProfile.phone,
        mentor: payload.mentor ?? heritageProfile.mentor,
        years: payload.years ?? heritageProfile.years,
        intro: payload.intro ?? heritageProfile.intro,
      }
      if ('honor' in payload) pub.honors = payload.honor || ''
      if (Array.isArray(payload.cert_files)) pub.cert_files = payload.cert_files.slice()
      // 同步公开档案；即使失败也不影响账号资料已经保存成功的结果
      await apiUpdateInheritor(heritageProfile.profileId, pub).catch(() => {})
    }
    if (Array.isArray(payload.cert_files)) heritageProfile.certs = payload.cert_files.slice()
    return { ok: true }
  } catch (e) {
    return { ok: false, msg: (e.data && (e.data.detail || e.data.msg)) || '保存失败' }
  }
}
