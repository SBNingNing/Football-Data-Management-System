// 简单内存缓存模块：key -> { value, expiry }
// 提供 get/set/invalidate/clear 及 withCache 帮助函数。

const store = new Map();

export function setCache(key, value, ttlMs) {
  if (!key) return;
  const expiry = ttlMs ? Date.now() + ttlMs : null;
  store.set(key, { value, expiry });
}

export function getCache(key) {
  if (!key) return undefined;
  const entry = store.get(key);
  if (!entry) return undefined;
  if (entry.expiry && Date.now() > entry.expiry) {
    store.delete(key);
    return undefined;
  }
  return entry.value;
}

export function invalidate(key) { if (key) store.delete(key); }
export function clearCache() { store.clear(); }

export async function withCache(key, ttlMs, loader) {
  const hit = getCache(key);
  if (hit !== undefined) return { data: hit, cache: 'hit' };
  const data = await loader();
  setCache(key, data, ttlMs);
  return { data, cache: 'miss' };
}

export default { setCache, getCache, invalidate, clearCache, withCache };
