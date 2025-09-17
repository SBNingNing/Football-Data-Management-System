// tournaments.js: 赛事相关接口 -> 后端 /api/tournaments
// 统一使用 utils/httpClient.js (axios 实例 + 拦截器)
import http from '@/utils/httpClient';

export const fetchTournaments = (params) => http.get('/tournaments', { params });              // GET 全部(支持 group_by_name)
export const fetchTournamentByNameOrId = (nameOrId) => http.get(`/tournaments/${encodeURIComponent(nameOrId)}`); // GET 按名称或ID
export const createTournament = (data) => http.post('/tournaments', data);                     // POST 创建赛事实例 (competition_id + season_id)
export const updateTournament = (id, data) => http.put(`/tournaments/${id}`, data);            // PUT 更新赛事
export const deleteTournament = (id) => http.delete(`/tournaments/${id}`);                    // DELETE 删除赛事

// 赛事实例 (competition+season 组合) CRUD
export const createTournamentInstance = (data) => http.post('/tournaments/instances', data);  // POST 创建赛事实例
export const updateTournamentInstance = (id, data) => http.put(`/tournaments/instances/${id}`, data); // PUT 更新赛事实例

// 快速创建（可 dryRun）
export const quickCreateTournament = (data) => http.post('/tournaments/quick', data);          // POST 快速创建/复用