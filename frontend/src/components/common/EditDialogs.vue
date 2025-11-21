<template>
  <div>
    <!-- 球队编辑对话框 -->
    <el-dialog :model-value="editTeamDialog" @update:model-value="$emit('close-team-dialog')" title="编辑球队信息" width="600px">
      <el-form :model="localTeamForm" label-width="100px">
        <el-form-item label="球队名称" required>
          <el-input v-model="localTeamForm.teamName" placeholder="请输入球队名称"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select 
            v-model="localTeamForm.matchType" 
            placeholder="请选择比赛类型" 
            style="width: 100%;"
            @focus="loadCompetitionTypes"
            :loading="competitionsLoading"
          >
            <el-option 
              v-for="type in availableCompetitionTypes" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球员信息">
          <div class="team-players-container">
            <div v-if="!localTeamForm.players || localTeamForm.players.length === 0" class="no-players-text">
              暂无球员
            </div>
            <div v-for="(player, index) in localTeamForm.players" :key="index" class="player-card-item">
              <div class="player-card-content">
                <div class="player-info-row">
                  <span class="player-name">{{ player.name }}</span>
                  <el-tag size="small" type="info">#{{ player.number }}</el-tag>
                </div>
                <div class="player-id-row">
                  <span class="player-id">学号: {{ player.studentId }}</span>
                </div>
              </div>
              <div class="player-card-actions">
                <el-button type="danger" link @click="removePlayerFromTeam(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          <div class="add-player-section" style="margin-top: 10px; border-top: 1px dashed #eee; padding-top: 10px;">
             <div v-if="!isAddingPlayer">
                <el-button type="primary" size="small" @click="startAddingPlayer" style="width: 100%;">+ 添加球员</el-button>
             </div>
             <div v-else class="add-player-controls" style="display: flex; gap: 10px;">
                <el-select 
                  v-model="selectedPlayerToAdd" 
                  placeholder="搜索/选择球员" 
                  filterable 
                  remote
                  :remote-method="searchAvailablePlayers"
                  :loading="playersLoading"
                  style="flex: 1;"
                  @focus="loadAvailablePlayers"
                >
                  <el-option
                    v-for="player in availablePlayersToAdd"
                    :key="player.id"
                    :label="`${player.name} (${player.studentId})`"
                    :value="player.id"
                  />
                </el-select>
                <el-button type="primary" size="small" @click="addPlayerToTeam" :disabled="!selectedPlayerToAdd">确定</el-button>
                <el-button size="small" @click="cancelAddingPlayer">取消</el-button>
             </div>
             <div v-if="isAddingPlayer && availablePlayersToAdd.length === 0 && !playersLoading" class="no-players-tip" style="font-size: 12px; color: #999; margin-top: 5px;">
                没有可添加的球员（所有球员均已归属队伍）
             </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('close-team-dialog')">取消</el-button>
        <el-button type="primary" @click="emitUpdateTeam">确定</el-button>
      </template>
    </el-dialog>

    <!-- 比赛编辑对话框 -->
    <el-dialog :model-value="editMatchDialog" @update:model-value="$emit('close-match-dialog')" title="编辑比赛信息" width="600px">
      <el-form :model="localMatchForm" label-width="100px">
        <el-form-item label="比赛名称" required>
          <el-input v-model="localMatchForm.matchName" placeholder="请输入比赛名称"></el-input>
        </el-form-item>
        <el-form-item label="球队1" required>
          <el-select 
            v-model="localMatchForm.team1" 
            placeholder="请选择球队1" 
            style="width: 100%;"
            @focus="loadTeamsForMatch"
            filterable
            loading-text="加载中..."
            :loading="matchTeamsLoading"
          >
            <el-option 
              v-for="team in availableMatchTeams" 
              :key="team.id" 
              :label="`${team.teamName} (${getMatchTypeLabel(team.matchType)})`"
              :value="team.teamName"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球队2" required>
          <el-select 
            v-model="localMatchForm.team2" 
            placeholder="请选择球队2" 
            style="width: 100%;"
            @focus="loadTeamsForMatch"
            filterable
            loading-text="加载中..."
            :loading="matchTeamsLoading"
          >
            <el-option 
              v-for="team in availableMatchTeams.filter(t => t.teamName !== localMatchForm.team1)" 
              :key="team.id" 
              :label="`${team.teamName} (${getMatchTypeLabel(team.matchType)})`"
              :value="team.teamName"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="比赛时间" required>
          <el-date-picker 
            v-model="localMatchForm.date" 
            type="datetime" 
            placeholder="选择比赛时间"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="比赛地点" required>
          <el-input v-model="localMatchForm.location" placeholder="请输入比赛地点"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select 
            v-model="localMatchForm.matchType" 
            placeholder="请选择比赛类型" 
            style="width: 100%;"
            @focus="loadCompetitionTypes"
            :loading="competitionsLoading"
          >
            <el-option 
              v-for="type in availableCompetitionTypes" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('close-match-dialog')">取消</el-button>
        <el-button type="primary" @click="emitUpdateMatch">确定</el-button>
      </template>
    </el-dialog>

    <!-- 事件编辑对话框 -->
    <el-dialog :model-value="editEventDialog" @update:model-value="$emit('close-event-dialog')" title="编辑事件信息" width="500px">
      <el-form :model="localEventForm" label-width="100px">
        <el-form-item label="比赛名称" required>
          <el-select 
            v-model="localEventForm.matchName" 
            placeholder="请选择比赛" 
            style="width: 100%;"
            @focus="loadMatches"
            filterable
            loading-text="加载中..."
            :loading="matchesLoading"
            disabled
          >
            <el-option 
              v-for="match in availableMatches" 
              :key="match.id" 
              :label="`${match.matchName} (${match.team1} vs ${match.team2})`"
              :value="match.matchName"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型" required>
          <el-select v-model="localEventForm.eventType" placeholder="请选择事件类型" style="width: 100%;">
            <el-option label="进球" value="进球"></el-option>
            <el-option label="黄牌" value="黄牌"></el-option>
            <el-option label="红牌" value="红牌"></el-option>
            <el-option label="乌龙球" value="乌龙球"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球员姓名" required>
          <el-select 
            v-model="localEventForm.playerName" 
            placeholder="请选择球员" 
            style="width: 100%;"
            @focus="loadPlayers"
            filterable
            loading-text="加载中..."
            :loading="playersLoading"
          >
            <el-option 
              v-for="player in availablePlayers" 
              :key="player.id || player.studentId" 
              :label="`${player.name} (${player.teamName || '无队伍'})`"
              :value="player.name"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件时间" required>
          <el-input v-model="localEventForm.eventTime" placeholder="请输入事件时间（分钟）" type="number"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select 
            v-model="localEventForm.matchType" 
            placeholder="请选择比赛类型" 
            style="width: 100%;"
            @focus="loadCompetitionTypes"
            :loading="competitionsLoading"
            :disabled="!availableCompetitionTypes.length"
          >
            <el-option 
              v-for="type in availableCompetitionTypes" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('close-event-dialog')">取消</el-button>
        <el-button type="primary" @click="emitUpdateEvent">确定</el-button>
      </template>
    </el-dialog>

    <!-- 球员编辑对话框 -->
    <el-dialog :model-value="editPlayerDialog" @update:model-value="$emit('close-player-dialog')" title="编辑球员信息" width="500px">
      <el-form :model="localPlayerForm" label-width="100px">
        <el-form-item label="球员姓名" required>
          <el-input v-model="localPlayerForm.name" placeholder="请输入球员姓名"></el-input>
        </el-form-item>
        <el-form-item label="学号" required>
          <el-input v-model="localPlayerForm.studentId" placeholder="请输入学号" disabled></el-input>
        </el-form-item>
        <el-form-item label="球衣号码">
          <el-input v-model="localPlayerForm.number" placeholder="请输入球衣号码" type="number"></el-input>
        </el-form-item>
        <el-form-item label="所属球队">
          <el-select 
            v-model="localPlayerForm.teamName" 
            placeholder="请选择球队" 
            style="width: 100%;"
            @focus="loadTeams"
            filterable
            loading-text="加载中..."
            :loading="teamsLoading"
          >
            <el-option 
              v-for="team in availableTeams" 
              :key="team.id" 
              :label="`${team.teamName} (${getMatchTypeLabel(team.matchType)})`"
              :value="team.teamName"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="比赛类型">
          <el-select 
            v-model="localPlayerForm.matchType" 
            placeholder="请选择比赛类型" 
            style="width: 100%;"
            @focus="loadCompetitionTypes"
            :loading="competitionsLoading"
          >
            <el-option 
              v-for="type in availableCompetitionTypes" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('close-player-dialog')">取消</el-button>
        <el-button type="primary" @click="emitUpdatePlayer">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, reactive, computed } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import http from '@/utils/httpClient'
import logger from '@/utils/logger'
import useCompetitions from '@/composables/admin/useCompetitions'

// 运行时 props 定义（无需 withDefaults，已提供 default）
const props = defineProps({
  editTeamDialog: { type: Boolean, default: false },
  editMatchDialog: { type: Boolean, default: false },
  editEventDialog: { type: Boolean, default: false },
  editPlayerDialog: { type: Boolean, default: false },
  editTeamForm: { type: Object, default: () => ({}) },
  editMatchForm: { type: Object, default: () => ({}) },
  editEventForm: { type: Object, default: () => ({}) },
  editPlayerForm: { type: Object, default: () => ({}) },
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  players: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'close-team-dialog', 'close-match-dialog', 'close-event-dialog', 'close-player-dialog',
  'update-team','update-match','update-event','update-player','add-edit-player','remove-edit-player'
])

const { competitionOptions, fetchCompetitions, getCompetitionLabel } = useCompetitions()

// 响应式数据
const availableTeams = ref([])
const teamsLoading = ref(false)
const availableMatches = ref([])
const matchesLoading = ref(false)
const availablePlayers = ref([])
const playersLoading = ref(false)
const availableMatchTeams = ref([])
const matchTeamsLoading = ref(false)
const availableCompetitionTypes = computed(() => competitionOptions.value)
const competitionsLoading = ref(false)

// New state for team player management
const selectedPlayerToAdd = ref('')
const availablePlayersToAdd = ref([])
const isAddingPlayer = ref(false)

// 本地副本（避免直接修改父级传入的表单对象）
const clone = (obj, fallback) => {
  if (!obj || typeof obj !== 'object') return fallback
  try { return JSON.parse(JSON.stringify(obj)) } catch { return fallback }
}
const localTeamForm = reactive(clone(props.editTeamForm, { teamName:'', matchType:'' }))
const localMatchForm = reactive(clone(props.editMatchForm, { matchName:'', team1:'', team2:'', date:'', location:'', matchType:'' }))
const localEventForm = reactive(clone(props.editEventForm, { matchName:'', eventType:'', playerName:'', eventTime:'', matchType:'' }))
const localPlayerForm = reactive(clone(props.editPlayerForm, { id: '', name:'', studentId:'', number:'', teamName:'', matchType:'' }))

// 同步父 prop 更新（当父重新赋值时刷新本地）
watch(() => props.editTeamForm, v => Object.assign(localTeamForm, clone(v, {})), { deep: true })
watch(() => props.editMatchForm, v => Object.assign(localMatchForm, clone(v, {})), { deep: true })
watch(() => props.editEventForm, v => Object.assign(localEventForm, clone(v, {})), { deep: true })
watch(() => props.editPlayerForm, v => Object.assign(localPlayerForm, clone(v, {})), { deep: true })

// 提交时 emit 更新后的副本
const emitUpdateTeam = () => emit('update-team', clone(localTeamForm, {}))
const emitUpdateMatch = () => emit('update-match', clone(localMatchForm, {}))
const emitUpdateEvent = () => emit('update-event', clone(localEventForm, {}))
const emitUpdatePlayer = () => emit('update-player', clone(localPlayerForm, {}))

// 方法
const getMatchTypeLabel = (type) => {
  return getCompetitionLabel(type)
}

// 加载赛事类型（从数据库中获取唯一的比赛类型）
const loadCompetitionTypes = async () => {
  competitionsLoading.value = true
  try {
    await fetchCompetitions()
  } finally {
    competitionsLoading.value = false
  }
}

// Load players who don't have a team
const loadAvailablePlayers = async () => {
  playersLoading.value = true
  try {
    // Force reload to get latest status
    const res = await http.get('/players', { 
      params: { _t: Date.now() } 
    })
    if (res.ok) {
      const allPlayers = res.data.data || res.data || []
      // Filter players who don't have a teamName or team property
      availablePlayersToAdd.value = allPlayers.filter(p => !p.teamName && !p.team)
    }
  } catch (e) {
    logger.error('Failed to load available players', e)
  } finally {
    playersLoading.value = false
  }
}

const searchAvailablePlayers = async (query) => {
  if (!query) {
    await loadAvailablePlayers()
    return
  }
  playersLoading.value = true
  try {
    // Client-side filtering for now as backend might not support complex filtering
    const res = await http.get('/players')
    if (res.ok) {
      const allPlayers = res.data.data || res.data || []
      availablePlayersToAdd.value = allPlayers.filter(p => 
        (!p.teamName && !p.team) && 
        (p.name.includes(query) || p.studentId.includes(query))
      )
    }
  } finally {
    playersLoading.value = false
  }
}

const startAddingPlayer = () => {
    isAddingPlayer.value = true
    loadAvailablePlayers()
}

const cancelAddingPlayer = () => {
    isAddingPlayer.value = false
    selectedPlayerToAdd.value = ''
}

const addPlayerToTeam = () => {
  if (!selectedPlayerToAdd.value) return
  
  const player = availablePlayersToAdd.value.find(p => p.id === selectedPlayerToAdd.value)
  if (player) {
    if (!localTeamForm.players) localTeamForm.players = []
    // Add to local form
    localTeamForm.players.push({
      id: player.id,
      name: player.name,
      number: player.number || '', // Allow editing number later? Or just add as is.
      studentId: player.studentId
    })
    // Remove from available list
    availablePlayersToAdd.value = availablePlayersToAdd.value.filter(p => p.id !== player.id)
    selectedPlayerToAdd.value = ''
    isAddingPlayer.value = false
  }
}

const removePlayerFromTeam = (index) => {
  if (localTeamForm.players && localTeamForm.players[index]) {
    const player = localTeamForm.players[index]
    // Add back to available list if we have it loaded (optional, but good UX)
    if (player.id) {
      availablePlayersToAdd.value.push({
        id: player.id,
        name: player.name,
        studentId: player.studentId,
        number: player.number
      })
    }
    localTeamForm.players.splice(index, 1)
  }
}

// 通用的球队加载函数
// 通用数据加载函数
const loadGenericData = async (endpoint, targetRef, loadingRef, logPrefix, propsFallback = null, options = {}) => {
  if (targetRef.value.length > 0 && !options.forceReload) return
  
  loadingRef.value = true
  try {
    const requestOptions = {
      retry: {
        times: 2,
        delay: (attempt) => attempt * 1000,
        onRetry: (error, attempt) => {
          logger.warn(`${logPrefix}数据获取失败，第${attempt}次重试:`, error.message)
        }
      },
      ...options.requestOptions
    }
    
    const result = await http.get(endpoint, requestOptions)
    
    if (!result.ok) {
      logger.error(`获取${logPrefix}列表失败:`, result.error)
      if (propsFallback && Array.isArray(propsFallback)) {
        targetRef.value = propsFallback
      }
      return
    }
    
    const response = result.data
    let dataArray = [];
    if (Array.isArray(response)) {
      dataArray = response;
    } else if (response && typeof response === 'object') {
      const possibleKeys = ['data', 'records', logPrefix.toLowerCase(), `${logPrefix.toLowerCase()}s`]
      for (const key of possibleKeys) {
        if (Array.isArray(response[key])) {
          dataArray = response[key];
          break;
        }
      }
    }
    targetRef.value = dataArray;
  } catch (error) {
    logger.error(`查询${logPrefix}失败:`, error)
    if (propsFallback && Array.isArray(propsFallback)) {
      targetRef.value = propsFallback
    }
  } finally {
    loadingRef.value = false
  }
}

const loadTeams = async () => {
  return loadGenericData('/teams', availableTeams, teamsLoading, '球队', props.teams)
}

const loadMatches = async () => {
  return loadGenericData('/matches', availableMatches, matchesLoading, '比赛', props.matches)
}

const loadPlayers = async () => {
  // 强制重新加载，确保获取最新球员数据
  return loadGenericData('/players', availablePlayers, playersLoading, '球员', props.players, {
    forceReload: true,
    requestOptions: {
      headers: { 'Cache-Control': 'no-cache' },
      params: { _t: Date.now() } // 添加时间戳避免缓存
    }
  })
}

const loadTeamsForMatch = async () => {
  return loadGenericData('/teams', availableMatchTeams, matchTeamsLoading, '比赛球队', props.teams)
}

// 监听球员编辑对话框打开
watch(() => props.editPlayerDialog, (newValue) => {
  if (newValue) {
    loadTeams()
    loadCompetitionTypes()
  }
})

watch(() => props.editEventDialog, (newValue) => {
  if (newValue) {
    loadMatches()
    loadPlayers()
    loadCompetitionTypes()
  }
})

watch(() => props.editMatchDialog, (newValue) => {
  if (newValue) {
    loadTeamsForMatch()
    loadCompetitionTypes()
  }
})
</script>

<style scoped>
/* 局部样式已抽离到 admin-management.css，如需个性化覆写可在此扩展 */
.team-players-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #fff;
}

.player-card-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #ecf5ff; /* 浅蓝色背景 */
  border-radius: 6px;
  border: 1px solid #d9ecff;
  transition: all 0.3s ease;
  position: relative;
}

.player-card-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
  z-index: 1;
}

.player-card-content {
  flex: 1;
  overflow: hidden;
}

.player-info-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.player-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80px;
}

.player-id-row {
  font-size: 12px;
  color: #606266;
}

.player-card-actions {
  margin-left: 8px;
}

.no-players-text {
  grid-column: span 3;
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>