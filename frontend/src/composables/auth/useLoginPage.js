// useLoginPage (inlined)
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules'
import { ElMessage } from 'element-plus'
export function useLoginPage(){
	const router = useRouter(); const authStore = useAuthStore()
	const loginFormRef = ref(null); const activeTab = ref('guest'); const guestLoading = ref(false); const loginForm = reactive({ username:'', password:'' })
	const rules = { username:[ { required:true, message:'请输入管理员账号', trigger:'blur' }, { min:3, max:20, message:'账号长度在 3 到 20 个字符', trigger:'blur' } ], password:[ { required:true, message:'请输入管理员密码', trigger:'blur' }, { min:6, message:'密码至少需要6个字符', trigger:'blur' } ] }
	const guestLogin = async ()=>{ guestLoading.value=true; try { await authStore.guest(); ElMessage.success('欢迎游客访问'); setTimeout(()=> router.push('/home'), 300) } catch { ElMessage.error(authStore.error || '进入失败，请重试') } finally { guestLoading.value=false } }
	const submitForm = async ()=>{ if(!loginFormRef.value) return; await loginFormRef.value.validate(async (valid)=>{ if(!valid) return; const adminData = { ...loginForm, role:'admin' }; const success = await authStore.adminLogin(adminData); if(success){ ElMessage.success('管理员登录成功'); router.push('/admin/board') } else { ElMessage.error(authStore.error || '登录失败，请检查账号密码') } }) }
	const handleTabChange = (tabName)=>{ if(tabName==='admin'){ loginForm.username=''; loginForm.password=''; loginFormRef.value && loginFormRef.value.clearValidate() } }
	return { authStore, loginFormRef, activeTab, guestLoading, loginForm, rules, guestLogin, submitForm, handleTabChange }
}
