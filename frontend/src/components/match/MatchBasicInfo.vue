<template>
  <el-card class="match-basic-info">
    <div class="match-header">
      <div class="back-button-container">
        <el-button type="primary" :icon="ArrowLeft" plain @click="$emit('back')" class="back-button">返回</el-button>
      </div>
      <div class="status-container">
        <span class="match-status" :class="statusClass">{{ statusText }}</span>
      </div>
      <h1 class="match-title">{{ match?.home_team_name || '主队' }} VS {{ match?.away_team_name || '客队' }}</h1>
      <div class="match-meta">
        <span class="meta-item"><el-icon><Calendar /></el-icon>比赛时间: {{ match?.match_date || '待定' }}</span>
        <span class="meta-item"><el-icon><Trophy /></el-icon>赛事: {{ match?.tournament_name || '-' }}</span>
        <span class="meta-item"><el-icon><Location /></el-icon>赛季: {{ match?.season_name || '未知赛季' }}</span>
      </div>
      <div class="match-score">
        <span class="score">{{ match?.home_score || 0 }} : {{ match?.away_score || 0 }}</span>
      </div>
    </div>
  </el-card>
</template>
<script setup>
import { ArrowLeft, Calendar, Trophy, Location } from '@element-plus/icons-vue'
defineEmits(['back'])
defineProps({
  match: { 
    type: [Object, null], 
    required: false,
    default: () => null,
    validator: (value) => {
      // 允许null或包含必要字段的对象
      return value === null || (typeof value === 'object' && value !== null)
    }
  },
  statusClass: { type: String, required: false, default: 'status-completed' },
  statusText: { type: String, required: false, default: '未知状态' }
})
</script>
