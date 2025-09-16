<template>
  <el-card class="competition-seasons">
    <template #header><div class="clearfix"><span>赛事赛季表现</span></div></template>
    <el-collapse v-model="localActive">
      <el-collapse-item v-for="season in records" :key="season.id" :name="season.id" @change="() => onSeasonToggle(season)">
        <template #title>
          <div class="season-title">
            <span>{{ season.seasonName }} ({{ season.seasonStartTime ? new Date(season.seasonStartTime).getFullYear() : '' }})</span>
            <span class="season-info">球队数: {{ season.teamCount }} | 总进球: {{ season.totalGoals }}</span>
          </div>
        </template>
        <!-- 射手榜 -->
        <el-row :gutter="20" style="margin-bottom:20px;">
          <el-col :span="24">
            <h4>射手榜</h4>
            <el-table :data="leaderboards[season.id]?.topScorers || []" style="width:100%;" max-height="300">
              <el-table-column prop="player_name" label="球员" />
              <el-table-column prop="team_name" label="球队" />
              <el-table-column prop="player_number" label="球衣号码" />
              <el-table-column prop="goals" label="进球数" sortable />
            </el-table>
          </el-col>
        </el-row>
        <!-- 红黄牌榜 -->
        <el-row :gutter="20" style="margin-bottom:20px;">
          <el-col :span="24">
            <h4>红黄牌榜</h4>
            <el-table :data="leaderboards[season.id]?.topCards || []" style="width:100%;" max-height="300">
              <el-table-column prop="player_name" label="球员" />
              <el-table-column prop="team_name" label="球队" />
              <el-table-column prop="player_number" label="球衣号码" />
              <el-table-column prop="yellowCards" label="黄牌数" sortable />
              <el-table-column prop="redCards" label="红牌数" sortable />
            </el-table>
          </el-col>
        </el-row>
        <!-- 赛季积分榜 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <h4>赛季积分榜</h4>
            <el-table :data="season.teams" style="width: 100%">
              <el-table-column prop="rank" label="排名" sortable />
              <el-table-column prop="name" label="球队" />
              <el-table-column prop="points" label="积分" sortable />
              <el-table-column prop="goals" label="进球数" sortable />
              <el-table-column prop="goalsConceded" label="失球数" sortable />
              <el-table-column prop="goalDifference" label="净胜球" sortable />
              <el-table-column prop="yellowCards" label="黄牌数" sortable />
              <el-table-column prop="redCards" label="红牌数" sortable />
              <el-table-column prop="playerCount" label="球员数" />
            </el-table>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>
  </el-card>
</template>
<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  records: { type: Array, default: () => [] },
  activeSeason: { type: [String, Number, null], default: null },
  leaderboards: { type: Object, required: true }
})
const emit = defineEmits(['update:active-season', 'ensure-season'])

const localActive = ref(props.activeSeason)
watch(() => props.activeSeason, v => { if(v !== localActive.value) localActive.value = v })
watch(localActive, v => emit('update:active-season', v))

function onSeasonToggle(season){
  emit('ensure-season', season)
}
</script>
