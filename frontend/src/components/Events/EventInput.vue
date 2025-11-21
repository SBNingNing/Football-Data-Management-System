<template>
  <el-card class="form-card event-input-card">
    <template #header>
      <div class="form-header">
        <h3 class="form-title">
          <el-icon class="form-icon events-color"><Flag /></el-icon>
          {{ matchTypeLabel }}事件录入
        </h3>
      </div>
    </template>
    <el-form ref="eventFormRef" :model="eventForm" label-width="120px" class="event-form">
      <el-form-item label="比赛名称">
        <el-select v-model="eventForm.matchName" placeholder="请选择比赛" @change="handleMatchSelect" class="w-full" filterable>
          <el-option 
            v-for="match in filteredMatches" 
            :key="match.id" 
            :label="`${match.matchName} (${match.team1} vs ${match.team2})`" 
            :value="match.id" 
          />
        </el-select>
      </el-form-item>
      <el-form-item label="事件信息">
        <div class="event-section-header">
          <el-button type="primary" @click="addEvent" class="add-event-btn">添加事件</el-button>
          <span class="event-count-text">已添加 {{ eventForm.events.length }} 个事件</span>
        </div>
        <div class="event-list-container" v-if="eventForm.events.length">
          <transition-group name="player-list" tag="div">
            <div v-for="(ev, index) in eventForm.events" :key="`event-${index}`" class="event-item-card compact-card">
              <div class="event-item-content">
                <span class="event-index-badge">#{{ index + 1 }}</span>
                <el-select v-model="ev.eventType" placeholder="类型" class="event-field small-field">
                  <el-option label="进球" value="进球" />
                  <el-option label="红牌" value="红牌" />
                  <el-option label="黄牌" value="黄牌" />
                  <el-option label="乌龙球" value="乌龙球" />
                </el-select>
                <el-select 
                  v-model="ev.playerId" 
                  placeholder="选择球员" 
                  class="event-field medium-field"
                  filterable
                  :loading="playerSearchLoading"
                >
                  <el-option v-for="player in filteredMatchPlayers" :key="player.id || player.studentId" :label="`${player.name} (${player.teamName || '无队伍'})`" :value="player.id" />
                </el-select>
                <el-input v-model="ev.eventTime" placeholder="时间(分)" class="event-field small-field" />
                <el-button type="danger" link @click="removeEvent(index)" class="delete-btn" size="small"><el-icon><Delete /></el-icon></el-button>
              </div>
            </div>
          </transition-group>
        </div>
        <div v-else class="empty-players empty-events">
          <el-empty description="暂无事件" :image-size="80">
          </el-empty>
        </div>
      </el-form-item>
      <el-form-item class="entity-submit-zone">
        <el-button type="primary" @click="submitEvents" :disabled="!canSubmit" :loading="submitting" class="submit-btn btn-entity-submit">提交事件信息</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Flag, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getMatchTypeLabel } from '@/constants/domain'
import { createEventsBatch } from '@/domain/event/eventService'

const props = defineProps({
  matchType: { type: [String, Number], default: '' },
  matches: { type: Array, default: () => [] },
  teams: { type: Array, default: () => [] }
})
const emit = defineEmits(['submit', 'refresh-data'])

const eventFormRef = ref(null)
const eventForm = reactive({ matchName: '', events: [] })
const currentMatchPlayers = ref([])
const submitting = ref(false)
const playerSearchLoading = ref(false)
const playerSearchQuery = ref('')

const matchTypeLabel = computed(() => getMatchTypeLabel(props.matchType))
const canSubmit = computed(() => {
  return !!eventForm.matchName && 
         eventForm.events.length > 0 && 
         !submitting.value &&
         eventForm.events.every(e => e.eventType && e.playerId && e.eventTime)
})

// 过滤当前赛事类型的比赛
const filteredMatches = computed(() => {
  if (!props.matchType) return props.matches
  return props.matches.filter(m => {
    // 兼容多种字段名 (matchType, competitionId, tournamentId 等)
    // 假设 props.matchType 是 competitionId
    return m.competitionId == props.matchType || m.matchType == props.matchType
  })
})

// 过滤后的比赛球员（支持搜索）
const filteredMatchPlayers = computed(() => {
  // 移除自定义过滤逻辑，交给 el-select 的 filterable 处理
  return currentMatchPlayers.value
})

const addEvent = () => {
  eventForm.events.push({ eventType: '', playerId: '', eventTime: '' })
}
const removeEvent = (index) => {
  eventForm.events.splice(index, 1)
}
const handleMatchSelect = (matchId) => {
  const selectedMatch = props.matches.find(m => m.id === matchId)
  if (selectedMatch) {
    refreshPlayerList()
  } else {
    currentMatchPlayers.value = []
  }
}

// 刷新球员列表（确保获取最新数据）
const refreshPlayerList = async () => {
  if (!eventForm.matchName) return
  
  const selectedMatch = props.matches.find(m => m.id === eventForm.matchName)
  if (!selectedMatch) {
    currentMatchPlayers.value = []
    return
  }
  
  // 强制刷新props.teams数据（通过触发父组件重新加载）
  emit('refresh-data')
  
  // 使用最新的teams数据重新计算球员列表
  // 尝试匹配 team1/team2 (名称) 或 homeTeamId/awayTeamId (ID)
  // 注意：props.teams 可能是 TeamTournamentParticipation 列表，包含 teamName 和 id
  
  let team1 = null
  let team2 = null

  // 优先尝试通过 ID 匹配 (如果 selectedMatch 有 homeTeamId/awayTeamId)
  if (selectedMatch.homeTeamId) {
    team1 = props.teams.find(t => t.id === selectedMatch.homeTeamId)
  }
  if (selectedMatch.awayTeamId) {
    team2 = props.teams.find(t => t.id === selectedMatch.awayTeamId)
  }

  // 如果 ID 匹配失败，尝试通过名称匹配 (兼容旧数据)
  if (!team1 && selectedMatch.team1) {
    team1 = props.teams.find(t => t.teamName === selectedMatch.team1)
  }
  if (!team2 && selectedMatch.team2) {
    team2 = props.teams.find(t => t.teamName === selectedMatch.team2)
  }
  
  const team1Players = (team1?.players || []).map(p => ({ ...p, teamName: team1?.teamName || '主队' }))
  const team2Players = (team2?.players || []).map(p => ({ ...p, teamName: team2?.teamName || '客队' }))
  
  currentMatchPlayers.value = [...team1Players, ...team2Players]
}

// 搜索球员功能 (本地过滤)
const searchPlayers = (query) => {
  // 移除远程搜索逻辑，仅保留本地状态更新供 computed 使用
  // playerSearchQuery.value = query 
  // 由于移除了 remote，el-select 会自动处理 filterable
}
const submitEvents = () => {
  if (!canSubmit.value || submitting.value) return
  const clone = JSON.parse(JSON.stringify(eventForm))
  submitting.value = true
  createEventsBatch(clone.events.map(e => ({
    matchId: clone.matchName, // matchName 实际上存储的是 ID
    eventType: e.eventType,
    playerId: e.playerId,
    eventTime: e.eventTime
  }))).then(({ ok, data, error }) => {
    if(!ok){
      ElMessage.error(error?.message || '批量创建事件失败')
      return
    }
    try {
      import('@/utils/httpClient').then(m => {
        // 失效相关缓存（简单容错）
        m.default.cache.invalidate('events:list')
        m.default.cache.invalidate('stats:dashboard')
        m.default.cache.invalidate('stats:rankings')
      })
  } catch { /* ignore invalidate error */ }
    const success = data?.success || 0
    const total = data?.total || clone.events.length
    ElMessage.success(`事件提交完成：成功 ${success}/${total}`)
    emit('submit', clone)
    eventForm.matchName = ''
    eventForm.events = []
    currentMatchPlayers.value = []
  }).catch(_err => {
    ElMessage.error('事件提交异常')
  }).finally(()=>{ submitting.value = false })
}
</script>

<style scoped>
/* 局部样式覆盖，优化事件录入列表 */
.event-list-container {
  max-height: 300px;
  overflow-y: auto;
  padding: 4px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  margin-bottom: 16px;
}

.event-item-card.compact-card {
  padding: 8px 12px;
  margin-bottom: 8px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  background-color: var(--el-fill-color-blank);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.event-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.event-index-badge {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: bold;
  min-width: 24px;
}

.event-field {
  margin-bottom: 0 !important;
}

.small-field {
  width: 100px;
  flex-shrink: 0;
}

.medium-field {
  flex-grow: 1;
}

.delete-btn {
  margin-left: auto;
  padding: 4px;
}

/* 滚动条样式 */
.event-list-container::-webkit-scrollbar {
  width: 6px;
}
.event-list-container::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color);
  border-radius: 3px;
}
.event-list-container::-webkit-scrollbar-track {
  background-color: var(--el-fill-color-lighter);
}
</style>