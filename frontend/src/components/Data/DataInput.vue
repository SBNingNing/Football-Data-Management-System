<template>
  <div class="data-input-container">
    <!-- 页面头部（组件化） -->
    <InputHeader 
      @refresh="refreshData"
      @scroll-top="scrollToMatchTypeSelection(matchTypeSelectorRef)"
    />

    <!-- 比赛类型选择与统计 (拆分组件) -->
    <MatchTypeSelector
      ref="matchTypeSelectorRef"
      v-model="matchTypeForm.matchType"
      :get-match-type-label="getMatchTypeLabel"
      :get-match-type-tag-type="getMatchTypeTagType"
      @change="handleMatchTypeChange"
    >
      <template #stats>
        <TypeStatsPanel
          :match-type="currentMatchType"
          :team-count="filteredTeams.length"
          :match-count="filteredMatches.length"
          :event-count="getEventCount()"
          @back="goBackToSelection"
          @team-submit="handleTeamSubmit"
          @schedule-submit="handleScheduleSubmit"
          @event-submit="handleEventSubmit"
        />
      </template>
    </MatchTypeSelector>

    <!-- 录入类型选择 -->
    <section
      v-if="currentMatchType"
      ref="typeSelectionContainer"
      class="input-type-selection"
    >
      <InputTypeCards
        v-model="selectedInputType"
        :team-count="filteredTeams.length"
        :match-count="filteredMatches.length"
        :event-count="getEventCount()"
        @select="selectInputType"
      />
    </section>

    <!-- 信息录入表单区域 -->
    <section
      v-if="currentMatchType && selectedInputType"
      class="input-form-container"
    >
      <InputFormsWrapper
        :type="selectedInputType"
        :match-type="currentMatchType"
        :teams="filteredTeams"
        :matches="filteredMatches"
        @back="goBackToSelection"
        @team-submit="handleTeamSubmit"
        @schedule-submit="handleScheduleSubmit"
        @event-submit="handleEventSubmit"
        @refresh-data="refreshData"
      />
    </section>

    <!-- 空状态提示（组件化） -->
    <EmptyState v-if="!currentMatchType" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { useScrollHelpers } from '@/composables/scroll'
import { useMatchTypeMeta } from '@/composables/domain/match'
import MatchTypeSelector from './data-input/MatchTypeSelector.vue'
import TypeStatsPanel from './data-input/TypeStatsPanel.vue'
import InputTypeCards from './data-input/InputTypeCards.vue'
import InputFormsWrapper from './data-input/InputFormsWrapper.vue'
import InputHeader from './data-input/InputHeader.vue'
import EmptyState from './data-input/EmptyState.vue'
// 无需在此处引入图标组件，样式与图标在子组件各自维护
// 全局抽离样式在 input-management.css 中引入（在 main.js 全局载入或此组件局部按需载入）

// props & emits
const props = defineProps({
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] }
})

const emit = defineEmits(['team-submit', 'schedule-submit', 'event-submit', 'refresh-data'])

// reactive state
const matchTypeForm = reactive({ matchType: '' })
const currentMatchType = ref('')
const selectedInputType = ref('')
const typeSelectionContainer = ref(null)
const matchTypeSelectorRef = ref(null)

// computed
const filteredTeams = computed(() => props.teams.filter(t => t.competitionId === currentMatchType.value))
const filteredMatches = computed(() => props.matches.filter(m => m.competitionId === currentMatchType.value))

// match type meta & scroll helpers
const { getMatchTypeLabel: getMetaLabel, getMatchTypeTagType, getMatchTypeStats } = useMatchTypeMeta()
const { scrollToBottom, scrollToTypeSelection, scrollToTypeSelectionAfterMatchType, scrollToMatchTypeSelection } =
  useScrollHelpers({ offsets: { typeSelection: 120, matchType: 100 } })
const getMatchTypeLabel = (type) => type ? getMetaLabel(type) : getMetaLabel(currentMatchType.value)

// 使用 computed 确保响应式更新统计数据
const stats = computed(() => getMatchTypeStats(currentMatchType.value, { 
  teams: props.teams, 
  matches: props.matches, 
  events: props.events 
}))
const getEventCount = () => stats.value.events

// interactions
const handleMatchTypeChange = (val) => {
  console.log('[DataInput] handleMatchTypeChange:', val)
  currentMatchType.value = val
  selectedInputType.value = ''
  if (val) nextTick(() => scrollToTypeSelectionAfterMatchType(typeSelectionContainer))
}
const selectInputType = (type) => {
  selectedInputType.value = type
  nextTick(() => scrollToBottom())
}
const goBackToSelection = () => {
  selectedInputType.value = ''
  nextTick(() => scrollToTypeSelection(typeSelectionContainer))
}

// submit wrappers
const handleTeamSubmit = (teamData) => {
  emit('team-submit', { ...teamData, matchType: currentMatchType.value })
  setTimeout(goBackToSelection, 1000)
}
const handleScheduleSubmit = (scheduleData) => {
  emit('schedule-submit', { ...scheduleData, matchType: currentMatchType.value })
  setTimeout(goBackToSelection, 1000)
}
const handleEventSubmit = (eventData) => {
  emit('event-submit', { ...eventData, matchType: currentMatchType.value })
  setTimeout(goBackToSelection, 1000)
}
const refreshData = () => emit('refresh-data')
</script>

<!-- 样式已合并至全局 admin-management.css，无需局部引入 -->