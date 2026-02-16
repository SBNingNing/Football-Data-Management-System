/**
 * matches API
 * 统一比赛相关接口封装; 返回均为 axios Promise。
 * 注意: getMatchDetail 结果传入 mapper(toMatchViewModel) 做字段标准化。
 * 扩展: 若新增分页/筛选, 在此追加函数, 避免组件直接拼接 URL。
 */
import http from '@/utils/httpClient';

export const fetchMatches = (params) => http.get('/matches', { params });                 // GET 列表
export const fetchMatchRecords = (params) => http.get('/matches/match-records', { params }); // GET 比赛记录
export const createMatch = (data) => http.post('/matches', data);       // POST 创建
export const updateMatch = (id, data) => http.put(`/matches/${id}`, data); // PUT 更新
export const deleteMatch = (id) => http.delete(`/matches/${id}`);       // DELETE 删除
export const completeMatch = (id) => http.put(`/matches/${id}/complete`); // PUT 完赛
export const getMatchDetail = (id, opts) => http.get(`/matches/${id}`, opts);       // GET 详情 (包含 players/events 复合数据)