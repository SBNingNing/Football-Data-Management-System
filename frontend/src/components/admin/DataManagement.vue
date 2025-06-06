<template>
  <el-tabs v-model="activeTab" type="card">
    <!-- 球队管理 -->
    <el-tab-pane label="球队管理" name="teams">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" icon="el-icon-refresh">刷新</el-button>
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
        <el-table-column label="球员信息" min-width="200">
          <template #default="{ row }">
            <div v-if="row && row.players && row.players.length > 0" class="players-preview">
              <el-tag v-for="player in row.players.slice(0, 3)" :key="player.name" size="small" class="player-tag">
                {{ player.name }}({{ player.number }})
              </el-tag>
              <span v-if="row.players.length > 3" class="more-players">+{{ row.players.length - 3 }}人</span>
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

    <!-- 比赛管理 -->
    <el-tab-pane label="比赛管理" name="matches">
      <div class="manage-header">
        <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 200px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
        <el-button type="primary" @click="$emit('refresh')" icon="el-icon-refresh">刷新</el-button>
      </div>
      <el-table :data="displayMatches" border style="width: 100%">
        <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
        <el-table-column prop="team1" label="球队1" width="150"></el-table-column>
        <el-table-column prop="team2" label="球队2" width="150"></el-table-column>
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div v-if="row">
              <el-button size="small" type="primary" @click="$emit('edit-match', row)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-match', row.id)">删除</el-button>
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
        <el-button type="primary" @click="$emit('refresh')" icon="el-icon-refresh">刷新</el-button>
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
  </el-tabs>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

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
  manageMatchType: {
    type: String,
    default: ''
  }
})

// 定义 emits
const emit = defineEmits(['filter-change', 'refresh', 'edit-team', 'delete-team', 'edit-match', 'delete-match', 'edit-event', 'delete-event'])

// 响应式数据
const activeTab = ref('teams')

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

.players-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.player-tag {
  margin: 0;
}

.more-players {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.no-players {
  color: #c0c4cc;
  font-style: italic;
}
</style>
