<template>
  <el-tabs v-model="activeTab" type="card">
    <!-- 比赛管理 -->
    <el-tab-pane label="比赛管理" name="matches">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" class="refresh-btn">
          刷新数据
        </el-button>
      </div>
      <el-table :data="displayMatches" border style="width: 100%">
        <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
        <el-table-column prop="team1" label="球队1" width="150"></el-table-column>
        <el-table-column prop="team2" label="球队2" width="150"></el-table-column>
        <el-table-column label="比分" width="120">
          <template #default="{ row }">
            <span v-if="row" class="match-score">
              {{ row.home_score || 0 }} : {{ row.away_score || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="比赛时间" width="180">
          <template #default="{ row }">
            <span v-if="row">{{ formatDate(row.date) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="比赛地点" width="150"></el-table-column>
        <el-table-column prop="matchType" label="比赛类型" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ getMatchTypeLabel(row.matchType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="比赛状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row" :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <div v-if="row">
              <el-button size="small" type="primary" @click="$emit('edit-match', row)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-match', row.id)">删除</el-button>
              <el-button 
                v-if="row.status !== 'completed' && row.status !== '已完赛'" 
                size="small" 
                type="success" 
                @click="$emit('complete-match', row.id)"
              >
                完赛
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <!-- 事件管理 -->
    <el-tab-pane label="事件管理" name="events">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" class="refresh-btn">
          刷新数据
        </el-button>
      </div>
      <el-table :data="displayEvents" border style="width: 100%">
        <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
        <el-table-column prop="eventType" label="事件类型" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ getEventTypeLabel(row.eventType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="playerName" label="球员" width="150"></el-table-column>
        <el-table-column prop="eventTime" label="事件时间" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ row.eventTime }}分钟</span>
          </template>
        </el-table-column>
        <el-table-column prop="matchType" label="比赛类型" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ getMatchTypeLabel(row.matchType) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div v-if="row">
              <el-button size="small" type="primary" @click="$emit('edit-event', row)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-event', row.id)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <!-- 球员管理 -->
    <el-tab-pane label="球员管理" name="players">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" class="refresh-btn">
          刷新数据
        </el-button>
      </div>
      <el-table :data="displayPlayers" border style="width: 100%">
        <el-table-column prop="name" label="球员姓名" width="150"></el-table-column>
        <el-table-column prop="number" label="球衣号码" width="120"></el-table-column>
        <el-table-column prop="studentId" label="学号" width="150"></el-table-column>
        <el-table-column prop="teamName" label="所属球队" width="200"></el-table-column>
        <el-table-column prop="matchType" label="比赛类型" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ getMatchTypeLabel(row.matchType) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="统计信息" min-width="200">
          <template #default="{ row }">
            <div v-if="row" class="player-stats">
              <el-tag size="small" type="success">进球: {{ getPlayerGoals(row.name) }}</el-tag>
              <el-tag size="small" type="warning">黄牌: {{ getPlayerCards(row.name, '黄牌') }}</el-tag>
              <el-tag size="small" type="danger">红牌: {{ getPlayerCards(row.name, '红牌') }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div v-if="row">
              <el-button size="small" type="primary" @click="$emit('edit-player', row)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-player', row.id || row.studentId)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <!-- 球队管理 -->
    <el-tab-pane label="球队管理" name="teams">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" class="refresh-btn">
          刷新数据
        </el-button>
      </div>
      <el-table :data="displayTeams" border style="width: 100%">
        <el-table-column prop="teamName" label="球队名称" width="200"></el-table-column>
        <el-table-column prop="matchType" label="比赛类型" width="150">
          <template #default="{ row }">
            <span v-if="row">{{ getMatchTypeLabel(row.matchType) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="球员数量" width="120">
          <template #default="{ row }">
            <span v-if="row">{{ row.players ? row.players.length : 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="球员信息" min-width="300">
          <template #default="{ row }">
            <div v-if="row && row.players && row.players.length > 0" class="players-info">
              
              <!-- 直接显示所有球员 -->
              <div class="players-list">
                <el-tag 
                  v-for="player in row.players" 
                  :key="player.studentId || player.id" 
                  size="small" 
                  class="player-tag"
                  :title="`学号: ${player.studentId || player.id}`"
                >
                  {{ player.name }}({{ player.number }})
                </el-tag>
              </div>
            </div>
            <span v-else class="no-players">暂无球员</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div v-if="row">
              <el-button size="small" type="primary" @click="$emit('edit-team', row)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-team', row.id)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { Refresh } from '@element-plus/icons-vue'

const RefreshIcon = Refresh

// 定义 props
const props = defineProps({
  teams: {
    type: Array,
    default: () => []
  },
  matches: {
    type: Array,
    default: () => []
  },
  events: {
    type: Array,
    default: () => []
  },
  players: {
    type: Array,
    default: () => []
  },
  manageMatchType: {
    type: String,
    default: ''
  }
})

// 定义 emits
const emit = defineEmits(['filter-change', 'refresh', 'edit-team', 'delete-team', 'edit-match', 'delete-match', 'edit-event', 'delete-event', 'edit-player', 'delete-player', 'complete-match'])

// 响应式数据
const activeTab = ref('matches')

// 计算属性
const displayTeams = computed(() => {
  return props.manageMatchType ? 
    props.teams.filter(team => team.matchType === props.manageMatchType) : 
    props.teams
})

const displayMatches = computed(() => {
  return props.manageMatchType ? 
    props.matches.filter(match => match.matchType === props.manageMatchType) : 
    props.matches
})

const displayEvents = computed(() => {
  return props.manageMatchType ? 
    props.events.filter(event => event.matchType === props.manageMatchType) : 
    props.events
})

const displayPlayers = computed(() => {
  try {
    if (!props.players || !Array.isArray(props.players)) {
      return []
    }
    
    const filteredPlayers = props.manageMatchType ? 
      props.players.filter(player => player && player.matchType === props.manageMatchType) : 
      props.players.filter(player => player != null)
    
    return filteredPlayers
  } catch (error) {
    console.error('处理球员数据时出错:', error)
    return []
  }
})

// 方法
const getMatchTypeLabel = (type) => {
  const labels = {
    'champions-cup': '冠军杯',
    'womens-cup': '巾帼杯',
    'eight-a-side': '八人制比赛'
  }
  return labels[type] || ''
}

const getEventTypeLabel = (type) => {
  const labels = {
    '进球': '进球',
    '红牌': '红牌', 
    '黄牌': '黄牌',
    '乌龙球': '乌龙球'
  }
  return labels[type] || type
}

const formatDate = (date) => {
  if (!date) return ''
  try {
    return new Date(date).toLocaleString('zh-CN')
  } catch (error) {
    return date
  }
}

// 获取球员进球数
const getPlayerGoals = (playerName) => {
  try {
    if (!playerName || !props.events || !Array.isArray(props.events)) {
      return 0
    }
    return props.events.filter(event => 
      event && event.playerName === playerName && (event.eventType === '进球' || event.eventType === 'goal')
    ).length
  } catch (error) {
    console.error('获取球员进球数时出错:', error)
    return 0
  }
}

// 获取球员卡牌数
const getPlayerCards = (playerName, cardType) => {
  try {
    if (!playerName || !cardType || !props.events || !Array.isArray(props.events)) {
      return 0
    }
    return props.events.filter(event => 
      event && event.playerName === playerName && event.eventType === cardType
    ).length
  } catch (error) {
    console.error('获取球员卡牌数时出错:', error)
    return 0
  }
}

// 获取比赛状态标签
const getStatusLabel = (status) => {
  const labels = {
    'pending': '未开始',
    'ongoing': '进行中', 
    'completed': '已完赛',
    '已完赛': '已完赛',
    '未开始': '未开始',
    '进行中': '进行中'
  }
  return labels[status] || '未开始'
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const types = {
    'pending': 'info',      // 灰色
    'ongoing': 'warning',   // 橙色
    'completed': 'success', // 绿色
    '已完赛': 'success',
    '未开始': 'info',
    '进行中': 'warning'
  }
  return types[status] || 'info'
}
</script>

<style scoped>
.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.refresh-btn {
  min-width: 100px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.players-info {
  max-width: 100%;
}

.players-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.players-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.player-tag {
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  font-size: 12px;
}

.no-players {
  color: #c0c4cc;
  font-style: italic;
}

.player-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.player-stats .el-tag {
  margin: 0;
}

.match-score {
  font-weight: bold;
  color: #409eff;
  font-size: 14px;
}
</style>
