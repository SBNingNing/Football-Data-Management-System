// teams.js: 球队相关接口 -> 后端 /api/teams
import http from '@/utils/httpClient';

export const fetchTeams = () => http.get('/teams');              // GET 列表
export const createTeam = (data) => http.post('/teams', data);   // POST 创建
export const updateTeam = (id, data) => http.put(`/teams/${id}`, data); // PUT 更新(参赛实例)
export const deleteTeam = (id) => http.delete(`/teams/${id}`);   // DELETE 删除参赛实例
export const fetchTeamByName = (name) => http.get(`/teams/${encodeURIComponent(name)}`); // GET 按名称聚合