<template>
  <div class="match-detail">
    <PanelSkeleton v-if="loading" height="420px" />
    <ErrorBanner v-else-if="error" :error="error" @retry="retry" />
    <template v-else>
      <MatchBasicInfo :match="match" :status-class="getMatchStatusClass()" :status-text="getMatchStatusText" @back="goBack" />
      <MatchStatsOverview :match="match" />
      <TeamComparison :match="match" />
      <PlayerPerformances
        :match="match"
        :players="filteredPlayers"
        :selected-team="selectedTeam"
        :current-page="currentPage"
        :page-size="pageSize"
        @update:selected-team="val => selectedTeam = val"
        @update:current-page="val => currentPage = val"
        @update:page-size="val => pageSize = val"
        @view-player="viewPlayerHistory"
      />
      <MatchEventsTimeline :events="events" />
    </template>
  </div>
</template>

<script setup>
/*
 * 重构说明:
 * - 大文件拆分为独立子组件: MatchBasicInfo / MatchStatsOverview / TeamComparison / PlayerPerformances / MatchEventsTimeline
 * - 样式抽离至 src/styles/match-detail.css，减少重复与提升复用性
 * - 保留 useMatchDetailPage 组合式管理状态与分页/过滤逻辑
 */
import { onMounted } from 'vue'
import PanelSkeleton from '@/components/common/PanelSkeleton.vue'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import MatchBasicInfo from '@/components/match/MatchBasicInfo.vue'
import MatchStatsOverview from '@/components/match/MatchStatsOverview.vue'
import TeamComparison from '@/components/match/TeamComparison.vue'
import PlayerPerformances from '@/components/match/PlayerPerformances.vue'
import MatchEventsTimeline from '@/components/match/MatchEventsTimeline.vue'
import { useMatchDetailPage } from '@/composables/domain/match'
import '@/assets/styles/match-detail.css'

const {
  match, events, loading, error,
  selectedTeam, currentPage, pageSize,
  filteredPlayers,
  init, retry, viewPlayerHistory,
  getMatchStatusClass, getMatchStatusText, goBack
} = useMatchDetailPage()

// 分页/筛选的具体处理逻辑已在组合式中，由子组件通过 update:* 事件驱动，这里无需额外包装函数

onMounted(init)

defineExpose({ retry, viewPlayerHistory })
</script>

<!-- 样式集中管理: src/styles/match-detail.css -->