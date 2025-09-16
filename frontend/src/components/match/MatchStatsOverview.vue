<template>
  <el-card class="match-stats">
    <template #header><span>比赛统计数据</span></template>
    <el-row :gutter="20">
      <el-col :span="5">
        <div class="stat-item" style="background-color:#1e88e5;color:#fff;">
          <el-icon style="color:#fff;font-size:40px;"><Finished /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match.totalGoals }}</div><div class="stat-label">总进球数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item" style="background-color:#ff9800;color:#fff;">
          <el-icon style="color:#fff;font-size:40px;"><Football /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match.totalOwnGoals }}</div><div class="stat-label">乌龙球数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item" style="background-color:#f39c12;color:#fff;">
          <el-icon style="color:#fff;font-size:40px;"><Warning /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match.totalYellowCards }}</div><div class="stat-label">黄牌数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item" style="background-color:#e74c3c;color:#fff;">
          <el-icon style="color:#fff;font-size:40px;"><CircleClose /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match.totalRedCards }}</div><div class="stat-label">红牌数</div></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-item" style="background-color:#27ae60;color:#fff;">
          <el-icon style="color:#fff;font-size:40px;"><User /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match.totalPlayers }}</div><div class="stat-label">参赛球员</div></div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { Finished, Football, Warning, CircleClose, User } from '@element-plus/icons-vue'
defineProps({ match: { type: Object, required: true } })
</script>
