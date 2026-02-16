<template>
  <el-card class="team-name-card">
    <EntityHeader :title="team.team_name || '未知球队'" variant="blue" @back="$emit('back')" />
  </el-card>
</template>
<script setup>
import EntityHeader from '@/components/EntityHeader.vue'
defineEmits(['back'])
defineProps({
  team: { type: Object, required: true }
})
</script>
