<template>
  <div class="data-input-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h2 class="page-title">
            <el-icon class="title-icon"><EditPen /></el-icon>
            信息录入管理
          </h2>
          <p class="page-description">请先选择比赛类型，然后选择要录入的信息类型进行操作</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" class="refresh-button" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button text @click="scrollToMatchTypeSelection">
            <el-icon><ArrowUp /></el-icon>
            回到顶部
          </el-button>
        </div>
      </div>
    </div>

    <!-- 比赛类型选择与统计 (拆分组件) -->
    <MatchTypeSelector
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
        />
      </template>
    </MatchTypeSelector>

    <!-- 录入类型选择 -->
    <div v-if="currentMatchType && !selectedInputType" class="input-type-selection" ref="typeSelectionContainer">
      <InputTypeCards
        v-model="selectedInputType"
        :team-count="filteredTeams.length"
        :match-count="filteredMatches.length"
        :event-count="getEventCount()"
        @select="selectInputType"
      />
    </div>

    <!-- 录入表单区域 -->
    <div v-if="selectedInputType" class="input-form-container" ref="inputFormContainer">
      <InputFormsWrapper
        :type="selectedInputType"
        :match-type="currentMatchType"
        :teams="filteredTeams"
        :matches="filteredMatches"
        @back="goBackToSelection"
        @team-submit="handleTeamSubmit"
        @schedule-submit="handleScheduleSubmit"
        @event-submit="handleEventSubmit"
      />
    </div>

    <!-- 空状态提示 -->
    <div v-if="!currentMatchType" class="empty-state">
      <el-empty
        description="请先选择比赛类型开始录入"
        :image-size="160"
      >
        <template #image>
          <div class="empty-icon">
            <el-icon size="160" color="#d1d5db"><Box /></el-icon>
          </div>
        </template>
      </el-empty>
    </div>
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
import { 
  EditPen, 
  Box,
  Refresh,
  ArrowUp
} from '@element-plus/icons-vue'
// 全局抽离样式在 input-management.css 中引入（在 main.js 全局载入或此组件局部按需载入）

// props & emits
const props = defineProps({
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] }
})
const emit = defineEmits(['team-submit', 'schedule-submit', 'event-submit', 'refresh-data'])

// state
const matchTypeForm = reactive({ matchType: '' })
const currentMatchType = ref('')
const selectedInputType = ref('')

// refs (仅需要仍在父级中的容器)
const typeSelectionContainer = ref(null)
const inputFormContainer = ref(null)

// computed
const filteredTeams = computed(() => props.teams.filter(t => t.matchType === currentMatchType.value))
const filteredMatches = computed(() => props.matches.filter(m => m.matchType === currentMatchType.value))

// match type meta & scroll helpers
const { getMatchTypeLabel: getMetaLabel, getMatchTypeTagType, createReactiveStats } = useMatchTypeMeta()
const { scrollToBottom, scrollToTypeSelection, scrollToTypeSelectionAfterMatchType, scrollToMatchTypeSelection } =
  useScrollHelpers({ offsets: { typeSelection: 120, matchType: 100 } })
const getMatchTypeLabel = (type) => type ? getMetaLabel(type) : getMetaLabel(currentMatchType.value)
const statsRef = createReactiveStats(currentMatchType, { teams: props.teams, matches: props.matches, events: props.events })
const getEventCount = () => statsRef.value.events

// interactions
const handleMatchTypeChange = (val) => {
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

<style scoped>
.data-input-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 0 100px 0; /* 增加底部内边距 */
}

/* 页面头部样式 */
.page-header {
  margin-bottom: 32px;
  padding: 32px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  min-height: 80px;
}

.header-main {
  flex: 1;
  min-width: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  align-items: flex-start;
  padding-top: 8px;
}

.refresh-button {
  min-width: 120px;
  white-space: nowrap;
  font-weight: 600;
}

/* 步骤指示器 */
.steps-container {
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* 比赛类型选择卡片 */
.match-type-card {
  margin-bottom: 32px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  scroll-margin-top: 100px; /* 添加滚动偏移 */
}

.match-type-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.card-title .el-icon {
  margin-right: 10px;
  color: #f59e0b;
  font-size: 20px;
}

.current-type-tag {
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}

.header-refresh-btn {
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.header-refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.match-type-content {
  padding: 8px 0;
}

/* 类型选择器样式 */
.type-selector-wrapper {
  padding: 16px 0;
}

/* 下拉框样式优化 */
:deep(.type-selector .el-select__wrapper) {
  min-height: 48px;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.type-selector .el-select__wrapper:hover) {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

:deep(.type-selector .el-select__wrapper.is-focused) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 选择器选中值显示样式 */
:deep(.type-selector .el-select__selected-item) {
  font-weight: 500;
  color: #1f2937;
}

/* 下拉选项样式 */
.option-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
  width: 100%;
}

.option-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.option-info {
  flex: 1;
  min-width: 0;
}

.option-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
  line-height: 1.2;
}

.option-desc {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
  line-height: 1.2;
}

/* 下拉菜单样式 */
:global(.match-type-dropdown .el-select-dropdown__item) {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.2s ease;
  min-height: 48px;
  display: flex;
  align-items: center;
}

:global(.match-type-dropdown .el-select-dropdown__item:hover) {
  background: rgba(59, 130, 246, 0.05);
}

:global(.match-type-dropdown .el-select-dropdown__item.is-selected) {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  font-weight: 600;
}

/* 信息统计区域 */
.match-type-info {
  padding: 16px 0;
}

.info-header {
  margin-bottom: 16px;
}

.info-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.no-match-type {
  padding: 40px;
  text-align: center;
}

.empty-illustration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-icon {
  font-size: 48px;
  color: #f59e0b;
}

.empty-text {
  color: #6b7280;
  font-size: 16px;
}

/* 录入类型选择 */
.input-type-selection {
  margin-bottom: 32px;
  scroll-margin-top: 120px; /* 添加滚动偏移 */
  position: relative;
}

.selection-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
}

.type-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 8px 0;
}

/* 信息录入区域 */
.input-form-container {
  margin-bottom: 80px; /* 增加底部边距 */
  scroll-margin-top: 100px; /* 为现代浏览器提供滚动偏移 */
}

/* 为页面滚动到底部时添加一个提示效果 */
.input-form-container::after {
  content: '';
  display: block;
  height: 20px;
  background: linear-gradient(to bottom, transparent, rgba(59, 130, 246, 0.05));
  border-radius: 0 0 16px 16px;
  margin-top: 20px;
}

/* 优化滚动体验 */
/* 响应式滚动优化 */
@media (max-width: 768px) {
  .input-form-container {
    scroll-margin-top: 100px; /* 移动端减少一些偏移 */
  }
  
  /* 移动端滚动偏移量调整 */
  .form-card {
    margin-top: 20px;
  }
}

@media (max-width: 576px) {
  .input-form-container {
    scroll-margin-top: 80px; /* 小屏幕进一步减少偏移 */
  }
}

/* 增强点击反馈 */
.type-card:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
