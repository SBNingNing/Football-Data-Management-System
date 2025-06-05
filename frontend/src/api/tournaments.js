import request from '@/utils/request'

// 获取所有赛事列表
export function getTournaments(params) {
  return request({
    url: '/tournaments',
    method: 'get',
    params
  })
}

// 根据赛事名称获取赛事详情和统计数据
export function getTournamentStats(tournamentName) {
  return request({
    url: `/tournaments/${encodeURIComponent(tournamentName)}`,
    method: 'get'
  })
}

// 创建赛事
export function createTournament(data) {
  return request({
    url: '/tournaments',
    method: 'post',
    data
  })
}

// 更新赛事
export function updateTournament(tournamentId, data) {
  return request({
    url: `/tournaments/${tournamentId}`,
    method: 'put',
    data
  })
}

// 删除赛事
export function deleteTournament(tournamentId) {
  return request({
    url: `/tournaments/${tournamentId}`,
    method: 'delete'
  })
}