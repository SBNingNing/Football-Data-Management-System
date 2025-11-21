/**
 * 管理端过滤、搜索、分页组合函数
 * 处理球队、比赛、事件、球员的统一过滤逻辑
 */
import { ref, computed, watch } from 'vue'

/**
 * 分页尺寸默认值（按 UI 布局列数确定）
 */
const DEFAULT_PAGE_SIZES = Object.freeze({
  match: 9,
  event: 12,
  player: 9,
  team: 6
})

/**
 * 管理端复合过滤/搜索/分页组合函数
 * - 防御式处理：过滤过程中允许数据项为 null/undefined
 * - search debounce：300ms（单独字段触发，不共享跨类型）
 *
 * @param {object} propsRef 组件 props 引用（包含 matches/events/players/teams 数组）
 * @param {() => string} getMatchType 返回当前管理视图选中的 matchType
 * @returns {Object} 过滤相关状态和方法
 */
export default function useManagementFilters(propsRef, getMatchType) {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 搜索关键词
  const matchSearchKeyword = ref('')
  const eventSearchKeyword = ref('')
  const playerSearchKeyword = ref('')
  const teamSearchKeyword = ref('')

  // 过滤器
  const matchStatusFilter = ref('')
  const eventTypeFilter = ref('')
  const playerTeamFilter = ref('')
  const teamPlayerCountFilter = ref('')

  // 分页状态
  const matchCurrentPage = ref(1)
  const matchPageSize = ref(DEFAULT_PAGE_SIZES.match)
  const eventCurrentPage = ref(1)
  const eventPageSize = ref(DEFAULT_PAGE_SIZES.event)
  const playerCurrentPage = ref(1)
  const playerPageSize = ref(DEFAULT_PAGE_SIZES.player)
  const teamCurrentPage = ref(1)
  const teamPageSize = ref(DEFAULT_PAGE_SIZES.team)

  // =========================
  // 搜索防抖处理
  // =========================
  
  let searchTimer = null
  
  /**
   * 防抖重置分页
   * @param {string} type 数据类型
   */
  const debounceResetPage = (type) => {
    if (searchTimer) {
      clearTimeout(searchTimer)
    }
    
    searchTimer = setTimeout(() => {
      switch (type) {
        case 'match':
          matchCurrentPage.value = 1
          break
        case 'event':
          eventCurrentPage.value = 1
          break
        case 'player':
          playerCurrentPage.value = 1
          break
        case 'team':
          teamCurrentPage.value = 1
          break
      }
    }, 300)
  }

  // 搜索处理函数
  const handleMatchSearch = () => debounceResetPage('match')
  const handleEventSearch = () => debounceResetPage('event')
  const handlePlayerSearch = () => debounceResetPage('player')
  const handleTeamSearch = () => debounceResetPage('team')

  // =========================
  // 过滤逻辑
  // =========================

  /**
   * 过滤比赛数据
   */
  const filteredMatches = computed(() => {
    // 后端已处理类型和状态过滤，前端仅处理搜索
    let filtered = propsRef.matches.filter(match => match != null)

    // 关键词搜索过滤
    if (matchSearchKeyword.value.trim()) {
      const keyword = matchSearchKeyword.value.trim().toLowerCase()
      
      filtered = filtered.filter(match =>
        (match.matchName && match.matchName.toLowerCase().includes(keyword)) ||
        (match.name && match.name.toLowerCase().includes(keyword)) ||
        (match.team1 && match.team1.toLowerCase().includes(keyword)) ||
        (match.team2 && match.team2.toLowerCase().includes(keyword)) ||
        (match.homeTeam && match.homeTeam.toLowerCase().includes(keyword)) ||
        (match.awayTeam && match.awayTeam.toLowerCase().includes(keyword))
      )
    }
    
    return filtered
  })

  /**
   * 过滤事件数据
   */
  const filteredEvents = computed(() => {
    const manageMatchType = getMatchType()
    
    // 根据比赛类型过滤
    let filtered = manageMatchType
      ? propsRef.events.filter(event => 
          event && (
            event.matchType === manageMatchType || 
            event.type === manageMatchType ||
            event.competitionId == manageMatchType
          )
        )
      : propsRef.events.filter(event => event != null)

    // 关键词搜索过滤
    if (eventSearchKeyword.value.trim()) {
      const keyword = eventSearchKeyword.value.trim().toLowerCase()
      
      filtered = filtered.filter(event =>
        (event.matchName && event.matchName.toLowerCase().includes(keyword)) ||
        (event.match && event.match.toLowerCase().includes(keyword)) ||
        (event.playerName && event.playerName.toLowerCase().includes(keyword)) ||
        (event.player && event.player.toLowerCase().includes(keyword))
      )
    }

    // 事件类型过滤
    if (eventTypeFilter.value) {
      filtered = filtered.filter(event =>
        event.eventType === eventTypeFilter.value || event.type === eventTypeFilter.value
      )
    }
    
    return filtered
  })

  /**
   * 过滤球员数据
   */
  const filteredPlayers = computed(() => {
    const manageMatchType = getMatchType()
    
    // 根据比赛类型过滤
    let filtered = manageMatchType
      ? propsRef.players.filter(player => 
          player && (
            player.matchType === manageMatchType || 
            player.type === manageMatchType ||
            player.competitionId == manageMatchType
          )
        )
      : propsRef.players.filter(player => player != null)

    // 关键词搜索过滤
    if (playerSearchKeyword.value.trim()) {
      const keyword = playerSearchKeyword.value.trim().toLowerCase()
      filtered = filtered.filter(player =>
        (player.name && player.name.toLowerCase().includes(keyword)) ||
        (player.studentId && player.studentId.toString().toLowerCase().includes(keyword)) ||
        (player.id && player.id.toString().toLowerCase().includes(keyword))
      )
    }

    // 团队过滤
    if (playerTeamFilter.value) {
      filtered = filtered.filter(player =>
        player.teamName === playerTeamFilter.value || player.team === playerTeamFilter.value
      )
    }
    
    return filtered
  })

  /**
   * 过滤球队数据
   */
  const filteredTeams = computed(() => {
    const manageMatchType = getMatchType()
    
    // 根据比赛类型过滤
    let filtered = manageMatchType
      ? propsRef.teams.filter(team => 
          team && (
            team.matchType === manageMatchType || 
            team.type === manageMatchType ||
            team.competitionId == manageMatchType
          )
        )
      : propsRef.teams.filter(team => team != null)

    // 关键词搜索过滤
    if (teamSearchKeyword.value.trim()) {
      const keyword = teamSearchKeyword.value.trim().toLowerCase()
      
      filtered = filtered.filter(team =>
        (team.teamName && team.teamName.toLowerCase().includes(keyword)) ||
        (team.name && team.name.toLowerCase().includes(keyword))
      )
    }

    // 球员数量过滤
    if (teamPlayerCountFilter.value) {
      filtered = filtered.filter(team => {
        const count = (team.players && team.players.length) || 0
        
        switch (teamPlayerCountFilter.value) {
          case '1-5':
            return count >= 1 && count <= 5
          case '6-10':
            return count >= 6 && count <= 10
          case '11+':
            return count >= 11
          default:
            return true
        }
      })
    }
    
    return filtered
  })

  // =========================
  // 分页逻辑
  // =========================

  /**
   * 分页比赛数据
   */
  const paginatedMatches = computed(() => {
    const start = (matchCurrentPage.value - 1) * matchPageSize.value
    return filteredMatches.value.slice(start, start + matchPageSize.value)
  })

  /**
   * 分页事件数据
   */
  const paginatedEvents = computed(() => {
    const start = (eventCurrentPage.value - 1) * eventPageSize.value
    return filteredEvents.value.slice(start, start + eventPageSize.value)
  })

  /**
   * 分页球员数据
   */
  const paginatedPlayers = computed(() => {
    const start = (playerCurrentPage.value - 1) * playerPageSize.value
    return filteredPlayers.value.slice(start, start + playerPageSize.value)
  })

  /**
   * 分页球队数据
   */
  const paginatedTeams = computed(() => {
    const start = (teamCurrentPage.value - 1) * teamPageSize.value
    return filteredTeams.value.slice(start, start + teamPageSize.value)
  })

  // =========================
  // 监听器
  // =========================

  // 监听过滤器变化统一重置分页
  watch(
    [matchStatusFilter, eventTypeFilter, playerTeamFilter, teamPlayerCountFilter],
    () => {
      matchCurrentPage.value = 1
      eventCurrentPage.value = 1
      playerCurrentPage.value = 1
      teamCurrentPage.value = 1
    }
  )

  // =========================
  // 返回值
  // =========================

  return {
    // 搜索关键词
    matchSearchKeyword,
    eventSearchKeyword,
    playerSearchKeyword,
    teamSearchKeyword,
    
    // 过滤器
    matchStatusFilter,
    eventTypeFilter,
    playerTeamFilter,
    teamPlayerCountFilter,
    
    // 分页状态
    matchCurrentPage,
    matchPageSize,
    eventCurrentPage,
    eventPageSize,
    playerCurrentPage,
    playerPageSize,
    teamCurrentPage,
    teamPageSize,
    
    // 过滤后的集合
    filteredMatches,
    filteredEvents,
    filteredPlayers,
    filteredTeams,
    
    // 分页后的集合
    paginatedMatches,
    paginatedEvents,
    paginatedPlayers,
    paginatedTeams,
    
    // 处理函数
    handleMatchSearch,
    handleEventSearch,
    handlePlayerSearch,
    handleTeamSearch
  }
}