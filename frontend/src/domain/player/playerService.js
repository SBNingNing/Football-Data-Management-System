// playerService: 球员领域数据访问与聚合
// 功能: 1) 聚合历史数据 2) 获取球员列表
// 说明: loader 方式可注入真实 API；内部带简单缓存
import logger from '@/utils/logger'
import { toPlayerHistoryViewModel } from '@/utils/mappers/playerMapper'
import cache from '@/domain/common/cache'
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

// 原始历史数据加载（可被真实 API 替换）
async function fetchRawPlayerHistory(playerId, { loader }) {
  if (loader) {
    return loader(playerId)
  }
  throw new Error('缺少 loader，尚未接入真实 API')
}

// 获取球员聚合历史视图
export async function fetchPlayerAggregate(playerId, { force = false, loader, cacheTTL = 20000 } = {}) {
  if (!playerId && playerId !== 0) throw buildError('缺少 playerId', 'PLAYER_ID_MISSING')
  const cacheKey = `player:${playerId}`
  if (!force) {
    const hit = cache.getCache?.(cacheKey)
    if (hit) return hit
  }
  const res = await fetchRawPlayerHistory(playerId, { loader })
  // 兼容 axios client 返回体结构 r.data 可能已是 {status:'success',data:{...}} 或直接 {...}
  let dataPayload = res
  if (res && res.data) dataPayload = res.data
  const ok = (dataPayload && (dataPayload.success === true || dataPayload.status === 'success')) || !!dataPayload?.player_info || Array.isArray(dataPayload?.seasons)
  const dataObj = dataPayload?.data && (dataPayload.success === true || dataPayload.status === 'success') ? dataPayload.data : dataPayload
  if (!ok || !dataObj) {
    throw buildError(dataPayload?.message || '获取球员历史失败', 'PLAYER_HISTORY_FETCH_FAILED', dataPayload)
  }
  const vm = toPlayerHistoryViewModel(dataObj, playerId)
  try {
    const seasonCount = vm.seasons?.length || 0
    const tournamentSet = new Set()
    vm.seasons?.forEach(s => {
      Object.values(s.tournaments || {}).forEach(t => tournamentSet.add(t.tournament_name))
    })
    vm.meta = { seasonCount, tournamentCount: tournamentSet.size }
  } catch (e) {
    logger.warn('[playerService] 计算附加统计失败', e)
  }
  const result = {
    player: vm,
    stats: {
      totalGoals: vm.totalGoals,
      totalYellowCards: vm.totalYellowCards,
      totalRedCards: vm.totalRedCards,
      seasons: vm.seasons?.length || 0,
      tournaments: vm.meta?.tournamentCount || 0
    },
    seasons: vm.seasons || [],
    teamHistories: vm.teamHistories || []
  }
  cache.setCache?.(cacheKey, result, cacheTTL)
  logger.debug?.('[playerService] fetchPlayerAggregate success', { playerId, seasons: result.seasons.length })
  return result
}

// 安全包装：提供与其他 service 一致的 { ok,data,error } 形式 (可供组件直接调用)
export function fetchPlayerAggregateSafe(playerId, opts) {
  return serviceWrap(async () => fetchPlayerAggregate(playerId, opts))
}

// ------------------ 单个球员 ------------------
export function fetchPlayer(playerId) {
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId', 'PLAYER_ID_MISSING')
    const res = await http.get(`/players/${playerId}`)
    if(!res.ok) throw buildError(res.error?.message || '获取球员详情失败', 'PLAYER_FETCH_FAILED', res.error)
    // 后端返回 { status:'success', data: {...} }
    return res.data?.data || res.data
  })
}

// ------------------ 球员列表 ------------------
function normalizePlayersPayload(raw) {
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.data)) return raw.data
  if ((raw.success === true || raw.status === 'success') && Array.isArray(raw.data)) return raw.data
  return []
}

export async function fetchPlayers({ force = false } = {}) {
  return serviceWrap(async () => {
    // 基于 httpClient baseURL('/api')，此处不要再写 /api 前缀，避免 /api/api/players
    const res = await http.get('/players', { force })
    if (!res.ok) throw buildError(res.error?.message || '获取球员列表失败', 'PLAYERS_FETCH_FAILED', res.error, { status: res.status })
    return normalizePlayersPayload(res.data)
  })
}

// ========== 额外 CRUD（如果前端需要直接调用，可使用这些安全包装） ==========
export function createPlayer(payload){
  return serviceWrap(async () => {
    const res = await http.post('/players', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建球员失败', 'PLAYER_CREATE_FAILED', res.error)
    return res.data
  })
}
export function updatePlayer(playerId, payload){
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId', 'PLAYER_ID_MISSING')
    const res = await http.put(`/players/${playerId}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新球员失败', 'PLAYER_UPDATE_FAILED', res.error)
    return res.data
  })
}
export function deletePlayer(playerId){
  return serviceWrap(async () => {
    if(!playerId) throw buildError('缺少 playerId', 'PLAYER_ID_MISSING')
    const res = await http.delete(`/players/${playerId}`)
    if(!res.ok) throw buildError(res.error?.message || '删除球员失败', 'PLAYER_DELETE_FAILED', res.error)
    return { success:true }
  })
}
