<template>
  <el-card class="team-comparison">
    <template #header><span>球队表现对比</span></template>
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="team-stats">
          <h3>{{ match?.homeTeam || '主队' }}</h3>
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
          <h3>{{ match?.awayTeam || '客队' }}</h3>
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
const props = defineProps({ 
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
const homeItems = computed(()=>[
  { label:'进球', value: props.match?.homeTeamStats?.goals || 0 },
  { label:'乌龙球', value: props.match?.homeTeamStats?.ownGoals || 0 },
  { label:'黄牌', value: props.match?.homeTeamStats?.yellowCards || 0 },
  { label:'红牌', value: props.match?.homeTeamStats?.redCards || 0 }
])
const awayItems = computed(()=>[
  { label:'进球', value: props.match?.awayTeamStats?.goals || 0 },
  { label:'乌龙球', value: props.match?.awayTeamStats?.ownGoals || 0 },
  { label:'黄牌', value: props.match?.awayTeamStats?.yellowCards || 0 },
  { label:'红牌', value: props.match?.awayTeamStats?.redCards || 0 }
])
</script>