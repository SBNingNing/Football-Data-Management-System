// useAuthGuard (inlined)
import { useAuthStore } from '@/store/modules'
export function useAuthGuard(){
	const auth = useAuthStore()
	function check(to){ const requiresAuth = to.meta?.requiresAuth; const allowGuest = to.meta?.allowGuest; const requiredRoles = to.meta?.roles; if(!requiresAuth) return { allow:true }; if(!auth.isAuthenticated){ if(allowGuest) return { allow:true }; return { allow:false, redirect:'/login', reason:'NOT_AUTH' } } if(requiredRoles && Array.isArray(requiredRoles) && requiredRoles.length){ const userRole = auth.user?.role; if(!userRole || !requiredRoles.includes(userRole)){ return { allow:false, redirect:'/home', reason:'ROLE_FORBIDDEN' } } } return { allow:true } }
	return { check }
}
