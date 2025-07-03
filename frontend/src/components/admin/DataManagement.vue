<template>
  <el-tabs v-model="activeTab" type="card">
    <!-- 比赛管理 -->
    <el-tab-pane label="比赛管理" name="matches">
      <el-card class="manage-card">
        <template #header>
          <div class="card-header">
            <span>比赛管理</span>
            <div class="header-stats">
              共 {{ filteredMatches.length }} 场比赛
            </div>
          </div>
        </template>

        <!-- 搜索区域 -->
        <div class="search-section">
          <el-row :gutter="15">
            <el-col :span="8">
              <el-input
                v-model="matchSearchKeyword"
                placeholder="搜索比赛名称、球队名称"
                @input="handleMatchSearch"
                clearable
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 100%;">
                <el-option label="全部" value=""></el-option>
                <el-option label="冠军杯" value="champions-cup"></el-option>
                <el-option label="巾帼杯" value="womens-cup"></el-option>
                <el-option label="八人制比赛" value="eight-a-side"></el-option>
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="matchStatusFilter" placeholder="比赛状态" clearable style="width: 100%;">
                <el-option label="未开始" value="pending"></el-option>
                <el-option label="进行中" value="ongoing"></el-option>
                <el-option label="已完赛" value="completed"></el-option>
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">
                刷新
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 比赛卡片 -->
        <div class="cards-container">
          <div v-if="paginatedMatches.length === 0" class="no-data">
            <el-empty description="暂无比赛数据" />
          </div>
          <el-row :gutter="20" v-else>
            <el-col :span="8" v-for="match in paginatedMatches" :key="match.id || match.matchId">
              <el-card shadow="hover" class="match-card">
                <div class="match-info">
                  <div class="match-title">{{ match.matchName || match.name || '未命名比赛' }}</div>
                  <div class="match-teams">
                    <span class="team">{{ match.team1 || match.homeTeam || '主队' }}</span>
                    <span class="vs">VS</span>
                    <span class="team">{{ match.team2 || match.awayTeam || '客队' }}</span>
                  </div>
                  <div class="match-score">
                    {{ match.home_score || match.homeScore || 0 }} : {{ match.away_score || match.awayScore || 0 }}
                  </div>
                  <div class="match-meta">
                    <div class="meta-item">
                      <el-icon><Calendar /></el-icon>
                      <span>{{ formatDate(match.date || match.matchDate) }}</span>
                    </div>
                    <div class="meta-item">
                      <el-icon><LocationFilled /></el-icon>
                      <span>{{ match.location || match.venue || '未定' }}</span>
                    </div>
                    <div class="meta-item">
                      <el-icon><Trophy /></el-icon>
                      <span>{{ getMatchTypeLabel(match.matchType || match.type) }}</span>
                    </div>
                  </div>
                  <div class="match-status">
                    <el-tag :type="getStatusTagType(match.status)">
                      {{ getStatusLabel(match.status) }}
                    </el-tag>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button size="small" type="primary" @click="$emit('edit-match', match)">编辑</el-button>
                  <el-button size="small" type="danger" @click="$emit('delete-match', match.id || match.matchId)">删除</el-button>
                  <el-button 
                    v-if="match.status !== 'completed' && match.status !== '已完赛'" 
                    size="small" 
                    type="success" 
                    @click="$emit('complete-match', match.id || match.matchId)"
                  >
                    完赛
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="filteredMatches.length > matchPageSize">
          <el-pagination
            v-model:current-page="matchCurrentPage"
            v-model:page-size="matchPageSize"
            :page-sizes="[9, 18, 36]"
            :total="filteredMatches.length"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-card>
    </el-tab-pane>

    <!-- 事件管理 -->
    <el-tab-pane label="事件管理" name="events">
      <el-card class="manage-card">
        <template #header>
          <div class="card-header">
            <span>事件管理</span>
            <div class="header-stats">
              共 {{ filteredEvents.length }} 个事件
            </div>
          </div>
        </template>

        <!-- 搜索区域 -->
        <div class="search-section">
          <el-row :gutter="15">
            <el-col :span="8">
              <el-input
                v-model="eventSearchKeyword"
                placeholder="搜索比赛名称、球员姓名"
                @input="handleEventSearch"
                clearable
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 100%;">
                <el-option label="全部" value=""></el-option>
                <el-option label="冠军杯" value="champions-cup"></el-option>
                <el-option label="巾帼杯" value="womens-cup"></el-option>
                <el-option label="八人制比赛" value="eight-a-side"></el-option>
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="eventTypeFilter" placeholder="事件类型" clearable style="width: 100%;">
                <el-option label="进球" value="进球"></el-option>
                <el-option label="黄牌" value="黄牌"></el-option>
                <el-option label="红牌" value="红牌"></el-option>
                <el-option label="乌龙球" value="乌龙球"></el-option>
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">
                刷新
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 事件卡片 -->
        <div class="cards-container">
          <div v-if="paginatedEvents.length === 0" class="no-data">
            <el-empty description="暂无事件数据" />
          </div>
          <el-row :gutter="20" v-else>
            <el-col :span="6" v-for="event in paginatedEvents" :key="event.id || event.eventId">
              <el-card shadow="hover" class="event-card">
                <div class="event-info">
                  <div class="event-type">
                    <el-tag :type="getEventTagType(event.eventType || event.type)" size="large">
                      {{ getEventTypeLabel(event.eventType || event.type) }}
                    </el-tag>
                  </div>
                  <div class="event-match">{{ event.matchName || event.match || '未知比赛' }}</div>
                  <div class="event-player">
                    <el-icon><User /></el-icon>
                    <span>{{ event.playerName || event.player || '未知球员' }}</span>
                  </div>
                  <div class="event-time">
                    <el-icon><Clock /></el-icon>
                    <span>{{ event.eventTime || event.time || 0 }}分钟</span>
                  </div>
                  <div class="event-match-type">
                    <el-icon><Trophy /></el-icon>
                    <span>{{ getMatchTypeLabel(event.matchType || event.type) }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button size="small" type="primary" @click="$emit('edit-event', event)">编辑</el-button>
                  <el-button size="small" type="danger" @click="$emit('delete-event', event.id || event.eventId)">删除</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="filteredEvents.length > eventPageSize">
          <el-pagination
            v-model:current-page="eventCurrentPage"
            v-model:page-size="eventPageSize"
            :page-sizes="[12, 24, 48]"
            :total="filteredEvents.length"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-card>
    </el-tab-pane>

    <!-- 球员管理 -->
    <el-tab-pane label="球员管理" name="players">
      <el-card class="manage-card">
        <template #header>
          <div class="card-header">
            <span>球员管理</span>
            <div class="header-stats">
              共 {{ filteredPlayers.length }} 名球员
            </div>
          </div>
        </template>

        <!-- 搜索区域 -->
        <div class="search-section">
          <el-row :gutter="15">
            <el-col :span="8">
              <el-input
                v-model="playerSearchKeyword"
                placeholder="搜索球员姓名、学号"
                @input="handlePlayerSearch"
                clearable
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 100%;">
                <el-option label="全部" value=""></el-option>
                <el-option label="冠军杯" value="champions-cup"></el-option>
                <el-option label="巾帼杯" value="womens-cup"></el-option>
                <el-option label="八人制比赛" value="eight-a-side"></el-option>
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="playerTeamFilter" placeholder="所属球队" clearable style="width: 100%;">
                <el-option
                  v-for="team in playerTeamOptions"
                  :key="team"
                  :label="team"
                  :value="team"
                />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">
                刷新
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 球员卡片 -->
        <div class="cards-container">
          <div v-if="paginatedPlayers.length === 0" class="no-data">
            <el-empty description="暂无球员数据" />
          </div>
          <el-row :gutter="20" v-else>
            <el-col :span="8" v-for="player in paginatedPlayers" :key="player.id || player.studentId">
              <el-card shadow="hover" class="player-card">
                <div class="player-info">
                  <div class="player-avatar">
                    <el-icon class="avatar-icon"><User /></el-icon>
                  </div>
                  <div class="player-details">
                    <div class="player-name">{{ player.name || '未知球员' }}</div>
                    <div class="player-meta">
                      <div class="meta-item">
                        <el-icon><CreditCard /></el-icon>
                        <span>{{ player.studentId || player.id || '未知' }}</span>
                      </div>
                      <div class="meta-item">
                        <el-icon><Tickets /></el-icon>
                        <span>{{ player.number || player.jerseyNumber || '未知' }}号</span>
                      </div>
                      <div class="meta-item">
                        <el-icon><Trophy /></el-icon>
                        <span>{{ player.teamName || player.team || '未知球队' }}</span>
                      </div>
                      <div class="meta-item">
                        <el-icon><Collection /></el-icon>
                        <span>{{ getMatchTypeLabel(player.matchType || player.type) }}</span>
                      </div>
                    </div>
                    <div class="player-stats">
                      <span class="stat-badge goals">
                        <el-icon><Football /></el-icon>
                        {{ getPlayerGoals(player.name) }}球
                      </span>
                      <span class="stat-badge yellow-cards">
                        <el-icon><Warning /></el-icon>
                        {{ getPlayerCards(player.name, '黄牌') }}黄
                      </span>
                      <span class="stat-badge red-cards">
                        <el-icon><CircleClose /></el-icon>
                        {{ getPlayerCards(player.name, '红牌') }}红
                      </span>
                    </div>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button size="small" type="primary" @click="$emit('edit-player', player)">编辑</el-button>
                  <el-button size="small" type="danger" @click="$emit('delete-player', player.id || player.studentId)">删除</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="filteredPlayers.length > playerPageSize">
          <el-pagination
            v-model:current-page="playerCurrentPage"
            v-model:page-size="playerPageSize"
            :page-sizes="[9, 18, 36]"
            :total="filteredPlayers.length"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-card>
    </el-tab-pane>

    <!-- 球队管理 -->
    <el-tab-pane label="球队管理" name="teams">
      <el-card class="manage-card">
        <template #header>
          <div class="card-header">
            <span>球队管理</span>
            <div class="header-stats">
              共 {{ filteredTeams.length }} 支球队
            </div>
          </div>
        </template>

        <!-- 搜索区域 -->
        <div class="search-section">
          <el-row :gutter="15">
            <el-col :span="8">
              <el-input
                v-model="teamSearchKeyword"
                placeholder="搜索球队名称"
                @input="handleTeamSearch"
                clearable
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select :model-value="manageMatchType" placeholder="请选择比赛类型" @update:model-value="$emit('filter-change', $event)" style="width: 100%;">
                <el-option label="全部" value=""></el-option>
                <el-option label="冠军杯" value="champions-cup"></el-option>
                <el-option label="巾帼杯" value="womens-cup"></el-option>
                <el-option label="八人制比赛" value="eight-a-side"></el-option>
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="teamPlayerCountFilter" placeholder="球员数量" clearable style="width: 100%;">
                <el-option label="1-5人" value="1-5"></el-option>
                <el-option label="6-10人" value="6-10"></el-option>
                <el-option label="11人以上" value="11+"></el-option>
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">
                刷新
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 球队卡片 -->
        <div class="cards-container">
          <div v-if="paginatedTeams.length === 0" class="no-data">
            <el-empty description="暂无球队数据" />
          </div>
          <el-row :gutter="20" v-else>
            <el-col :span="12" v-for="team in paginatedTeams" :key="team.id || team.teamId">
              <el-card shadow="hover" class="team-card">
                <div class="team-info">
                  <div class="team-header">
                    <div class="team-name">{{ team.teamName || team.name || '未知球队' }}</div>
                    <div class="team-type">
                      <el-tag :type="getMatchTypeTagType(team.matchType || team.type)">
                        {{ getMatchTypeLabel(team.matchType || team.type) }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="team-stats">
                    <div class="stat-item">
                      <el-icon><User /></el-icon>
                      <span>{{ (team.players && team.players.length) || 0 }} 名球员</span>
                    </div>
                  </div>
                  <div class="team-players">
                    <div class="players-header">球员列表:</div>
                    <div class="players-list" v-if="team.players && team.players.length > 0">
                      <el-tag 
                        v-for="player in team.players.slice(0, 8)" 
                        :key="player.studentId || player.id" 
                        size="small" 
                        class="player-tag"
                      >
                        {{ player.name || '未知' }}({{ player.number || player.jerseyNumber || '?' }})
                      </el-tag>
                      <el-tag
                        v-if="team.players.length > 8"
                        type="info"
                        size="small"
                        class="more-tag"
                      >
                        +{{ team.players.length - 8 }}
                      </el-tag>
                    </div>
                    <span v-else class="no-players">暂无球员</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button size="small" type="primary" @click="$emit('edit-team', team)">编辑</el-button>
                  <el-button size="small" type="danger" @click="$emit('delete-team', team.id || team.teamId)">删除</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="filteredTeams.length > teamPageSize">
          <el-pagination
            v-model:current-page="teamCurrentPage"
            v-model:page-size="teamPageSize"
            :page-sizes="[6, 12, 24]"
            :total="filteredTeams.length"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-card>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, watch } from 'vue'
import { 
  Refresh, 
  Search, 
  Calendar, 
  LocationFilled, 
  Trophy, 
  User, 
  Clock, 
  CreditCard, 
  Tickets, 
  Football, 
  Warning, 
  CircleClose,
  Collection
} from '@element-plus/icons-vue'

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

// 搜索关键词
const matchSearchKeyword = ref('')
const eventSearchKeyword = ref('')
const playerSearchKeyword = ref('')
const teamSearchKeyword = ref('')

// 过滤器
const matchStatusFilter = ref('')
const eventTypeFilter = ref('')
const playerTeamFilter = ref('')
const teamPlayerCountFilter = ref('')

// 分页数据
const matchCurrentPage = ref(1)
const matchPageSize = ref(9)
const eventCurrentPage = ref(1)
const eventPageSize = ref(12)
const playerCurrentPage = ref(1)
const playerPageSize = ref(9)
const teamCurrentPage = ref(1)
const teamPageSize = ref(6)

// 搜索定时器
let searchTimer = null

// 过滤后的数据
const filteredMatches = computed(() => {
  let filtered = props.manageMatchType ? 
    props.matches.filter(match => match && (match.matchType === props.manageMatchType || match.type === props.manageMatchType)) : 
    props.matches.filter(match => match != null)

  if (matchSearchKeyword.value.trim()) {
    const keyword = matchSearchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(match => 
      (match.matchName && match.matchName.toLowerCase().includes(keyword)) ||
      (match.name && match.name.toLowerCase().includes(keyword)) ||
      (match.team1 && match.team1.toLowerCase().includes(keyword)) ||
      (match.team2 && match.team2.toLowerCase().includes(keyword)) ||
      (match.homeTeam && match.homeTeam.toLowerCase().includes(keyword)) ||
      (match.awayTeam && match.awayTeam.toLowerCase().includes(keyword))
    )
  }

  if (matchStatusFilter.value) {
    filtered = filtered.filter(match => match.status === matchStatusFilter.value)
  }

  return filtered
})

const filteredEvents = computed(() => {
  let filtered = props.manageMatchType ? 
    props.events.filter(event => event && (event.matchType === props.manageMatchType || event.type === props.manageMatchType)) : 
    props.events.filter(event => event != null)

  if (eventSearchKeyword.value.trim()) {
    const keyword = eventSearchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(event => 
      (event.matchName && event.matchName.toLowerCase().includes(keyword)) ||
      (event.match && event.match.toLowerCase().includes(keyword)) ||
      (event.playerName && event.playerName.toLowerCase().includes(keyword)) ||
      (event.player && event.player.toLowerCase().includes(keyword))
    )
  }

  if (eventTypeFilter.value) {
    filtered = filtered.filter(event => 
      event.eventType === eventTypeFilter.value || event.type === eventTypeFilter.value
    )
  }

  return filtered
})

const filteredPlayers = computed(() => {
  let filtered = props.manageMatchType ? 
    props.players.filter(player => player && (player.matchType === props.manageMatchType || player.type === props.manageMatchType)) : 
    props.players.filter(player => player != null)

  if (playerSearchKeyword.value.trim()) {
    const keyword = playerSearchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(player => 
      (player.name && player.name.toLowerCase().includes(keyword)) ||
      (player.studentId && player.studentId.toString().toLowerCase().includes(keyword)) ||
      (player.id && player.id.toString().toLowerCase().includes(keyword))
    )
  }

  if (playerTeamFilter.value) {
    filtered = filtered.filter(player => 
      player.teamName === playerTeamFilter.value || player.team === playerTeamFilter.value
    )
  }

  return filtered
})

const filteredTeams = computed(() => {
  let filtered = props.manageMatchType ? 
    props.teams.filter(team => team && (team.matchType === props.manageMatchType || team.type === props.manageMatchType)) : 
    props.teams.filter(team => team != null)

  if (teamSearchKeyword.value.trim()) {
    const keyword = teamSearchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(team => 
      (team.teamName && team.teamName.toLowerCase().includes(keyword)) ||
      (team.name && team.name.toLowerCase().includes(keyword))
    )
  }

  if (teamPlayerCountFilter.value) {
    filtered = filtered.filter(team => {
      const count = (team.players && team.players.length) || 0
      switch (teamPlayerCountFilter.value) {
        case '1-5':
          return count >= 1 && count <= 5
        case '6-10':
          return count >= 6 && count <= 10
        case '11+':
          return count >= 11
        default:
          return true
      }
    })
  }

  return filtered
})

// 分页后的数据
const paginatedMatches = computed(() => {
  const start = (matchCurrentPage.value - 1) * matchPageSize.value
  const end = start + matchPageSize.value
  return filteredMatches.value.slice(start, end)
})

const paginatedEvents = computed(() => {
  const start = (eventCurrentPage.value - 1) * eventPageSize.value
  const end = start + eventPageSize.value
  return filteredEvents.value.slice(start, end)
})

const paginatedPlayers = computed(() => {
  const start = (playerCurrentPage.value - 1) * playerPageSize.value
  const end = start + playerPageSize.value
  return filteredPlayers.value.slice(start, end)
})

const paginatedTeams = computed(() => {
  const start = (teamCurrentPage.value - 1) * teamPageSize.value
  const end = start + teamPageSize.value
  return filteredTeams.value.slice(start, end)
})

// 显示数据（保持原有逻辑）
const displayTeams = computed(() => filteredTeams.value)
const displayMatches = computed(() => filteredMatches.value)
const displayEvents = computed(() => filteredEvents.value)
const displayPlayers = computed(() => filteredPlayers.value)

// 球员队伍选项
const playerTeamOptions = computed(() => {
  const teams = new Set()
  props.players.forEach(player => {
    if (player && (player.teamName || player.team)) {
      teams.add(player.teamName || player.team)
    }
  })
  return Array.from(teams).sort()
})

// 方法
const getMatchTypeLabel = (type) => {
  const labels = {
    'champions-cup': '冠军杯',
    'womens-cup': '巾帼杯',
    'eight-a-side': '八人制比赛'
  }
  return labels[type] || type || '未知'
}

const getEventTypeLabel = (type) => {
  const labels = {
    '进球': '进球',
    '红牌': '红牌', 
    '黄牌': '黄牌',
    '乌龙球': '乌龙球',
    'goal': '进球',
    'yellow_card': '黄牌',
    'red_card': '红牌',
    'own_goal': '乌龙球'
  }
  return labels[type] || type || '未知'
}

const formatDate = (date) => {
  if (!date) return '未定'
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
      event && (event.playerName === playerName || event.player === playerName) && 
      (event.eventType === '进球' || event.eventType === 'goal' || event.type === '进球' || event.type === 'goal')
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
      event && (event.playerName === playerName || event.player === playerName) && 
      (event.eventType === cardType || event.type === cardType)
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
  return labels[status] || status || '未开始'
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

// 获取事件标签类型
const getEventTagType = (eventType) => {
  switch (eventType) {
    case '进球':
    case 'goal':
      return 'success'
    case '黄牌':
    case 'yellow_card':
      return 'warning'
    case '红牌':
    case 'red_card':
      return 'danger'
    case '乌龙球':
    case 'own_goal':
      return 'info'
    default:
      return 'info'
  }
}

// 获取比赛类型标签类型
const getMatchTypeTagType = (matchType) => {
  switch (matchType) {
    case 'champions-cup':
      return 'primary'
    case 'womens-cup':
      return 'success'
    case 'eight-a-side':
      return 'warning'
    default:
      return 'info'
  }
}

// 搜索处理函数
const handleSearch = (keyword, type) => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  
  searchTimer = setTimeout(() => {
    // 搜索时重置到第一页
    switch (type) {
      case 'match':
        matchCurrentPage.value = 1
        break
      case 'event':
        eventCurrentPage.value = 1
        break
      case 'player':
        playerCurrentPage.value = 1
        break
      case 'team':
        teamCurrentPage.value = 1
        break
    }
  }, 300)
}

const handleMatchSearch = () => handleSearch(matchSearchKeyword.value, 'match')
const handleEventSearch = () => handleSearch(eventSearchKeyword.value, 'event')
const handlePlayerSearch = () => handleSearch(playerSearchKeyword.value, 'player')
const handleTeamSearch = () => handleSearch(teamSearchKeyword.value, 'team')

// 监听过滤器变化
watch([matchStatusFilter, eventTypeFilter, playerTeamFilter, teamPlayerCountFilter], () => {
  // 过滤器变化时重置到第一页
  matchCurrentPage.value = 1
  eventCurrentPage.value = 1
  playerCurrentPage.value = 1
  teamCurrentPage.value = 1
})
</script>

<style scoped>
.manage-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-stats {
  color: #909399;
  font-size: 14px;
}

.search-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-input {
  width: 100%;
}

.cards-container {
  min-height: 400px;
}

.match-card, .event-card, .player-card, .team-card {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  min-height: 200px;
}

.match-card:hover, .event-card:hover, .player-card:hover, .team-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.match-info {
  padding: 10px 0;
}

.match-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}

.team {
  font-weight: 500;
  color: #409eff;
}

.vs {
  color: #909399;
  font-weight: bold;
}

.match-score {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 15px;
}

.match-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #606266;
}

.match-status {
  text-align: center;
  margin-bottom: 10px;
}

.event-card {
  min-height: 180px;
}

.event-info {
  padding: 10px 0;
}

.event-type {
  text-align: center;
  margin-bottom: 10px;
}

.event-match {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  text-align: center;
}

.event-player, .event-time, .event-match-type {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.player-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
}

.player-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #409EFF, #36A3FF);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 24px;
}

.player-details {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.player-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 10px;
}

.player-stats {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.stat-badge.goals {
  background-color: #e8f5e8;
  color: #67c23a;
}

.stat-badge.yellow-cards {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-badge.red-cards {
  background-color: #fef0f0;
  color: #f56c6c;
}

.team-info {
  padding: 10px 0;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.team-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.team-stats {
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #606266;
}

.team-players {
  margin-bottom: 15px;
}

.players-header {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.players-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.player-tag {
  font-size: 11px;
  margin: 0;
}

.more-tag {
  font-size: 11px;
  cursor: pointer;
}

.no-players {
  color: #c0c4cc;
  font-style: italic;
  font-size: 12px;
}

.card-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}
</style>
