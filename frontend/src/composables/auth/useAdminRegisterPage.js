/**
 * useAdminRegisterPage - 管理员注册页面逻辑
 * 从 useRegisterPage 改造而来，专门用于管理员账号创建
 * 
 * 核心变更:
 * 1. 注册逻辑直接创建管理员账号（role: 'admin'）
 * 2. 表单验证针对管理员账号优化
 * 3. 预留游客权限控制扩展点
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules'
import { ElMessage } from 'element-plus'

export function useAdminRegisterPage() {
  const router = useRouter()
  const authStore = useAuthStore()
  const registerFormRef = ref(null)
  
  const registerForm = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  // 密码验证规则
  const validatePass = (rule, value, callback) => {
    if (!value) return callback(new Error('请输入密码'))
    if (registerForm.confirmPassword) {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }

  const validatePass2 = (rule, value, callback) => {
    if (!value) return callback(new Error('请再次输入密码'))
    if (value !== registerForm.password) {
      return callback(new Error('两次输入密码不一致'))
    }
    callback()
  }

  // 管理员注册表单验证规则
  const rules = {
    username: [
      { required: true, message: '请输入管理员用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
      { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入管理员邮箱地址', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码至少需要6个字符', trigger: 'blur' },
      { validator: validatePass, trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请再次输入密码', trigger: 'blur' },
      { validator: validatePass2, trigger: 'blur' }
    ]
  }

  // 提交管理员注册表单
  const submitForm = async () => {
    if (!registerFormRef.value) return

    await registerFormRef.value.validate(async (valid) => {
      if (!valid) return

      // 构造管理员注册数据
      const adminData = {
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
        role: 'admin' // 明确指定为管理员角色
      }

      try {
        // 调用管理员注册接口
        const success = await authStore.registerAdmin(adminData)
        
        if (success) {
          ElMessage.success('管理员账号创建成功，请使用管理员身份登录')
          // 注册成功后跳转到登录页面的管理员登录选项卡
          router.push('/login?tab=admin')
        } else {
          ElMessage.error(authStore.error || '管理员账号创建失败')
        }
      } catch (error) {
        console.error('管理员注册失败:', error)
        ElMessage.error('管理员账号创建失败，请稍后重试')
      }
    })
  }

  return {
    authStore,
    registerFormRef,
    registerForm,
    rules,
    submitForm
  }
}