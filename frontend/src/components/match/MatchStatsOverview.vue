<template>
  <el-card class="match-stats">
    <template #header><span>比赛统计数据</span></template>
    <el-row :gutter="20">
      <el-col :span="5">
        <div class="stat-item stat-card--goals">
          <el-icon style="color:#fff;font-size:40px;"><Finished /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match?.total_goals || 0 }}</div><div class="stat-label">总进球数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item stat-card--own-goals">
          <el-icon style="color:#fff;font-size:40px;"><Football /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match?.total_own_goals || 0 }}</div><div class="stat-label">乌龙球数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item stat-card--yellow">
          <el-icon style="color:#fff;font-size:40px;"><Warning /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match?.total_yellow_cards || 0 }}</div><div class="stat-label">黄牌数</div></div>
        </div>
      </el-col>
      <el-col :span="5">
        <div class="stat-item stat-card--red">
          <el-icon style="color:#fff;font-size:40px;"><CircleClose /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match?.total_red_cards || 0 }}</div><div class="stat-label">红牌数</div></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-item stat-card--success">
          <el-icon style="color:#fff;font-size:40px;"><User /></el-icon>
          <div class="stat-info"><div class="stat-number">{{ match?.total_players || 0 }}</div><div class="stat-label">参赛球员</div></div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { Finished, Football, Warning, CircleClose, User } from '@element-plus/icons-vue'

defineProps({
  match: {
    type: [Object, null],
    required: false,
    default: () => null,
    validator: (value) => {
      // 允许null或包含必要字段的对象
      return value === null || (typeof value === 'object' && value !== null)
    }
  }
})
</script>
