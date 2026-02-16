/**
 * 球队历史组合函数
 * 提供球队详情和比赛记录的加载和管理
 */
import { ref } from 'vue'
import { fetchTeamByName } from '@/api/teams'
import { useTeamHistoryStore } from '@/store/modules'
import logger from '@/utils/logger'

/**
 * 球队历史组合函数
 * @param {Object} options - 配置选项
 * @param {Function} options.loader - 自定义加载器函数
 * @returns {Object} 球队历史相关的响应式数据和方法
 */
export function useTeamHistory() {
  const store = useTeamHistoryStore()
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
   * @param {string} team_name - 球队名称
   * @param {Object} options - 加载选项
   * @param {boolean} options.force - 是否强制刷新
   */
  async function load(team_name, { force = false } = {}) {
    // 参数验证
    if (!team_name) {
      error.value = new Error('缺少 team_name')
      return
    }

    // 设置加载状态
    loading.value = true
    error.value = null

    try {
      // 1. 获取球队基础信息以拿到 team_base_id
      const teamRes = await fetchTeamByName(team_name)
      const teamInfo = teamRes.data
      
      if (!teamInfo || !teamInfo.team_base_id) {
         // 如果没有 team_base_id，尝试直接使用返回的数据（如果是旧接口格式）
         if (teamInfo && teamInfo.records) {
             team.value = teamInfo
             records.value = teamInfo.records || []
             return
         }
         throw new Error('无法获取球队ID')
      }

      // 2. 使用 Store 加载完整历史
      const res = await store.loadComplete(teamInfo.team_base_id, { force })
      
      if (res.success) {
        // Flatten tournaments from all seasons
        const allTournaments = res.data.records ? res.data.records.flatMap(seasonBlock => 
            (seasonBlock.tournaments || []).map(t => ({
                ...t,
                season_name: seasonBlock.season_info?.name,
                players: t.players || []
            }))
        ) : []

        team.value = res.data.team_info
        records.value = allTournaments
      } else {
        throw new Error(res.error || '加载失败')
      }
    } catch (err) {
      error.value = err
      logger.error('[useTeamHistory] 加载失败:', err)
    } finally {
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
