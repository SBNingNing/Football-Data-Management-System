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
  console.log('发送API请求，赛事名称:', tournamentName)
  const encodedName = encodeURIComponent(tournamentName)
  console.log('编码后的URL:', `/tournaments/${encodedName}`)
  console.log('完整请求URL:', `${import.meta.env.VITE_API_BASE_URL}/tournaments/${encodedName}`)
  
  return request({
    url: `/tournaments/${encodedName}`,
    method: 'get',
    timeout: 10000 // 10秒超时
  }).catch(error => {
    console.error('API请求失败:', error)
    throw error
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