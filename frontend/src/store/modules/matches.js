// useMatchStore: 比赛数据
import { defineStore } from 'pinia'
import { fetchMatches, createMatch, updateMatch, deleteMatch, completeMatch } from '@/api/matches'

export const useMatchStore = defineStore('matches', {
  state: () => ({ list: [], loading: false, error: null }),
  actions: {
  _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode}},
    async loadAll(){ this.loading=true; this.error=null; try{ const r=await fetchMatches(); const d=r.data; this.list = Array.isArray(d.data)?d.data: (Array.isArray(d)?d:[]); return {success:true,data:this.list}; }catch(e){ return this._err(e,'获取比赛列表'); } finally { this.loading=false } },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createMatch(payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'创建比赛'); } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updateMatch(id,payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'更新比赛'); } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteMatch(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'删除比赛'); } finally { this.loading=false } },
    async complete(id){ this.loading=true; this.error=null; try{ const r=await completeMatch(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'完赛操作'); } finally { this.loading=false } }
  }
})
