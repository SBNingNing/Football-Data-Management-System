/**
 * 首页仪表板组合函数
 * 管理首页的统计数据、排行榜、淘汰赛对阵图、小组排名和最近比赛
 */
import { ref } from 'vue'
import { useMatchRecords } from '../match/useMatchRecords.js'
import logger from '@/utils/logger'
import { 
  fetchOverallStats, 
  fetchOverallRankings
} from '@/api/stats'
import { fetchMatches } from '@/api/matches'
import { fetchCompetitions } from '@/api/competitions'
import { fetchSeasons } from '@/api/seasons'

/**
 * 首页仪表板组合函数
 * @param {Object} options - 配置选项
 * @param {Object} options.feedback - 反馈处理器，用于显示加载状态和错误信息
 * @returns {Object} 仪表板相关的响应式数据和方法
 */
export function useHomeDashboard({ feedback }) {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 统计数据：总比赛数、即将到来的比赛数、已完成的比赛数
  const statsData = ref({
    totalMatches: 0,
    upcomingMatches: 0,
    completedMatches: 0
  })

  // 赛事列表
  const competitions = ref([])
  
  // 赛季列表
  const seasons = ref([])

  // 选中的赛季ID - 尝试从 sessionStorage 恢复
  const savedSeasonId = sessionStorage.getItem('home_selectedSeasonId')
  const selectedSeasonId = ref(savedSeasonId ? Number(savedSeasonId) : null)

  // 排行榜数据：动态键值 comp_{id}
  const rankings = ref({})

  // 淘汰赛对阵图数据
  const playoffBracket = ref({})

  // 小组排名数据
  const groupRankings = ref({})

  // 最近比赛数据
  const recentMatches = ref([])

  // 重试机制
  const retryCount = ref(0)
  const maxRetries = 3

  // 页面刷新检测
  const isPageRefresh = ref(!!(
    window.performance && 
    window.performance.navigation && 
    window.performance.navigation.type === 1
  ))

  // 比赛记录相关状态
  const matchRecordsC = useMatchRecords()
  const matchRecords = matchRecordsC.records
  const matchRecordsTotal = matchRecordsC.total
  const matchRecordsQuery = matchRecordsC.query

  // =========================
  // 辅助函数
  // =========================

  /**
   * 设置默认排行榜数据
   */
  function setDefaultRankings() {
    rankings.value = {}
  }

  // =========================
  // 数据加载函数
  // =========================

  /**
   * 加载赛事列表
   */
  async function loadCompetitions() {
    try {
      const res = await fetchCompetitions()
      if (res.ok) {
        const payload = res.data
        // 优先检查 payload.data.competitions (标准结构)
        if (payload && payload.data && Array.isArray(payload.data.competitions)) {
          competitions.value = payload.data.competitions
        } 
        // 其次检查 payload.competitions (直接返回)
        else if (payload && Array.isArray(payload.competitions)) {
          competitions.value = payload.competitions
        }
        // 再次检查 payload 本身是否为数组
        else if (Array.isArray(payload)) {
          competitions.value = payload
        }
        else {
          competitions.value = []
          logger.warn('Unexpected competitions response format', payload)
        }
        logger.debug('Loaded competitions:', competitions.value.length)
      }
    } catch (e) {
      logger.error('Failed to load competitions', e)
    }
  }

  /**
   * 加载统计数据
   */
  async function loadStats() {
    // 移除 token 依赖
    const { ok, data } = await fetchOverallStats()
    if (ok) {
      const d = data || {}
      statsData.value = {
        totalMatches: d.totalMatches || 0,
        upcomingMatches: d.upcomingMatches || 0,
        completedMatches: d.completedMatches || 0
      }
    }
  }

  /**
   * 加载小组排名数据
   */
  async function loadGroupRankings() {
    // 占位：后端无 /group-rankings
    groupRankings.value = { groups: [] }
  }

  /**
   * 加载淘汰赛对阵图数据
   */
  async function loadPlayoffBracket() {
    // 占位：后端无 /playoff-bracket
    playoffBracket.value = { rounds: [] }
  }

  /**
   * 加载赛季列表
   */
  async function loadSeasons() {
    try {
      const res = await fetchSeasons()
      if (res.ok) {
        const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
        seasons.value = list
      }
    } catch (e) {
      logger.error('Failed to load seasons', e)
    }
  }

  /**
   * 加载排行榜数据
   * @param {number} seasonId - 赛季ID
   */
  async function loadRankings(seasonId) {
    const params = {}
    if (seasonId) params.season_id = seasonId
    const { ok, data, error } = await fetchOverallRankings({ params })
    
    if (!ok) {
      logger.warn('rankings fail', error)
      setDefaultRankings()
      return
    }

    const newRankings = {}
    if (data) {
      Object.keys(data).forEach(key => {
        if (key.startsWith('comp_')) {
          newRankings[key] = data[key]
        }
      })
    }
    rankings.value = newRankings
  }
  /**
   * 获取比赛记录数据
   * @param {Object} params - 查询参数
   */
  async function fetchMatchRecords(params = {}) {
    const key = 'svc:match:records'
    feedback?.begin(key)
    
    try {
      // 支持强制刷新，确保获取最新数据
      await matchRecordsC.setFilter({ ...params })
    } catch (e) {
      feedback?.pushError(e)
    } finally {
      feedback?.end(key)
    }
  }

  /**
   * 获取最近比赛数据
   */
  async function fetchRecent() {
    const key = 'svc:recent-matches'
    feedback?.begin(key)
    
    try {
      const { ok, data, error } = await fetchMatches({ limit: 5, sort: 'desc' })
      
      if (!ok) {
        logger.warn('recent matches fail', error)
        recentMatches.value = []
        return
      }

      // 兼容后端返回格式：可能是数组，也可能是 { records: [] }
      // 注意：后端 get_all_matches 返回的是 { status: 'success', data: [...] }
      const list = Array.isArray(data) ? data : (data?.data || data?.records || [])
      recentMatches.value = list.map(m => ({
        ...m,
        type: m.matchType || m.competitionId, // Alias for component compatibility
        team1: m.team1 || m.home_team_name,
        team2: m.team2 || m.away_team_name,
        location: m.location || '待定'
      }))
    } finally {
      feedback?.end(key)
    }
  }

  // =========================
  // 事件处理函数
  // =========================

  /**
   * 处理比赛搜索
   * @param {Object} params - 搜索参数
   */
  function handleMatchSearch(params) {
    fetchMatchRecords(params)
  }

  /**
   * 处理比赛过滤
   * @param {Object} params - 过滤参数
   */
  function handleMatchFilter(params) {
    fetchMatchRecords(params)
  }

  /**
   * 处理比赛分页变化
   * @param {Object} params - 分页参数
   */
  function handleMatchPageChange(params) {
    fetchMatchRecords(params)
  }

  /**
   * 加载所有数据
   */
  async function loadAllData() {
    const key = 'view:home:init'
    feedback?.begin(key)
    
    try {
      await Promise.all([
        loadCompetitions(),
        loadSeasons(),
        loadStats(),
        loadGroupRankings(),
        loadPlayoffBracket(),
        loadRankings(selectedSeasonId.value),
        fetchMatchRecords({}),
        fetchRecent()
      ])
      
      retryCount.value = 0
    } catch (e) {
      logger.error('loadAllData error', e)
      feedback?.pushError(e)
      handleLoadError()
    } finally {
      feedback?.end(key)
    }
  }

  /**
   * 处理加载错误（重试机制）
   */
  function handleLoadError() {
    if (retryCount.value < maxRetries) {
      retryCount.value++
      setTimeout(() => loadAllData(), 600)
    }
  }

  /**
   * 刷新数据
   */
  function refreshData() {
    loadAllData()
  }

  /**
   * 比赛类型变化处理（预留接口）
   */
  function onCompetitionChange() {
    // 预留给未来的过滤逻辑
  }

  /**
   * 处理赛季变更
   * @param {number} seasonId
   */
  function handleSeasonChange(seasonId) {
    selectedSeasonId.value = seasonId
    if (seasonId) {
      sessionStorage.setItem('home_selectedSeasonId', seasonId)
    } else {
      sessionStorage.removeItem('home_selectedSeasonId')
    }
    loadRankings(seasonId)
  }

  /**
   * 排行榜标签页变化处理（预留接口）
   */
  function onRankingsTabChange() {
    // 预留接口
  }

  /**
   * 获取最近比赛的包装函数
   */
  function fetchRecentMatchesWrapper() {
    fetchRecent()
  }

  /**
   * 页面可见性变化处理
   * 当页面重新可见时刷新最近比赛数据
   */
  function handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
      fetchRecent()
    }
  }

  // =========================
  // 返回值
  // =========================

  return {
    // 响应式数据
    statsData,
    competitions,
    seasons,
    selectedSeasonId,
    rankings,
    playoffBracket,
    groupRankings,
    recentMatches,
    retryCount,
    isPageRefresh,
    matchRecords,
    matchRecordsTotal,
    matchRecordsQuery,
    
    // 方法
    loadAllData,
    fetchMatchRecords,
    fetchRecent: fetchRecentMatchesWrapper,
    handleSeasonChange,
    handleMatchSearch,
    handleMatchFilter,
    handleMatchPageChange,
    refreshData,
    onCompetitionChange,
    onRankingsTabChange,
    handleVisibilityChange
  }
}
