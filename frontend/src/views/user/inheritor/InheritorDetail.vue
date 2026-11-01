<!-- 传承人详情页：展示个人档案、荣誉证书、技艺专长、代表作品与在授课程 -->
<template>
  <div class="inheritor-detail-page">
    <!-- 首屏：传承人头像、姓名、级别、技艺与简介 -->
    <header v-if="master" class="id-hero">
      <div class="id-detail-head">
        <div class="detail-avatar">
          <span class="id-detail-glyph">{{ glyphOf(master) }}</span>
        </div>
        <div class="detail-head-info">
          <div class="id-detail-seal">匠 心 传 人</div>
          <h1 class="id-detail-name">{{ master.name }}</h1>
          <p class="detail-level">
            <span class="id-verified">✓</span>{{ master.level }}非遗传承人 · {{ master.craft }}技艺
          </p>
          <p class="detail-bio">{{ master.intro }}</p>
        </div>
      </div>
    </header>

    <Nav />

    <div class="id-detail-wrap" v-if="master">
      <!-- 返回传承人列表 -->
      <button class="id-back-btn" @click="goBack">‹ 返回传承人</button>

      <!-- 传承档案：性别、年龄、从艺年限、师承、资质、联系方式 -->
      <section class="id-block">
        <div class="id-section-head">
          <h2 class="id-section-cn">传承档案</h2>
          <span class="id-section-en">PROFILE</span>
        </div>
        <div class="profile-grid">
          <div class="profile-item"><span class="profile-label">性别</span><span class="profile-value">{{ master.gender || '—' }}</span></div>
          <div class="profile-item"><span class="profile-label">年龄</span><span class="profile-value">{{ master.age || '—' }}</span></div>
          <div class="profile-item"><span class="profile-label">从艺年限</span><span class="profile-value">{{ master.years || 0 }} 年</span></div>
          <div class="profile-item"><span class="profile-label">师承关系</span><span class="profile-value">{{ master.mentor || '—' }}</span></div>
          <div class="profile-item"><span class="profile-label">教学资质</span><span class="profile-value">{{ master.qual || '—' }}</span></div>
          <div class="profile-item"><span class="profile-label">联系方式</span><span class="profile-value">{{ master.phone || '—' }}</span></div>
        </div>
      </section>

      <!-- 所获荣誉：文字荣誉标签 + 可下载的证书附件 -->
      <section class="id-block" v-if="honors.length || certs.length">
        <div class="id-section-head">
          <h2 class="id-section-cn">所获荣誉</h2>
          <span class="id-section-en">HONORS</span>
        </div>
        <div v-if="honors.length" class="honor-tags">
          <span v-for="(h, i) in honors" :key="i" class="honor-tag">{{ h }}</span>
        </div>
        <div v-if="certs.length" class="honor-certs">
          <div v-for="(c, i) in certs" :key="i" class="honor-cert">
            <span class="honor-cert-glyph">{{ certGlyph(c) }}</span>
            <a class="honor-cert-link" :href="c.url" target="_blank" rel="noopener">{{ c.name }}</a>
          </div>
        </div>
      </section>

      <!-- 技艺专长：该传承人名下已审核的技艺档案，点击进入技艺详情 -->
      <section class="id-block" v-if="masterSkills.length">
        <div class="id-section-head">
          <h2 class="id-section-cn">技艺专长</h2>
          <span class="id-section-en">SKILLS</span>
        </div>
        <div class="works-grid">
          <div
            v-for="sk in masterSkills"
            :key="sk.id"
            class="id-work-card"
            @click="goArchive(sk.id)"
          >
            <div class="work-cover" :style="skillCoverStyle(sk)">
              <span v-if="!sk.image" class="id-work-glyph">{{ sk.glyph || (sk.name || '').charAt(0) }}</span>
            </div>
            <h4 class="id-work-name">{{ sk.name }}</h4>
            <p class="work-sub">{{ sk.level }}非遗 · {{ sk.category }}</p>
          </div>
        </div>
      </section>

      <!-- 代表作品：该传承人已审核的文创作品，点击进入作品详情 -->
      <section class="id-block" v-if="masterWorks.length">
        <div class="id-section-head">
          <h2 class="id-section-cn">代表作品</h2>
          <span class="id-section-en">WORKS</span>
        </div>
        <div class="works-grid">
          <div
            v-for="w in masterWorks"
            :key="w.id"
            class="id-work-card"
            @click="goProduct(w.id)"
          >
            <div class="work-cover" :style="coverStyle(w)">
              <span class="id-work-glyph">{{ w.glyph }}</span>
            </div>
            <h4 class="id-work-name">{{ w.name }}</h4>
            <p class="work-sub">{{ w.craft }} · {{ w.category }}</p>
          </div>
        </div>
      </section>

      <!-- 在授课程：按授课人姓名匹配课程，点击进入课程详情 -->
      <section class="id-block" v-if="masterCourses.length">
        <div class="id-section-head">
          <h2 class="id-section-cn">在授课程</h2>
          <span class="id-section-en">COURSES</span>
        </div>
        <div class="courses-list">
          <div
            v-for="c in masterCourses"
            :key="c.id"
            class="course-row"
            @click="goCourse(c.id)"
          >
            <div class="course-row-glyph">{{ c.glyph }}</div>
            <div class="course-row-body">
              <h4 class="course-row-name">{{ c.name }}</h4>
              <p class="course-row-sub">{{ c.stage }} · {{ c.duration }} · {{ c.region }}</p>
            </div>
            <span class="course-row-arrow">›</span>
          </div>
        </div>
      </section>

      <!-- 作品与课程都为空时的提示 -->
      <div v-if="!masterWorks.length && !masterCourses.length" class="id-detail-empty">
        <p class="id-empty-text">该传承人暂未发布作品与课程</p>
      </div>
    </div>

    <!-- 找不到该传承人时的空状态 -->
    <div v-else class="id-detail-empty">
      <p class="id-empty-text">未找到该传承人</p>
      <button class="id-btn" @click="goBack">返回传承人列表</button>
    </div>
  </div>
</template>

<script setup>
/* 传承人详情：按路由 id 取传承人，并从共享状态关联其技艺、作品与课程 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'
import { inheritors, loadInheritors, heritageSkills, loadSkills, heritageProducts, loadProducts, courses, ensureCourses } from '@/store'

const route = useRoute()
const router = useRouter()

// 进入页面时并行加载传承人、作品、课程、技艺数据；单个请求失败不影响其他数据
onMounted(() => {
  Promise.all([
    loadInheritors().catch(() => {}),
    loadProducts().catch(() => {}),
    ensureCourses().catch(() => {}),
    loadSkills().catch(() => {}),
  ])
})

/* 当前传承人：把路由参数转成数字后查找，找不到返回 null */
const master = computed(() => {
  const id = Number(route.params.id)
  return inheritors.find((m) => m.id === id) || null
})

/* 头像占位字：优先取技艺首字，其次姓名首字，最后用「匠」兜底 */
function glyphOf(m) {
  return (m.craft || m.name || '匠').charAt(0)
}

/* 代表作品：按传承人姓名关联已审核通过的作品 */
const masterWorks = computed(() => {
  if (!master.value) return []
  return heritageProducts
    .filter((p) => p.status === 'approved' && p.inheritor === master.value.name)
    .map((p) => ({
      id: p.id,
      glyph: p.glyph || p.name.charAt(0),
      name: p.name,
      craft: p.craft,
      category: p.category,
      cover: p.cover || '',
    }))
})

/* 在授课程：按授课人姓名关联课程 */
const masterCourses = computed(() => {
  if (!master.value) return []
  return courses
    .filter((c) => c.teacher === master.value.name)
    .map((c) => ({ id: c.id, glyph: c.glyph, name: c.name, stage: c.stage, duration: c.duration, region: c.region }))
})

/* 技艺专长：按 ownerName 关联已审核通过的技艺档案 */
const masterSkills = computed(() => {
  if (!master.value) return []
  return heritageSkills.filter((s) => s.status === 'approved' && s.ownerName === master.value.name)
})

/* 荣誉：把以「｜」分隔的字符串拆成标签数组 */
const honors = computed(() =>
  (master.value?.honors || '').split('｜').map((x) => x.trim()).filter(Boolean)
)

/* 证书附件：仅当 cert_files 是数组时才使用，避免脏数据报错 */
const certs = computed(() =>
  Array.isArray(master.value?.cert_files) ? master.value.cert_files : []
)
/* 证书图标：文档类附件显示「文」，图片类显示奖牌图标 */
function certGlyph(c) {
  return (c.name || '').match(/\.(pdf|docx?|xlsx?|pptx?)$/i) ? '文' : '🏅'
}

/* 作品封面样式：有封面时生成背景图 */
function coverStyle(p) {
  if (p.cover) {
    return { backgroundImage: 'url(' + p.cover + ')' }
  }
  return {}
}
/* 技艺封面样式：有图片时生成背景图 */
function skillCoverStyle(sk) {
  if (sk.image) {
    return { backgroundImage: 'url(' + sk.image + ')' }
  }
  return {}
}

/* 以下为各类详情页与返回列表的跳转 */
function goProduct(id) {
  router.push('/product/' + id)
}
function goCourse(id) {
  router.push('/course/' + id)
}
function goArchive(id) {
  router.push('/archive/' + id)
}
function goBack() {
  router.push('/inheritor')
}
</script>

<style src="./InheritorDetail.css"></style>
