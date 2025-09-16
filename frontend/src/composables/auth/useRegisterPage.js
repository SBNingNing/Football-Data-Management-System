// useRegisterPage (inlined)
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules'
import { ElMessage } from 'element-plus'
export function useRegisterPage(){
	const router = useRouter(); const authStore = useAuthStore(); const registerFormRef = ref(null)
	const registerForm = reactive({ username:'', email:'', password:'', confirmPassword:'' })
	const validatePass = (rule,value,callback)=>{ if(!value) return callback(new Error('请输入密码')); if(registerForm.confirmPassword) registerFormRef.value?.validateField('confirmPassword'); callback() }
	const validatePass2 = (rule,value,callback)=>{ if(!value) return callback(new Error('请再次输入密码')); if(value !== registerForm.password) return callback(new Error('两次输入密码不一致')); callback() }
	const rules = { username:[ { required:true, message:'请输入用户名', trigger:'blur' }, { min:3, max:20, message:'长度在 3 到 20 个字符', trigger:'blur' } ], email:[ { required:true, message:'请输入邮箱地址', trigger:'blur' }, { type:'email', message:'请输入正确的邮箱地址', trigger:'blur' } ], password:[ { required:true, message:'请输入密码', trigger:'blur' }, { min:6, message:'密码至少需要6个字符', trigger:'blur' }, { validator:validatePass, trigger:'blur' } ], confirmPassword:[ { required:true, message:'请再次输入密码', trigger:'blur' }, { validator:validatePass2, trigger:'blur' } ] }
	const submitForm = async ()=>{ if(!registerFormRef.value) return; await registerFormRef.value.validate(async (valid)=>{ if(!valid) return; const userData = { username:registerForm.username, email:registerForm.email, password:registerForm.password }; const success = await authStore.register(userData); if(success){ ElMessage.success('注册成功，请登录'); router.push('/login') } else { ElMessage.error(authStore.error || '注册失败') } }) }
	return { authStore, registerFormRef, registerForm, rules, submitForm }
}
