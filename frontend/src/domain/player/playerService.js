// playerService: 球员领域数据访问与聚合
// 功能: 1) 聚合历史数据 2) 获取球员列表
// 说明: loader 方式可注入真实 API；内部带简单缓存
import logger from '@/utils/logger'
import { toPlayerHistoryViewModel } from '@/utils/mappers/playerMapper'
import cache from '@/domain/common/cache'
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

// 获取球员聚合历史视图
export async function fetchPlayerAggregate(playerId, { force = false, cacheTTL = 20000 } = {}) {
  if (!playerId && playerId !== 0) throw buildError('缺少 playerId', 'PLAYER_ID_MISSING');
  const cacheKey = `player:${playerId}`;
  
  if (!force) {
    const hit = cache.getCache?.(cacheKey);
    if (hit) return hit;
  }

  const res = await http.get(`/player-history/${playerId}/complete`);
  logger.debug(`[playerService] fetchPlayerAggregate raw response for playerId ${playerId}:`, res);

  // 首先检查 httpClient 返回的 'ok' 或 'success' 标志
  if (res.ok === false) {
    // 如果请求不成功，抛出一个标准的错误对象
    throw res.error || buildError('API 请求失败', 'API_REQUEST_FAILED', res);
  }

  // 如果请求成功，res.data 应该包含我们需要的核心数据
  const data = res.data;

  // 验证响应是否包含有效数据
  if (!data || !data.player_info || !Array.isArray(data.seasons)) {
    logger.error('[playerService] Invalid data structure from API', data);
    throw buildError('获取球员历史失败：数据结构无效', 'PLAYER_HISTORY_FETCH_FAILED', data);
  }

  // 从 seasons 中手动生成 teamHistories 以兼容旧组件
  const teamHistories = data.seasons.flatMap(season => 
    (season.teams ?? []).map(team => ({
      season_name: season.season_name || '未知赛季',
      team_name: team.team_name || '未知队伍',
      tournament_name: team.tournament_info?.name || '未知赛事',
      player_number: team.player_number ?? null,
      goals_scored: team.goals_scored ?? 0,
      yellow_cards: team.yellow_cards ?? 0,
      red_cards: team.red_cards ?? 0,
    }))
  );

  // 转换数据为视图模型
  const viewModel = toPlayerHistoryViewModel(data);
  logger.debug(`[playerService] ViewModel after mapping:`, viewModel);

  // 为视图模型附加我们手动生成的 teamHistories
  viewModel.teamHistories = teamHistories;
  
  // 缓存处理
  cache.setCache?.(cacheKey, viewModel, cacheTTL);
  
  return viewModel;
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
