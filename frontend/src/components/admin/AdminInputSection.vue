<template>
  <div class="tab-content">
    <div class="content-header">
      <div class="header-left">
        <h2 class="header-title">数据录入中心</h2>
        <p class="header-subtitle">录入新的球队、比赛和事件信息</p>
      </div>
    </div>
    <MetaDataSection />
    <DataInput 
      ref="dataInputRef"
      :teams="teams" 
      :matches="matches" 
      :events="events"
      @team-submit="$emit('team-submit', $event)"
      @schedule-submit="$emit('schedule-submit', $event)"
      @event-submit="$emit('event-submit', $event)"
      @refresh-data="$emit('refresh-data')"
    />
  </div>
</template>
<script setup>
import { ref } from 'vue'
import MetaDataSection from '@/components/common/MetaDataSection.vue'
import DataInput from '@/components/Data/DataInput.vue'

defineProps({
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] }
})

const dataInputRef = ref(null)
defineExpose({ dataInputRef })
defineEmits(['team-submit','schedule-submit','event-submit','refresh-data'])
</script>