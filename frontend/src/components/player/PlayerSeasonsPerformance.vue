<template>
  <el-card class="player-seasons" v-if="player.seasons?.length">
    <template #header><span>球员赛季表现</span></template>
    <el-collapse v-model="activeSeasonLocal">
      <el-collapse-item
        v-for="season in player.seasons"
        :key="season.season_name"
        :name="season.season_name"
      >
        <template #title>
          <div class="season-title">
            <span>{{ season.season_name }}</span>
            <span class="season-info">总进球: {{ season.total_goals }} | 黄牌: {{ season.total_yellow_cards }} | 红牌: {{ season.total_red_cards }}</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="6" v-for="meta in summaryMeta(season)" :key="meta.label">
            <div class="season-stat">
              <div class="season-label">{{ meta.label }}</div>
              <div class="season-number">{{ meta.value }}</div>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top:20px;">
          <el-col :span="24">
            <div v-for="(tournament, tKey) in season.tournaments" :key="tKey" style="margin-bottom:20px;">
              <h4>{{ tournament.tournament_name }}</h4>
              <div class="tournament-meta">
                <span class="meta-badge match-type">{{ getMatchTypeText(tournament.match_type) }}</span>
              </div>
              <div v-for="team in tournament.teams" :key="team.team_id" class="team-performance">
                <el-row :gutter="20">
                  <el-col :span="6" v-for="detail in teamMeta(team)" :key="detail.label">
                    <div class="season-stat">
                      <div class="season-label">{{ detail.label }}</div>
                      <div class="season-number">{{ detail.value }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>
  </el-card>
</template>
<script setup>
import { ref, watch } from 'vue'
import { getMatchTypeText } from '@/constants/matchTypes'
const props = defineProps({ player:{ type:Object, required:true }, activeSeason:{ type:String, default:'' } })
const emits = defineEmits(['update:activeSeason'])
const activeSeasonLocal = ref(props.activeSeason)
watch(()=>props.activeSeason, v=>{ if(v!==activeSeasonLocal.value) activeSeasonLocal.value = v })
watch(activeSeasonLocal, v=> emits('update:activeSeason', v))
function summaryMeta(season){ return [
  { label:'总进球数', value: season.total_goals },
  { label:'总黄牌数', value: season.total_yellow_cards },
  { label:'总红牌数', value: season.total_red_cards }
] }
function teamMeta(team){ return [
  { label:'球队', value: team.team_name },
  { label:'球衣号码', value: team.player_number || '-' },
  { label:'进球数', value: team.tournament_goals },
  { label:'黄牌数', value: team.tournament_yellow_cards },
  { label:'红牌数', value: team.tournament_red_cards }
] }
</script>