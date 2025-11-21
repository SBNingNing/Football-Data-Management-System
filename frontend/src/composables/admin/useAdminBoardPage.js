/**
 * 管理员面板页面组合式函数
 * 提供管理球队、比赛、事件、球员的完整功能
 */
import { ref, reactive, computed, nextTick } from 'vue'
import { useAuthStore, useTeamStore, useMatchStore, useEventStore, usePlayerStore } from '@/store/modules'
import { ElMessage, ElMessageBox } from 'element-plus'
import logger from '@/utils/logger'

export function useAdminBoardPage() {
  // Store 实例
  const authStore = useAuthStore()
  const teamStore = useTeamStore()
  const matchStore = useMatchStore()
  const eventStore = useEventStore()
  const playerStore = usePlayerStore()

  // 页面状态
  const activeTab = ref('manage')
  const manageMatchType = ref('')
  const dataInputRef = ref(null)
  
  // 全局加载状态
  // 优化：仅在加载核心数据（球队、比赛）时显示全局遮罩，事件和球员数据后台加载
  const loading = computed(() => 
    teamStore.loading || 
    matchStore.loading
  )

  // 编辑对话框状态
  const editTeamDialog = ref(false)
  const editMatchDialog = ref(false)
  const editEventDialog = ref(false)
  const editPlayerDialog = ref(false)

  // 编辑表单数据
  const editTeamForm = reactive({
    id: '',
    teamName: '',
    matchType: '',
    players: []
  })

  const editMatchForm = reactive({
    id: '',
    matchName: '',
    team1: '',
    team2: '',
    date: '',
    location: '',
    matchType: ''
  })

  const editEventForm = reactive({
    id: '',
    matchName: '',
    eventType: '',
    playerName: '',
    eventTime: '',
    matchType: ''
  })

  const editPlayerForm = reactive({
    id: '',
    name: '',
    number: '',
    studentId: '',
    teamName: '',
    matchType: ''
  })

  // 数据列表计算属性
  const teams = computed(() => teamStore.list)
  const matches = computed(() => matchStore.list)
  const events = computed(() => eventStore.list)
  const players = computed(() => playerStore.list)
  
  /**
   * 加载所有管理数据
   * @param {Object} filters - 筛选条件
   */
  async function loadAllData(filters = {}) {
    // 优化：如果已经在加载中，则跳过（避免重复请求）
    if (loading.value) return

    teamStore.loading = true
    
    try {
      logger.info('[admin/board] start loading data (composable)', filters)
      
      // 构建比赛查询参数
      const matchParams = {}
      if (filters.status) matchParams.status = filters.status
      if (filters.type) matchParams.type = filters.type
      
      // 1. 优先加载核心数据（球队和比赛）
      const results = await Promise.allSettled([
        teamStore.loadAll(),
        matchStore.loadAll(matchParams)
      ])
      
      const names = ['球队', '比赛']
      results.forEach((result, index) => {
        if (result.status === 'rejected') {
          logger.error(`[admin/board] 加载${names[index]}数据失败`, result.reason)
          ElMessage.warning(`加载${names[index]}数据失败: ${result.reason?.message || '未知错误'}`)
        } else if (result.value && !result.value.success) {
          logger.error(`[admin/board] 加载${names[index]}数据失败`, result.value.error)
          ElMessage.warning(`加载${names[index]}数据失败: ${result.value.error}`)
        }
      })

      // 2. 后台加载次要数据（事件和球员）
      Promise.allSettled([
        eventStore.loadAll(),
        playerStore.loadAll()
      ]).then(() => {
        logger.info('[admin/board] background data loaded', {
          events: events.value.length,
          players: players.value.length
        })
      })
      
      logger.info('[admin/board] core data loaded', {
        counts: {
          teams: teams.value.length,
          matches: matches.value.length
        }
      })
    } catch (err) {
      logger.error('[admin/board] 加载数据失败', err)
      ElMessage.error('数据加载失败，请刷新页面重试')
    } finally {
      teamStore.loading = false
    }
  }

  /**
   * 处理筛选变更
   * @param {Object} filters - 新的筛选条件 { status, type, ... }
   */
  async function handleFilterChange(filters) {
    // 仅重新加载比赛数据，避免全量刷新导致性能问题
    try {
      const matchParams = {}
      if (filters.status) matchParams.status = filters.status
      if (filters.type) matchParams.type = filters.type
      
      await matchStore.loadAll(matchParams)
    } catch (err) {
      logger.error('[admin/board] 筛选比赛失败', err)
      ElMessage.error('筛选失败')
    }
  }

  /**
   * 滚动到输入模块
   */
  function scrollToInputModule(moduleType) {
    if (dataInputRef.value?.scrollToModule) {
      dataInputRef.value.scrollToModule(moduleType)
    }
  }

  /**
   * 处理输入类型点击
   */
  function handleInputTypeClick(inputType) {
    if (activeTab.value !== 'input') {
      activeTab.value = 'input'
      nextTick(() => scrollToInputModule(inputType))
    } else {
      scrollToInputModule(inputType)
    }
  }
  /**
   * 提交球队数据
   * 注意：TeamInput 组件内部已经完成了创建操作，这里只需要刷新列表
   */
  async function handleTeamSubmit(teamData) {
    try {
      // 仅刷新列表，不重复创建
      await teamStore.loadAll()
      // 成功提示已在组件内显示
    } catch (error) {
      logger.error('刷新球队列表失败', error)
    }
  }

  /**
   * 提交赛程数据
   * 注意：ScheduleInput 组件内部已经完成了创建操作，这里只需要刷新列表
   */
  async function handleScheduleSubmit(scheduleData) {
    try {
      // 仅刷新列表，不重复创建
      await matchStore.loadAll()
      // 成功提示已在组件内显示
    } catch (error) {
      logger.error('刷新赛程列表失败', error)
    }
  }

  /**
   * 提交事件数据
   * 注意：EventInput 组件内部已经完成了创建操作，这里只需要刷新列表
   */
  async function handleEventSubmit(eventData) {
    try {
      // 刷新事件列表
      await eventStore.loadAll()
      
      // 优化：仅刷新受影响的比赛，而不是全量刷新
      if (eventData && eventData.matchName) {
        // eventData.matchName 在 EventInput 中绑定的是 matchId
        await matchStore.refreshMatch(eventData.matchName)
      } else {
        // 降级方案：全量刷新
        const params = {}
        if (manageMatchType.value) {
          params.type = manageMatchType.value
        }
        await matchStore.loadAll(params)
      }
      
    } catch (error) {
      logger.error('刷新事件列表失败', error)
    }
  }
  // =========================
  // 球队管理相关函数
  // =========================

  /**
   * 编辑球队
   */
  function editTeam(team) {
    logger.info('[admin/board] 编辑球队', team?.id)
    
    Object.assign(editTeamForm, {
      id: team.id,
      teamName: team.teamName,
      matchType: team.matchType,
      players: team.players ? [...team.players] : []
    })
    
    editTeamDialog.value = true
  }

  /**
   * 添加编辑球员
   */
  function addEditPlayer() {
    editTeamForm.players.push({
      name: '',
      number: '',
      studentId: ''
    })
  }

  /**
   * 移除编辑球员
   */
  function removeEditPlayer(index) {
    editTeamForm.players.splice(index, 1)
  }

  /**
   * 更新球队
   */
  async function updateTeam(updatedData) {
    const dataToSubmit = updatedData || editTeamForm
    
    // 检查是否有变更
    const isChanged = 
      dataToSubmit.teamName !== editTeamForm.teamName ||
      dataToSubmit.matchType !== editTeamForm.matchType ||
      JSON.stringify(dataToSubmit.players) !== JSON.stringify(editTeamForm.players)

    if (!isChanged) {
      editTeamDialog.value = false
      return
    }

    const result = await teamStore.update(dataToSubmit.id, dataToSubmit)
    
    if (result.success) {
      ElMessage.success('球队信息更新成功')
      editTeamDialog.value = false
    } else {
      ElMessage.error(result.error || '球队信息更新失败')
    }
  }

  /**
   * 删除球队
   */
  function deleteTeam(teamId) {
    ElMessageBox.confirm(
      '此操作将永久删除该球队, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      const result = await teamStore.remove(teamId)
      
      if (result.success) {
        ElMessage.success('删除成功')
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    }).catch(() => {})
  }
  // =========================
  // 比赛管理相关函数
  // =========================

  /**
   * 编辑比赛
   */
  function editMatch(match) {
    Object.assign(editMatchForm, {
      id: match.id,
      matchName: match.matchName,
      team1: match.team1,
      team2: match.team2,
      date: match.date,
      location: match.location,
      matchType: match.matchType
    })
    
    editMatchDialog.value = true
  }

  /**
   * 更新比赛
   */
  async function updateMatch(updatedData) {
    const dataToSubmit = updatedData || editMatchForm
    const result = await matchStore.update(dataToSubmit.id, dataToSubmit)
    
    if (result.success) {
      ElMessage.success('比赛信息更新成功')
      editMatchDialog.value = false
    } else {
      ElMessage.error(result.error || '比赛信息更新失败')
    }
  }

  /**
   * 删除比赛
   */
  function deleteMatch(matchId) {
    ElMessageBox.confirm(
      '此操作将永久删除该比赛, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      const result = await matchStore.remove(matchId)
      
      if (result.success) {
        ElMessage.success('删除成功')
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    }).catch(() => {})
  }

  /**
   * 完成比赛
   */
  function completeMatch(matchId) {
    // 前端预检查：如果比赛时间未到，提示用户
    const match = matches.value.find(m => (m.id === matchId || m.matchId === matchId))
    if (match) {
      const matchTime = new Date(match.date || match.matchDate || match.matchTime)
      const now = new Date()
      if (matchTime > now) {
        ElMessage.warning('该比赛还未开始')
        return
      }
    }

    ElMessageBox.confirm(
      '确定要标记该比赛为已完赛吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        const result = await matchStore.complete(matchId)
        
        if (result.success) {
          ElMessage.success('比赛已标记为完赛')
          await matchStore.loadAll()
        } else {
          ElMessage.error(result.error || '操作失败')
        }
      } catch (error) {
        logger.error('完赛操作失败', error)
        ElMessage.error('操作失败，请重试')
      }
    }).catch(() => {})
  }
  // =========================
  // 事件管理相关函数
  // =========================

  /**
   * 编辑事件
   */
  function editEvent(event) {
    Object.assign(editEventForm, {
      id: event.id,
      matchName: event.matchName,
      eventType: event.eventType,
      playerName: event.playerName,
      eventTime: event.eventTime,
      matchType: event.matchType
    })
    
    editEventDialog.value = true
  }

  /**
   * 更新事件
   */
  async function updateEvent(updatedData) {
    const dataToSubmit = updatedData || editEventForm
    const result = await eventStore.update(dataToSubmit.id, dataToSubmit)
    
    if (result.success) {
      ElMessage.success('事件信息更新成功')
      editEventDialog.value = false
      
      // 优化：尝试刷新关联的比赛
      // 注意：updatedData 可能不包含 matchId，需要从 editEventForm 或原始数据中获取
      // 如果无法获取 matchId，则回退到全量刷新
      // 这里假设 dataToSubmit 中可能包含 matchId 或者我们可以从 store 中找到它
      // 但通常 updateEvent 接口返回的数据可能包含 matchId
      
      // 简单起见，如果能获取到 matchId 则单条刷新，否则全量
      // editEventForm 通常包含 matchName (可能是 ID 或 名称)，这里需要确认
      // 在 editEvent 函数中：matchName: event.matchName
      // 如果 event.matchName 是 ID，则可以直接用。如果是名称，则需要查找。
      // 鉴于 updateEvent 频率较低，全量刷新也可以接受，但为了统一体验，尝试优化
      
      // 暂时保持全量刷新，因为 updateEvent 场景下 matchId 获取可能不直接
      const params = {}
      if (manageMatchType.value) {
        params.type = manageMatchType.value
      }
      await matchStore.loadAll(params)
    } else {
      ElMessage.error(result.error || '事件信息更新失败')
    }
  }

  /**
   * 删除事件
   */
  function deleteEvent(eventId) {
    // 获取事件信息以便知道属于哪场比赛（优化刷新）
    const eventToDelete = events.value.find(e => e.id === eventId)
    
    ElMessageBox.confirm(
      '此操作将永久删除该事件, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      const result = await eventStore.remove(eventId)
      
      if (result.success) {
        ElMessage.success('删除成功')
        
        // 优化：如果知道 matchId，仅刷新该比赛
        if (eventToDelete && (eventToDelete.matchId || eventToDelete.match_id)) {
           await matchStore.refreshMatch(eventToDelete.matchId || eventToDelete.match_id)
        } else {
           // 降级：全量刷新
           const params = {}
           if (manageMatchType.value) {
             params.type = manageMatchType.value
           }
           await matchStore.loadAll(params)
        }
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    }).catch(() => {})
  }
  // =========================
  // 球员管理相关函数
  // =========================

  /**
   * 编辑球员
   */
  function editPlayer(player) {
    Object.assign(editPlayerForm, {
      id: player.id || player.studentId,
      name: player.name,
      number: player.number,
      studentId: player.studentId || player.id,
      teamName: player.teamName,
      matchType: player.matchType
    })
    
    editPlayerDialog.value = true
  }

  /**
   * 更新球员
   */
  async function updatePlayer(updatedData) {
    try {
      const dataToSubmit = updatedData || editPlayerForm
      const playerId = dataToSubmit.id || dataToSubmit.studentId
      const result = await playerStore.update(playerId, dataToSubmit)
      
      if (result.success) {
        ElMessage.success('球员信息更新成功')
        editPlayerDialog.value = false
        await playerStore.loadAll()
      } else {
        ElMessage.error(result.error || '球员信息更新失败')
      }
    } catch (error) {
      logger.error('更新球员失败', error)
      ElMessage.error('球员信息更新失败')
    }
  }

  /**
   * 删除球员
   */
  function deletePlayer(playerId) {
    ElMessageBox.confirm(
      '此操作将永久删除该球员, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        const result = await playerStore.remove(playerId)
        
        if (result.success) {
          ElMessage.success('删除成功')
        } else {
          ElMessage.error(result.error || '删除失败')
        }
      } catch (error) {
        logger.error('删除球员失败', error)
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
  }

  // =========================
  // 其他功能函数
  // =========================

  /**
   * 登出功能
   */
  function logout() {
    ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      authStore.logout()
      localStorage.removeItem('userToken')
      localStorage.removeItem('token') // 确保清除 httpClient 使用的 token
      localStorage.removeItem('userInfo')
      sessionStorage.clear()
      ElMessage.success('已退出登录')
      
      setTimeout(() => {
        window.location.href = '/login'
      }, 500)
    }).catch(() => {})
  }
  // =========================
  // 返回所有公开的状态和方法
  // =========================
  return {
    // 页面状态
    activeTab,
    manageMatchType,
    loading,
    dataInputRef,
    
    // 对话框状态
    editTeamDialog,
    editMatchDialog,
    editEventDialog,
    editPlayerDialog,
    
    // 表单数据
    editTeamForm,
    editMatchForm,
    editEventForm,
    editPlayerForm,
    
    // 数据列表
    teams,
    matches,
    events,
    players,
    
    // 基础功能
    loadAllData,
    handleFilterChange,
    handleInputTypeClick,
    
    // 数据提交
    handleTeamSubmit,
    handleScheduleSubmit,
    handleEventSubmit,
    
    // 球队管理
    editTeam,
    addEditPlayer,
    removeEditPlayer,
    updateTeam,
    deleteTeam,
    
    // 比赛管理
    editMatch,
    updateMatch,
    deleteMatch,
    completeMatch,
    
    // 事件管理
    editEvent,
    updateEvent,
    deleteEvent,
    
    // 球员管理
    editPlayer,
    updatePlayer,
    deletePlayer,
    
    // 其他功能
    logout
  }
}