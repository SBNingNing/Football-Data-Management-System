/**
 * 用户注册页面组合函数
 * 处理普通用户注册功能
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules'
import { ElMessage } from 'element-plus'

/**
 * 用户注册页面组合函数
 * @returns {Object} 注册相关状态和方法
 */
export function useRegisterPage() {
  // 路由和存储
  const router = useRouter()
  const authStore = useAuthStore()
  
  // 组件引用
  const registerFormRef = ref(null)
  
  // 表单数据
  const registerForm = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  
  /**
   * 密码验证函数
   * @param {Object} rule 验证规则
   * @param {string} value 输入值
   * @param {Function} callback 回调函数
   */
  const validatePass = (rule, value, callback) => {
    if (!value) {
      return callback(new Error('请输入密码'))
    }
    
    if (registerForm.confirmPassword) {
      registerFormRef.value?.validateField('confirmPassword')
    }
    
    callback()
  }
  
  /**
   * 确认密码验证函数
   * @param {Object} rule 验证规则
   * @param {string} value 输入值
   * @param {Function} callback 回调函数
   */
  const validatePass2 = (rule, value, callback) => {
    if (!value) {
      return callback(new Error('请再次输入密码'))
    }
    
    if (value !== registerForm.password) {
      return callback(new Error('两次输入密码不一致'))
    }
    
    callback()
  }
  
  // 表单验证规则
  const rules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
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
  
  /**
   * 提交注册表单
   */
  const submitForm = async () => {
    if (!registerFormRef.value) return
    
    await registerFormRef.value.validate(async (valid) => {
      if (!valid) return
      
      const userData = {
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password
      }
      
      const success = await authStore.register(userData)
      
      if (success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } else {
        ElMessage.error(authStore.error || '注册失败')
      }
    })
  }
  
  return {
    // Store
    authStore,
    
    // 组件引用
    registerFormRef,
    
    // 表单数据
    registerForm,
    rules,
    
    // 方法
    submitForm
  }
}
