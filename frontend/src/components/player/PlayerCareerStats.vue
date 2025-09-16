<template>
  <el-card class="player-career-stats">
    <template #header><span>球员职业生涯数据</span></template>
    <el-row :gutter="20">
      <el-col :span="8">
        <div class="stat-item stat-card stat-card--goals">
          <el-icon style="color:#fff;font-size:40px;"><Finished /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ player.totalGoals }}</div>
            <div class="stat-label">总进球数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item stat-card stat-card--yellow">
          <el-icon style="color:#fff;font-size:40px;"><Warning /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ player.totalYellowCards }}</div>
            <div class="stat-label">黄牌数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-item stat-card stat-card--red">
          <el-icon style="color:#fff;font-size:40px;"><CircleClose /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ player.totalRedCards }}</div>
            <div class="stat-label">红牌数</div>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { Finished, Warning, CircleClose } from '@element-plus/icons-vue'
defineProps({ player: { type:Object, required:true } })
</script>