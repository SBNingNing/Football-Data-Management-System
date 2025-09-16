// tournaments.js: 赛事相关接口 -> 后端 /api/tournaments
// 统一使用 api/client.js (axios 实例 + 拦截器)
import client from './client';

export const fetchTournaments = (params) => client.get('/tournaments', { params });              // GET 全部(支持 group_by_name)
export const fetchTournamentByNameOrId = (nameOrId) => client.get(`/tournaments/${encodeURIComponent(nameOrId)}`); // GET 按名称或ID
export const createTournament = (data) => client.post('/tournaments', data);                     // POST 创建赛事(含首赛季)
export const updateTournament = (id, data) => client.put(`/tournaments/${id}`, data);            // PUT 更新赛事
export const deleteTournament = (id) => client.delete(`/tournaments/${id}`);                    // DELETE 删除赛事

// 赛事实例 (competition+season 组合) CRUD
export const createTournamentInstance = (data) => client.post('/tournaments/instances', data);  // POST 创建赛事实例
export const updateTournamentInstance = (id, data) => client.put(`/tournaments/instances/${id}`, data); // PUT 更新赛事实例

// 快速创建（可 dryRun）
export const quickCreateTournament = (data) => client.post('/tournaments/quick', data);          // POST 快速创建/复用
