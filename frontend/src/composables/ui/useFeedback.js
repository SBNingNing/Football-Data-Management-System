/**
 * 反馈系统组合函数
 * 提供统一的错误处理和加载状态管理
 */
import { ref, reactive, computed } from 'vue'
import { normalizeError } from '@/utils/error'

/**
 * 反馈系统组合函数
 * @returns {Object} 反馈系统相关状态和方法
 */
export function useFeedback() {
  // 待处理任务计数器
  const pendings = reactive(new Map())
  
  // 错误列表
  const errors = ref([])
  
  /**
   * 开始一个待处理任务
   * @param {string} key 任务标识
   */
  function begin(key) {
    pendings.set(key, (pendings.get(key) || 0) + 1)
  }
  
  /**
   * 结束一个待处理任务
   * @param {string} key 任务标识
   */
  function end(key) {
    const count = pendings.get(key)
    if (!count) return
    
    if (count <= 1) {
      pendings.delete(key)
    } else {
      pendings.set(key, count - 1)
    }
  }
  
  /**
   * 添加错误
   * @param {Error|Object} err 错误对象
   */
  function pushError(err) {
    errors.value.push(normalizeError(err))
  }
  
  /**
   * 清除错误
   * @param {number} index 错误索引，不传则清除所有错误
   */
  function clearError(index) {
    if (index == null) {
      errors.value = []
      return
    }
    
    errors.value.splice(index, 1)
  }
  
  /**
   * 是否有任务正在加载
   */
  const isLoading = computed(() => pendings.size > 0)
  
  /**
   * 跟踪 Promise 执行并管理加载状态
   * @param {string} key 任务标识
   * @param {Promise} promise Promise 对象
   * @returns {Promise} 执行结果
   */
  async function trackPromise(key, promise) {
    begin(key)
    
    try {
      return await promise
    } finally {
      end(key)
    }
  }
  
  return {
    // 状态
    isLoading,
    pendings,
    errors,
    
    // 方法
    begin,
    end,
    pushError,
    clearError,
    trackPromise
  }
}
