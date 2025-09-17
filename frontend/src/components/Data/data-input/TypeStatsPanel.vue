<template>
  <div v-if="matchType" class="match-type-info">
    <div class="info-header"><h3 class="info-title">当前类型统计</h3></div>
    <div class="info-grid">
      <div class="info-card teams-card">
        <div class="info-icon teams-icon"><el-icon><UserFilled /></el-icon></div>
        <div class="info-content">
          <div class="info-value">{{ teamCount }}</div>
          <div class="info-label">参赛队伍</div>
        </div>
      </div>
      <div class="info-card matches-card">
        <div class="info-icon matches-icon"><el-icon><Calendar /></el-icon></div>
        <div class="info-content">
          <div class="info-value">{{ matchCount }}</div>
          <div class="info-label">已登记赛程</div>
        </div>
      </div>
      <div class="info-card events-card">
        <div class="info-icon events-icon"><el-icon><Flag /></el-icon></div>
        <div class="info-content">
          <div class="info-value">{{ eventCount }}</div>
          <div class="info-label">赛事事件</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { UserFilled, Calendar, Flag } from '@element-plus/icons-vue'
const props = defineProps({
  matchType: { type: String, default: '' },
  teamCount: { type: Number, default: 0 },
  matchCount: { type: Number, default: 0 },
  eventCount: { type: Number, default: 0 }
})
void props.matchType
</script>
