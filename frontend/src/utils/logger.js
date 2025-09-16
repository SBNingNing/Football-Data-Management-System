/* eslint-disable no-console */
// 简易日志工具：在生产环境屏蔽 info/debug 级别普通日志，保留 warn / error。
// 可根据需要扩展（比如持久化、上报、打点）。

// 仅依赖 Vite 的 import.meta.env，避免在前端环境引用 process 导致 no-undef
const ENV = (import.meta && import.meta.env && (import.meta.env.MODE || import.meta.env.VITE_ENV)) || 'development'
const isProd = ENV === 'production'
// 可选：启用日志上报到后端 /api/logs
const ENABLE_UPLOAD = !!(import.meta && import.meta.env && import.meta.env.VITE_ENABLE_LOG_UPLOAD)
const UPLOAD_LEVELS = (import.meta && import.meta.env && import.meta.env.VITE_LOG_UPLOAD_LEVELS) || 'warn,error'
const uploadLevels = new Set(UPLOAD_LEVELS.split(',').map(s => s.trim().toLowerCase()).filter(Boolean))

let queue = []
let timer = null
function enqueue(level, args){
  try{
    const message = args && args.length ? (typeof args[0] === 'string' ? args[0] : JSON.stringify(args[0])) : ''
    const context = args && args.length>1 ? { extra: Array.from(args.slice(1)).map(x=>safeJson(x)) } : {}
    queue.push({ level, message, ts: Date.now(), context })
    if(!timer){ timer = setTimeout(flush, 1000) }
    if(queue.length>100){ flush() }
  }catch{ /* ignore */ }
}
function safeJson(v){ try{ return typeof v === 'string' ? v : JSON.parse(JSON.stringify(v)) } catch{ return String(v) } }
async function flush(){
  const batch = queue.splice(0, queue.length)
  clearTimeout(timer); timer=null
  if(!ENABLE_UPLOAD || !batch.length) return
  try{
    // 使用 fetch，避免引入 axios；后端已在同域 /api
    await fetch('/api/logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ logs: batch })
    })
  }catch{ /* 忽略上报失败 */ }
}

function formatArgs(level, args) {
  const ts = new Date().toISOString().replace('T', ' ').replace('Z', '')
  return [`[%c${level.toUpperCase()}%c][${ts}]`, level === 'error' ? 'color:#f56c6c;' : level === 'warn' ? 'color:#e6a23c;' : 'color:#409EFF;', 'color:inherit;', ...args]
}

export const logger = {
  info: (...args) => { if (!isProd) console.log(...formatArgs('info', args)); if(ENABLE_UPLOAD && uploadLevels.has('info')) enqueue('info', args) },
  debug: (...args) => { if (!isProd) console.log(...formatArgs('debug', args)); if(ENABLE_UPLOAD && uploadLevels.has('debug')) enqueue('debug', args) },
  log:  (...args) => { if (!isProd) console.log(...formatArgs('log', args));  if(ENABLE_UPLOAD && uploadLevels.has('log')) enqueue('info', args) },
  warn: (...args) => { console.warn(...formatArgs('warn', args)); if(ENABLE_UPLOAD && uploadLevels.has('warn')) enqueue('warn', args) },
  error:(...args) => { console.error(...formatArgs('error', args)); if(ENABLE_UPLOAD && uploadLevels.has('error')) enqueue('error', args) }
}

export default logger
