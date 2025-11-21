<template>
  <el-tabs v-model="activeTab" type="card">
    <el-tab-pane label="比赛管理" name="matches">
      <EntityTab
        title="比赛管理"
        unit-label="场"
        total-label-unit="场比赛"
        empty-description="暂无比赛数据"
        :items="paginatedMatches"
        :total="filteredMatches.length"
        :card-span="8"
        :page-sizes="[9,18,36]"
        v-model:current-page="matchCurrentPage"
        v-model:page-size="matchPageSize"
      >
        <template #search>
          <SearchSection>
            <el-col :span="8">
              <el-input v-model="matchSearchKeyword" placeholder="搜索比赛名称、球队名称" @input="handleMatchSearch" clearable class="search-input">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select 
                v-model="manageMatchType" 
                placeholder="请选择比赛类型" 
                style="width: 100%;"
              >
                <el-option label="全部" value="" />
                <el-option v-for="opt in competitionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-col>
              <el-col :span="5">
                <el-select 
                  v-model="matchStatusFilter" 
                  placeholder="选择比赛状态" 
                  clearable
                >
                  <el-option label="未开始" value="P" />
                  <el-option label="已完赛" value="F" />
                </el-select>
              </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">刷新</el-button>
            </el-col>
          </SearchSection>
        </template>
        <template #card="{ entity: match }">
          <el-card shadow="hover" class="match-card">
            <div class="match-info">
              <div class="match-title">{{ match.matchName || match.name || '未命名比赛' }}</div>
              <div class="match-teams">
                <span class="team">{{ match.team1 || match.homeTeam || '主队' }}</span>
                <span class="vs">VS</span>
                <span class="team">{{ match.team2 || match.awayTeam || '客队' }}</span>
              </div>
              <div class="match-score">{{ match.home_score || match.homeScore || 0 }} : {{ match.away_score || match.awayScore || 0 }}</div>
              <div class="match-meta">
                <div class="meta-item"><el-icon><Calendar /></el-icon><span>{{ formatDate(match.date || match.matchDate) }}</span></div>
                <div class="meta-item"><el-icon><LocationFilled /></el-icon><span>{{ match.location || match.venue || '未定' }}</span></div>
                <div class="meta-item"><el-icon><Trophy /></el-icon><span>{{ getMatchTypeLabel(match.matchType || match.type) }}</span></div>
              </div>
              <div class="match-status"><el-tag :type="getStatusTagType(match.status)">{{ getStatusLabel(match.status) }}</el-tag></div>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click="$emit('edit-match', match)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-match', match.id || match.matchId)">删除</el-button>
              <el-button v-if="['P', 'pending', '待开始', '未开始'].includes(match.status)" size="small" type="success" @click="$emit('complete-match', match.id || match.matchId)">完赛</el-button>
            </div>
          </el-card>
        </template>
      </EntityTab>
    </el-tab-pane>

    <el-tab-pane label="事件管理" name="events">
      <EntityTab
        title="事件管理"
        unit-label="个"
        total-label-unit="个事件"
        empty-description="暂无事件数据"
        :items="paginatedEvents"
        :total="filteredEvents.length"
        :card-span="6"
        :page-sizes="[12,24,48]"
        v-model:current-page="eventCurrentPage"
        v-model:page-size="eventPageSize"
      >
        <template #search>
          <SearchSection>
            <el-col :span="8">
              <el-input v-model="eventSearchKeyword" placeholder="搜索比赛名称、球员姓名" @input="handleEventSearch" clearable class="search-input">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select 
                v-model="manageMatchType" 
                placeholder="请选择赛事类型" 
                style="width: 100%;"
              >
                <el-option label="全部" value="" />
                <el-option v-for="opt in competitionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="eventTypeFilter" placeholder="事件类型" clearable style="width: 100%;">
                <el-option label="进球" value="进球" />
                <el-option label="黄牌" value="黄牌" />
                <el-option label="红牌" value="红牌" />
                <el-option label="乌龙球" value="乌龙球" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">刷新</el-button>
            </el-col>
          </SearchSection>
        </template>
        <template #card="{ entity: event }">
          <el-card shadow="hover" class="event-card">
            <div class="event-info">
              <div class="event-type"><el-tag :type="getEventTagType(event.eventType || event.type)" size="large">{{ getEventTypeLabel(event.eventType || event.type) }}</el-tag></div>
              <div class="event-match">{{ event.matchName || event.match || '未知比赛' }}</div>
              <div class="event-player"><el-icon><User /></el-icon><span>{{ event.playerName || event.player || '未知球员' }}</span></div>
              <div class="event-time"><el-icon><Clock /></el-icon><span>{{ event.eventTime || event.time || 0 }}分钟</span></div>
              <div class="event-match-type"><el-icon><Trophy /></el-icon><span>{{ getMatchTypeLabel(event.matchType || event.type) }}</span></div>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click="$emit('edit-event', event)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-event', event.id || event.eventId)">删除</el-button>
            </div>
          </el-card>
        </template>
      </EntityTab>
    </el-tab-pane>

    <el-tab-pane label="球员管理" name="players">
      <EntityTab
        title="球员管理"
        unit-label="名"
        total-label-unit="名球员"
        empty-description="暂无球员数据"
        :items="paginatedPlayers"
        :total="filteredPlayers.length"
        :card-span="8"
        :page-sizes="[9,18,36]"
        v-model:current-page="playerCurrentPage"
        v-model:page-size="playerPageSize"
      >
        <template #search>
          <SearchSection>
            <el-col :span="8">
              <el-input v-model="playerSearchKeyword" placeholder="搜索球员姓名、学号" @input="handlePlayerSearch" clearable class="search-input">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select 
                v-model="manageMatchType" 
                placeholder="请选择比赛类型" 
                style="width: 100%;"
              >
                <el-option label="全部" value="" />
                <el-option v-for="opt in competitionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="playerTeamFilter" placeholder="所属球队" clearable style="width: 100%;">
                <el-option v-for="team in playerTeamOptions" :key="team" :label="team" :value="team" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">刷新</el-button>
            </el-col>
          </SearchSection>
        </template>
        <template #card="{ entity: player }">
          <el-card shadow="hover" class="player-card">
            <div class="player-info">
              <div class="player-avatar">
                <el-icon class="avatar-icon"><User /></el-icon>
              </div>
              <div class="player-details">
                <div class="player-name">{{ player.name || '未知球员' }}</div>
                <div class="player-meta">
                  <div class="meta-item"><el-icon><CreditCard /></el-icon><span>{{ player.studentId || player.id || '无学号' }}</span></div>
                  <div class="meta-item"><el-icon><Football /></el-icon><span>{{ player.teamName || player.team || '无球队' }}</span></div>
                  <div class="meta-item"><el-icon><Trophy /></el-icon><span>{{ getMatchTypeLabel(player.matchType || player.type) }}</span></div>
                  <div class="meta-item"><el-icon><Tickets /></el-icon><span>号码: {{ player.number || player.jerseyNumber || '?' }}</span></div>
                </div>
                <div class="player-stats">
                  <span class="stat-badge goals" v-if="getPlayerGoals(player.id) > 0">
                    <el-icon><Football /></el-icon> {{ getPlayerGoals(player.id) }}
                  </span>
                  <span class="stat-badge yellow-cards" v-if="getPlayerCards(player.id).yellow > 0">
                    <div style="width:10px;height:14px;background:#f59e0b;border-radius:2px;margin-right:2px;"></div> {{ getPlayerCards(player.id).yellow }}
                  </span>
                  <span class="stat-badge red-cards" v-if="getPlayerCards(player.id).red > 0">
                    <div style="width:10px;height:14px;background:#ef4444;border-radius:2px;margin-right:2px;"></div> {{ getPlayerCards(player.id).red }}
                  </span>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click="$emit('edit-player', player)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-player', player.id || player.playerId)">删除</el-button>
            </div>
          </el-card>
        </template>
      </EntityTab>
    </el-tab-pane>

    <el-tab-pane label="球队管理" name="teams">
      <EntityTab
        title="球队管理"
        unit-label="支"
        total-label-unit="支球队"
        empty-description="暂无球队数据"
        :items="paginatedTeams"
        :total="filteredTeams.length"
        :card-span="12"
        :page-sizes="[6,12,24]"
        v-model:current-page="teamCurrentPage"
        v-model:page-size="teamPageSize"
      >
        <template #search>
          <SearchSection>
            <el-col :span="8">
              <el-input v-model="teamSearchKeyword" placeholder="搜索球队名称" @input="handleTeamSearch" clearable class="search-input">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select 
                v-model="manageMatchType" 
                placeholder="请选择比赛类型" 
                style="width: 100%;"
              >
                <el-option label="全部" value="" />
                <el-option v-for="opt in competitionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="teamPlayerCountFilter" placeholder="球员数量" clearable style="width: 100%;">
                <el-option label="1-5人" value="1-5" />
                <el-option label="6-10人" value="6-10" />
                <el-option label="11人以上" value="11+" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="$emit('refresh')" :icon="RefreshIcon" style="width: 100%;">刷新</el-button>
            </el-col>
          </SearchSection>
        </template>
        <template #card="{ entity: team }">
          <el-card shadow="hover" class="team-card">
            <div class="team-info">
              <div class="team-header">
                <div class="team-name">{{ team.teamName || team.name || '未知球队' }}</div>
                <div class="team-type"><el-tag :type="getMatchTypeTagType(team.matchType || team.type)">{{ getMatchTypeLabel(team.matchType || team.type) }}</el-tag></div>
              </div>
              <div class="team-stats"><div class="stat-item"><el-icon><User /></el-icon><span>{{ (team.players && team.players.length) || 0 }} 名球员</span></div></div>
              <div class="team-players">
                <div class="players-header">球员列表:</div>
                <div class="players-list" v-if="team.players && team.players.length > 0">
                  <el-tag v-for="player in team.players.slice(0, 8)" :key="player.studentId || player.id" size="small" class="player-tag">{{ player.name || '未知' }}({{ player.number || player.jerseyNumber || '?' }})</el-tag>
                  <el-tag v-if="team.players.length > 8" type="info" size="small" class="more-tag">+{{ team.players.length - 8 }}</el-tag>
                </div>
                <span v-else class="no-players">暂无球员</span>
              </div>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click="$emit('edit-team', team)">编辑</el-button>
              <el-button size="small" type="danger" @click="$emit('delete-team', team.id || team.teamId)">删除</el-button>
            </div>
          </el-card>
        </template>
      </EntityTab>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import EntityTab from './data-management/EntityTab.vue'
import SearchSection from './SearchSection.vue'
import usePlayerStats from '@/composables/admin/usePlayerStats'
import useManagementFilters from '@/composables/admin/useManagementFilters'
import useManagementLabels from '@/composables/admin/useManagementLabels'
import { formatDate } from '@/utils/formatters'
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
import useCompetitions from '@/composables/admin/useCompetitions'

const RefreshIcon = Refresh

const { competitionOptions, fetchCompetitions, getCompetitionLabel } = useCompetitions()

onMounted(() => {
  fetchCompetitions()
})

const props = defineProps({
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] },
  players: { type: Array, default: () => [] },
  manageMatchType: { type: String, default: '' }
})

// 事件声明
const emit = defineEmits(['filter-change', 'refresh', 'edit-team', 'delete-team', 'edit-match', 'delete-match', 'edit-event', 'delete-event', 'edit-player', 'delete-player', 'complete-match'])

const activeTab = ref('matches')

const manageMatchType = defineModel('manageMatchType')

const {
  matchSearchKeyword, eventSearchKeyword, playerSearchKeyword, teamSearchKeyword,
  matchStatusFilter, eventTypeFilter, playerTeamFilter, teamPlayerCountFilter,
  matchCurrentPage, matchPageSize, eventCurrentPage, eventPageSize,
  playerCurrentPage, playerPageSize, teamCurrentPage, teamPageSize,
  filteredMatches, filteredEvents, filteredPlayers, filteredTeams,
  paginatedMatches, paginatedEvents, paginatedPlayers, paginatedTeams,
  handleMatchSearch, handleEventSearch, handlePlayerSearch, handleTeamSearch
} = useManagementFilters(props, () => manageMatchType.value)

// 监听筛选条件变化，触发后端筛选
watch([matchStatusFilter, manageMatchType], ([newStatus, newType]) => {
  emit('filter-change', { status: newStatus, type: newType })
})

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

// 标签与映射（抽离）
const { 
  getEventTypeLabel,
  getEventTagType,
  getMatchTypeTagType,
  getStatusTagType,
  getStatusLabel
} = useManagementLabels()

// Use dynamic label function from useCompetitions
const getMatchTypeLabel = getCompetitionLabel

// 统计逻辑抽离
const { getPlayerGoals, getPlayerCards } = usePlayerStats(computed(() => props.events))

// 事件 / 比赛类型标签类型、状态标签与文本已在 useManagementLabels 中统一

// （过滤、搜索、分页逻辑已抽离到 useManagementFilters）
</script>

<style scoped>
.card-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}
.header-stats { 
  color: var(--color-neutral-600); 
  font-size: 14px; 
}
</style>