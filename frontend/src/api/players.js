// players.js: 球员接口 -> 后端 /api/players
import http from '@/utils/httpClient';

export const fetchPlayers = () => http.get('/players');                 // GET 列表
export const fetchPlayerById = (id) => http.get(`/players/${id}`);      // GET 详情
export const createPlayer = (data) => http.post('/players', data);      // POST 创建
export const updatePlayer = (id, data) => http.put(`/players/${id}`, data); // PUT 更新
export const deletePlayer = (id) => http.delete(`/players/${id}`);      // DELETE 删除