<template>
  <div class="team-info">
    <PanelSkeleton v-if="loading" height="400px" />
    <ErrorBanner v-else-if="error" :error="error" @retry="handleRetry" />
    <template v-else>
      <TeamBasicInfo :team="team" @back="goToHomePage" />
      <TeamKeyStats :team="team" :refreshing="refreshing" @refresh="refreshTeamData" />
      <TeamSeasonRecords
        :records="records"
        v-model:active-season="activeSeason"
        @view-player="navigateToPlayer"
      />
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PanelSkeleton from '@/components/common/PanelSkeleton.vue'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import TeamBasicInfo from '@/components/team/TeamBasicInfo.vue'
import TeamKeyStats from '@/components/team/TeamKeyStats.vue'
import TeamSeasonRecords from '@/components/team/TeamSeasonRecords.vue'
import { useTeamHistoryPage } from '@/composables/domain/team'
import '@/styles/team-history.css'

const { team, records, loading, error, activeSeason, refreshing, refreshTeamData, navigateToPlayer, goToHomePage, init, handleRetry } = useTeamHistoryPage()

onMounted(init)

defineExpose({ refreshTeamData, navigateToPlayer })
</script>

<!-- 样式集中管理: src/styles/team-history.css -->