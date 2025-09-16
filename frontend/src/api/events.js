// events.js: 事件(进球/牌等)接口 -> 后端 /api/events
import client from './client';

export const fetchEvents = () => client.get('/events');                 // GET 列表
export const createEvent = (data) => client.post('/events', data);      // POST 创建
export const updateEvent = (id, data) => client.put(`/events/${id}`, data); // PUT 更新
export const deleteEvent = (id) => client.delete(`/events/${id}`);      // DELETE 删除
