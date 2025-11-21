// useTeamStore: 专注球队数据（列表 + 详情拉取与 CRUD）
import { defineStore } from 'pinia'
import { fetchTeams, createTeam, updateTeam, deleteTeam, fetchTeamByName } from '@/api/teams'

export const useTeamStore = defineStore('teams', {
  state: () => ({
    list: [],
    loading: false,
    error: null,
    current: null
  }),
  actions: {
  _err(e, op){ const msg = e?.message || op + '失败'; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode}},
    async loadAll(){ 
      this.loading=true; 
      this.error=null; 
      try{ 
        const response = await fetchTeams(); 
        let rawData = response.data || response;
        
        if (rawData && typeof rawData === 'object' && !Array.isArray(rawData) && Array.isArray(rawData.data)) {
          this.list = rawData.data;
        } else if (Array.isArray(rawData)) {
          this.list = rawData;
        } else {
          this.list = [];
        }
        
        return {success:true, data:this.list}; 
      }catch(e){ 
        return this._err(e,'获取球队列表'); 
      } finally { 
        this.loading=false 
      } 
    },
    async loadByName(name){ this.loading=true; this.error=null; try{ const data=await fetchTeamByName(name); if(data.success===true || data.status==='success'){ this.current=data.data; return {success:true,data:data.data}; } return {success:false,error:data.message||'获取失败'} }catch(e){ return this._err(e,'获取球队详情'); } finally { this.loading=false } },
    async create(payload){ this.loading=true; this.error=null; try{ const r=await createTeam(payload); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true,data:r.data}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'创建球队'); } finally { this.loading=false } },
    async update(id,payload){ 
      this.loading=true; 
      this.error=null; 
      try{ 
        const r=await updateTeam(id,payload); 
        if (!r.ok) return {success:false, error: r.error?.message || '更新失败'};
        if(r.data.success===true || r.data.status==='success'){ 
          await this.loadAll(); 
          return {success:true,data:r.data}; 
        } 
        return {success:false,error:r.data.message}; 
      }catch(e){ 
        return this._err(e,'更新球队'); 
      } finally { 
        this.loading=false 
      } 
    },
    async remove(id){ this.loading=true; this.error=null; try{ const r=await deleteTeam(id); if(r.data.success===true || r.data.status==='success'){ await this.loadAll(); return {success:true}; } return {success:false,error:r.data.message}; }catch(e){ return this._err(e,'删除球队'); } finally { this.loading=false } }
  }
})
