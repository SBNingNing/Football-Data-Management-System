/**
 * 登录页面组合函数
 * 处理管理员登录和游客访问功能
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/modules'
import { ElMessage } from 'element-plus'

/**
 * 登录页面组合函数
 * @returns {Object} 登录相关状态和方法
 */
export function useLoginPage() {
  // 路由和存储
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  
  // 组件引用
  const loginFormRef = ref(null)
  
  // 页面状态
  const activeTab = ref('guest') // 默认游客选项卡
  const guestLoading = ref(false)
  
  // 表单数据
  const loginForm = reactive({
    username: '',
    password: ''
  })
  
  // 表单验证规则
  const rules = {
    username: [
      { 
        required: true, 
        message: '请输入管理员账号', 
        trigger: 'blur' 
      },
      { 
        min: 3, 
        max: 20, 
        message: '账号长度在3到20个字符', 
        trigger: 'blur' 
      }
    ],
    password: [
      { 
        required: true, 
        message: '请输入管理员密码', 
        trigger: 'blur' 
      },
      { 
        min: 6, 
        message: '密码至少需要6个字符', 
        trigger: 'blur' 
      }
    ]
  }
  
  // 初始化逻辑
  onMounted(() => {
    // 支持 URL 参数控制初始选项卡
    if (route.query.tab === 'admin') {
      activeTab.value = 'admin'
    }
  })
  
  /**
   * 游客登录
   */
  const guestLogin = async () => {
    guestLoading.value = true
    
    try {
      await authStore.guest()
      ElMessage.success('欢迎游客访问')
      
      setTimeout(() => {
        router.push('/home')
      }, 300)
    } catch {
      ElMessage.error(authStore.error || '进入失败，请重试')
    } finally {
      guestLoading.value = false
    }
  }
  
  /**
   * 管理员登录表单提交
   */
  const submitForm = async () => {
    if (!loginFormRef.value) return
    
    await loginFormRef.value.validate(async (valid) => {
      if (!valid) return
      
      const success = await authStore.adminLogin(loginForm)
      
      if (success && success.success) {
        ElMessage.success('管理员登录成功')
        router.push('/admin/board')
      } else {
        // 确保错误信息被正确显示
        const errorMsg = authStore.error || '登录失败，请检查账号密码';
        ElMessage.error(errorMsg)
      }
    })
  }
  
  /**
   * 处理选项卡切换
   * @param {string} tabName 选项卡名称
   */
  const handleTabChange = (tabName) => {
    if (tabName === 'admin') {
      // 切换到管理员选项卡时清空表单
      loginForm.username = ''
      loginForm.password = ''
      
      if (loginFormRef.value) {
        loginFormRef.value.clearValidate()
      }
    }
  }
  
  return {
    // Store
    authStore,
    
    // 组件引用
    loginFormRef,
    
    // 页面状态
    activeTab,
    guestLoading,
    
    // 表单数据
    loginForm,
    rules,
    
    // 方法
    guestLogin,
    submitForm,
    handleTabChange
  }
}