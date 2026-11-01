/*路由表、路由守卫、路由跳转*/
/*模块用途：集中定义前端路由（URL 与页面组件的对应关系），并通过全局守卫控制登录与角色权限*/
import { createRouter, createWebHistory } from 'vue-router'   // 导入创建路由实例和历史模式的两个方法

// 以下为用户端页面组件：首页、档案、课程、商品、传承人、个人中心、关于等
import HomeView from '../views/user/home/Home.vue'
import ArchiveList from '../views/user/archive/ArchiveList.vue'
import ArchiveDetail from '../views/user/archive/ArchiveDetail.vue'
import CourseList from '../views/user/course/CourseList.vue'
import CourseDetail from '../views/user/course/CourseDetail.vue'
import ProductList from '../views/user/product/ProductList.vue'
import ProductDetail from '../views/user/product/ProductDetail.vue'
import InheritorShow from '../views/user/inheritor/InheritorShow.vue'
import InheritorDetail from '../views/user/inheritor/InheritorDetail.vue'
import Profile from '../views/user/profile/Profile.vue'
import MyEnroll from '../views/user/profile/MyEnroll.vue'
import MyOrder from '../views/user/profile/MyOrder.vue'
import MyFavorite from '../views/user/profile/MyFavorite.vue'
import MyAddress from '../views/user/profile/MyAddress.vue'
import Pay from '../views/user/profile/Pay.vue'
import MyLearn from '../views/user/profile/MyLearn.vue'
import About from '../views/user/about/About.vue'
import Contact from '../views/user/about/Contact.vue'
import Agreement from '../views/user/about/Agreement.vue'

// 以下为传承人工作台（/console）的页面组件
import ConsoleOverview from '../views/console/ConsoleOverview.vue'
import ConsoleCourses from '../views/console/ConsoleCourses.vue'
import ConsoleCourseEdit from '../views/console/ConsoleCourseEdit.vue'
import ConsoleWorks from '../views/console/ConsoleWorks.vue'
import ConsoleInventory from '../views/console/ConsoleInventory.vue'
import ConsoleSkills from '../views/console/ConsoleSkills.vue'
import ConsoleStudents from '../views/console/ConsoleStudents.vue'
import ConsoleTraining from '../views/console/ConsoleTraining.vue'
import ConsoleProfile from '../views/console/ConsoleProfile.vue'

// 以下为管理员后台（/admin）的页面组件
import AdminOverview from '../views/admin/AdminOverview.vue'
import AdminCourses from '../views/admin/AdminCourses.vue'
import AdminVideos from '../views/admin/AdminVideos.vue'
import AdminSkills from '../views/admin/AdminSkills.vue'
import AdminProductReview from '../views/admin/AdminProductReview.vue'
import AdminOrders from '../views/admin/AdminOrders.vue'
import AdminStudents from '../views/admin/AdminStudents.vue'
import AdminTraining from '../views/admin/AdminTraining.vue'
import AdminInheritors from '../views/admin/AdminInheritors.vue'
import AdminProducts from '../views/admin/AdminProducts.vue'
import AdminAccounts from '../views/admin/AdminAccounts.vue'
import AdminConfig from '../views/admin/AdminConfig.vue'
import AdminLogs from '../views/admin/AdminLogs.vue'
import AdminMessages from '../views/admin/AdminMessages.vue'
// 登录/注册页，以及全局状态工具（登录判断、当前用户、角色首页）
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import { isLoggedIn, authState, homeOf } from '../store'

let lastPortPath = ''   // 记录最近一次访问的工作台完整路径（如 /console/courses），用于后退时恢复
/* 判断路径是否属于工作台：/console 开头是传承人工作台，/admin 开头是管理员后台。
   参数 p：路径字符串；返回值：布尔值。*/
function isPortPath(p) {
  return p.startsWith('/console') || p.startsWith('/admin')
}
/* popstate 是浏览器事件：用户点击前进/后退按钮或调用 history.go()/back() 时触发。
   这里的目的：传承人/管理员登录后如果在工作台里点浏览器后退，退到了普通用户页面，就自动把他送回工作台。
   关键流程：读取当前用户角色 -> 判断角色是否是传承人/管理员 -> 判断当前地址是否已离开工作台 ->
   选出要回去的地址 -> 用 pushState 补一条历史记录，让地址栏回到工作台。*/
window.addEventListener('popstate', () => {
  const role = authState.user && authState.user.role   // 当前登录用户的角色
  if (role !== 'heritage' && role !== 'admin') return   // 普通用户或未登录不处理
  const here = window.location.pathname   // 当前浏览器地址的路径部分
  if (!isPortPath(here)) {
    // 优先回到上一次访问的工作台页面，没有记录时回到角色首页（/console 或 /admin）
    const backTo = isPortPath(lastPortPath) ? lastPortPath : homeOf(role)
    try {
      const cur = window.history.state   // 当前历史记录携带的 state 对象
      const position = cur && typeof cur.position === 'number' ? cur.position + 1 : window.history.length   // 估算新记录的位置，供路由内部使用
      const backUrl = window.location.pathname + window.location.search + window.location.hash   // 保存当前普通页面地址，便于以后返回
      const st = { back: backUrl, current: backTo, forward: null, position, scroll: null, replaced: false }
      /* history.pushState(state, title, url) 会向浏览器历史栈压入一条新记录，
         并修改地址栏的 URL，但不会刷新页面；state 可存放自定义数据，之后在 popstate 事件里能读到。*/
      window.history.pushState(st, '', backTo)
    } catch (e) {
      // 某些浏览器在特殊情况下可能抛错（如跨域限制），这里静默忽略，不影响页面
    }
  }
})

/* createRouter({ history, routes, scrollBehavior }) 用于创建路由实例：
   history 指定用哪种方式管理 URL，routes 是路由表，scrollBehavior 控制切换页面后的滚动位置。
   返回值是一个 router 对象，交给 app.use(router) 安装后，<router-view> 才能渲染页面。*/
const router = createRouter({
  /* createWebHistory(base) 表示使用 HTML5 History 模式：
     URL 形如 /course/1（没有 #），由浏览器 history API 管理；部署时服务器需把未知路径回退到 index.html。
     import.meta.env.BASE_URL 是 Vite 提供的应用基础路径。*/
  history: createWebHistory(import.meta.env.BASE_URL),
  /* 路由切换后的滚动行为：to 是目标路由，from 是来源路由，savedPosition 是浏览器前进/后退时保存的位置。
     返回 savedPosition 表示恢复原来的滚动位置；否则回到页面顶部。*/
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
  // 路由表：每个对象是一条路由规则，path 是地址，name 是唯一名称，component 是对应页面组件
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/archive',
      name: 'archive-list',
      component: ArchiveList,
    },
    // :id 是动态路径参数，例如 /archive/12 中的 12 会被当作 id，页面里可通过 route.params.id 读取
    {
      path: '/archive/:id',
      name: 'archive-detail',
      component: ArchiveDetail,
    },
    {
      path: '/course',
      name: 'course-list',
      component: CourseList,
    },
    {
      path: '/course/:id',
      name: 'course-detail',
      component: CourseDetail,
    },
    {
      path: '/product',
      name: 'product-list',
      component: ProductList,
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetail,
    },
    {
      path: '/inheritor',
      name: 'inheritor-list',
      component: InheritorShow,
    },
    {
      path: '/inheritor/:id',
      name: 'inheritor-detail',
      component: InheritorDetail,
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
    },
    {
      path: '/profile/enroll',
      name: 'profile-enroll',
      component: MyEnroll,
    },
    {
      path: '/profile/order',
      name: 'profile-order',
      component: MyOrder,
    },
    {
      path: '/profile/favorite',
      name: 'profile-favorite',
      component: MyFavorite,
    },
    {
      path: '/profile/address',
      name: 'profile-address',
      component: MyAddress,
    },
    {
      path: '/pay/:courseId',
      name: 'pay',
      component: Pay,
    },
    {
      path: '/learn/:courseId',
      name: 'learn',
      component: MyLearn,
    },
    {
      path: '/about',
      name: 'about',
      component: About,
    },
    {
      path: '/contact',
      name: 'contact',
      component: Contact,
    },
    {
      path: '/agreement',
      name: 'agreement',
      component: Agreement,
    },

    // 传承人工作台路由（需要 heritage 角色，具体校验在下面的 beforeEach 守卫中）
    {
      path: '/console',
      name: 'console-overview',
      component: ConsoleOverview,
    },
    {
      path: '/console/works',
      name: 'console-works',
      component: ConsoleWorks,
    },
    {
      path: '/console/courses',
      name: 'console-courses',
      component: ConsoleCourses,
    },
    {
      path: '/console/courses/new',
      name: 'console-course-new',
      component: ConsoleCourseEdit,
    },
    {
      path: '/console/courses/:id/edit',
      name: 'console-course-edit',
      component: ConsoleCourseEdit,
    },
    {
      path: '/console/skills',
      name: 'console-skills',
      component: ConsoleSkills,
    },
    {
      path: '/console/inventory',
      name: 'console-inventory',
      component: ConsoleInventory,
    },
    {
      path: '/console/students',
      name: 'console-students',
      component: ConsoleStudents,
    },
    {
      path: '/console/training',
      name: 'console-training',
      component: ConsoleTraining,
    },
    {
      path: '/console/profile',
      name: 'console-profile',
      component: ConsoleProfile,
    },

    // 管理员后台路由（需要 admin 角色，具体校验在下面的 beforeEach 守卫中）
    {
      path: '/admin',
      name: 'admin-overview',
      component: AdminOverview,
    },
    {
      path: '/admin/courses',
      name: 'admin-courses',
      component: AdminCourses,
    },
    {
      path: '/admin/videos',
      name: 'admin-videos',
      component: AdminVideos,
    },
    {
      path: '/admin/skills',
      name: 'admin-skills',
      component: AdminSkills,
    },
    {
      path: '/admin/product-review',
      name: 'admin-product-review',
      component: AdminProductReview,
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: AdminOrders,
    },
    {
      path: '/admin/students',
      name: 'admin-students',
      component: AdminStudents,
    },
    {
      path: '/admin/training',
      name: 'admin-training',
      component: AdminTraining,
    },
    {
      path: '/admin/inheritors',
      name: 'admin-inheritors',
      component: AdminInheritors,
    },
    {
      path: '/admin/products',
      name: 'admin-products',
      component: AdminProducts,
    },
    {
      path: '/admin/config',
      name: 'admin-config',
      component: AdminConfig,
    },
    {
      path: '/admin/logs',
      name: 'admin-logs',
      component: AdminLogs,
    },
    {
      path: '/admin/accounts',
      name: 'admin-accounts',
      component: AdminAccounts,
    },
    {
      path: '/admin/messages',
      name: 'admin-messages',
      component: AdminMessages,
    },

    // 登录、注册页
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
  ],
})

/* router.afterEach(回调) 注册“每次导航完成之后”执行的钩子，常用于统计、记录日志或修改页面标题。
   参数 to 是导航完成后的目标路由对象；这里如果目标属于工作台，就记录其完整路径，供上面的 popstate 逻辑恢复使用。*/
router.afterEach((to) => {
  if (isPortPath(to.path)) {
    lastPortPath = to.fullPath   // fullPath 包含查询参数，例如 /console/courses?page=2
  }
})


/* router.beforeEach(回调) 注册“每次导航开始之前”执行的钩子，用来做登录校验和角色权限拦截。
   回调参数 to 是即将进入的路由对象；返回值决定导航结果：
   - 不返回（undefined）或返回 true：放行；
   - 返回 { path, query }：取消原导航并重定向到新地址，常用于跳到登录页。
   下面的判断顺序是：需要登录的普通页面 -> 支付页角色限制 -> 工作台/后台角色限制 -> 工作台用户禁止访问用户端。*/
router.beforeEach((to) => {
  const needHeritage = to.path.startsWith('/console')   // 目标是否是传承人工作台
  const needAdmin = to.path.startsWith('/admin')   // 目标是否是管理员后台

  // 这些前缀的页面必须登录后才能访问（课程/商品详情、支付、学习、个人中心子页）
  const needLoginPage =
    to.path.startsWith('/course/') ||
    to.path.startsWith('/product/') ||
    to.path.startsWith('/pay') ||
    to.path.startsWith('/learn') ||
    to.path.startsWith('/profile/')

  if (needLoginPage && !isLoggedIn()) {
    // 未登录：跳转登录页；query.redirect 记住原目标地址，登录成功后可以回到这里
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // 支付页只允许普通用户（user）；传承人和管理员访问时跳回各自首页
  if (to.path.startsWith('/pay') && isLoggedIn() && authState.user?.role !== 'user') {
    return homeOf(authState.user?.role)
  }

  if (needHeritage || needAdmin) {
    if (!isLoggedIn()) {
      // 未登录访问工作台/后台：先登录
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    const role = authState.user?.role   // 已登录用户的角色
    if (needHeritage && role !== 'heritage') {
      // 非传承人访问 /console：送回该角色自己的首页
      return homeOf(role)
    }
    if (needAdmin && role !== 'admin') {
      // 非管理员访问 /admin：送回该角色自己的首页
      return homeOf(role)
    }
  }

  // 已登录的传承人/管理员只能待在各自工作台、登录页和注册页；访问普通用户页面会被送回工作台首页
  const role = authState.user?.role
  if (isLoggedIn() && (role === 'heritage' || role === 'admin')) {
    const isWorkstationPort =
      to.path.startsWith('/console') ||
      to.path.startsWith('/admin') ||
      to.path === '/login' ||
      to.path === '/register'
    if (!isWorkstationPort) {
      return homeOf(role)
    }
  }

})

export default router
