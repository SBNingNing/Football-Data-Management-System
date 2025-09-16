// players.js: 球员接口 -> 后端 /api/players
import client from './client';

export const fetchPlayers = () => client.get('/players');                 // GET 列表
export const fetchPlayerById = (id) => client.get(`/players/${id}`);      // GET 详情
export const createPlayer = (data) => client.post('/players', data);      // POST 创建
export const updatePlayer = (id, data) => client.put(`/players/${id}`, data); // PUT 更新
export const deletePlayer = (id) => client.delete(`/players/${id}`);      // DELETE 删除
