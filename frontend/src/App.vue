<!-- 应用根组件：负责渲染当前路由页面，并在用户端页面底部显示公共页脚 -->
<!-- <template>：<template> 是 Vue 单文件组件（SFC）的模板部分，用来编写页面的 HTML 结构；Vue 会把其中以 v- 开头的指令和 {{ }} 插值编译成动态渲染逻辑。 -->
<template>
  <div class="app-shell">
    <div class="app-content">
      <!-- <router-view>：<router-view> 是路由占位组件：当前 URL 匹配到哪个路由，就把该路由对应的页面组件渲染在这个位置。 -->
      <router-view />
    </div>
    <!-- v-if：v-if 是条件渲染指令：showFoot 为 true 时才渲染 <Foot> 组件，为 false 时该组件不会出现在 DOM 中。 -->
    <Foot v-if="showFoot" />
  </div>
</template>

<script setup>
/* <script setup> 是 Vue 3 组合式 API 的语法糖：脚本在组件创建时执行，
   顶层声明的变量、函数和导入的组件可以直接在模板中使用，不需要再写 return 或注册 components。 */
// computed：computed(getter) 创建一个计算属性：结果由依赖的响应式数据自动计算并缓存，依赖变化时才重新计算；在代码中通过 showFoot.value 读取结果。
import { computed } from 'vue'
// useRoute：useRoute() 返回当前路由对象 route，可读取 route.path、route.query、route.params 等信息（只读，适合用来判断当前页面）。
import { useRoute } from 'vue-router'
import Foot from '@/views/user/common/foot.vue'   // 公共页脚组件

const route = useRoute()   // 当前路由对象

/* 计算是否显示页脚：传承人工作台（/console）和管理员后台（/admin）有自己的布局，登录页也不需要页脚，
   其余普通用户页面都显示页脚。返回值：布尔值，true 表示显示页脚。*/
const showFoot = computed(() => {
  const p = route.path   // 当前页面路径，例如 /course/1
  // 依次排除工作台、后台和登录页
  return !p.startsWith('/console') && !p.startsWith('/admin') && p !== '/login'
})
</script>

<style>
/* <style>：<style> 是单文件组件的样式区，用来编写当前组件的 CSS；本文件中的样式会全局生效。 */
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.app-content {
  flex: 1 0 auto;
  display: flex;
  flex-direction: column;
}
</style>
