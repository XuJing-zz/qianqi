/*公共端课程状态：缓存已审核通过的课程列表，供前台首页、课程列表、课程详情等页面共享*/
import { reactive } from 'vue'
import { listCourses, getCourse } from '@/api/courses'
import { mapKeys } from '@/api/utils'

/*公共课程列表：由 loadCourses / ensureCourses 填充，前台页面直接读取*/
export const courses = reactive([])

/*
 * 把后端课程数据转换成前台展示用的课程对象。
 * 参数 c：后端返回的单条课程；返回值：字段补全后的课程对象。
 * 主要做三件事：把下划线字段转成驼峰、补默认文案、补全章节的缺省字段。
 */
function mapPublicCourse(c) {
  const m = mapKeys(c)
  // 教师名缺省时显示“非遗传承人”，避免详情页出现空白
  const teacher = m.ownerName || '非遗传承人'
  const name = m.name || ''
  return {
    ...m,
    glyph: m.glyph || name.charAt(0) || '漆',
    teacher,
    level: m.level || '',
    region: m.region || '',
    price: m.priceNum != null ? '¥' + m.priceNum : '',
    priceNum: m.priceNum ?? 0,
    flag: m.flag || '',
    intro: m.intro || m.desc || '',
    masterBio: m.masterBio || '',
    notices: m.notices || [],
    // 逐个章节补全标题、地址、视频、排课时间等默认值
    lessons: (m.lessons || []).map((l) => ({
      ...l,
      title: l.title || '',
      desc: l.desc || '',
      address: l.address || '',
      video: l.video || '',
      videoStatus: l.videoStatus || 'draft',
      scheduleDate: l.scheduleDate || '',
      scheduleTime: l.scheduleTime || '',
    })),
  }
}

/*
 * 加载公共课程：调用 listCourses({ status: 'approved' }) 只取已审核通过的课程，
 * 并用结果整体替换本地 courses；返回值：更新后的 courses。
 */
export async function loadCourses() {
  const data = await listCourses({ status: 'approved' })
  // splice：splice(起始下标, 删除个数, ...新元素) 可原地增删数组；这里删除全部旧元素并插入新数据，保持数组引用不变
  courses.splice(0, courses.length, ...data.map(mapPublicCourse))
  return courses
}

/*
 * 获取单门课程详情：调用 getCourse(id)，返回映射后的课程对象（不写入 courses 缓存）。
 * 参数 id：课程 ID；返回值：可直接渲染的课程详情。
 */
export async function fetchCourseDetail(id) {
  const raw = await getCourse(id)
  return mapPublicCourse(raw)
}

// 模块级标记：记录公共课程是否已成功加载过，避免多个页面重复发请求
let _loaded = false
/*
 * 确保公共课程已加载：已加载且缓存非空时直接返回，否则先调用 loadCourses 再返回。
 * 返回值：courses 列表；适合页面初始化时调用，减少重复请求。
 */
export async function ensureCourses() {
  if (_loaded && courses.length) return courses
  await loadCourses()
  _loaded = true
  return courses
}
