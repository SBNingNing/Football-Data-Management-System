// 管理端过滤/搜索/分页逻辑抽离 (Matches / Events / Players / Teams)
import { ref, computed, watch } from 'vue'

/**
 * 分页尺寸默认值（按 UI 布局列数确定, 可在调用前覆写）
 * @type {{ match:number, event:number, player:number, team:number }}
 */
const DEFAULT_PAGE_SIZES = Object.freeze({ match: 9, event: 12, player: 9, team: 6 })

/**
 * @typedef {Object} ManagementFiltersReturn
 * @property {import('vue').Ref<string>} matchSearchKeyword
 * @property {import('vue').Ref<string>} eventSearchKeyword
 * @property {import('vue').Ref<string>} playerSearchKeyword
 * @property {import('vue').Ref<string>} teamSearchKeyword
 * @property {import('vue').Ref<string>} matchStatusFilter
 * @property {import('vue').Ref<string>} eventTypeFilter
 * @property {import('vue').Ref<string>} playerTeamFilter
 * @property {import('vue').Ref<string>} teamPlayerCountFilter
 * @property {import('vue').Ref<number>} matchCurrentPage
 * @property {import('vue').Ref<number>} matchPageSize
 * @property {import('vue').Ref<number>} eventCurrentPage
 * @property {import('vue').Ref<number>} eventPageSize
 * @property {import('vue').Ref<number>} playerCurrentPage
 * @property {import('vue').Ref<number>} playerPageSize
 * @property {import('vue').Ref<number>} teamCurrentPage
 * @property {import('vue').Ref<number>} teamPageSize
 * @property {import('vue').ComputedRef<Array>} filteredMatches
 * @property {import('vue').ComputedRef<Array>} filteredEvents
 * @property {import('vue').ComputedRef<Array>} filteredPlayers
 * @property {import('vue').ComputedRef<Array>} filteredTeams
 * @property {import('vue').ComputedRef<Array>} paginatedMatches
 * @property {import('vue').ComputedRef<Array>} paginatedEvents
 * @property {import('vue').ComputedRef<Array>} paginatedPlayers
 * @property {import('vue').ComputedRef<Array>} paginatedTeams
 * @property {() => void} handleMatchSearch
 * @property {() => void} handleEventSearch
 * @property {() => void} handlePlayerSearch
 * @property {() => void} handleTeamSearch
 */

/**
 * 管理端复合过滤/搜索/分页 组合函数。
 * - 防御式处理：过滤过程中允许数据项为 null/undefined。
 * - search debounce：300ms（单独字段触发，不共享跨类型）。
 *
 * @param {object} propsRef 直接传入组件中的 props（要求包含 matches/events/players/teams 数组）
 * @param {() => string} getMatchType 返回当前管理视图选中的 matchType（可为空字符串）
 * @returns {ManagementFiltersReturn}
 */
export default function useManagementFilters(propsRef, getMatchType) {
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

  // 分页
  const matchCurrentPage = ref(1)
  const matchPageSize = ref(DEFAULT_PAGE_SIZES.match)
  const eventCurrentPage = ref(1)
  const eventPageSize = ref(DEFAULT_PAGE_SIZES.event)
  const playerCurrentPage = ref(1)
  const playerPageSize = ref(DEFAULT_PAGE_SIZES.player)
  const teamCurrentPage = ref(1)
  const teamPageSize = ref(DEFAULT_PAGE_SIZES.team)

  let searchTimer = null
  const debounceResetPage = (type) => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      switch (type) {
        case 'match': matchCurrentPage.value = 1; break
        case 'event': eventCurrentPage.value = 1; break
        case 'player': playerCurrentPage.value = 1; break
        case 'team': teamCurrentPage.value = 1; break
      }
    }, 300)
  }

  const handleMatchSearch = () => debounceResetPage('match')
  const handleEventSearch = () => debounceResetPage('event')
  const handlePlayerSearch = () => debounceResetPage('player')
  const handleTeamSearch = () => debounceResetPage('team')

  // 基础过滤集合
  const filteredMatches = computed(() => {
    const manageMatchType = getMatchType()
    let filtered = manageMatchType ?
      propsRef.matches.filter(match => match && (match.matchType === manageMatchType || match.type === manageMatchType)) :
      propsRef.matches.filter(match => match != null)

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

    if (matchStatusFilter.value) {
      filtered = filtered.filter(match => match.status === matchStatusFilter.value)
    }
    return filtered
  })

  const filteredEvents = computed(() => {
    const manageMatchType = getMatchType()
    let filtered = manageMatchType ?
      propsRef.events.filter(event => event && (event.matchType === manageMatchType || event.type === manageMatchType)) :
      propsRef.events.filter(event => event != null)

    if (eventSearchKeyword.value.trim()) {
      const keyword = eventSearchKeyword.value.trim().toLowerCase()
      filtered = filtered.filter(event =>
        (event.matchName && event.matchName.toLowerCase().includes(keyword)) ||
        (event.match && event.match.toLowerCase().includes(keyword)) ||
        (event.playerName && event.playerName.toLowerCase().includes(keyword)) ||
        (event.player && event.player.toLowerCase().includes(keyword))
      )
    }

    if (eventTypeFilter.value) {
      filtered = filtered.filter(event =>
        event.eventType === eventTypeFilter.value || event.type === eventTypeFilter.value
      )
    }
    return filtered
  })

  const filteredPlayers = computed(() => {
    const manageMatchType = getMatchType()
    let filtered = manageMatchType ?
      propsRef.players.filter(player => player && (player.matchType === manageMatchType || player.type === manageMatchType)) :
      propsRef.players.filter(player => player != null)

    if (playerSearchKeyword.value.trim()) {
      const keyword = playerSearchKeyword.value.trim().toLowerCase()
      filtered = filtered.filter(player =>
        (player.name && player.name.toLowerCase().includes(keyword)) ||
        (player.studentId && player.studentId.toString().toLowerCase().includes(keyword)) ||
        (player.id && player.id.toString().toLowerCase().includes(keyword))
      )
    }

    if (playerTeamFilter.value) {
      filtered = filtered.filter(player =>
        player.teamName === playerTeamFilter.value || player.team === playerTeamFilter.value
      )
    }
    return filtered
  })

  const filteredTeams = computed(() => {
    const manageMatchType = getMatchType()
    let filtered = manageMatchType ?
      propsRef.teams.filter(team => team && (team.matchType === manageMatchType || team.type === manageMatchType)) :
      propsRef.teams.filter(team => team != null)

    if (teamSearchKeyword.value.trim()) {
      const keyword = teamSearchKeyword.value.trim().toLowerCase()
      filtered = filtered.filter(team =>
        (team.teamName && team.teamName.toLowerCase().includes(keyword)) ||
        (team.name && team.name.toLowerCase().includes(keyword))
      )
    }

    if (teamPlayerCountFilter.value) {
      filtered = filtered.filter(team => {
        const count = (team.players && team.players.length) || 0
        switch (teamPlayerCountFilter.value) {
          case '1-5': return count >= 1 && count <= 5
          case '6-10': return count >= 6 && count <= 10
          case '11+': return count >= 11
          default: return true
        }
      })
    }
    return filtered
  })

  // 分页派生
  const paginatedMatches = computed(() => {
    const start = (matchCurrentPage.value - 1) * matchPageSize.value
    return filteredMatches.value.slice(start, start + matchPageSize.value)
  })
  const paginatedEvents = computed(() => {
    const start = (eventCurrentPage.value - 1) * eventPageSize.value
    return filteredEvents.value.slice(start, start + eventPageSize.value)
  })
  const paginatedPlayers = computed(() => {
    const start = (playerCurrentPage.value - 1) * playerPageSize.value
    return filteredPlayers.value.slice(start, start + playerPageSize.value)
  })
  const paginatedTeams = computed(() => {
    const start = (teamCurrentPage.value - 1) * teamPageSize.value
    return filteredTeams.value.slice(start, start + teamPageSize.value)
  })

  // 监听过滤器变化统一重置分页
  watch([matchStatusFilter, eventTypeFilter, playerTeamFilter, teamPlayerCountFilter], () => {
    matchCurrentPage.value = 1
    eventCurrentPage.value = 1
    playerCurrentPage.value = 1
    teamCurrentPage.value = 1
  })

  return {
    // raw / filters
    matchSearchKeyword, eventSearchKeyword, playerSearchKeyword, teamSearchKeyword,
    matchStatusFilter, eventTypeFilter, playerTeamFilter, teamPlayerCountFilter,
    // pagination state
    matchCurrentPage, matchPageSize, eventCurrentPage, eventPageSize,
    playerCurrentPage, playerPageSize, teamCurrentPage, teamPageSize,
    // filtered collections
    filteredMatches, filteredEvents, filteredPlayers, filteredTeams,
    // paginated collections
    paginatedMatches, paginatedEvents, paginatedPlayers, paginatedTeams,
    // handlers
    handleMatchSearch, handleEventSearch, handlePlayerSearch, handleTeamSearch
  }
}
