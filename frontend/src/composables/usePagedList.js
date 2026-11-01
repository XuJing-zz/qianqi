/*分页处理（公共）*/
import { ref } from 'vue'   //{}是具名导入 只导入ref这一个  ref是vue3中响应式的一个方法  用来创建响应式数据
// 导入element-plus的消息提示组件
// ElMessage.error()是element-plus提供的一个方法，用来显示错误消息
import { ElMessage } from 'element-plus'

export function usePagedList({ fetchPage, map = (x) => x, pageSize = 8, errorText = '加载失败' }) { 
  /*export function usePagedList是一个导出函数，接受一个对象作为参数，该对象包含fetchPage、map、pageSize和errorText属性。
  export是ES6的模块化语法，用于导出函数、对象或变量，使其可以在其他文件中被导入和使用。
  usePagedList是一个自定义的组合函数，用于处理分页数据的加载和管理。
  fetchPage是一个异步函数，用于获取分页数据；
  map是一个函数，用于映射数据；
  pageSize是每页显示的条目数；
  errorText是加载失败时的错误提示文本，默认为'加载失败'。*/
  const rows = ref([])  //rows初始值为空数组，用于存储当前页的数据
  const total = ref(0)  //total初始值为0，用于存储数据的总条目数 
  const page = ref(1) //page初始值为1，用于存储当前页码
  const loading = ref(false)  //loading初始值为false，用于表示数据是否正在加载

  let seq = 0 //seq是一个计数器，用于标识当前的加载请求，防止异步请求返回顺序不一致导致的数据覆盖问题 是一个局部变量，用于跟踪加载请求的顺序，确保只处理最新的请求结果。

  async function loadRows() {
    /*loadRows是一个异步函数，用于加载当前页的数据。
    它会根据当前页码和每页条目数调用fetchPage函数获取数据，并将结果映射后存储到rows中，同时更新total的值。
    async是ES2017引入的关键字，用于定义异步函数*/

    const my = ++seq  //my是当前加载请求的序号
    loading.value = true  //loading.value设置为true，表示数据正在加载 value是ref对象的一个属性，用于访问和修改响应式数据的值
    try {
      //try是一个异常处理块，用于捕获可能发生的错误
      const res = await fetchPage({ page: page.value, page_size: pageSize })  //await是ES2017引入的关键字，用于等待一个Promise对象的解析结果
      //await是为了把数据返回给res 如果没有await res会是一个Promise对象 
      //promise是ES6引入的一个对象，用于表示异步操作的最终完成（或失败）及其结果值
      if (Array.isArray(res)) {   //Array.isArray()是一个静态方法，用于判断一个值是否为数组 是数组则返回true，否则返回false
        rows.value = res.map(map) //map是数组的一个方法，用于对数组中的每个元素执行一个函数，并返回一个新数组
        total.value = res.length  
      } else {
        rows.value = (res.results || []).map(map) /*res.results是一个数组，存储了当前页的数据，如果res.results不存在，则使用空数组[] 防止出现undefined的情况 
      走一遍map函数 是防止出现页面显示错误或崩溃 */
        total.value = res.count || 0  //res.count是一个数字，表示数据的总条目数，如果res.count不存在，则使用0 防止出现NaN或undefined的情况
      }
      if (!rows.value.length && page.value > 1 && total.value > 0) {
        page.value = 1
        return loadRows()
      }
    } catch (e) {
      //catch是一个异常处理块，用于处理捕获到的错误
      if (my !== seq) return    //用于防止用户点击过快导致页码与数据不对版
      ElMessage.error((e && e.message) || errorText)  //e是捕获到的错误对象，e.message是错误消息，如果e不存在，则使用errorText作为默认错误消息
    } finally {
      //finally是一个异常处理块，无论是否发生错误，都会执行finally块中的代码
      if (my === seq) loading.value = false
    }
  }

  function onFilter() {
    //
    page.value = 1
    loadRows()
  }

  function onPage(p) {
    page.value = p
    loadRows()
  }

  return { rows, total, page, pageSize, loading, loadRows, onFilter, onPage }
}
