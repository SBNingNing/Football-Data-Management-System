<template>
  <el-card class="team-stats float-shadow" v-if="team">
    <template #header>
      <div class="clearfix">
        <span>球队关键统计数据</span>
        <div style="float:right; display:flex; gap:8px;">
          <el-button type="primary" size="small" @click="$emit('refresh', false)" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button type="success" size="small" plain @click="$emit('refresh', true)" :loading="refreshing">强制刷新</el-button>
        </div>
      </div>
    </template>
    <el-row :gutter="20">
      <el-col :span="8">
        <div class="stat-item-common stat-goals">
          <el-icon><Finished /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalGoals }}</div>
            <div class="stat-label">总进球数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item-common stat-conceded">
          <el-icon><Warning /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalGoalsConceded }}</div>
            <div class="stat-label">总失球数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item-common stat-difference">
          <el-icon><Top /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalGoalDifference }}</div>
            <div class="stat-label">总净胜球</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <div class="stat-item-common stat-yellow">
          <el-icon><Warning /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalYellowCards }}</div>
            <div class="stat-label">总黄牌数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item-common stat-red">
          <el-icon><CircleClose /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalRedCards }}</div>
            <div class="stat-label">总红牌数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item-common stat-rank">
          <el-icon><Trophy /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.bestRank || '暂无' }}</div>
            <div class="stat-label">历史最好排名</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="stat-item-common stat-points">
          <el-icon><Star /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ team.totalPoints }}</div>
            <div class="stat-label">总积分</div>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { Finished, Warning, CircleClose, Top, Trophy, Star, Refresh } from '@element-plus/icons-vue'
import '@/assets/styles/team-stats.css'

defineEmits(['refresh'])
defineProps({
  team: { type: Object, required: true },
  refreshing: { type: Boolean, default: false }
})
</script>