<template>
  <el-card class="competition-history-stats">
    <template #header><div class="clearfix"><span>赛事历史数据</span></div></template>
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in statItems" :key="item.label">
        <div class="stat-item" :class="item.cssClass">
          <el-icon style="color:#ffffff;font-size:40px;"><component :is="item.icon" /></el-icon>
          <div class="stat-info">
            <div class="stat-number">{{ item.value }}</div>
            <div class="stat-label">{{ item.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { Finished, Warning, CircleClose, User } from '@element-plus/icons-vue'
const props = defineProps({ competition: { type: Object, required: true } })
const statItems = [
  { label:'总进球数', value: props.competition.totalGoals, icon: Finished, cssClass: 'stat-card--goals' },
  { label:'黄牌数', value: props.competition.totalYellowCards, icon: Warning, cssClass: 'stat-card--yellow' },
  { label:'红牌数', value: props.competition.totalRedCards, icon: CircleClose, cssClass: 'stat-card--red' },
  { label:'赛季数', value: props.competition.totalSeasons, icon: User, cssClass: 'stat-card--success' }
]
</script>
