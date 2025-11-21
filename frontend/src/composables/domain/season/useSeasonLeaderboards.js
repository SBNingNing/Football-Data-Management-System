/**
 * 赛季排行榜组合函数
 * 基于赛季数据计算射手榜和卡牌榜
 */
import { computed } from 'vue'

/**
 * 赛季排行榜组合函数
 * @param {import('vue').Ref} seasonRef - 赛季数据的响应式引用
 * @returns {Object} 包含射手榜和卡牌榜的计算属性
 */
export function useSeasonLeaderboards(seasonRef) {
  /**
   * 射手榜计算属性
   * 按进球数降序排列，取前10名
   */
  const topScorers = computed(() => {
    const season = seasonRef?.value
    
    // 验证数据结构
    if (!season || !Array.isArray(season.teams)) {
      return []
    }

    const scorersList = []

    // 遍历所有球队和球员，收集进球数据
    season.teams.forEach(team => {
      if (!Array.isArray(team.players)) return

      team.players.forEach(player => {
        const goals = player.goals || 0
        
        if (goals > 0) {
          scorersList.push({
            ...player,
            team_name: team.name
          })
        }
      })
    })

    // 按进球数降序排序，取前10名
    return scorersList
      .sort((a, b) => (b.goals || 0) - (a.goals || 0))
      .slice(0, 10)
  })

  /**
   * 卡牌榜计算属性
   * 按总卡牌数（红牌+黄牌）降序排列，取前10名
   */
  const topCards = computed(() => {
    const season = seasonRef?.value
    
    // 验证数据结构
    if (!season || !Array.isArray(season.teams)) {
      return []
    }

    const cardsList = []

    // 遍历所有球队和球员，收集卡牌数据
    season.teams.forEach(team => {
      if (!Array.isArray(team.players)) return

      team.players.forEach(player => {
        const yellowCards = player.yellowCards || 0
        const redCards = player.redCards || 0
        
        // 只统计有卡牌记录的球员
        if (yellowCards > 0 || redCards > 0) {
          cardsList.push({
            ...player,
            team_name: team.name
          })
        }
      })
    })

    // 按总卡牌数降序排序（红牌+黄牌），取前10名
    return cardsList
      .sort((a, b) => {
        const totalA = (a.redCards || 0) + (a.yellowCards || 0)
        const totalB = (b.redCards || 0) + (b.yellowCards || 0)
        return totalB - totalA
      })
      .slice(0, 10)
  })

  return {
    topScorers,
    topCards
  }
}
