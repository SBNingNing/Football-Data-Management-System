/**
 * teamService (领域: team)
 * --------------------------------------------------
 * 聚合球队历史 / 赛季记录 / 球员参赛统计。与 team_history.vue 原内联逻辑解耦。
 */
import { toTeamHistoryViewModel } from '@/utils/mappers/teamHistoryMapper'
import logger from '@/utils/logger'
import cache from '@/domain/common/cache'
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

// 适配器：通过传入的 loader (例如 pinia store 的 loadComplete) 获取原始数据
async function fetchRawTeamHistory(teamName, { loader, force }) {
  if (!loader) throw new Error('缺少 loader 实现')
  return loader(teamName, { force })
}

/**
 * 获取球队聚合视图
 * @param {string} teamName
 * @param {{force?:boolean, loader?:Function}} options
 */
export async function fetchTeamAggregate(teamName, { force = false, loader, cacheTTL = 20000 } = {}) {
  if (!teamName) throw buildError('缺少 teamName', 'TEAM_NAME_MISSING')
  const cacheKey = `team:${teamName}`
  if (!force) {
    const hit = cache.getCache?.(cacheKey)
    if (hit) return hit
  }
  const res = await fetchRawTeamHistory(teamName, { loader, force })
  if (!res || !res.success || !res.data) {
    throw buildError(res?.error || '获取球队历史失败', 'TEAM_HISTORY_FETCH_FAILED', res)
  }
  const vm = toTeamHistoryViewModel(res.data, teamName)
  try {
    const tournamentCount = vm.records?.length || 0
    let goalSum = 0
    vm.records?.forEach(r => { goalSum += r.goals || 0 })
    vm.meta = {
      tournamentCount,
      avgGoalsPerTournament: tournamentCount ? (goalSum / tournamentCount) : 0
    }
  } catch (e) {
    logger.warn('[teamService] 附加统计失败', e)
  }
  const result = { team: vm, records: vm.records || [] }
  cache.setCache?.(cacheKey, result, cacheTTL)
  logger.debug?.('[teamService] fetchTeamAggregate success', { teamName, records: result.records.length })
  return result
}

// 提供一致风格的安全包装
export function fetchTeamAggregateSafe(teamName, opts) {
  return serviceWrap(async () => fetchTeamAggregate(teamName, opts))
}

// ------------------ 球队列表 ------------------
function normalizeTeamsPayload(raw) {
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (Array.isArray(raw.data)) return raw.data
  if ((raw.success === true || raw.status === 'success') && Array.isArray(raw.data)) return raw.data
  return []
}

// 统一字段映射，避免组件重复写兼容逻辑
function mapTeam(team) {
  return {
    ...team,
    id: team.id || `team_${Math.random().toString(36).slice(2, 10)}`,
    teamName: team.teamName || team.name || '未知球队',
    matchType: team.matchType || 'champions-cup',
    tournamentId: team.tournamentId || team.tournament_id,
    tournamentName: team.tournamentName || team.tournament_name,
    rank: team.rank || team.tournament_rank,
    goals: team.goals || team.tournament_goals || 0,
    goalsConceded: team.goalsConceded || team.tournament_goals_conceded || 0,
    goalDifference: team.goalDifference || team.tournament_goal_difference || 0,
    points: team.points || team.tournament_points || 0,
    yellowCards: team.yellowCards || team.tournament_yellow_cards || 0,
    redCards: team.redCards || team.tournament_red_cards || 0,
    players: team.players || []
  }
}

export async function fetchTeams({ force = false, cacheTTL = 15000 } = {}) {
  return serviceWrap(async () => {
    // httpClient baseURL 已是 /api，这里使用 /teams 避免 /api/teams 重复
    const res = await http.get('/teams', { cache: { ttl: cacheTTL, force } })
    if (!res.ok) throw buildError(res.error?.message || '获取球队列表失败', 'TEAMS_FETCH_FAILED', res.error, { status: res.status })
    const rawTeams = normalizeTeamsPayload(res.data)
    return rawTeams.map(mapTeam)
  })
}

// ========== CRUD ==========
export function createTeam(payload){
  return serviceWrap(async () => {
    const res = await http.post('/teams', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建球队失败', 'TEAM_CREATE_FAILED', res.error)
    return res.data
  })
}
export function updateTeam(teamId, payload){
  return serviceWrap(async () => {
    if(teamId===undefined || teamId===null) throw buildError('缺少 teamId', 'TEAM_ID_MISSING')
    const res = await http.put(`/teams/${teamId}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新球队失败', 'TEAM_UPDATE_FAILED', res.error)
    return res.data
  })
}
export function deleteTeam(teamId){
  return serviceWrap(async () => {
    if(teamId===undefined || teamId===null) throw buildError('缺少 teamId', 'TEAM_ID_MISSING')
    const res = await http.delete(`/teams/${teamId}`)
    if(!res.ok) throw buildError(res.error?.message || '删除球队失败', 'TEAM_DELETE_FAILED', res.error)
    return { success:true }
  })
}
export function fetchTeamByName(teamName){
  return serviceWrap(async () => {
    if(!teamName) throw buildError('缺少 teamName', 'TEAM_NAME_MISSING')
    const res = await http.get(`/teams/${encodeURIComponent(teamName)}`)
    if(!res.ok) throw buildError(res.error?.message || '获取球队详情失败', 'TEAM_FETCH_FAILED', res.error)
    return res.data
  })
}

// ========== 扩展接口（按名称更新 & 新API） ==========
export function updateTeamByName(teamName, payload){
  return serviceWrap(async () => {
    if(!teamName) throw buildError('缺少 teamName', 'TEAM_NAME_MISSING')
    const res = await http.put(`/teams/by-name/${encodeURIComponent(teamName)}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '按名称更新球队失败', 'TEAM_UPDATE_BY_NAME_FAILED', res.error)
    return res.data
  })
}
export function fetchTeamNewApi(teamName){
  return serviceWrap(async () => {
    if(!teamName) throw buildError('缺少 teamName', 'TEAM_NAME_MISSING')
    const res = await http.get(`/teams/${encodeURIComponent(teamName)}/new-api`)
    if(!res.ok) throw buildError(res.error?.message || '获取球队新接口数据失败', 'TEAM_FETCH_NEW_API_FAILED', res.error)
    return res.data
  })
}
