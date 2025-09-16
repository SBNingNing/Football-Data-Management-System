<template>
  <el-card class="match-basic-info">
    <div class="match-header">
      <div class="back-button-container">
        <el-button type="primary" :icon="ArrowLeft" plain @click="$emit('back')" class="back-button">返回</el-button>
      </div>
      <div class="status-container">
        <span class="match-status" :class="statusClass">{{ statusText }}</span>
      </div>
      <h1 class="match-title">{{ match.homeTeam }} VS {{ match.awayTeam }}</h1>
      <div class="match-meta">
        <span class="meta-item"><el-icon><Calendar /></el-icon>比赛时间: {{ match.matchDate }}</span>
        <span class="meta-item"><el-icon><Trophy /></el-icon>赛事: {{ match.tournament }}</span>
        <span class="meta-item"><el-icon><Location /></el-icon>赛季: {{ match.season }}</span>
      </div>
      <div class="match-score">
        <span class="score">{{ match.homeScore }} : {{ match.awayScore }}</span>
      </div>
    </div>
  </el-card>
</template>
<script setup>
import { ArrowLeft, Calendar, Trophy, Location } from '@element-plus/icons-vue'
defineEmits(['back'])
defineProps({
  match: { type: Object, required: true },
  statusClass: { type: String, required: true },
  statusText: { type: String, required: true }
})
</script>
