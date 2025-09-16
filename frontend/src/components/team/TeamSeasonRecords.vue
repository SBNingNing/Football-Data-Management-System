<template>
  <el-card class="team-matches">
    <template #header>
      <div class="clearfix"><span>球队参加的比赛信息</span></div>
    </template>
    <el-collapse v-model="localActive">
      <el-collapse-item v-for="record in records" :key="record.id" :name="record.id">
        <template #title>
          <div class="season-title">
            <span>{{ record.tournamentName }} ({{ getMatchTypeText(record.matchType) }})</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="4" v-for="item in seasonStatItems(record)" :key="item.label">
            <div class="season-stat">
              <div class="season-label">{{ item.label }}</div>
              <div class="season-number">{{ item.value }}</div>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <el-table :data="record.players" style="width:100%;" max-height="400">
              <el-table-column prop="name" label="球员">
                <template #default="scope">
                  <span class="clickable-player" @click="$emit('view-player', scope.row)">
                    <el-icon class="player-icon"><User /></el-icon>
                    {{ scope.row.name }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="playerId" label="球员ID" />
              <el-table-column prop="goals" label="进球数" />
              <el-table-column prop="yellowCards" label="黄牌数" />
              <el-table-column prop="redCards" label="红牌数" />
            </el-table>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>
  </el-card>
</template>
<script setup>
import { watch, ref } from 'vue'
import { User } from '@element-plus/icons-vue'

const props = defineProps({
  records: { type: Array, default: () => [] },
  activeSeason: { type: [String, Number, null], default: null }
})
const emit = defineEmits(['update:activeSeason', 'view-player'])

const localActive = ref(props.activeSeason)
watch(() => props.activeSeason, v => { if(v !== localActive.value) localActive.value = v })
watch(localActive, v => emit('update:activeSeason', v))

function getMatchTypeText(matchType){
  const map = { 'champions-cup':'冠军杯','womens-cup':'巾帼杯','eight-a-side':'八人制比赛' }
  return map[matchType] || '未知类型'
}

const seasonStatItems = (r) => [
  { label: '排名', value: r.rank || '暂无' },
  { label: '进球数', value: r.goals },
  { label: '失球数', value: r.goalsConceded },
  { label: '净胜球', value: r.goalDifference },
  { label: '黄牌', value: r.yellowCards },
  { label: '红牌', value: r.redCards }
]
</script>
