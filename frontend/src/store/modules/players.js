// usePlayerStore: 专注球员数据
import { defineStore } from 'pinia'
import { fetchPlayers, fetchPlayerById, createPlayer, updatePlayer, deletePlayer } from '@/api/players'

export const usePlayerStore = defineStore('players', {
  state: () => ({ list: [], loading: false, error: null, current: null }),
  actions: {
  _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode}},
    async loadAll(){ this.loading=true; this.error=null; try{ const r=await fetchPlayers(); const d=r.data; this.list = Array.isArray(d.data)?d.data: (Array.isArray(d)?d:[]); return {success:true,data:this.list}; }catch(e){ return this._err(e,'获取球员列表'); } finally { this.loading=false } },
    async loadById(id){ this.loading=true; this.error=null; try{ const r=await fetchPlayerById(id); const d=r.data; if(d.success===true || d.status==='success'){ this.current=d.data; return {success:true,data:d.data}; } return {success:false,error:d.message||'获取失败'} }catch(e){ return this._err(e,'获取球员详情'); } finally { this.loading=false } },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createPlayer(payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'创建球员'); } finally { this.loading=false } },
    async update(id,payload){ this.loading=true; this.error=null; try{ const r=await updatePlayer(id,payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'更新球员'); } finally { this.loading=false } },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deletePlayer(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'删除球员'); } finally { this.loading=false } }
  }
})
