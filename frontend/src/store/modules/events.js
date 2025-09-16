// useEventStore: 事件数据（进球/牌等）
import { defineStore } from 'pinia'
import http from '@/utils/httpClient'

export const useEventStore = defineStore('events', {
  state: () => ({ list: [], loading: false, error: null }),
  actions: {
  _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode}},
    async loadAll(){
      this.loading=true; this.error=null;
      try{
        const { ok, data, error } = await http.get('/events', { cache:{ ttl:10000, key:'events:list'} })
        if(!ok) throw error || new Error('获取事件失败')
        const body = data?.data || data // 兼容两种格式
        const list = Array.isArray(body) ? body : (Array.isArray(body?.data)? body.data: [])
        this.list = list
        return { success:true, data:list }
      }catch(e){ return this._err(e,'获取事件列表') } finally { this.loading=false }
    },
    async create(payload){
      this.loading=true; this.error=null;
      try{
        const { ok, data, error } = await http.post('/events', payload, { throwOnError:false })
        if(!ok || data?.status!=='success') throw (error || new Error(data?.message||'创建事件失败'))
        http.cache.invalidate('events:list')
        await this.loadAll();
        return { success:true, data }
      }catch(e){ return this._err(e,'创建事件') } finally { this.loading=false }
    },
    async update(id,payload){
      this.loading=true; this.error=null;
      try{
        const { ok, data, error } = await http.put(`/events/${id}`, payload)
        if(!ok || data?.status!=='success') throw (error || new Error(data?.message||'更新事件失败'))
        http.cache.invalidate('events:list')
        await this.loadAll();
        return { success:true, data }
      }catch(e){ return this._err(e,'更新事件') } finally { this.loading=false }
    },
    async remove(id){
      this.loading=true; this.error=null;
      try{
        const { ok, data, error } = await http.delete(`/events/${id}`)
        if(!ok || data?.status!=='success') throw (error || new Error(data?.message||'删除事件失败'))
        http.cache.invalidate('events:list')
        await this.loadAll();
        return { success:true }
      }catch(e){ return this._err(e,'删除事件') } finally { this.loading=false }
    }
  }
})
