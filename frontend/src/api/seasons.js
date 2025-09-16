// seasons.js: 赛季相关接口 -> 后端 /api/seasons
import client from './client'

export const fetchSeasons = () => client.get('/seasons')              // GET 列表
export const fetchSeasonById = (id) => client.get(`/seasons/${id}`)    // GET 详情
export const createSeason = (data) => client.post('/seasons', data)    // POST 创建
export const updateSeason = (id, data) => client.put(`/seasons/${id}`, data) // PUT 更新
export const deleteSeason = (id) => client.delete(`/seasons/${id}`)    // DELETE 删除
