/**
 * 加载状态组合函数
 * 提供统一的加载状态管理
 */
import { ref } from 'vue'

/**
 * 加载状态组合函数
 * @returns {Object} 加载状态和方法
 */
export function useLoading() {
  const loading = ref(false)
  
  /**
   * 执行异步操作并管理加载状态
   * @param {Function} factory 异步操作函数
   * @returns {Promise} 操作结果
   */
  async function run(factory) {
    loading.value = true
    
    try {
      return await factory()
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    run
  }
}
