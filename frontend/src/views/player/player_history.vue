<template>
  <div class="player-career">
    <PanelSkeleton v-if="loading" height="400px" />
    <ErrorBanner v-else-if="error" :error="error" @retry="retry" />
    <template v-else>
      <PlayerBasicInfo :player="player" @back="goToHomePage" />
      <PlayerTeamHistory :team-histories="player.teamHistories" />
      <PlayerCareerStats :player="player" />
      <PlayerSeasonsPerformance
        :player="player"
        v-model:active-season="activeSeason"
      />
    </template>
  </div>
</template>

<script setup>
/* 重构说明:
 * - 拆分为 PlayerBasicInfo / PlayerTeamHistory / PlayerCareerStats / PlayerSeasonsPerformance 子组件
 * - 样式迁移至 src/styles/player-history.css
 * - 仍保留组合式 usePlayerHistoryPage 负责数据加载与状态
 */
import { onMounted } from 'vue'
import PanelSkeleton from '@/components/common/PanelSkeleton.vue'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import PlayerBasicInfo from '@/components/player/PlayerBasicInfo.vue'
import PlayerTeamHistory from '@/components/player/PlayerTeamHistory.vue'
import PlayerCareerStats from '@/components/player/PlayerCareerStats.vue'
import PlayerSeasonsPerformance from '@/components/player/PlayerSeasonsPerformance.vue'
import { usePlayerHistoryPage } from '@/composables/domain/player'
import '@/styles/player-history.css'

const { player, loading, error, activeSeason, init, refreshPlayer, retry, goToHomePage } = usePlayerHistoryPage()
onMounted(init)
defineExpose({ refreshPlayer })
</script>

<!-- 样式集中管理: src/styles/player-history.css -->