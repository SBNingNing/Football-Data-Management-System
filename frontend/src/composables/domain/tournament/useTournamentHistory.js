/**
 * 锦标赛历史组合函数
 * 提供锦标赛数据、射手榜、卡牌榜和所有比赛的加载和管理
 */
import { ref } from 'vue'
import { fetchTournamentByNameOrId } from '@/api/tournaments'
import logger from '@/utils/logger'
import { normalizeError } from '@/utils/error'

/**
 * 锦标赛历史组合函数
 * @returns {Object} 锦标赛历史相关的响应式数据和方法
 */
export function useTournamentHistory() {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 比赛/锦标赛基本信息
  const competition = ref(null)
  
  // 射手榜数据
  const topScorers = ref([])
  
  // 卡牌榜数据
  const topCards = ref([])
  
  // 所有比赛列表
  const allMatches = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)
  
  // 最后加载的赛事名称（用于重试）
  const lastLoadedName = ref(null)
  
  // 重试次数
  const retryCount = ref(0)

  /**
   * 加载锦标赛历史数据
   * @param {string} name - 赛事名称
   * @param {Object} options - 加载选项
   * @param {boolean} options.silent - 是否静默加载（不显示加载状态）
   */
  async function load(name, { silent = false } = {}) {
    // 参数验证
    if (!name) {
      error.value = normalizeError(new Error('缺少赛事名称'))
      return
    }

    // 设置加载状态
    if (!silent) {
      loading.value = true
    }
    
    error.value = null
    lastLoadedName.value = name

    try {
      // 调用服务获取数据
      const res = await fetchTournamentByNameOrId(name)

      if (res.ok) {
        const data = res.data
        
        // Aggregate all matches from all records and map fields for frontend table
        const allMatchesList = data.records ? data.records.flatMap(r => (r.matches || []).map(m => ({
            ...m,
            matchDate: m.match_time,
            tournament: m.tournament_name,
            season: r.seasonName,
            homeTeam: m.home_team_name,
            awayTeam: m.away_team_name,
            homeScore: m.home_score,
            awayScore: m.away_score,
            totalYellowCards: 0, // Not provided in basic match list
            totalRedCards: 0     // Not provided in basic match list
        }))) : []

        // Aggregate all players for stats
        let allPlayers = []
        if (data.records) {
            data.records.forEach(record => {
                if (record.teams) {
                    record.teams.forEach(team => {
                        if (team.players) {
                            team.players.forEach(p => {
                                allPlayers.push({
                                    ...p,
                                    teamName: team.name,
                                    seasonName: record.seasonName
                                })
                            })
                        }
                    })
                }
            })
        }

        // Calculate top scorers
        const topScorersList = [...allPlayers]
            .sort((a, b) => b.goals - a.goals)
            .slice(0, 10)
            .map(p => ({
                name: p.player_name,
                team: p.teamName,
                goals: p.goals,
                season: p.seasonName
            }))

        // Calculate top cards
        const topCardsList = [...allPlayers]
            .sort((a, b) => (b.redCards * 2 + b.yellowCards) - (a.redCards * 2 + a.yellowCards))
            .slice(0, 10)
            .map(p => ({
                name: p.player_name,
                team: p.teamName,
                yellowCards: p.yellowCards,
                redCards: p.redCards,
                season: p.seasonName
            }))

        const vm = {
            competition: data,
            topScorers: topScorersList,
            topCards: topCardsList,
            allMatches: allMatchesList
        }

        // 简单适配，如果需要特定字段映射，可以在这里手动处理，或者直接使用后端字段
        if (!vm.competition.name && name) vm.competition.name = name
        // 成功时更新所有数据
        competition.value = vm.competition
        topScorers.value = vm.topScorers
        topCards.value = vm.topCards
        allMatches.value = vm.allMatches || []
        
        // 重置重试计数
        retryCount.value = 0
      } else {
        // 处理业务错误
        error.value = normalizeError(res.error)
        logger.error('[useTournamentHistory] 加载失败:', res.error)
      }
    } catch (e) {
      // 处理网络或其他异常
      error.value = normalizeError(e)
      logger.error('[useTournamentHistory] 加载异常:', e)
    } finally {
      // 清除加载状态
      if (!silent) {
        loading.value = false
      }
    }
  }

  /**
   * 重试加载数据
   * 使用最后一次加载的赛事名称重新加载
   */
  async function retry() {
    if (!lastLoadedName.value) {
      return
    }

    retryCount.value += 1
    return load(lastLoadedName.value)
  }

  return {
    // 响应式数据
    competition,
    topScorers,
    topCards,
    allMatches,
    loading,
    error,
    retryCount,
    
    // 方法
    load,
    retry
  }
}
