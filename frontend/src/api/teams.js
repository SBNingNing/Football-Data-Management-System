// teams.js: 球队相关接口 -> 后端 /api/teams
import client from './client';

export const fetchTeams = () => client.get('/teams');              // GET 列表
export const createTeam = (data) => client.post('/teams', data);   // POST 创建
export const updateTeam = (id, data) => client.put(`/teams/${id}`, data); // PUT 更新(参赛实例)
export const deleteTeam = (id) => client.delete(`/teams/${id}`);   // DELETE 删除参赛实例
export const fetchTeamByName = (name) => client.get(`/teams/${encodeURIComponent(name)}`); // GET 按名称聚合
