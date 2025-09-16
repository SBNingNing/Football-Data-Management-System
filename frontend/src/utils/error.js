// utils/error.js
// ------------------------------------------------------------------
// 统一错误构造与标准化工具，为 service 层与组合式提供一致 error shape。
// 约定标准化结构：
// { message: string, code?: string, cause?: any, retryable?: boolean, isNormalized: true }

export function buildError(message, code, cause, extra = {}) {
  const err = new Error(message || '未知错误')
  if (code) err.code = code
  if (cause) err.cause = cause
  Object.assign(err, extra)
  return err
}

export function normalizeError(e) {
  if (!e) return { message: '未知错误', code: 'UNKNOWN', isNormalized: true }
  if (e.isNormalized) return e
  const message = e.message || '请求失败'
  const code = e.code || e.statusCode || 'ERROR'
  return { message, code, cause: e, isNormalized: true, retryable: !!e.retryable }
}

/**
 * 包装一个返回 Promise 的函数并附加重试
 * @param {Function} fn () => Promise<any>
 * @param {Object} opts { attempts=2, factor=1.5, base=300, maxDelay=4000 }
 */
export async function withRetry(fn, opts = {}) {
  const { attempts = 2, factor = 1.5, base = 300, maxDelay = 4000 } = opts
  let attempt = 0
  let lastErr
  while (attempt <= attempts) {
    try {
      return await fn()
    } catch (e) {
      lastErr = e
      if (attempt === attempts) break
      const delay = Math.min(base * Math.pow(factor, attempt), maxDelay)
      await new Promise(r => setTimeout(r, delay))
      attempt++
    }
  }
  throw lastErr
}

/**
 * 简化 service 层 try-catch：
 * 使用：
 * return serviceWrap(async () => { const data = await http.get(...); return data })
 * 输出：{ ok:true, data } 或 { ok:false, error }
 */
export async function serviceWrap(executor) {
  try {
    const data = await executor()
    return { ok: true, data }
  } catch (e) {
    return { ok: false, error: normalizeError(e) }
  }
}
