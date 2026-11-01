// 调试用：比较原文件与当前文件编译后的差异位置
// 用法: node diff-normalized.mjs <原文件> <当前文件>
import fs from 'node:fs'
import * as esbuild from 'esbuild'
import { parse, compileTemplate, compileStyle } from '@vue/compiler-sfc'

const [origFile, curFile] = process.argv.slice(2)

function normJs(code) {
  return esbuild.transformSync(code, { loader: 'js', minify: true, format: 'esm' }).code
}

function parts(code, filename) {
  const { descriptor } = parse(code, { filename })
  const out = {}
  for (const s of [descriptor.script, descriptor.scriptSetup]) {
    if (s) out.script = (out.script || '') + normJs(s.content)
  }
  if (descriptor.template) {
    out.template = compileTemplate({
      source: descriptor.template.content,
      filename,
      id: 'verify',
      compilerOptions: { comments: false },
    }).code
  }
  if (descriptor.styles.length) {
    out.style = descriptor.styles
      .map((st) => compileStyle({ source: st.content, filename, id: 'verify', scoped: st.scoped }).code.replace(/\/\*[\s\S]*?\*\//g, ''))
      .join('\n')
  }
  return out
}

const a = parts(fs.readFileSync(origFile, 'utf8'), origFile)
const b = parts(fs.readFileSync(curFile, 'utf8'), curFile)

for (const key of ['script', 'template', 'style']) {
  const x = a[key] || ''
  const y = b[key] || ''
  if (x === y) {
    console.log(`${key}: SAME`)
    continue
  }
  let i = 0
  while (i < x.length && i < y.length && x[i] === y[i]) i++
  console.log(`\n${key}: DIFF at ${i}`)
  console.log('ORIG: ' + JSON.stringify(x.slice(Math.max(0, i - 150), i + 250)))
  console.log('CUR : ' + JSON.stringify(y.slice(Math.max(0, i - 150), i + 250)))
}
