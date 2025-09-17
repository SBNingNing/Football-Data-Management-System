// seasons.js: 赛季相关接口 -> 后端 /api/seasons
import http from '@/utils/httpClient'

export const fetchSeasons = () => http.get('/seasons')              // GET 列表
export const fetchSeasonById = (id) => http.get(`/seasons/${id}`)    // GET 详情
export const createSeason = (data) => http.post('/seasons', data)    // POST 创建
export const updateSeason = (id, data) => http.put(`/seasons/${id}`, data) // PUT 更新
export const deleteSeason = (id) => http.delete(`/seasons/${id}`)    // DELETE 删除