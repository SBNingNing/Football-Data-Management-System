<template>
  <div>
    <!-- 球队编辑对话框 -->
    <el-dialog :model-value="editTeamDialog" @update:model-value="$emit('close-team-dialog')" title="编辑球队信息" width="600px">
      <el-form :model="localTeamForm" label-width="100px">
        <el-form-item label="球队名称" required>
          <el-input v-model="localTeamForm.teamName" placeholder="请输入球队名称"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型" required>
          <el-select v-model="localTeamForm.matchType" placeholder="请选择比赛类型" style="width: 100%;">
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球员信息">
          <div v-for="(player, index) in localTeamForm.players" :key="index" class="player-input-row">
            <el-input v-model="player.name" placeholder="球员姓名" class="player-field-name"></el-input>
            <el-input v-model="player.number" placeholder="球衣号码" class="player-field-number"></el-input>
            <el-input v-model="player.studentId" placeholder="学号" class="player-field-student"></el-input>
            <div class="player-field-actions">
              <el-button type="danger" size="small" @click="$emit('remove-edit-player', index)">删除</el-button>
            </div>
          </div>
          <el-button type="primary" size="small" @click="$emit('add-edit-player')">添加球员</el-button>
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
          <el-select v-model="localMatchForm.matchType" placeholder="请选择比赛类型" style="width: 100%;">
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
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
          <el-select v-model="localEventForm.matchType" placeholder="请选择比赛类型" style="width: 100%;" disabled>
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
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
          <el-select v-model="localPlayerForm.matchType" placeholder="请选择比赛类型" style="width: 100%;">
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
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
import { ref, watch, reactive } from 'vue'
import http from '@/utils/httpClient'
import logger from '@/utils/logger'

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


// 响应式数据
const availableTeams = ref([])
const teamsLoading = ref(false)
const availableMatches = ref([])
const matchesLoading = ref(false)
const availablePlayers = ref([])
const playersLoading = ref(false)
const availableMatchTeams = ref([])
const matchTeamsLoading = ref(false)

// 本地副本（避免直接修改父级传入的表单对象）
const clone = (obj, fallback) => {
  if (!obj || typeof obj !== 'object') return fallback
  try { return JSON.parse(JSON.stringify(obj)) } catch { return fallback }
}
const localTeamForm = reactive(clone(props.editTeamForm, { teamName:'', matchType:'', players:[] }))
const localMatchForm = reactive(clone(props.editMatchForm, { matchName:'', team1:'', team2:'', date:'', location:'', matchType:'' }))
const localEventForm = reactive(clone(props.editEventForm, { matchName:'', eventType:'', playerName:'', eventTime:'', matchType:'' }))
const localPlayerForm = reactive(clone(props.editPlayerForm, { name:'', studentId:'', number:'', teamName:'', matchType:'' }))

// 同步父 prop 更新（当父重新赋值时刷新本地）
watch(() => props.editTeamForm, v => Object.assign(localTeamForm, clone(v, {})))
watch(() => props.editMatchForm, v => Object.assign(localMatchForm, clone(v, {})))
watch(() => props.editEventForm, v => Object.assign(localEventForm, clone(v, {})))
watch(() => props.editPlayerForm, v => Object.assign(localPlayerForm, clone(v, {})))

// 提交时 emit 更新后的副本
const emitUpdateTeam = () => emit('update-team', clone(localTeamForm, {}))
const emitUpdateMatch = () => emit('update-match', clone(localMatchForm, {}))
const emitUpdateEvent = () => emit('update-event', clone(localEventForm, {}))
const emitUpdatePlayer = () => emit('update-player', clone(localPlayerForm, {}))

// 方法
const getMatchTypeLabel = (type) => {
  const labels = {
    'champions-cup': '冠军杯',
    'womens-cup': '巾帼杯',
    'eight-a-side': '八人制比赛'
  }
  return labels[type] || ''
}

const loadTeams = async () => {
  if (availableTeams.value.length > 0) return 
  
  teamsLoading.value = true
  try {
    const { ok, data } = await http.get('/teams')
  if (ok && (data?.success === true || data?.status === 'success')) {
      const list = Array.isArray(data.data)?data.data: Array.isArray(data.records)?data.records : data.data
      availableTeams.value = Array.isArray(list)?list:[]
    } else {
      logger.error('获取球队列表失败:', data?.message || '未知错误')
    }
  } catch (error) {
    logger.error('查询球队失败:', error)
    if (props.teams && Array.isArray(props.teams)) {
      availableTeams.value = props.teams
    }
  } finally {
    teamsLoading.value = false
  }
}

const loadMatches = async () => {
  if (availableMatches.value.length > 0) return 
  
  matchesLoading.value = true
  try {
    const { ok, data } = await http.get('/matches')
  if (ok && (data?.success === true || data?.status === 'success')) {
      const list = Array.isArray(data.data)?data.data: Array.isArray(data.records)?data.records : data.data
      availableMatches.value = Array.isArray(list)?list:[]
    } else {
      logger.error('获取比赛列表失败:', data?.message || '未知错误')
    }
  } catch (error) {
    logger.error('查询比赛失败:', error)
    if (props.matches && Array.isArray(props.matches)) {
      availableMatches.value = props.matches
    }
  } finally {
    matchesLoading.value = false
  }
}

const loadPlayers = async () => {
  if (availablePlayers.value.length > 0) return 
  
  playersLoading.value = true
  try {
    const { ok, data } = await http.get('/players')
  if (ok && (data?.success === true || data?.status === 'success')) {
      const list = Array.isArray(data.data)?data.data: Array.isArray(data.records)?data.records : data.data
      availablePlayers.value = Array.isArray(list)?list:[]
    } else {
      logger.error('获取球员列表失败:', data?.message || '未知错误')
    }
  } catch (error) {
    logger.error('查询球员失败:', error)
    if (props.players && Array.isArray(props.players)) {
      availablePlayers.value = props.players
    }
  } finally {
    playersLoading.value = false
  }
}

const loadTeamsForMatch = async () => {
  if (availableMatchTeams.value.length > 0) return 
  
  matchTeamsLoading.value = true
  try {
    const { ok, data } = await http.get('/teams')
  if (ok && (data?.success === true || data?.status === 'success')) {
      const list = Array.isArray(data.data)?data.data: Array.isArray(data.records)?data.records : data.data
      availableMatchTeams.value = Array.isArray(list)?list:[]
    } else {
      logger.error('获取球队列表失败:', data?.message || '未知错误')
    }
  } catch (error) {
    logger.error('查询球队失败:', error)
    if (props.teams && Array.isArray(props.teams)) {
      availableMatchTeams.value = props.teams
    }
  } finally {
    matchTeamsLoading.value = false
  }
}

// 监听球员编辑对话框打开
watch(() => props.editPlayerDialog, (newValue) => {
  if (newValue) {
    loadTeams()
  }
})

watch(() => props.editEventDialog, (newValue) => {
  if (newValue) {
    loadMatches()
    loadPlayers()
  }
})

watch(() => props.editMatchDialog, (newValue) => {
  if (newValue) {
    loadTeamsForMatch()
  }
})
</script>

<style scoped>
/* 局部样式已抽离到 admin-management.css，如需个性化覆写可在此扩展 */
</style>
