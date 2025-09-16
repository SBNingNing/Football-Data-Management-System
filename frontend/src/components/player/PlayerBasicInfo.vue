<template>
  <el-card class="player-basic-info">
    <EntityHeader :title="player.name || '未知球员'" variant="blue" @back="$emit('back')">
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