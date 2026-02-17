// useAuthStore: 只负责用户身份 & token；不夹杂业务数据列表
import { defineStore } from 'pinia'
import { login, register, registerAdmin as apiRegisterAdmin, guestLogin, adminLogin, getMe, logout as apiLogout } from '@/api/auth'
import { setAuthToken } from '@/utils/httpClient'
import logger from '@/utils/logger'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    currentUser: (s) => s.user,
    // 后续游客/管理员权限扩展预留
    userRole: (s) => s.user?.role || 'guest',
    isGuest: (s) => s.user?.role === 'guest',
    isAdmin: (s) => s.user?.role === 'admin',
    // 游客界面权限控制：用于组件级别的权限判断
    canAccessAdminFeatures: (s) => s.user?.role === 'admin',
    shouldShowGuestOnlyUI: (s) => s.user?.role === 'guest'
  },
  actions: {
    init(){ 
      logger.info('[Auth Store] 初始化, token:', this.token);
      if(this.token) setAuthToken(this.token) 
    },
    _err(e, fallback){ const msg = e?.message || fallback; this.error = msg; return {success:false,error:msg,statusCode:e?.statusCode} },
    async fetchMe(){
      if(!this.token) return false;
      try{
        const me = await getMe();
        if(me && typeof me === 'object') this.user = me;
        return !!this.user;
      }catch{
        // token 失效则清空
        this.user = null; this.token = null; setAuthToken(null);
        return false;
      }
    },
    async login(credentials){
      this.loading=true; this.error=null;
      try{
        const { token, user } = await login(credentials);
        this.token=token; this.user=user;
        setAuthToken(token); // 确保 httpClient 获得 token
        localStorage.setItem('token', token);
        // 强一致：再拉取一次 /auth/me，确保角色与状态最新
        try { this.user = await getMe(); } catch { /* ignore me refresh */ }
        return {success:true}
      }catch(e){
        return this._err(e,'登录失败');
      } finally { this.loading=false }
    },
    async register(userData){ this.loading=true; this.error=null; try{ await register(userData); return {success:true} }catch(e){ return this._err(e,'注册失败'); } finally { this.loading=false } },
    async registerAdmin(adminData){ 
      this.loading=true; this.error=null; 
      try{ 
        const res = await apiRegisterAdmin(adminData); 
        // 检查 http 客户端返回的 ok 状态
        if (!res.ok) {
           // 优先尝试获取后端直接返回的 error 字段
           // 后端返回格式通常为: {'error': '具体错误信息'} 或 {'error': '参数验证失败', 'details': [...]}
           const rawData = res.error?.raw?.response?.data;
           const explicitError = rawData?.error;
           
           // 如果有 details 数组，可能需要将其格式化为字符串
           let detailedMsg = '';
           if (rawData?.details && Array.isArray(rawData.details)) {
             detailedMsg = rawData.details.map(d => `${d.loc?.[0]}: ${d.msg}`).join('; ');
           }

           const finalMsg = explicitError 
             ? (detailedMsg ? `${explicitError}: ${detailedMsg}` : explicitError)
             : (res.error?.message || '管理员注册失败');

           throw new Error(finalMsg);
        }
        return true; 
      }catch(e){ 
        this.error = e.message;
        return false; 
      } finally { 
        this.loading=false 
      } 
    },
    async guest(){
      this.loading=true; this.error=null;
      try{
        const { token } = await guestLogin();
        this.token=token; this.user={ role:'guest', username:'guest' };
        setAuthToken(token); // 确保 httpClient 获得 token
        localStorage.setItem('token', token);
        logger.info('[Auth Store] 游客登录成功, token:', token);
        try { this.user = await getMe(); } catch { /* ignore me refresh for guest */ }
        return {success:true}
      }catch(e){
        return this._err(e,'游客登录失败');
      } finally { this.loading=false }
    },
    async adminLogin(credentials){
      this.loading=true; this.error=null;
      try{
        const { token, user } = await adminLogin(credentials);
        this.token=token; this.user=user;
        setAuthToken(token); // 确保 httpClient 获得 token
        localStorage.setItem('token', token);
        logger.info('[Auth Store] 管理员登录成功, token:', token);
        try { this.user = await getMe(); } catch { /* ignore me refresh */ }
        return {success:true}
      }catch(e){
        return this._err(e,'管理员登录失败');
      } finally { this.loading=false }
    },
    logout(){ apiLogout(); this.user=null; this.token=null; setAuthToken(null); }
  }
})