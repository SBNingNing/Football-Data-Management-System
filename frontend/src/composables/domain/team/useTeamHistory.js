/**
 * 球队历史组合函数
 * 提供球队详情和比赛记录的加载和管理
 */
import { ref } from 'vue'
import { fetchTeamAggregate } from '@/domain/team/teamService'
import logger from '@/utils/logger'

/**
 * 球队历史组合函数
 * @param {Object} options - 配置选项
 * @param {Function} options.loader - 自定义加载器函数
 * @returns {Object} 球队历史相关的响应式数据和方法
 */
export function useTeamHistory({ loader } = {}) {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 球队基本信息
  const team = ref(null)
  
  // 球队比赛记录
  const records = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)

  /**
   * 加载球队历史数据
   * @param {string} teamName - 球队名称
   * @param {Object} options - 加载选项
   * @param {boolean} options.force - 是否强制刷新
   */
  async function load(teamName, { force = false } = {}) {
    // 参数验证
    if (!teamName) {
      error.value = new Error('缺少 teamName')
      return
    }

    // 设置加载状态
    loading.value = true
    error.value = null

    try {
      // 获取球队聚合数据
      const aggregateData = await fetchTeamAggregate(teamName, { 
        force, 
        loader 
      })

      // 更新数据
      team.value = aggregateData.team
      records.value = aggregateData.records
      
    } catch (e) {
      // 处理错误
      error.value = e
      logger.error('[useTeamHistory] 加载失败:', e)
    } finally {
      // 清除加载状态
      loading.value = false
    }
  }

  return {
    // 响应式数据
    team,
    records,
    loading,
    error,
    
    // 方法
    load
  }
}
