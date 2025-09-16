<template>
  <div class="competition-history">
    <PanelSkeleton v-if="loading" height="400px" />
    <ErrorBanner v-else-if="error" :error="error" @retry="handleRetry" />
    <template v-else>
      <TournamentBasicInfo :competition="competition" @back="goToHomePage" />
      <TournamentHistoryStats :competition="competition" />
      <TournamentSeasonsRecords
        :records="competition.records"
        :leaderboards="leaderboards"
        v-model:active-season="activeSeason"
        @ensure-season="ensureSeasonComputed"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTournamentHistory } from '@/composables/domain/tournament'
import { useSeasonLeaderboards } from '@/composables/domain/season'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import PanelSkeleton from '@/components/common/PanelSkeleton.vue'
import TournamentBasicInfo from '@/components/tournament/TournamentBasicInfo.vue'
import TournamentHistoryStats from '@/components/tournament/TournamentHistoryStats.vue'
import TournamentSeasonsRecords from '@/components/tournament/TournamentSeasonsRecords.vue'
import '@/styles/tournament-history.css'

const route = useRoute()
const router = useRouter()
const activeSeason = ref(null)
const { competition, loading, error, load, retry } = useTournamentHistory()
const leaderboards = reactive({})

onMounted(async () => {
  const name = route.params.tournamentName
  if(!name){
    ElMessage.error('缺少赛事名称参数')
    return
  }
  await load(name)
  if(error.value){
    ElMessage.error(error.value.message || '加载失败')
  }else{
    ElMessage.success('赛事数据加载成功')
  }
})

function ensureSeasonComputed(season){
  if(!season || leaderboards[season.id]) return
  const seasonRef = ref(season)
  const { topScorers, topCards } = useSeasonLeaderboards(seasonRef)
  leaderboards[season.id] = { topScorers, topCards }
}

function handleRetry(){ retry() }
function goToHomePage(){ router.push('/home') }
</script>

<!-- 样式集中管理: src/styles/tournament-history.css -->