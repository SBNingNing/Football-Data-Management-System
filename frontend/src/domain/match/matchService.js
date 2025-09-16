/**
 * matchService (领域: match)
 * --------------------------------------------------
 * 目标: 聚合比赛详情与事件数据, 生成统一视图模型 (含补全统计和球员聚合)
 * 与之前的 domain/services 层等价, 但使用按领域分文件夹的命名方式。
 */
// 重构: 使用统一 httpClient + 内置缓存，而非直接依赖 api/* 模块
import http from '@/utils/httpClient'
import { toMatchViewModel } from '@/utils/mappers/matchMapper'
import logger from '@/utils/logger'
import { getMatchStatusTagType, MATCH_EVENT_TYPES } from '@/constants/match'
import { serviceWrap, buildError } from '@/utils/error'

// TODO: 后续把状态/事件常量迁移到 constants/match.js

function normSuccessArray(raw) {
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  if (raw.status === 'success' && Array.isArray(raw.data)) return raw.data
  if (Array.isArray(raw.data?.records)) return raw.data.records
  return []
}

function recomputeStatsFromEvents(matchVM, events = []) {
  if (!events.length) return matchVM
  let totalGoals = 0, totalOwnGoals = 0, totalYellowCards = 0, totalRedCards = 0
  let homeGoals = 0, awayGoals = 0, homeOwnGoals = 0, awayOwnGoals = 0
  let homeYellowCards = 0, awayYellowCards = 0, homeRedCards = 0, awayRedCards = 0
  const playerStatsMap = new Map()
  events.forEach(e => {
    const teamName = e.team_name
    if (e.player_id) {
      if (!playerStatsMap.has(e.player_id)) {
        playerStatsMap.set(e.player_id, {
          playerId: e.player_id,
            playerName: e.player_name || '未知球员',
            teamName: teamName || '未知球队',
            playerNumber: e.player_number || 0,
            goals: 0, ownGoals: 0, yellowCards: 0, redCards: 0
        })
      }
      const ps = playerStatsMap.get(e.player_id)
      switch (e.event_type) {
        case MATCH_EVENT_TYPES.GOAL: ps.goals++; totalGoals++; teamName === matchVM.homeTeam ? homeGoals++ : (teamName === matchVM.awayTeam && awayGoals++); break
        case MATCH_EVENT_TYPES.OWN_GOAL: ps.ownGoals++; totalOwnGoals++; teamName === matchVM.homeTeam ? homeOwnGoals++ : (teamName === matchVM.awayTeam && awayOwnGoals++); break
        case MATCH_EVENT_TYPES.YELLOW: ps.yellowCards++; totalYellowCards++; teamName === matchVM.homeTeam ? homeYellowCards++ : (teamName === matchVM.awayTeam && awayYellowCards++); break
        case MATCH_EVENT_TYPES.RED: ps.redCards++; totalRedCards++; teamName === matchVM.homeTeam ? homeRedCards++ : (teamName === matchVM.awayTeam && awayRedCards++); break
      }
    }
  })
  return {
    ...matchVM,
    totalGoals, totalOwnGoals, totalYellowCards, totalRedCards,
    totalPlayers: playerStatsMap.size || matchVM.totalPlayers,
    homeTeamStats: { ...matchVM.homeTeamStats, goals: homeGoals, ownGoals: homeOwnGoals, yellowCards: homeYellowCards, redCards: homeRedCards },
    awayTeamStats: { ...matchVM.awayTeamStats, goals: awayGoals, ownGoals: awayOwnGoals, yellowCards: awayYellowCards, redCards: awayRedCards },
    players: Array.from(playerStatsMap.values()) || matchVM.players
  }
}

export async function fetchMatchAggregate(matchId) {
  return serviceWrap(async () => {
    if (!matchId && matchId !== 0) {
      throw buildError('缺少 matchId', 'MATCH_ID_MISSING')
    }
    // 详情请求：使用缓存，避免短时间内重复点击造成多次网络访问
    const { ok: okDetail, data: detailData, error: detailError } = await http.get(`/matches/${matchId}`, {
      cache: { ttl: 15000, key: `match:${matchId}` }
    })
    if (!okDetail) {
      throw buildError(detailError?.message || '获取比赛详情失败', 'MATCH_FETCH_FAILED', detailError)
    }
    // 后端规范假设: { status: 'success', data: {...} }
  if (!(detailData?.success === true || detailData?.status === 'success')) {
      throw buildError(detailData?.message || '获取比赛详情失败', 'MATCH_FETCH_INVALID_STATUS', detailData)
    }
  // httpClient 已可能解包，兼容原 detailData.data
  const detailObj = detailData?.data && !detailData.__raw ? detailData.data : detailData
  const matchVM = toMatchViewModel(detailObj || {})
    let finalMatch = matchVM
    let events = matchVM.events || []
    let players = matchVM.players || []

    // 事件单独请求：允许失败降级。暂不缓存（事件更新频次可能较高），但可在需要时添加。
    try {
      const { ok: okEvents, data: eventsData } = await http.get('/events', {
        params: { match_id: matchId }
      })
  if (okEvents && (eventsData?.success === true || eventsData?.status === 'success')) {
    const evArr = Array.isArray(eventsData.data)?eventsData.data: Array.isArray(eventsData.records)?eventsData.records: eventsData.data
    if(Array.isArray(evArr)) events = evArr
        finalMatch = recomputeStatsFromEvents(matchVM, events)
        players = finalMatch.players
      } else {
        logger.info('[matchService] 事件接口返回空或非数组，沿用 match 详情内嵌数据')
      }
    } catch (err) {
      logger.warn('[matchService] 获取事件失败，使用 match 详情内 events', err)
    }
    logger.debug?.('[matchService] fetchMatchAggregate success', { matchId, players: players.length, events: events.length })
    return { match: finalMatch, players, events }
  })
}

// 比赛记录（分页）—— 从 statsService 迁移
export async function fetchMatchRecords({ token, params = {}, force = false } = {}) {
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined
  const res = await http.get('/matches/match-records', { params: {
    type: params.type || '',
    status: params.status || '',
    keyword: params.keyword || '',
    page: params.page || 1,
    pageSize: params.pageSize || 10
  }, headers, cache: { ttl: 8000, force } })
  if (!res.ok) return { ok:false, data:{ records:[], total:0 }, error: res.error }
  const records = normSuccessArray(res.data)
  const total = res.data?.data?.total || records.length
  const mapped = records.map(item => ({
    ...item,
    id: item.id || item.match_id || item.matchId || Math.random().toString(36).slice(2,10),
    score: item.score || `${item.home_score || 0} : ${item.away_score || 0}`,
    status: item.status || '待进行',
    name: item.name || item.match_name || `${item.team1 || '队伍1'} vs ${item.team2 || '队伍2'}`,
    team1: item.team1 || item.home_team || '队伍1',
    team2: item.team2 || item.away_team || '队伍2',
    date: item.date || item.match_time || '',
    location: item.location || '待定',
    type: item.type || 'championsCup'
  }))
  return { ok:true, data:{ records: mapped, total } }
}

// 近期比赛（固定取前5条）
export async function fetchRecentMatches({ token, force = false } = {}) {
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined
  const res = await http.get('/matches/match-records', { params: { page:1, pageSize:5 }, headers, cache: { ttl: 5000, force } })
  if (!res.ok) return { ok:false, data:[], error: res.error }
  const records = normSuccessArray(res.data)
  return { ok:true, data: records }
}

// 兼容导出：保持旧调用不报错（若有遗留引用），内部转调新常量方法
export function getStatusTagType(status){
  return getMatchStatusTagType(status)
}

// ========== 基础 CRUD ==========
export function createMatch(payload){
  return serviceWrap(async () => {
    const res = await http.post('/matches', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建比赛失败', 'MATCH_CREATE_FAILED', res.error)
    return res.data
  })
}
export function updateMatch(matchId, payload){
  return serviceWrap(async () => {
    if(matchId===undefined || matchId===null) throw buildError('缺少 matchId', 'MATCH_ID_MISSING')
    const res = await http.put(`/matches/${matchId}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新比赛失败', 'MATCH_UPDATE_FAILED', res.error)
    return res.data
  })
}
export function deleteMatch(matchId){
  return serviceWrap(async () => {
    if(matchId===undefined || matchId===null) throw buildError('缺少 matchId', 'MATCH_ID_MISSING')
    const res = await http.delete(`/matches/${matchId}`)
    if(!res.ok) throw buildError(res.error?.message || '删除比赛失败', 'MATCH_DELETE_FAILED', res.error)
    return { success:true }
  })
}
export function completeMatch(matchId){
  return serviceWrap(async () => {
    if(matchId===undefined || matchId===null) throw buildError('缺少 matchId', 'MATCH_ID_MISSING')
    const res = await http.put(`/matches/${matchId}/complete`)
    if(!res.ok) throw buildError(res.error?.message || '标记完赛失败', 'MATCH_COMPLETE_FAILED', res.error)
    return res.data
  })
}

// ========== 全量列表（管理维度） ==========
export function fetchMatchesRaw({ force = false, cacheTTL = 8000 } = {}) {
  return serviceWrap(async () => {
    const res = await http.get('/matches', { cache: { ttl: cacheTTL, force } })
    if(!res.ok) throw buildError(res.error?.message || '获取比赛列表失败', 'MATCHES_FETCH_FAILED', res.error)
    // 后端返回 { status:'success', data:[...] } 或 data.records
    const list = normSuccessArray(res.data)
    return list
  })
}
