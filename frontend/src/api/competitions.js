// competitions.js: 竞赛（大项）相关接口 -> 后端 /api/competitions
import client from './client'

export const fetchCompetitions = (params) => client.get('/competitions', { params }) // 支持 sort_by / search
export const fetchCompetitionById = (id) => client.get(`/competitions/${id}`)
export const createCompetition = (data) => client.post('/competitions', data)
export const updateCompetition = (id, data) => client.put(`/competitions/${id}`, data)
export const deleteCompetition = (id) => client.delete(`/competitions/${id}`)
