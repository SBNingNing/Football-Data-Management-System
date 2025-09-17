<template>
  <div class="tab-content">
    <div class="content-header">
      <div class="header-left">
        <h2 class="header-title">数据管理中心</h2>
        <p class="header-subtitle">管理球队、比赛、球员和事件信息</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="$emit('refresh')" :loading="loading" class="refresh-btn">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>
    <DataManagement
      :teams="teams"
      :matches="matches"
      :events="events"
      :players="players"
      :manage-match-type="manageMatchType"
      @filter-change="$emit('filter-change', $event)"
      @refresh="$emit('refresh')"
      @edit-team="$emit('edit-team', $event)"
      @delete-team="$emit('delete-team', $event)"
      @edit-match="$emit('edit-match', $event)"
      @delete-match="$emit('delete-match', $event)"
      @edit-event="$emit('edit-event', $event)"
      @delete-event="$emit('delete-event', $event)"
      @edit-player="$emit('edit-player', $event)"
      @delete-player="$emit('delete-player', $event)"
      @complete-match="$emit('complete-match', $event)"
    />
  </div>
</template>
<script setup>
import { Refresh } from '@element-plus/icons-vue'
import DataManagement from '@/components/Data/DataManagement.vue'

defineProps({
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] },
  events: { type: Array, default: () => [] },
  players: { type: Array, default: () => [] },
  manageMatchType: { type: String, default: '' },
  loading: { type: Boolean, default: false }
})

defineEmits(['refresh','filter-change','edit-team','delete-team','edit-match','delete-match','edit-event','delete-event','edit-player','delete-player','complete-match'])
</script>