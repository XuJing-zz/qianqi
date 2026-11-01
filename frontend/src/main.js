
/*应用入口：创建 Vue 应用、注册路由与 Element Plus，并在启动时预加载公共配置和当前用户数据*/
import { createApp, watch } from 'vue'   // 导入创建应用实例的 createApp 和监听数据变化的 watch
import ElementPlus from 'element-plus'   // Element Plus UI 组件库，注册后模板中可直接使用 el-button、el-table 等组件
import 'element-plus/dist/index.css'   // 引入 Element Plus 的全局样式
import './assets/base.css'   // 引入项目自定义的基础样式
import App from './App.vue'   // 根组件，所有页面都渲染在它内部
import router from './router'   // 路由实例（URL 与页面组件的对应关系）
import { isLoggedIn, loadUserData, loadCourses, loadInheritors, loadConfig, systemConfig } from './store'   // 全局状态与数据加载方法

// 应用启动时预加载“传承人”和“课程”公共数据；catch(() => {}) 表示加载失败也不阻塞页面渲染
loadInheritors().catch(() => {})
loadCourses().catch(() => {})

// 预加载系统配置（如平台名称、Logo、首页配置等）
loadConfig().catch(() => {})
/* watch(监听源, 回调函数, 配置项) 用来监听响应式数据的变化。
   第一个参数写成 getter 函数 () => systemConfig.systemName，表示监听系统配置中的平台名称；
   第二个参数 (name) 是变化后的新值，这里把它同步到浏览器标签页标题；
   第三个参数 { immediate: true } 表示创建监听后立即先执行一次回调，保证首屏标题也正确。*/
watch(
  () => systemConfig.systemName,
  (name) => {
    document.title = name || '漆器非遗传承平台'   // 配置为空时使用默认标题
  },
  { immediate: true },
)

// 如果本地保存的登录状态有效，则拉取当前用户的收藏、报名、订单等数据
if (isLoggedIn()) {
  loadUserData().catch(() => {})
}

/* createApp(根组件) 根据根组件创建一个 Vue 应用实例，
   后续的插件注册、全局配置和挂载都基于这个 app 对象进行。*/
const app = createApp(App)
// app.use：app.use(插件) 用于安装插件；这里安装路由插件，让应用支持页面跳转和 <router-view>
app.use(router)
// 同样通过 app.use 注册 Element Plus，使所有组件都能直接使用其 UI 组件
app.use(ElementPlus)
// app.mount：app.mount('#app') 把应用挂载到 public/index.html 中 id="app" 的 DOM 元素上，页面开始渲染
app.mount('#app')
