<template>
  <el-dialog
    v-model="dialogVisible"
    :title="teamData?.team_name || '球队详情'"
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
            <span class="header-title">{{ teamDetails.team_name }}</span>
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
                <div class="stat-number">{{ teamDetails.total_goals || 0 }}</div>
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
                <div class="stat-number">{{ teamDetails.total_points || 0 }}</div>
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
                <div class="stat-number">{{ teamDetails.best_rank || '暂无' }}</div>
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
                <div class="stat-number">{{ teamDetails.total_goals_conceded || 0 }}</div>
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
                <div class="stat-number">{{ teamDetails.total_goal_difference || 0 }}</div>
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
                <div class="stat-number">{{ teamDetails.total_yellow_cards || 0 }}</div>
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
                <div class="stat-number">{{ teamDetails.total_red_cards || 0 }}</div>
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
                <span class="stat yellow" v-if="player.yellow_cards">{{ player.yellow_cards }}黄</span>
                <span class="stat red" v-if="player.red_cards">{{ player.red_cards }}红</span>
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
const teamName = ref('')

// Computed
const getAllPlayers = () => {
    // 兼容后端不同结构的 records (complete 接口返回的是 structurized seasons list，普通接口是 records array)
    // 这里主要处理 historyData.seasons 结构
    const tournaments = []
    
    // 如果有 historyData，优先从 seasoons 中提取
    if (historyData.value?.seasons) {
        historyData.value.seasons.forEach(s => {
            if (s.tournaments) tournaments.push(...s.tournaments)
        })
    } 
    // 否则尝试从 teamDetails.records 提取 (旧逻辑)
    else if (teamDetails.value?.records) {
        tournaments.push(...teamDetails.value.records)
    }

    const playersMap = new Map()
    tournaments.forEach(t => {
        if (t.players) {
            t.players.forEach(p => {
                // 注意后端新规范已经是 player_id (下划线)
                const key = p.player_id
                if (!playersMap.has(key)) {
                    // 初始化基础信息
                    playersMap.set(key, { 
                        player_id: key,
                        name: p.name,
                        number: p.number,
                        goals: 0,
                        yellow_cards: 0, 
                        red_cards: 0
                    })
                }
                
                // 累加统计数据 (注意下划线命名)
                const existing = playersMap.get(key)
                existing.goals += (p.goals || 0)
                existing.yellow_cards += (p.yellow_cards || 0)
                existing.red_cards += (p.red_cards || 0)
            })
        }
    })
    return Array.from(playersMap.values())
}

const getTeamStatusType = () => {
  if (!teamDetails.value) return 'info'
  const rank = teamDetails.value.best_rank
  if (rank === 1) return 'success'
  if (rank <= 3) return 'warning'
  return 'info'
}

const getTeamStatusText = () => {
  if (!teamDetails.value) return '球队'
  const rank = teamDetails.value.best_rank
  if (rank === 1) return '冠军球队'
  if (rank <= 3) return '优秀球队'
  return '参赛球队'
}

// Methods
const open = async (param) => {
  // 如果传来的是字符串，当做 team_name 处理
  if (typeof param === 'string') {
    teamName.value = param
  } 
  // 如果是对象，则取其 team_name 属性
  else if (param && typeof param === 'object') {
    teamName.value = param.team_name
  }

  if (!teamName.value) {
    ElMessage.error('无法获取球队名称')
    return
  }

  dialogVisible.value = true
  loading.value = true
  error.value = null
  teamDetails.value = null
  historyData.value = null

  try {
    // 1. 获取球队基础信息 (注意：后端返回的结构可能是列表或直接对象)
    const teamRes = await fetch(`/api/teams/${encodeURIComponent(teamName.value)}`)
    if (!teamRes.ok) throw new Error('球队基础信息请求失败')
    
    let teamInfo = await teamRes.json()
    // 适配后端不同的返回格式：可能是 {status:'success', data:{...}} 也可能是直接 {...}
    if (teamInfo.status === 'success' && teamInfo.data) {
        teamInfo = teamInfo.data
    } else if (teamInfo.data) {
        // 部分旧接口可能返回 {data: ...}
        teamInfo = teamInfo.data
    }

    if (!teamInfo || !teamInfo.team_base_id) {
        // 尝试从 props.teamData 兜底
        if (props.teamData && props.teamData.team_base_id) {
            teamInfo = { ...teamInfo, team_base_id: props.teamData.team_base_id }
        } else {
             throw new Error('无法解析球队ID')
        }
    }
    
    // 统一 ID 字段
    const baseId = teamInfo.team_base_id
    teamDetails.value = { ...teamInfo, team_base_id: baseId }

    // 2. 获取球队完整历史 (需要 team_base_id)
    const historyRes = await fetch(`/api/team-history/${baseId}/complete`)
    if (historyRes.ok) {
      const historyJson = await historyRes.json()
      // team-history 接口通常返回 {status:'success', data:{...}}
      if (historyJson.data) {
        historyData.value = historyJson.data
        // 如果基础信息里缺字段，用历史信息补全
        if (historyJson.data.team_info) {
             Object.assign(teamDetails.value, historyJson.data.team_info)
        }
      }
    }

  } catch (err) {
    console.error(err)
    error.value = '加载失败: ' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}


const handleClose = () => {
  dialogVisible.value = false
  emit('update:visible', false)
  emit('close')
}

const fetchTeamDetails = () => open(teamName.value)

// 计算乌龙球总数
const getOwnGoalsCount = () => {
  if (!teamDetails.value?.records) return 0
  
  let ownGoals = 0
  teamDetails.value.records.forEach(record => {
    if (record.players) {
      record.players.forEach(player => {
        ownGoals += player.own_goals || 0
      })
    }
  })
  
  return ownGoals
}

// Watchers
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.teamData?.team_name) {
    open(props.teamData)
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