<template>
  <div class="team-history-page">
    <div class="team-history-container">
      <PanelSkeleton v-if="loading" height="400px" />
      <ErrorBanner v-else-if="error" :error="error" @retry="handleRetry" />
      <template v-else-if="team">
        <div class="module-section basic-info-section">
          <TeamBasicInfo :team="team" @back="goToHomePage" />
        </div>
        
        <div class="module-section stats-section">
          <TeamKeyStats :team="team" :refreshing="refreshing" @refresh="refreshTeamData" />
        </div>
        
        <div class="module-section records-section">
          <TeamSeasonRecords
            :records="records"
            v-model:active-season="activeSeason"
            @view-player="navigateToPlayer"
          />
        </div>
      </template>
    </div>
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
import '@/assets/styles/team-history.css'

const { team, records, loading, error, activeSeason, refreshing, refreshTeamData, navigateToPlayer, goToHomePage, init, handleRetry } = useTeamHistoryPage()

onMounted(init)

defineExpose({ refreshTeamData, navigateToPlayer })
</script>

<!-- 样式集中管理: src/styles/team-history.css -->