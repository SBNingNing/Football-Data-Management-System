<template>
  <div class="meta-input-sections">
    <div class="meta-lists">
      <el-card class="meta-card card-hover" shadow="never">
        <template #header><div class="meta-card-header">学年列表 ({{ seasons.length }})</div></template>
        <div class="meta-list" v-if="seasons.length">
          <el-tag v-for="s in seasons" :key="s.id" size="small" class="meta-tag btn-hover">{{ s.name }}</el-tag>
        </div>
        <div v-else class="meta-empty">暂无学年</div>
      </el-card>
      <el-card class="meta-card card-hover" shadow="never">
        <template #header><div class="meta-card-header">赛事列表 ({{ competitions.length }})</div></template>
        <div class="meta-list" v-if="competitions.length">
          <el-tag v-for="c in competitions" :key="c.id" size="small" type="info" class="meta-tag btn-hover">{{ c.name }}</el-tag>
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
import '@/assets/styles/meta-data-section.css'

const { seasons, competitions, reloadSeasons, reloadCompetitions, reloadAll, handleTournamentQuick } = useMetaData()

onMounted(()=>{ reloadAll() })
</script>