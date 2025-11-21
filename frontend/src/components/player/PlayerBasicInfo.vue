<template>
  <el-card class="player-basic-info">
    <EntityHeader :title="player.name || '未知球员'" variant="light" @back="$emit('back')">
      <template #meta>
        <span class="meta-item">
          <el-icon><User /></el-icon>
          学号: {{ player.studentId || '-' }}
        </span>
        <span class="meta-item" v-if="player.teamHistories?.length">
          <el-icon><Trophy /></el-icon>
          参与队伍数: {{ player.teamHistories.length }}
        </span>
      </template>
      <template #stats>
        <StatCard :value="player.totalGoals" label="总进球" type="goals" />
        <StatCard :value="player.totalYellowCards" label="总黄牌" type="yellow" />
        <StatCard :value="player.totalRedCards" label="总红牌" type="red" />
      </template>
    </EntityHeader>
  </el-card>
</template>
<script setup>
import EntityHeader from '@/components/EntityHeader.vue'
import StatCard from '@/components/StatCard.vue'
import { User, Trophy } from '@element-plus/icons-vue'
defineProps({ player: { type:Object, required:true } })
defineEmits(['back'])
</script>

<style scoped>
.player-basic-info {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

.player-basic-info .el-card__body {
  padding: 0;
}

.player-basic-info .el-button,
.player-basic-info .el-button--primary {
  /* color: #ffffff !important; Removed to allow EntityHeader to style the button */
}

.player-basic-info .meta-item {
  margin-right: 12px;
  color: #718096;
}
</style>