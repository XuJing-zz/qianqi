// 校验「只加注释、未改代码」：把原备份和当前文件分别编译/压缩后比较
// 用法（必须从 frontend 目录运行，才能解析 node_modules）：
//   node verify-comments.mjs <备份的 src 目录>
import fs from 'node:fs'
import path from 'node:path'
import * as esbuild from 'esbuild'
import { parse, compileTemplate, compileStyle } from '@vue/compiler-sfc'

const CURRENT = path.resolve('src')
const ORIGINAL = path.resolve(process.argv[2] || '')

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name)
    if (ent.isDirectory()) walk(p, acc)
    else if (/\.(js|vue)$/.test(ent.name)) acc.push(p)
  }
  return acc
}

function normJs(code) {
  return esbuild.transformSync(code, { loader: 'js', minify: true, format: 'esm' }).code
}

function partsFor(file, code) {
  if (!file.endsWith('.vue')) return { script: normJs(code) }
  const { descriptor, errors } = parse(code, { filename: file })
  if (errors.length) throw new Error(errors.map((e) => e.message).join('; '))
  const out = {}
  for (const s of [descriptor.script, descriptor.scriptSetup]) {
    if (s) out.script = (out.script || '') + normJs(s.content)
  }
  if (descriptor.template) {
    out.template = compileTemplate({
      source: descriptor.template.content,
      filename: file,
      id: 'verify',
      compilerOptions: { comments: false },
    }).code
  }
  if (descriptor.styles.length) {
    out.style = descriptor.styles
      .map((st) => compileStyle({ source: st.content, filename: file, id: 'verify', scoped: st.scoped }).code.replace(/\/\*[\s\S]*?\*\//g, ''))
      .join('\n')
  }
  return out
}

function diffKind(a, b) {
  if ((a.script || '') !== (b.script || '')) return 'script'
  if ((a.template || '') !== (b.template || '')) return 'template'
  if ((a.style || '').replace(/\s+/g, '') !== (b.style || '').replace(/\s+/g, '')) return 'style'
  if ((a.style || '') !== (b.style || '')) return 'style-whitespace'
  return null
}

const origFiles = walk(ORIGINAL)
const diffs = []
const styleWhitespace = []
const missing = []
let checked = 0

for (const ofile of origFiles) {
  const rel = path.relative(ORIGINAL, ofile)
  const cfile = path.join(CURRENT, rel)
  if (!fs.existsSync(cfile)) {
    missing.push(rel)
    continue
  }
  checked++
  try {
    const a = partsFor(ofile, fs.readFileSync(ofile, 'utf8'))
    const b = partsFor(cfile, fs.readFileSync(cfile, 'utf8'))
    const kind = diffKind(a, b)
    if (kind === 'style-whitespace') styleWhitespace.push(rel)
    else if (kind) diffs.push(`${rel}  [${kind}]`)
  } catch (e) {
    diffs.push(`${rel}  [编译失败: ${e.message}]`)
  }
}

const curFiles = walk(CURRENT).map((f) => path.relative(CURRENT, f))
const added = curFiles.filter((f) => !fs.existsSync(path.join(ORIGINAL, f)))

console.log(`对比 ${checked} 个文件`)
console.log(`代码内容有差异: ${diffs.length}`)
if (diffs.length) console.log(diffs.map((d) => '  DIFF ' + d).join('\n'))
console.log(`样式区仅空白差异（无害）: ${styleWhitespace.length}`)
if (styleWhitespace.length) console.log(styleWhitespace.map((d) => '  WS ' + d).join('\n'))
console.log(`缺失文件: ${missing.length}`)
if (missing.length) console.log(missing.map((d) => '  MISSING ' + d).join('\n'))
console.log(`新增文件: ${added.length}`)
if (added.length) console.log(added.map((d) => '  ADDED ' + d).join('\n'))
