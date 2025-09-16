// useAuthStore: 只负责用户身份 & token；不夹杂业务数据列表
import { defineStore } from 'pinia'
import { login, register, guestLogin, adminLogin, logout as apiLogout } from '@/api/auth'
import { setAuthToken } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    currentUser: (s) => s.user
  },
  actions: {
    init(){ if(this.token) setAuthToken(this.token) },
    _err(e, fallback){ const msg = e?.message || fallback; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode} },
    async login(credentials){ this.loading=true; this.error=null; try{ const { token, user } = await login(credentials); this.token=token; this.user=user; return {success:true} }catch(e){ return this._err(e,'登录失败'); } finally { this.loading=false } },
    async register(userData){ this.loading=true; this.error=null; try{ await register(userData); return {success:true} }catch(e){ return this._err(e,'注册失败'); } finally { this.loading=false } },
    async guest(){ this.loading=true; this.error=null; try{ const { token } = await guestLogin(); this.token=token; this.user={ role:'guest' }; return {success:true} }catch(e){ return this._err(e,'游客登录失败'); } finally { this.loading=false } },
    async adminLogin(credentials){ this.loading=true; this.error=null; try{ const { token, user } = await adminLogin(credentials); this.token=token; this.user=user; return {success:true} }catch(e){ return this._err(e,'管理员登录失败'); } finally { this.loading=false } },
    logout(){ apiLogout(); this.user=null; this.token=null; setAuthToken(null); }
  }
})
