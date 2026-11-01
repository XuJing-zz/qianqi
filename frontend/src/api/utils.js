
/*字段命名与查询串工具：在“后端下划线命名（snake_case）”和“前端驼峰命名（camelCase）”之间转换，并把参数拼成查询字符串*/
/*把下划线命名转成驼峰命名：参数 s 是字符串（如 product_id）；返回转换后的字符串（productId）。
   String.prototype.replace(正则, 替换内容) 会用正则查找匹配部分并替换。
   这里正则 /_([a-z0-9])/g 表示“下划线 + 一个字母或数字”，g 表示全局匹配；
   第二个参数是回调函数 (m, c)：m 是整个匹配（如 "_i"），c 是括号捕获到的字符（如 "i"），
   回调返回 c.toUpperCase()，于是下划线被去掉、后面的字母变大写。*/
export function toCamel(s) {
  return s.replace(/_([a-z0-9])/g, (m, c) => c.toUpperCase())
}

/*递归地把对象/数组里的所有键从下划线命名转成驼峰命名：
   参数 obj 可以是对象、数组或基本类型；返回转换后的新对象/新数组，不修改原数据。
   规则：
   - 数组：对每个元素继续调用 mapKeys；
   - 普通对象：遍历每个键，把键名转驼峰，值继续递归处理（支持多层嵌套）；
   - 其他（字符串、数字、null 等）：原样返回。
   Object.keys(obj) 返回对象自身所有可枚举属性名组成的数组，配合 for...of 可逐个遍历键。
   递归就是函数在内部调用自己：遇到嵌套的对象或数组时，用同样的规则继续处理下一层，
   直到遇到基本类型（无法再拆分）才直接返回，这样多层数据结构也能一次性转换完。*/
export function mapKeys(obj) {
  if (Array.isArray(obj)) return obj.map(mapKeys)   // 数组：逐个元素递归
  if (obj !== null && typeof obj === 'object') {
    const out = {}
    for (const k of Object.keys(obj)) {   // 遍历对象的每个属性名
      out[toCamel(k)] = mapKeys(obj[k])   // 键转驼峰，值继续递归
    }
    return out
  }
  return obj   // 基本类型直接返回
}

/*把驼峰命名转成下划线命名：参数 s 是字符串（如 productId）；返回转换后的字符串（product_id）。
   正则 /[A-Z]/g 匹配每个大写字母，替换函数返回“下划线 + 该字母的小写形式”。*/
export function toSnake(s) {
  return s.replace(/[A-Z]/g, (c) => '_' + c.toLowerCase())
}

/*递归地把对象/数组里的所有键从驼峰命名转成下划线命名：
   参数 obj 可以是对象、数组或基本类型；返回新的对象/数组，不修改原数据。
   规则与 mapKeys 相同，只是每个键用 toSnake 转换，用于把前端数据提交给后端。*/
export function mapToSnake(obj) {
  if (Array.isArray(obj)) return obj.map(mapToSnake)   // 数组：逐个元素递归
  if (obj !== null && typeof obj === 'object') {
    const out = {}
    for (const k of Object.keys(obj)) {
      out[toSnake(k)] = mapToSnake(obj[k])   // 键转下划线，值继续递归
    }
    return out
  }
  return obj
}

/*把参数对象拼成 URL 查询字符串：参数 params 是键值对象（如 { page: 1, keyword: '漆器' }）；
   返回形如 "?page=1&keyword=%E6%BC%86%E5%99%A8" 的字符串；没有有效参数时返回空字符串 ""。
   流程：先遍历并过滤掉 undefined、null 和空字符串（避免把无效参数发给后端），再用 URLSearchParams 编码。*/
export function qs(params = {}) {
  const cleaned = {}   // 只保留有效参数
  for (const k of Object.keys(params)) {
    const v = params[k]
    if (v !== undefined && v !== null && v !== '') cleaned[k] = v   // 空值不参与拼接
  }
  /* URLSearchParams 是浏览器内置的查询参数处理类：
     接收对象或键值对后，toString() 会按 URL 规则自动编码特殊字符（如中文、空格、&），
     避免手动拼接查询串时出现转义错误。*/
  const s = new URLSearchParams(cleaned).toString()
  return s ? '?' + s : ''   // 有参数才加问号
}
