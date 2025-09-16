<template>
  <el-card class="player-team-history" v-if="teamHistories?.length">
    <template #header><span>球员队伍历史</span></template>
    <el-timeline>
      <el-timeline-item
        v-for="(th, idx) in teamHistories"
        :key="idx"
        :timestamp="th.season_name || '未知赛季'"
        placement="top"
      >
        <el-card class="team-history-card">
          <div class="team-info-row">
            <div class="team-detail">
              <h4>{{ th.team_name || '未知队伍' }}</h4>
              <p class="team-meta">
                <span class="meta-badge tournament">{{ th.tournament_name || '未知赛事' }}</span>
                <span class="meta-badge number" v-if="th.player_number">球衣号码: {{ th.player_number }}</span>
                <span class="meta-badge match-type">{{ getMatchTypeText(th.matchType) }}</span>
              </p>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>
<script setup>
import { getMatchTypeText } from '@/constants/matchTypes'
defineProps({ teamHistories: { type:Array, default:()=>[] } })
</script>