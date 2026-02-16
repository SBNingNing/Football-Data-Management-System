// events.js: 事件(进球/牌等)接口 -> 后端 /api/events
import http from '@/utils/httpClient';

export const fetchEvents = () => http.get('/events');                 // GET 列表
export const createEvent = (data) => http.post('/events', data);      // POST 创建
export const createEventsBatch = (data) => http.post('/events/batch', data); // POST 批量创建
export const updateEvent = (id, data) => http.put(`/events/${id}`, data); // PUT 更新
export const deleteEvent = (id) => http.delete(`/events/${id}`);      // DELETE 删除