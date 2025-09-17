<template>
  <div class="competition-history">
    <PanelSkeleton v-if="loading" height="400px" />
    <ErrorBanner v-else-if="error" :error="error" @retry="handleRetry" />
    <template v-else>
      <TournamentBasicInfo :competition="competition" @back="goToHomePage" />
      <TournamentHistoryStats :competition="competition" />
      <el-card class="competition-all-matches" v-if="allMatches && allMatches.length">
        <template #header>
          <div class="clearfix"><span>全部比赛 ({{ allMatches.length }})</span></div>
        </template>
        <el-table :data="mappedMatches" style="width:100%" max-height="420">
          <el-table-column prop="matchDate" label="日期" />
          <el-table-column prop="tournament" label="赛事" />
          <el-table-column prop="season" label="赛季" />
          <el-table-column prop="homeTeam" label="主队" />
          <el-table-column prop="awayTeam" label="客队" />
          <el-table-column prop="homeScore" label="主" width="60" />
          <el-table-column prop="awayScore" label="客" width="60" />
          <el-table-column prop="totalYellowCards" label="黄牌" width="80" />
          <el-table-column prop="totalRedCards" label="红牌" width="80" />
        </el-table>
      </el-card>
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
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTournamentHistory } from '@/composables/domain/tournament'
import { useSeasonLeaderboards } from '@/composables/domain/season'
import ErrorBanner from '@/components/common/ErrorBanner.vue'
import PanelSkeleton from '@/components/common/PanelSkeleton.vue'
import TournamentBasicInfo from '@/components/tournament/TournamentBasicInfo.vue'
import TournamentHistoryStats from '@/components/tournament/TournamentHistoryStats.vue'
import TournamentSeasonsRecords from '@/components/tournament/TournamentSeasonsRecords.vue'
// tournament-history.css样式已合并到base.css中
import { toMatchViewModel } from '@/utils/mappers/matchMapper'

const route = useRoute()
const router = useRouter()
const activeSeason = ref(null)
const { competition, allMatches, loading, error, load, retry } = useTournamentHistory()
const leaderboards = reactive({})
const mappedMatches = computed(()=> (allMatches?.value || []).map(toMatchViewModel))

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