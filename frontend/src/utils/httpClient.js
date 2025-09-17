// httpClient.js: 统一 HTTP 基础设施 (axios 封装)
// 核心功能:
// - 统一返回结构 { ok, data, error, status, headers, meta }
// - 自动认证 Token 管理和本地存储
// - 内置缓存系统 (支持 TTL, 委托给 domain/common/cache 模块)
// - 智能重试机制 (可配置重试次数、延迟和条件)
// - 数据 Transform 管线 (支持多层转换函数)
// - 完整的错误分类和规范化处理
// - 请求性能监控和日志记录
// - 统一响应自动解包 (支持 { success:true, data:... } 结构)
// - 缓存管理方法 (invalidate, clear)
// 
// 使用场景: 所有前端 API 调用的统一入口，提供一致的错误处理和性能监控

import axios from 'axios';
import logger from '@/utils/logger';
import cacheModule, { getCache as extGet, setCache as extSet } from '@/domain/common/cache';

const axiosInstance = axios.create({ baseURL: '/api', timeout: 15000 });

// 认证 Token 管理
export function setAuthToken(token) {
  if (token) {
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    try { localStorage.setItem('token', token); } catch { /* ignore storage set error */ }
  } else {
    delete axiosInstance.defaults.headers.common['Authorization'];
    try { localStorage.removeItem('token'); } catch { /* ignore storage remove error */ }
  }
}

// 初始化：若本地已有 token 自动恢复
try {
  const existing = localStorage.getItem('token');
  if (existing) setAuthToken(existing);
} catch { /* ignore restore token error (SSR / privacy mode) */ }

// 缓存逻辑委托给 domain/common/cache 模块
function getCache(key) { return extGet(key); }
function setCache(key, data, ttl) { extSet(key, data, ttl); }

// ----- 错误规范化 -----
function normalizeError(err) {
  if (err && err.__normalized) return err; // 避免重复包装
  const status = err?.response?.status;
  let code = 'UNKNOWN';
  let type = 'internal';

  if (axios.isCancel?.(err)) { code = 'ABORTED'; type = 'cancel'; }
  else if (err.code === 'ECONNABORTED') { code = 'NET_TIMEOUT'; type = 'network'; }
  else if (!status) { code = 'NETWORK_ERROR'; type = 'network'; }
  else {
    code = `HTTP_${status}`;
    type = 'http';
  }

  const message = err?.response?.data?.message || err?.message || '请求失败';
  return { __normalized: true, code, type, status, message, raw: err };
}

// 默认重试判断：仅网络类
function defaultRetryWhen(error) {
  return error.type === 'network';
}

async function core(method, url, options = {}) {
  const {
    data, params, headers, signal, timeout,
    cache, transform = [], retry, throwOnError,
  } = options;

  const perf = (typeof window !== 'undefined' && window.performance && typeof window.performance.now === 'function')
    ? window.performance
    : { now: () => Date.now() };
  const started = perf.now();
  const upperMethod = method.toUpperCase();

  // 缓存命中
  let cacheKey = null;
  if (cache) {
    cacheKey = cache.key || `${upperMethod}:${url}:${params ? JSON.stringify(params) : ''}`;
    if (!cache.force) {
      const cached = getCache(cacheKey);
      if (cached !== null && cached !== undefined) {
        return { ok: true, data: cached, status: 200, headers: {}, meta: { duration: 0, cache: 'hit' } };
      }
    }
  }

  let attempts = 0;
  const maxRetries = retry?.times || 0;

  while (true) {
    attempts++;
    try {
      const resp = await axiosInstance.request({ method, url, data, params, headers, signal, timeout });
      let payload = resp.data;
      // 统一响应自动解包：若为 { success:true, data:... } 结构则展开
      if(payload && typeof payload === 'object' && payload.success === true && Object.prototype.hasOwnProperty.call(payload,'data')){
        payload = { __raw: resp.data, ...payload.data };
      }
      for (const fn of transform) {
        payload = await fn(payload);
      }
      if (cacheKey) setCache(cacheKey, payload, cache.ttl);
      const duration = Math.round(perf.now() - started);
      logger?.debug?.(`[http] ${upperMethod} ${url} ${resp.status} ${duration}ms`);
      return { ok: true, data: payload, status: resp.status, headers: resp.headers, meta: { duration, attempts, cache: cacheKey ? 'miss' : undefined } };
    } catch (e) {
      const error = normalizeError(e);
      const shouldRetry = attempts <= maxRetries && (retry?.when ? retry.when(error) : defaultRetryWhen(error));
      if (shouldRetry) {
        const delay = retry?.delay ? retry.delay(attempts) : 300 * attempts;
        retry?.onRetry?.(error, attempts, delay);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      const duration = Math.round(perf.now() - started);
      logger?.warn?.(`[http] ${upperMethod} ${url} ERROR ${error.code} ${duration}ms`);
      if (throwOnError) throw error;
      return { ok: false, error, status: error.status, meta: { duration, attempts } };
    }
  }
}

const http = {
  get: (url, opts) => core('get', url, opts),
  post: (url, data, opts = {}) => core('post', url, { ...opts, data }),
  put: (url, data, opts = {}) => core('put', url, { ...opts, data }),
  patch: (url, data, opts = {}) => core('patch', url, { ...opts, data }),
  delete: (url, opts) => core('delete', url, opts),
  cache: {
    invalidate: cacheModule.invalidate,
    clear: cacheModule.clearCache
  }
};

export default http;