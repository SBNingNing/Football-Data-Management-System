<template>
  <div class="meta-input-sections">
    <div class="meta-lists">
      <el-card class="meta-card" shadow="never">
        <template #header><div class="meta-card-header">赛季列表 ({{ seasons.length }})</div></template>
        <div class="meta-list" v-if="seasons.length">
          <el-tag v-for="s in seasons" :key="s.id" size="small" class="meta-tag">{{ s.name }}</el-tag>
        </div>
        <div v-else class="meta-empty">暂无赛季</div>
      </el-card>
      <el-card class="meta-card" shadow="never">
        <template #header><div class="meta-card-header">赛事列表 ({{ competitions.length }})</div></template>
        <div class="meta-list" v-if="competitions.length">
          <el-tag v-for="c in competitions" :key="c.id" size="small" type="info" class="meta-tag">{{ c.name }}</el-tag>
        </div>
        <div v-else class="meta-empty">暂无赛事</div>
      </el-card>
    </div>
    <div class="meta-forms">
      <SeasonInput @submit="reloadSeasons" />
      <CompetitionInput @submit="reloadCompetitions" />
      <TournamentQuickInput @submit="handleTournamentQuick" />
    </div>
  </div>
</template>

<script setup>
import SeasonInput from '@/components/tournament/SeasonInput.vue'
import CompetitionInput from '@/components/tournament/CompetitionInput.vue'
import TournamentQuickInput from '@/components/tournament/TournamentQuickInput.vue'
import { useMetaData } from '@/composables/admin/useMetaData'
import { onMounted } from 'vue'

const { seasons, competitions, reloadSeasons, reloadCompetitions, reloadAll, handleTournamentQuick } = useMetaData()

onMounted(()=>{ reloadAll() })
</script>

<style scoped>
.meta-input-sections { display:flex; flex-wrap:wrap; gap:16px; margin-bottom:32px; }
.meta-lists { display:flex; gap:16px; flex:1 1 360px; min-width:320px; }
.meta-forms { flex:2 1 520px; display:flex; flex-direction:column; gap:12px; }
.meta-card { flex:1; }
.meta-card-header { font-weight:600; font-size:14px; }
.meta-list { display:flex; flex-wrap:wrap; gap:6px; }
.meta-tag { margin:0; }
.meta-empty { color:#999; font-size:12px; }
@media (max-width: 960px) {
  .meta-input-sections { flex-direction:column; }
  .meta-lists { flex-direction:column; }
  .meta-forms { width:100%; }
}
</style>