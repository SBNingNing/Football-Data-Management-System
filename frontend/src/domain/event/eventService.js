// eventService: 事件领域服务 (包装基础 CRUD + 可扩展批量)
// 统一 serviceWrap 返回 { ok,data,error } 结构
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

function normalizeEventsPayload(raw){
  if(!raw) return []
  if(Array.isArray(raw)) return raw
  if(Array.isArray(raw.data)) return raw.data
  // 兼容新旧字段：优先 success 布尔，其次旧 status 字符串
  if((raw.success===true || raw.status==='success') && Array.isArray(raw.data)) return raw.data
  return []
}

export function fetchEvents({ params = {}, force = false, cacheTTL = 10000 } = {}) {
  return serviceWrap(async () => {
    const res = await http.get('/events', { params, cache:{ ttl: cacheTTL, force } })
    if(!res.ok) throw buildError(res.error?.message || '获取事件列表失败', 'EVENTS_FETCH_FAILED', res.error)
    return normalizeEventsPayload(res.data)
  })
}

// 按比赛 ID 语义方法
export function fetchEventsByMatch(matchId, { force = false, cacheTTL = 6000 } = {}) {
  return serviceWrap(async () => {
    if(!matchId && matchId!==0) throw buildError('缺少 matchId', 'MATCH_ID_MISSING')
    const res = await http.get('/events', { params:{ match_id: matchId }, cache:{ ttl: cacheTTL, force, key: `events:match:${matchId}` } })
    if(!res.ok) throw buildError(res.error?.message || '获取比赛事件失败', 'EVENTS_BY_MATCH_FAILED', res.error)
    return normalizeEventsPayload(res.data)
  })
}

export function createEvent(payload){
  return serviceWrap(async () => {
    const res = await http.post('/events', payload)
    if(!res.ok) throw buildError(res.error?.message || '创建事件失败', 'EVENT_CREATE_FAILED', res.error)
    return res.data
  })
}

export function updateEvent(id, payload){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 eventId', 'EVENT_ID_MISSING')
    const res = await http.put(`/events/${id}`, payload)
    if(!res.ok) throw buildError(res.error?.message || '更新事件失败', 'EVENT_UPDATE_FAILED', res.error)
    return res.data
  })
}

export function deleteEvent(id){
  return serviceWrap(async () => {
    if(id===undefined || id===null) throw buildError('缺少 eventId', 'EVENT_ID_MISSING')
    const res = await http.delete(`/events/${id}`)
    if(!res.ok) throw buildError(res.error?.message || '删除事件失败', 'EVENT_DELETE_FAILED', res.error)
    return { success:true }
  })
}

// 批量创建（后端暂不支持批量接口时，前端串行/并发提交）
export async function createEventsBatch(list = [], { parallel = false } = {}) {
  return serviceWrap(async () => {
    const results = []
    if(parallel){
      const settled = await Promise.allSettled(list.map(p => http.post('/events', p)))
      settled.forEach((r,i) => {
        if(r.status==='fulfilled' && r.value.ok){
          results.push({ ok:true, data:r.value.data })
        } else {
          results.push({ ok:false, error:r.reason || r.value?.error, index:i })
        }
      })
    } else {
      for(let i=0;i<list.length;i++){
        const payload = list[i]
        const res = await http.post('/events', payload)
        if(res.ok) results.push({ ok:true, data:res.data })
        else results.push({ ok:false, error:res.error, index:i })
      }
    }
    return { total:list.length, success: results.filter(r=>r.ok).length, results }
  })
}
