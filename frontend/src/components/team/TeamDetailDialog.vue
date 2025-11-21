<template>
  <el-dialog
    v-model="dialogVisible"
    :title="teamData?.teamName || '球队详情'"
    width="80%"
    :before-close="handleClose"
    class="team-detail-dialog"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :loading="true" animated>
        <template #template>
          <el-skeleton-item variant="h1" style="width: 240px" />
          <div style="padding: 14px;">
            <el-skeleton-item variant="rect" style="width: 100%; height: 240px" />
            <div style="padding: 14px;">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <el-skeleton-item variant="text" style="width: 100%" />
              <el-skeleton-item variant="text" style="width: 100%" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="fetchTeamDetails">重试</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="teamDetails" class="team-detail-content">
      <!-- 球队基本信息卡片 -->
      <el-card class="team-summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><Trophy /></el-icon>
            <span class="header-title">{{ teamDetails.teamName }}</span>
            <el-tag :type="getTeamStatusType()" size="small">
              {{ getTeamStatusText() }}
            </el-tag>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-icon goals">
                <el-icon><Finished /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalGoals || 0 }}</div>
                <div class="stat-label">总进球数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-icon points">
                <el-icon><Medal /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalPoints || 0 }}</div>
                <div class="stat-label">总积分</div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-icon rank">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.bestRank || '暂无' }}</div>
                <div class="stat-label">最佳排名</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon conceded">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalGoalsConceded || 0 }}</div>
                <div class="stat-label">失球数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon difference">
                <el-icon><Top /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalGoalDifference || 0 }}</div>
                <div class="stat-label">净胜球</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon yellow">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalYellowCards || 0 }}</div>
                <div class="stat-label">黄牌</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon red">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ teamDetails.totalRedCards || 0 }}</div>
                <div class="stat-label">红牌</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon own-goals">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ getOwnGoalsCount() }}</div>
                <div class="stat-label">乌龙球</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 球员信息 -->
      <el-card class="players-card" shadow="hover" v-if="teamDetails.records?.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><User /></el-icon>
            <span class="header-title">球员阵容</span>
          </div>
        </template>
        
        <div class="players-grid">
          <div 
            v-for="(player, index) in getAllPlayers()" 
            :key="player.playerId || index"
            class="player-item"
          >
            <div class="player-avatar">
              <el-icon><User /></el-icon>
              <span class="player-number">{{ player.number || '?' }}</span>
            </div>
            <div class="player-info">
              <div class="player-name">{{ player.name || '未知球员' }}</div>
              <div class="player-stats">
                <span class="stat">{{ player.goals || 0 }}球</span>
                <span class="stat yellow" v-if="player.yellowCards">{{ player.yellowCards }}黄</span>
                <span class="stat red" v-if="player.redCards">{{ player.redCards }}红</span>
                <span class="stat own-goals" v-if="player.ownGoals">{{ player.ownGoals }}乌龙</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 赛季表现 -->
      <el-card class="seasons-card" shadow="hover" v-if="historyData?.seasons?.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><Calendar /></el-icon>
            <span class="header-title">赛季表现</span>
          </div>
        </template>
        
        <div class="seasons-list">
          <div 
            v-for="season in historyData.seasons" 
            :key="season.season_info.id"
            class="season-item"
          >
            <div class="season-header">
              <h4>{{ season.season_info.name }}</h4>
              <el-tag size="small">{{ season.season_totals.tournaments_count }}项赛事</el-tag>
            </div>
            <div class="season-stats">
              <span class="stat-item">进球: {{ season.season_totals.total_goals }}</span>
              <span class="stat-item">球员: {{ season.season_totals.total_players }}</span>
              <span class="stat-item">黄牌: {{ season.season_totals.total_yellow_cards }}</span>
              <span class="stat-item">红牌: {{ season.season_totals.total_red_cards }}</span>
            </div>
            
            <div class="tournaments-list" v-if="season.tournaments?.length > 0">
              <div 
                v-for="tournament in season.tournaments" 
                :key="tournament.tournament_id"
                class="tournament-item"
              >
                <div class="tournament-name">{{ tournament.tournament_name }}</div>
                <div class="tournament-ranking">排名: {{ tournament.final_ranking || '未知' }}</div>
                <div class="tournament-stats">
                  <span>{{ tournament.stats.total_goals }}球</span>
                  <span>{{ tournament.stats.players_count }}人</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Trophy, User, Medal, Star, Finished, Warning, CircleClose, Top, Calendar
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  teamData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:visible', 'close'])

// State
const dialogVisible = ref(false)
const loading = ref(false)
const error = ref(null)
const teamDetails = ref(null)
const historyData = ref(null)

// Computed
const getAllPlayers = () => {
  if (!teamDetails.value?.records) return []
  
  const playersMap = new Map()
  teamDetails.value.records.forEach(record => {
    if (record.players) {
      record.players.forEach(player => {
        const key = player.playerId || player.id
        if (!playersMap.has(key)) {
          playersMap.set(key, { ...player })
        } else {
          // 合并数据，累加统计
          const existing = playersMap.get(key)
          existing.goals = (existing.goals || 0) + (player.goals || 0)
          existing.yellowCards = (existing.yellowCards || 0) + (player.yellowCards || 0)
          existing.redCards = (existing.redCards || 0) + (player.redCards || 0)
        }
      })
    }
  })
  
  return Array.from(playersMap.values())
}

const getTeamStatusType = () => {
  if (!teamDetails.value) return 'info'
  const rank = teamDetails.value.bestRank
  if (rank === 1) return 'success'
  if (rank <= 3) return 'warning'
  return 'info'
}

const getTeamStatusText = () => {
  if (!teamDetails.value) return '球队'
  const rank = teamDetails.value.bestRank
  if (rank === 1) return '冠军球队'
  if (rank <= 3) return '优秀球队'
  return '参赛球队'
}

// Methods
const fetchTeamDetails = async () => {
  if (!props.teamData?.teamName) {
    error.value = '缺少球队信息'
    return
  }

  loading.value = true
  error.value = null

  try {
    // 获取球队基础信息
    const teamResponse = await fetch(`/api/teams/${encodeURIComponent(props.teamData.teamName)}`)
    if (!teamResponse.ok) {
      throw new Error(`获取球队信息失败: ${teamResponse.status}`)
    }
    
    const teamData = await teamResponse.json()
    if (!teamData.status === 'success' || !teamData.data) {
      throw new Error('球队信息格式错误')
    }

    teamDetails.value = {
      ...props.teamData,
      ...teamData.data
    }

    // 获取球队历史信息
    if (teamData.data.teamBaseId) {
      const historyResponse = await fetch(`/api/team-history/${teamData.data.teamBaseId}/complete`)
      if (historyResponse.ok) {
        const history = await historyResponse.json()
        if (history.data) {
          historyData.value = history.data
        }
      }
    }

  } catch (err) {
    error.value = err.message || '获取球队详情失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  emit('update:visible', false)
  emit('close')
}

// 计算乌龙球总数
const getOwnGoalsCount = () => {
  if (!teamDetails.value?.records) return 0
  
  let ownGoals = 0
  teamDetails.value.records.forEach(record => {
    if (record.players) {
      record.players.forEach(player => {
        ownGoals += player.ownGoals || 0
      })
    }
  })
  
  return ownGoals
}

// Watchers
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.teamData?.teamName) {
    fetchTeamDetails()
  }
})

watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})
</script>

<style scoped>
@import '@/assets/styles/team-detail-dialog.css';
</style>