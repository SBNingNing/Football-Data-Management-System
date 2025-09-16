// mutation.js: 提供通用变更封装 + 缓存失效策略
// 用法:
//   mutateAndInvalidate(() => createTeam(payload), { invalidate: ['teams:list', 'stats:dashboard'] })
import cache from '@/domain/common/cache'
import { serviceWrap } from '@/utils/error'

// 访问内部 Map 以实现高级失效 (注意: 这是一个轻量侵入；若后续重构可提供官方枚举 API)
// 由于 cache.js 未导出 store，这里通过弱引用维护一个 keySnapshot；
// 方案: monkey patch setCache/invalidate 以维护 keys 集合。
// 若未来暴露 listKeys() 则可替换。
const _keySet = new Set()
const _origSet = cache.setCache || (()=>{})
const _origInvalidate = cache.invalidate || (()=>{})
// 仅在首次导入时打补丁
if (!_origSet.__patched) {
  cache.setCache = function patchedSet(k, v, ttl){ _keySet.add(k); return _origSet(k, v, ttl) }
  cache.setCache.__patched = true
  cache.invalidate = function patchedInvalidate(k){ _keySet.delete(k); return _origInvalidate(k) }
}

function invalidateAdvanced({ prefixes = [], patterns = [] }) {
  if ((!prefixes || prefixes.length === 0) && (!patterns || patterns.length === 0)) return
  const toDelete = []
  _keySet.forEach(k => {
    if (prefixes.some(p => k.startsWith(p))) toDelete.push(k)
    else if (patterns.some(r => r.test && r.test(k))) toDelete.push(k)
  })
  toDelete.forEach(k => cache.invalidate(k))
  return toDelete
}

// 轻量策略: 调用方直接传递 exact keys (字符串)
export function mutateAndInvalidate(fn, { invalidate = [], invalidatePrefixes = [], invalidatePatterns = [], mapResult, onSuccess, onError: _onError } = {}) {
  return serviceWrap(async () => {
    const res = await fn()
    invalidate.forEach(k => { if (typeof k === 'string') cache.invalidate(k) })
    // 前缀/正则模式失效
    invalidateAdvanced({ prefixes: invalidatePrefixes, patterns: invalidatePatterns })
    const finalData = mapResult ? mapResult(res) : res
    onSuccess?.(finalData)
    return finalData
  })
}

export default { mutateAndInvalidate }
