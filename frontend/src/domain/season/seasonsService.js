/**
 * seasonsService (领域: season)
 * ---------------------------------------------
 * 提供赛季 CRUD & 基础列表获取。遵循 serviceWrap + buildError 规范。
 * 缓存键约定:
 *  - seasons:list         赛季列表
 *  - season:<id>          单个赛季详情
 */
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'
import { SEASON_KEYS } from '@/domain/cacheKeys'

function normalizeSeason(raw){
  if(!raw) return null
  // 后端直接返回 data = list 或单个对象 (status: success)
  return {
    id: raw.id,
    name: raw.name,
    startDate: raw.start_date || raw.startDate,
    endDate: raw.end_date || raw.endDate,
    createdAt: raw.created_at || raw.createdAt,
    updatedAt: raw.updated_at || raw.updatedAt
  }
}

export function fetchSeasons({ force = false, cacheTTL = 20000 } = {}) {
  return serviceWrap(async () => {
  const res = await http.get('/seasons', { cache: { ttl: cacheTTL, force, key: SEASON_KEYS.LIST } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛季列表失败', 'SEASONS_FETCH_FAILED', res.error)
    const list = (res.data?.data || res.data || []).map(normalizeSeason).filter(Boolean)
    return list
  })
}

export function fetchSeason(seasonId, { cacheTTL = 20000, force = false } = {}) {
  return serviceWrap(async () => {
    if(seasonId===undefined || seasonId===null) throw buildError('缺少 seasonId', 'SEASON_ID_MISSING')
  const res = await http.get(`/seasons/${seasonId}`, { cache: { ttl: cacheTTL, force, key: SEASON_KEYS.one(seasonId) } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛季失败', 'SEASON_FETCH_FAILED', res.error)
    const item = normalizeSeason(res.data?.data || res.data)
    return item
  })
}

export function createSeason(payload){
  return serviceWrap(async () => {
    if(!payload || !payload.name) throw buildError('缺少赛季名称', 'SEASON_NAME_MISSING')
    const res = await http.post('/seasons', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建赛季失败', 'SEASON_CREATE_FAILED', res.error)
    return normalizeSeason(res.data?.data || res.data)
  })
}

export function updateSeason(seasonId, payload){
  return serviceWrap(async () => {
    if(seasonId===undefined || seasonId===null) throw buildError('缺少 seasonId', 'SEASON_ID_MISSING')
    const res = await http.put(`/seasons/${seasonId}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新赛季失败', 'SEASON_UPDATE_FAILED', res.error)
    return normalizeSeason(res.data?.data || res.data)
  })
}

export function deleteSeason(seasonId){
  return serviceWrap(async () => {
    if(seasonId===undefined || seasonId===null) throw buildError('缺少 seasonId', 'SEASON_ID_MISSING')
    const res = await http.delete(`/seasons/${seasonId}`)
    if(!res.ok) throw buildError(res.error?.message || '删除赛季失败', 'SEASON_DELETE_FAILED', res.error)
    return { success: true }
  })
}

// 建议的缓存失效键集合，供 mutation 层引用
// 兼容导出（逐步淘汰）：
export const SEASON_CACHE_KEYS = SEASON_KEYS
