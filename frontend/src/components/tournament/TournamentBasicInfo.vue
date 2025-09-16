<template>
  <el-card class="competition-basic-info">
    <EntityHeader :title="competition.tournamentName || '未知赛事'" variant="blue" @back="$emit('back')">
      <template #meta>
        <span class="meta-item">
          <el-icon><Calendar /></el-icon>
          总赛季数: {{ competition.totalSeasons }}
        </span>
      </template>
    </EntityHeader>
  </el-card>
</template>
<script setup>
import EntityHeader from '@/components/EntityHeader.vue'
import { Calendar } from '@element-plus/icons-vue'

defineEmits(['back'])

defineProps({
  competition: { type: Object, required: true }
})
</script>
