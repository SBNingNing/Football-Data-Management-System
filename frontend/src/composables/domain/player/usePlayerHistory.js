/**
 * 球员历史组合函数
 * 提供球员详情、统计数据、赛季信息和球队历史的加载和管理
 */
import { ref } from 'vue'
import { fetchPlayerCompleteHistory } from '@/api/playerHistory'
import logger from '@/utils/logger'

/**
 * 球员历史组合函数
 * @param {Object} options - 配置选项
 * @param {Function} options.loader - 自定义加载器函数
 * @returns {Object} 球员历史相关的响应式数据和方法
 */
export function usePlayerHistory() {

  // 球员基本信息
  const player = ref(null)
  
  // 球员统计数据
  const stats = ref(null)
  
  // 球员参与的赛季列表
  const seasons = ref([])
  
  // 球员的球队历史
  const teamHistories = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)

  // =========================
  // 数据加载方法
  // =========================

  /**
   * 加载球员历史数据
   * @param {string} playerId - 球员ID
   * @param {Object} options - 加载选项
   * @param {boolean} options.force - 是否强制刷新
   */
  async function load(playerId, { force = false } = {}) {
    // 参数验证
    if (!playerId) {
      error.value = new Error('缺少 playerId')
      return
    }

    // 设置加载状态
    loading.value = true
    error.value = null

    try {
      // 获取球员聚合数据
      const res = await fetchPlayerCompleteHistory(playerId)
      
      if (res.ok) {
        const data = res.data
        logger.debug(`[usePlayerHistory] Received data:`, data);

        // Flatten teams from all seasons to create teamHistories
        const allTeams = data.seasons ? data.seasons.flatMap(season => season.teams.map(team => ({
            ...team,
            season_name: season.season_name,
            tournament_name: team.tournament_info?.name
        }))) : [];

        const viewModel = {
            ...data.player_info,
            ...data.career_summary,
            seasons: data.seasons,
            teamHistories: allTeams
        };

        // 更新各项数据
        player.value = viewModel;
        stats.value = viewModel; 
        seasons.value = viewModel.seasons;
        teamHistories.value = viewModel.teamHistories;
      } else {
        throw res.error || new Error('获取球员历史失败')
      }
      
    } catch (err) {
      // 处理错误
      const errorMessage = err.message || '未知错误';
      const errorDetails = err.details || {};
      error.value = err;
      logger.error(`[usePlayerHistory] 加载失败: ${errorMessage}`, { error: err, details: errorDetails });
    } finally {
      // 清除加载状态
      loading.value = false
    }
  }

  // =========================
  // 返回值
  // =========================

  return {
    // 响应式数据
    player,
    stats,
    seasons,
    teamHistories,
    loading,
    error,
    
    // 方法
    load
  }
}
