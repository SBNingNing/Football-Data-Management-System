/**
 * tournamentCrudService (领域: tournament)
 * ---------------------------------------------
 * 提供基础 CRUD + 实例管理 (instances/quick)。
 * 现有 tournamentService.js 专注聚合统计；本文件补齐基础操作。
 * 缓存键约定:
 *  - tournaments:list
 *  - tournament:<id>
 *  - tournament-instance:<id>
 */
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

function normalizeTournament(raw){
  if(!raw) return null
  return {
    id: raw.id,
    name: raw.name,
    seasonId: raw.season_id || raw.seasonId,
    competitionId: raw.competition_id || raw.competitionId,
    createdAt: raw.created_at || raw.createdAt,
    updatedAt: raw.updated_at || raw.updatedAt
  }
}

export function fetchTournaments({ force=false, cacheTTL=15000 } = {}){
  return serviceWrap(async () => {
    const res = await http.get('/tournaments', { cache:{ ttl: cacheTTL, force, key: 'tournaments:list' } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛事列表失败','TOURNAMENTS_FETCH_FAILED', res.error)
    const data = res.data?.data || res.data || {}
    // /tournaments GET 返回结构: data.status='success', data.data 含 group? records?
    // 这里尝试兼容: 若存在 records 列表则 flatten; 否则假设是 name 分组
    let list = []
    if(Array.isArray(data.records)) list = data.records
    else if(Array.isArray(data.tournaments)) list = data.tournaments
    else if(Array.isArray(data)) list = data
    else if(data.groups) {
      Object.values(data.groups).forEach(arr => { if(Array.isArray(arr)) list.push(...arr) })
    }
    return list.map(normalizeTournament).filter(Boolean)
  })
}

export function fetchTournamentById(id, { force=false, cacheTTL=15000 } = {}){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 tournamentId','TOURNAMENT_ID_MISSING')
    const res = await http.get(`/tournaments/${id}`, { cache:{ ttl: cacheTTL, force, key: `tournament:${id}` } })
    if(!res.ok) throw buildError(res.error?.message || '获取赛事失败','TOURNAMENT_FETCH_FAILED', res.error)
    // get /tournaments/<id or name> 返回包装结构，取 data.records[0]
    const raw = res.data?.data?.records?.[0] || res.data?.data || res.data
    return normalizeTournament(raw)
  })
}

export function createTournament(payload){
  return serviceWrap(async () => {
    if(!payload || !payload.name) throw buildError('缺少赛事名称','TOURNAMENT_NAME_MISSING')
    if(!payload.season_name && !payload.seasonName) throw buildError('缺少赛季名称','TOURNAMENT_SEASON_NAME_MISSING')
    const res = await http.post('/tournaments', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建赛事失败','TOURNAMENT_CREATE_FAILED', res.error)
    return normalizeTournament(res.data?.data || res.data)
  })
}

export function updateTournament(id, payload){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 tournamentId','TOURNAMENT_ID_MISSING')
    const res = await http.put(`/tournaments/${id}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新赛事失败','TOURNAMENT_UPDATE_FAILED', res.error)
    return { success:true }
  })
}

export function deleteTournament(id){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 tournamentId','TOURNAMENT_ID_MISSING')
    const res = await http.delete(`/tournaments/${id}`)
    if(!res.ok) throw buildError(res.error?.message || '删除赛事失败','TOURNAMENT_DELETE_FAILED', res.error)
    return { success:true }
  })
}

// 赛事实例
export function createTournamentInstance(payload){
  return serviceWrap(async () => {
    if(!payload || !payload.competition_id) throw buildError('缺少 competition_id','TOURNAMENT_INSTANCE_COMPETITION_ID_MISSING')
    if(!payload.season_id) throw buildError('缺少 season_id','TOURNAMENT_INSTANCE_SEASON_ID_MISSING')
    const res = await http.post('/tournaments/instances', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建赛事实例失败','TOURNAMENT_INSTANCE_CREATE_FAILED', res.error)
    return res.data?.data || res.data
  })
}

export function updateTournamentInstance(id, payload){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 tournamentInstanceId','TOURNAMENT_INSTANCE_ID_MISSING')
    const res = await http.put(`/tournaments/instances/${id}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新赛事实例失败','TOURNAMENT_INSTANCE_UPDATE_FAILED', res.error)
    return res.data?.data || res.data
  })
}

// 快速创建/复用
export function quickCreateTournamentInstance(payload){
  return serviceWrap(async () => {
    const res = await http.post('/tournaments/quick', payload)
    if(!res.ok) throw buildError(res.error?.message || '快速创建赛事实例失败','TOURNAMENT_QUICK_CREATE_FAILED', res.error)
    return res.data?.data || res.data
  })
}

export const TOURNAMENT_CACHE_KEYS = {
  LIST: 'tournaments:list',
  one: (id) => `tournament:${id}`,
  instance: (id) => `tournament-instance:${id}`
}
