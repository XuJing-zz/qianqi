<!-- 用户协议页：循环展示协议各章节内容，并提供联系入口 -->
<template>
  <div class="agreement-page">
    <!-- 全站顶部导航 -->
    <Nav />

    <div class="ua-wrap">
      <!-- 首屏：协议标题与更新日期 -->
      <header class="ua-hero">
        <span class="ua-hero-seal">约</span>
        <h1 class="ua-hero-title">用户协议</h1>
        <span class="ua-hero-en">TERMS OF SERVICE</span>
        <div class="ua-hero-line"></div>
        <p class="ua-hero-note">更新日期：2026 年 08 月 15 日</p>
      </header>

      <div class="ua-body">
        <!-- 协议正文：逐章渲染标题、段落，以及可选的条目列表 -->
        <section v-for="(sec, i) in sections" :key="i" class="ua-section">
          <h2 class="ua-section-title">
            <span class="ua-section-num">{{ numOf(i) }}</span>{{ sec.title }}
          </h2>
          <p v-for="(p, j) in sec.paras" :key="j" class="ua-para">{{ p }}</p>
          <ul v-if="sec.items && sec.items.length" class="ua-list">
            <li v-for="(it, k) in sec.items" :key="k" class="ua-item">{{ it }}</li>
          </ul>
        </section>

        <!-- 协议结尾：生效说明与联系方式入口 -->
        <div class="ua-foot">
          <p class="ua-foot-line">本协议自发布日期起生效。千漆保留依据法律法规及平台运营需要对协议进行更新调整的权利，更新后的协议将在本页面公示。</p>
          <p class="ua-foot-line">如您对本协议有任何疑问，欢迎通过「联系我们」与我们取得联系。</p>
          <button class="ua-btn ua-btn-solid" @click="goContact">联系我们</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Nav from '@/views/user/common/nav.vue'

// 路由实例：用于跳转到联系页
const router = useRouter()

/* 协议数据：每个章节包含标题 title、段落数组 paras 和可选的条目数组 items */
const sections = [
  {
    title: '协议的接受',
    paras: [
      '欢迎使用千漆平台（以下简称「平台」或「本平台」）。本平台是基于 Django 的漆器技艺教学与文创进销存管理系统，致力于非遗漆器技艺的传承、教学与文创推广。',
      '当您访问、注册或使用本平台提供的任何服务时，即视为您已阅读、理解并同意本《用户协议》的全部内容。如您不同意本协议的任何条款，请停止使用本平台的服务。',
    ],
  },
  {
    title: '服务内容',
    paras: [
      '本平台为用户提供漆器技艺学习、文创作品展示与收藏、传承人信息展示等服务，具体服务内容以平台实际提供的功能为准。',
    ],
    items: [
      '技艺教学：体验课程、系统课程、大师亲授等体系化课程信息展示与报名；',
      '文创推广：传承人作品的策展式展示与收藏；',
      '传承人扶持：认证传承人的信息展示与作品、课程关联。',
    ],
  },
  {
    title: '账户注册与安全',
    paras: [
      '您在使用本平台部分功能（如报名、收藏、下单等）时，可能需要注册账户。您应提供真实、准确、完整的个人信息，并妥善保管账户及密码。',
      '因您自身原因造成的账户、密码泄露或不当使用导致的损失，由您自行承担。如发现账户存在异常，请及时联系我们。',
    ],
  },
  {
    title: '知识产权',
    paras: [
      '本平台展示的传承人信息、课程内容、文创作品图片及文字介绍等内容的著作权及其他知识产权，归原作者、传承人或平台所有。',
      '未经权利人书面许可，任何单位或个人不得以复制、转载、传播、商用等任何方式使用上述内容。用户在本平台提交的留言、反馈等内容，视为授权平台用于改进服务。',
    ],
  },
  {
    title: '用户行为规范',
    paras: [
      '您在使用本平台时，应遵守中华人民共和国法律法规及社会公序良俗，不得利用本平台从事任何违法违规活动。',
    ],
    items: [
      '不得发布、传播违反法律法规或含有违法、有害、侵权等内容的信息；',
      '不得恶意攻击、干扰或破坏本平台的正常运行；',
      '不得冒用他人身份或进行任何欺诈行为；',
      '不得利用平台漏洞谋取不正当利益。',
    ],
  },
  {
    title: '免责声明',
    paras: [
      '本平台正在持续完善中，部分展示数据为演示数据。平台将尽合理努力保证服务的稳定性与信息的准确性，但对于因不可抗力、系统维护、网络故障等原因导致的服务中断或信息误差，平台不承担相应责任。',
      '本平台展示的作品、课程等信息以实际为准，交易相关事项请以双方另行约定为准。',
    ],
  },
  {
    title: '协议的变更与终止',
    paras: [
      '平台有权根据需要不时修改本协议，修改后的协议将在本页面公告，并自公告之日或约定的日期起生效。如您继续使用本平台，即视为接受修改后的协议。',
    ],
  },
  {
    title: '法律适用与争议解决',
    paras: [
      '本协议的订立、履行、解释及争议解决均适用中华人民共和国法律。因本协议产生的争议，双方应友好协商解决；协商不成的，任何一方均可向有管辖权的人民法院提起诉讼。',
    ],
  },
]

/* 章节序号：把 0 起始的下标转换成中文数字 */
const chineseNum = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
function numOf(i) {
  return chineseNum[i] || i + 1
}

/* 跳转到「联系我们」页面 */
function goContact() {
  router.push('/contact')
}
</script>

<style src="./Agreement.css"></style>
