<template>
  <el-dialog
    v-model="dialogVisible"
    :title="matchData?.match_name || '比赛详情'"
    width="80%"
    :before-close="handleClose"
    class="match-detail-dialog"
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
          <el-button type="primary" @click="fetchMatchDetails">重试</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="matchDetails" class="match-detail-content">
      <!-- 比赛基本信息卡片 -->
      <el-card class="match-summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><Trophy /></el-icon>
            <span class="header-title">{{ matchDetails.match_name }}</span>
            <el-tag :type="getMatchStatusType()" size="small">
              {{ matchDetails.status }}
            </el-tag>
          </div>
        </template>
        
        <!-- 对阵信息 -->
        <div class="teams-vs-section">
          <div class="team-info team-home">
            <div class="team-avatar">
              <el-icon><Flag /></el-icon>
            </div>
            <div class="team-details">
              <div class="team-name">{{ matchDetails.home_team || matchDetails.home_team_name }}</div>
              <div class="team-label">主队</div>
            </div>
          </div>
          
          <div class="vs-section">
            <div class="vs-text">VS</div>
            <div class="match-score" :class="getScoreClass()">
              {{ matchDetails.score || `${matchDetails.home_score || 0} - ${matchDetails.away_score || 0}` }}
            </div>
            <div class="match-time">{{ formatDate(matchDetails.match_time) }}</div>
          </div>
          
          <div class="team-info team-away">
            <div class="team-avatar">
              <el-icon><Flag /></el-icon>
            </div>
            <div class="team-details">
              <div class="team-name">{{ matchDetails.away_team || matchDetails.away_team_name }}</div>
              <div class="team-label">客队</div>
            </div>
          </div>
        </div>

        <!-- 比赛统计信息 -->
        <el-row :gutter="20" class="match-stats-row">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon type">
                <el-icon><Medal /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ getMatchTypeLabel(matchDetails.match_type) }}</div>
                <div class="stat-label">比赛类型</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon location">
                <el-icon><LocationFilled /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ matchDetails.location || '待定' }}</div>
                <div class="stat-label">比赛地点</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon status">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ matchDetails.status }}</div>
                <div class="stat-label">比赛状态</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-icon duration">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ matchDetails.duration || '90分钟' }}</div>
                <div class="stat-label">比赛时长</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 比赛事件 -->
      <el-card class="events-card" shadow="hover" v-if="matchDetails.events?.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><Notification /></el-icon>
            <span class="header-title">比赛事件</span>
            <el-tag type="info" size="small">{{ matchDetails.events?.length || 0 }} 个事件</el-tag>
          </div>
        </template>
        
        <div class="events-timeline">
          <div 
            v-for="(event, index) in matchDetails.events" 
            :key="index"
            class="event-item"
          >
            <div class="event-time">{{ event.time }}'</div>
            <div class="event-icon" :class="getEventIconClass(event.type)">
              <el-icon>
                <Football v-if="event.type === 'goal'" />
                <Warning v-else-if="event.type === 'yellow_card'" />
                <CircleClose v-else-if="event.type === 'red_card'" />
                <RefreshRight v-else-if="event.type === 'substitution'" />
                <Star v-else />
              </el-icon>
            </div>
            <div class="event-details">
              <div class="event-description">{{ event.description }}</div>
              <div class="event-player">{{ event.player }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 比赛详细信息 -->
      <el-card class="additional-info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><InfoFilled /></el-icon>
            <span class="header-title">详细信息</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-section">
              <h4>比赛规则</h4>
              <div class="info-item">
                <span class="info-label">比赛制度:</span>
                <span class="info-value">{{ getMatchFormat(matchDetails.match_type) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">比赛时长:</span>
                <span class="info-value">{{ matchDetails.duration || '90分钟' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">裁判:</span>
                <span class="info-value">{{ matchDetails.referee || '待定' }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-section">
              <h4>比赛环境</h4>
              <div class="info-item">
                <span class="info-label">天气条件:</span>
                <span class="info-value">{{ matchDetails.weather || '晴朗' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">温度:</span>
                <span class="info-value">{{ matchDetails.temperature || '22°C' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">观众人数:</span>
                <span class="info-value">{{ matchDetails.attendance || '0' }} 人</span>
              </div>
            </div>
          </el-col>
        </el-row>
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
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Trophy, Flag, Medal, Clock, LocationFilled, Timer, Notification, 
  Football, Warning, CircleClose, RefreshRight, Star, InfoFilled
} from '@element-plus/icons-vue'
import useCompetitions from '@/composables/admin/useCompetitions'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  matchData: {
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
const matchDetails = ref(null)

const { getCompetitionLabel, fetchCompetitions } = useCompetitions()

onMounted(() => {
  fetchCompetitions()
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '待定'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// 获取比赛类型标签
const getMatchTypeLabel = (type) => {
  return getCompetitionLabel(type) || type
}

// 获取比赛格式
const getMatchFormat = (type) => {
  // 简单的基于名称的推断，或者后续可以从后端获取更详细的规则
  const label = getMatchTypeLabel(type)
  if (label.includes('八人制')) return '8人制'
  return '11人制'
}

// 获取比赛状态类型
const getMatchStatusType = () => {
  if (!matchDetails.value) return 'info'
  const status = matchDetails.value.status
  if (status === '已结束') return 'success'
  if (status === '进行中') return 'warning' 
  if (status === '未开始') return 'info'
  return 'info'
}

// 获取比分样式
const getScoreClass = () => {
  if (!matchDetails.value?.status) return 'pending'
  if (matchDetails.value.status === '已结束') return 'finished'
  if (matchDetails.value.status === '进行中') return 'live'
  return 'pending'
}

// 获取事件图标样式
const getEventIconClass = (eventType) => {
  const classMap = {
    'goal': 'event-goal',
    'yellow_card': 'event-yellow',
    'red_card': 'event-red',
    'substitution': 'event-sub',
    'default': 'event-default'
  }
  return classMap[eventType] || classMap.default
}

// Methods
const fetchMatchDetails = async () => {
  if (!props.matchData?.id) {
    error.value = '缺少比赛信息'
    return
  }

  loading.value = true
  error.value = null

  try {
    // 这里可以调用API获取详细比赛信息
    // const response = await fetch(`/api/matches/${props.matchData.id}`)
    
    // 暂时使用传入的数据，并添加一些模拟的详细信息
    matchDetails.value = {
      ...props.matchData,
      events: [
        {
          time: 15,
          type: 'goal',
          description: '进球',
          player: '张三'
        },
        {
          time: 32,
          type: 'yellow_card', 
          description: '黄牌警告',
          player: '李四'
        },
        {
          time: 67,
          type: 'substitution',
          description: '换人',
          player: '王五 → 赵六'
        }
      ],
      referee: '裁判员：陈某',
      weather: '晴朗',
      temperature: '25°C',
      attendance: 150,
      duration: getMatchFormat(props.matchData.match_type) === '8人制' ? '60分钟' : '90分钟'
    }

  } catch (err) {
    error.value = err.message || '获取比赛详情失败'
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

// Watchers
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.matchData?.id) {
    fetchMatchDetails()
  }
})

watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})
</script>

<style scoped>
@import '@/assets/styles/match-detail-dialog.css';
</style>