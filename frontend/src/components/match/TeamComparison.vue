<template>
  <el-card class="team-comparison">
    <template #header><span>球队表现对比</span></template>
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="team-stats">
          <h3>{{ match.homeTeam }}</h3>
          <el-row :gutter="10">
            <el-col :span="6" v-for="item in homeItems" :key="item.label">
              <div class="team-stat-item">
                <div class="team-stat-number">{{ item.value }}</div>
                <div class="team-stat-label">{{ item.label }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="team-stats">
          <h3>{{ match.awayTeam }}</h3>
          <el-row :gutter="10">
            <el-col :span="6" v-for="item in awayItems" :key="item.label">
              <div class="team-stat-item">
                <div class="team-stat-number">{{ item.value }}</div>
                <div class="team-stat-label">{{ item.label }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ match: { type:Object, required:true } })
const homeItems = computed(()=>[
  { label:'进球', value: props.match.homeTeamStats?.goals },
  { label:'乌龙球', value: props.match.homeTeamStats?.ownGoals },
  { label:'黄牌', value: props.match.homeTeamStats?.yellowCards },
  { label:'红牌', value: props.match.homeTeamStats?.redCards }
])
const awayItems = computed(()=>[
  { label:'进球', value: props.match.awayTeamStats?.goals },
  { label:'乌龙球', value: props.match.awayTeamStats?.ownGoals },
  { label:'黄牌', value: props.match.awayTeamStats?.yellowCards },
  { label:'红牌', value: props.match.awayTeamStats?.redCards }
])
</script>