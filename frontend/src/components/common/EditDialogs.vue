<template>
  <div>
    <!-- 球队编辑对话框 -->
    <el-dialog :model-value="editTeamDialog" @update:model-value="$emit('close-team-dialog')" title="编辑球队信息" width="600px">
      <el-form :model="localTeamForm" label-width="100px">
        <el-form-item label="球队名称" required>
          <el-input v-model="localTeamForm.team_name" placeholder="请输入球队名称"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select 
            v-model="localTeamForm.match_type" 
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
                  <el-tag size="small" type="info">#{{ player.player_number || player.number }}</el-tag>
                </div>
                <div class="player-id-row">
                  <span class="player-id">学号: {{ player.student_id }}</span>
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
                    :label="`${player.name} (${player.student_id})`"
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
          <el-input v-model="localMatchForm.match_name" placeholder="请输入比赛名称"></el-input>
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
              :label="`${team.team_name} (${getMatchTypeLabel(team.match_type)})`"
              :value="team.team_name"
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
              v-for="team in availableMatchTeams.filter(t => t.team_name !== localMatchForm.team1)" 
              :key="team.id"
              :label="`${team.team_name} (${getMatchTypeLabel(team.match_type)})`"
              :value="team.team_name"
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
            v-model="localMatchForm.match_type" 
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
            v-model="localEventForm.match_name" 
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
              :label="`${match.match_name} (${match.team1} vs ${match.team2})`"
              :value="match.match_name"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型" required>
          <el-select v-model="localEventForm.event_type" placeholder="请选择事件类型" style="width: 100%;">
            <el-option label="进球" value="进球"></el-option>
            <el-option label="黄牌" value="黄牌"></el-option>
            <el-option label="红牌" value="红牌"></el-option>
            <el-option label="乌龙球" value="乌龙球"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球员姓名" required>
          <el-select 
            v-model="localEventForm.player_name" 
            placeholder="请选择球员" 
            style="width: 100%;"
            @focus="loadPlayers"
            filterable
            loading-text="加载中..."
            :loading="playersLoading"
          >
            <el-option 
              v-for="player in availablePlayers" 
              :key="player.id" 
              :label="`${player.name} (${player.team_name || '无队伍'})`"
              :value="player.name"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件时间" required>
          <el-input v-model="localEventForm.event_time" placeholder="请输入事件时间（分钟）" type="number"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select 
            v-model="localEventForm.match_type" 
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
          <el-input v-model="localPlayerForm.student_id" placeholder="请输入学号" disabled></el-input>
        </el-form-item>
        <el-form-item label="球衣号码">
          <el-input v-model="localPlayerForm.number" placeholder="请输入球衣号码" type="number"></el-input>
        </el-form-item>
        <el-form-item label="所属球队">
          <el-select 
            v-model="localPlayerForm.team_name" 
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
              :label="`${team.team_name} (${getMatchTypeLabel(team.match_type)})`"
              :value="team.team_name"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="比赛类型">
          <el-select 
            v-model="localPlayerForm.match_type" 
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
import { reactive, watch, ref } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import http from '@/utils/httpClient'
import logger from '@/utils/logger'
import useManagementLabels from '@/composables/admin/useManagementLabels'

const props = defineProps({
  editTeamDialog: Boolean,
  editMatchDialog: Boolean,
  editEventDialog: Boolean,
  editPlayerDialog: Boolean,
  editTeamForm: Object,
  editMatchForm: Object,
  editEventForm: Object,
  editPlayerForm: Object,
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  players: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'close-team-dialog', 'close-match-dialog', 'close-event-dialog', 'close-player-dialog',
  'update-team', 'update-match', 'update-event', 'update-player', 
  'add-edit-player', 'remove-edit-player'
])

const { getMatchTypeLabel } = useManagementLabels()

// 本地表单状态，统一使用下划线命名
const localTeamForm = reactive({
  id: '',
  team_name: '',
  match_type: '',
  players: []
})

const localMatchForm = reactive({
  id: '',
  match_name: '',
  team1: '',
  team2: '',
  date: '',
  location: '',
  match_type: ''
})

const localEventForm = reactive({
  id: '',
  match_name: '',
  event_type: '',
  player_name: '',
  event_time: '',
  match_type: ''
})

const localPlayerForm = reactive({
  id: '', 
  name: '',
  student_id: '',
  number: '',
  team_name: '',
  match_type: ''
})

// 监听父组件传来的表单数据变化，进行深拷贝
watch(() => props.editTeamForm, (newVal) => { 
  if(newVal) Object.assign(localTeamForm, newVal) 
}, { deep: true })

watch(() => props.editMatchForm, (newVal) => { 
  if(newVal) Object.assign(localMatchForm, newVal) 
}, { deep: true })

watch(() => props.editEventForm, (newVal) => { 
  if(newVal) Object.assign(localEventForm, newVal) 
}, { deep: true })

watch(() => props.editPlayerForm, (newVal) => { 
  if(newVal) Object.assign(localPlayerForm, newVal) 
}, { deep: true })


// 提交处理函数
const emitUpdateTeam = () => { emit('update-team', { ...localTeamForm }) }
const emitUpdateMatch = () => { emit('update-match', { ...localMatchForm }) }
const emitUpdateEvent = () => { emit('update-event', { ...localEventForm }) }
const emitUpdatePlayer = () => { emit('update-player', { ...localPlayerForm }) }

// 辅助状态和数据加载
const availableCompetitionTypes = ref([])
const competitionsLoading = ref(false)

const loadCompetitionTypes = async () => {
  if (availableCompetitionTypes.value.length > 0) return
  competitionsLoading.value = true
  try {
    const res = await http.get('/competitions')
    if (res.ok) {
      availableCompetitionTypes.value = (res.data.data || res.data).map(c => ({
        value: c.name,
        label: c.name
      }))
    }
  } catch (e) {
    logger.error('获取赛事类型失败', e)
  } finally {
    competitionsLoading.value = false
  }
}

// 动态数据源
const availableTeams = ref([])
const teamsLoading = ref(false)
const availableMatchTeams = ref([])
const matchTeamsLoading = ref(false)
const availableMatches = ref([])
const matchesLoading = ref(false)
const availablePlayers = ref([])
const playersLoading = ref(false)

// 添加球员相关逻辑
const isAddingPlayer = ref(false)
const selectedPlayerToAdd = ref('')
const availablePlayersToAdd = ref([])

const searchAvailablePlayers = async (query) => {
  if (query === '') {
    availablePlayersToAdd.value = []
    return
  }
  playersLoading.value = true
  try {
    const res = await http.get('/players')
    if (res.ok) {
      const allPlayers = res.data.data || res.data || []
      availablePlayersToAdd.value = allPlayers.filter(p => 
        (!p.team_name) && 
        (p.name.includes(query) || p.student_id.includes(query))
      )
    }
  } finally {
    playersLoading.value = false
  }
}

const loadAvailablePlayers = async () => {
  // 加载所有无队伍球员
  searchAvailablePlayers('') 
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
    localTeamForm.players.push({
      id: player.id,
      name: player.name,
      number: player.number || '',
      student_id: player.student_id
    })
    availablePlayersToAdd.value = availablePlayersToAdd.value.filter(p => p.id !== player.id)
    selectedPlayerToAdd.value = ''
    isAddingPlayer.value = false
  }
}

const removePlayerFromTeam = (index) => {
  if (localTeamForm.players && localTeamForm.players[index]) {
    localTeamForm.players.splice(index, 1)
  }
}

// 通用数据加载函数
const loadGenericData = async (endpoint, targetRef, loadingRef, logPrefix, propsFallback = null, options = {}) => {
  if (targetRef.value.length > 0 && !options.forceReload) return
  
  loadingRef.value = true
  try {
    const requestOptions = { ...options.requestOptions }
    const result = await http.get(endpoint, requestOptions)
    
    if (!result.ok) {
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
      // 尝试常见的后端返回字段
      const possibleKeys = ['data', 'records']
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
  // 仅在对话框打开时加载
  return loadGenericData('/teams', availableTeams, teamsLoading, '球队', props.teams)
}

const loadMatches = async () => {
  return loadGenericData('/matches', availableMatches, matchesLoading, '比赛', props.matches)
}

const loadPlayers = async () => {
  return loadGenericData('/players', availablePlayers, playersLoading, '球员', props.players, {
    forceReload: true,
    requestOptions: {
      headers: { 'Cache-Control': 'no-cache' },
      params: { _t: Date.now() }
    }
  })
}

const loadTeamsForMatch = async () => {
  return loadGenericData('/teams', availableMatchTeams, matchTeamsLoading, '比赛球队', props.teams)
}

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

</script>

<style scoped>
.team-players-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  min-height: 100px;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 5px;
}
.no-players-text {
  text-align: center;
  color: #909399;
  line-height: 100px;
}
.player-card-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  padding: 8px 0;
}
.player-card-item:last-child {
  border-bottom: none;
}
</style>
