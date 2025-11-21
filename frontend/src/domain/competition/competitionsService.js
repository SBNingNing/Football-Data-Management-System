/**
 * competitionsService (领域: competition)
 * ---------------------------------------------
 * CRUD + 查询过滤/排序参数支持。后端支持 ?sort_by=&search=
 * 缓存键约定:
 *  - competitions:list(+queryHash)
 *  - competition:<id>
 */
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'
import { COMPETITION_KEYS } from '@/domain/cacheKeys'

// hashQuery 由集中 cacheKeys 内部实现，通过 COMPETITION_KEYS.list 调用

function normalizeCompetition(raw){
  if(!raw) return null
  return {
    id: raw.id || raw.competition_id,
    name: raw.name,
    createdAt: raw.created_at || raw.createdAt,
    updatedAt: raw.updated_at || raw.updatedAt,
    statistics: raw.statistics // 若为列表响应添加统计字段
  }
}

export function fetchCompetitions(params = {}, { force=false, cacheTTL=20000 } = {}){
  return serviceWrap(async () => {
    const query = { ...params }
    // 避免在非浏览器/某些 ESLint 环境下 URLSearchParams no-undef，使用自定义序列化
    const qEntries = Object.entries(query).filter(([,v]) => v !== undefined && v !== null && v !== '')
    const qStr = qEntries.map(([k,v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&')
  const key = COMPETITION_KEYS.list(query)
    const res = await http.get(`/competitions${qStr?`?${qStr}`:''}`, { cache:{ ttl: cacheTTL, force, key } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛事列表失败', 'COMPETITIONS_FETCH_FAILED', res.error)
    const data = res.data?.data || res.data || {}
    const list = data.competitions || []
    return {
      competitions: list.map(normalizeCompetition).filter(Boolean),
      statistics: data.statistics || {}
    }
  })
}

export function fetchCompetition(competitionId, { cacheTTL=20000, force=false } = {}){
  return serviceWrap(async () => {
    if(competitionId===undefined || competitionId===null) throw buildError('缺少 competitionId','COMPETITION_ID_MISSING')
  const res = await http.get(`/competitions/${competitionId}`, { cache:{ ttl: cacheTTL, force, key: COMPETITION_KEYS.one(competitionId) } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛事失败', 'COMPETITION_FETCH_FAILED', res.error)
    const item = normalizeCompetition(res.data?.data || res.data)
    return item
  })
}

export function createCompetition(payload){
  return serviceWrap(async () => {
    if(!payload || !payload.name) throw buildError('缺少赛事名称','COMPETITION_NAME_MISSING')
    const res = await http.post('/competitions', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建赛事失败', 'COMPETITION_CREATE_FAILED', res.error)
    return normalizeCompetition(res.data?.data || res.data)
  })
}

export function updateCompetition(competitionId, payload){
  return serviceWrap(async () => {
    if(competitionId===undefined || competitionId===null) throw buildError('缺少 competitionId','COMPETITION_ID_MISSING')
    const res = await http.put(`/competitions/${competitionId}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新赛事失败', 'COMPETITION_UPDATE_FAILED', res.error)
    return normalizeCompetition(res.data?.data || res.data)
  })
}

export function deleteCompetition(competitionId){
  return serviceWrap(async () => {
    if(competitionId===undefined || competitionId===null) throw buildError('缺少 competitionId','COMPETITION_ID_MISSING')
    const res = await http.delete(`/competitions/${competitionId}`)
    if(!res.ok) throw buildError(res.error?.message || '删除赛事失败', 'COMPETITION_DELETE_FAILED', res.error)
    return { success:true }
  })
}

export const COMPETITION_CACHE_KEYS = COMPETITION_KEYS
