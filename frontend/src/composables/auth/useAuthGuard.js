/**
 * 权限守卫组合函数
 * 处理路由权限验证逻辑
 */
import { useAuthStore } from '@/store/modules'

/**
 * 权限守卫组合函数
 * @returns {Object} 权限验证方法
 */
export function useAuthGuard() {
  const auth = useAuthStore()
  
  /**
   * 检查路由权限
   * @param {Object} to 目标路由
   * @returns {Object} 权限检查结果
   */
  function check(to) {
    const requiresAuth = to.meta?.requiresAuth
    const allowGuest = to.meta?.allowGuest
    const requiredRoles = to.meta?.roles
    
    // 如果路由不需要认证，直接允许
    if (!requiresAuth) {
      return { allow: true }
    }
    
    // 检查用户是否已认证
    if (!auth.isAuthenticated) {
      // 如果允许游客访问，则允许
      if (allowGuest) {
        return { allow: true }
      }
      
      // 未认证且不允许游客，重定向到登录页
      return {
        allow: false,
        redirect: '/login',
        reason: 'NOT_AUTH'
      }
    }
    
    // 检查角色权限
    if (requiredRoles && Array.isArray(requiredRoles) && requiredRoles.length) {
      const userRole = auth.user?.role
      
      if (!userRole || !requiredRoles.includes(userRole)) {
        return {
          allow: false,
          redirect: '/home',
          reason: 'ROLE_FORBIDDEN'
        }
      }
    }
    
    return { allow: true }
  }
  
  return {
    check
  }
}
