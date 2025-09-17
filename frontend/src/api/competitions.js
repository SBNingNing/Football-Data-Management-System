// competitions.js: 竞赛（大项）相关接口 -> 后端 /api/competitions
import http from '@/utils/httpClient'

export const fetchCompetitions = (params) => http.get('/competitions', { params }) // 支持 sort_by / search
export const fetchCompetitionById = (id) => http.get(`/competitions/${id}`)
export const createCompetition = (data) => http.post('/competitions', data)
export const updateCompetition = (id, data) => http.put(`/competitions/${id}`, data)
export const deleteCompetition = (id) => http.delete(`/competitions/${id}`)