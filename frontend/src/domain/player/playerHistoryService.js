/**
 * playerHistoryService (领域: player-history)
 * ---------------------------------------------
 * 对应后端 blueprint url_prefix='/api/player-history'，前端 http baseURL 已是 '/api'，
 * 因此前端路径使用 '/player-history/...'
 * 功能: 完整历史 / 指定赛季表现 / 跨赛季对比 / 转队历史
 * 缓存键约定:
 *  - playerHistory:complete:<playerId>
 *  - playerHistory:season:<playerId>:<seasonId>
 *  - playerHistory:teamChanges:<playerId>
 *  - playerHistory:compare:<hash>
 */
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

function hash(arr){
  return (arr||[]).slice().sort().join('_') || 'none'
}

export function fetchPlayerCompleteHistory(playerId, { cacheTTL=30000, force=false } = {}){
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId','PLAYER_ID_MISSING')
    const res = await http.get(`/player-history/${encodeURIComponent(playerId)}/complete`, { cache:{ ttl: cacheTTL, force, key: `playerHistory:complete:${playerId}` } })
    if(!res.ok) throw buildError(res.error?.message || '获取球员完整历史失败','PLAYER_HISTORY_COMPLETE_FAILED', res.error)
    return res.data
  })
}

export function fetchPlayerSeasonPerformance(playerId, seasonId, { cacheTTL=30000, force=false } = {}){
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId','PLAYER_ID_MISSING')
    if(seasonId===undefined || seasonId===null) throw buildError('缺少 seasonId','SEASON_ID_MISSING')
    const res = await http.get(`/player-history/${encodeURIComponent(playerId)}/season/${seasonId}`, { cache:{ ttl: cacheTTL, force, key: `playerHistory:season:${playerId}:${seasonId}` } })
    if(!res.ok) throw buildError(res.error?.message || '获取球员赛季表现失败','PLAYER_HISTORY_SEASON_FAILED', res.error)
    return res.data
  })
}

export function comparePlayersAcrossSeasons(playerIds = [], seasonIds = [], { cacheTTL=30000, force=false } = {}){
  return serviceWrap(async () => {
    if(!Array.isArray(playerIds) || playerIds.length===0) throw buildError('缺少 playerIds','PLAYER_IDS_MISSING')
    const key = `playerHistory:compare:${hash(playerIds)}:${hash(seasonIds)}`
    const res = await http.post('/player-history/compare', { player_ids: playerIds, season_ids: seasonIds }, { cache:{ ttl: cacheTTL, force, key } })
    if(!res.ok) throw buildError(res.error?.message || '比较球员历史失败','PLAYER_HISTORY_COMPARE_FAILED', res.error)
    return res.data
  })
}

export function fetchPlayerTeamChanges(playerId, { cacheTTL=30000, force=false } = {}){
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId','PLAYER_ID_MISSING')
    const res = await http.get(`/player-history/team-changes/${encodeURIComponent(playerId)}`, { cache:{ ttl: cacheTTL, force, key: `playerHistory:teamChanges:${playerId}` } })
    if(!res.ok) throw buildError(res.error?.message || '获取球员转队历史失败','PLAYER_HISTORY_TEAM_CHANGES_FAILED', res.error)
    return res.data
  })
}

export const PLAYER_HISTORY_CACHE_KEYS = {
  complete: (id) => `playerHistory:complete:${id}`,
  season: (id, seasonId) => `playerHistory:season:${id}:${seasonId}`,
  teamChanges: (id) => `playerHistory:teamChanges:${id}`,
  compare: (playerIds, seasonIds) => `playerHistory:compare:${hash(playerIds)}:${hash(seasonIds)}`
}
