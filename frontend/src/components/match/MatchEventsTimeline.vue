<template>
  <el-card class="match-events">
    <template #header>
      <div class="clearfix">
        <span>比赛事件时间轴</span>
        <div class="events-stats">共 {{ events.length }} 个事件</div>
      </div>
    </template>
    <div class="events-timeline">
      <div v-if="events.length===0" class="no-events">
        <el-icon class="no-data-icon"><Clock /></el-icon>
        <p>暂无比赛事件记录</p>
      </div>
      <div v-else class="timeline-container">
        <div
          v-for="event in events"
          :key="event.id"
          class="timeline-item"
          :class="getEventClass(event.eventType || event.event_type)"
        >
          <div class="timeline-marker">
            <el-icon><component :is="getEventIcon(event.eventType || event.event_type)" /></el-icon>
          </div>
          <div class="timeline-content">
            <div class="event-header">
              <span class="event-time">{{ (event.eventTime || event.event_time) ?? '--' }}'</span>
              <span class="event-type">{{ event.eventType || event.event_type }}</span>
            </div>
            <div class="event-body">
              <span class="event-player">{{ event.playerName || event.player_name || event.player || '未知球员' }}</span>
              <span class="event-team">{{ event.teamName || event.team_name || '' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>
<script setup>
import { Clock } from '@element-plus/icons-vue'
import { getMatchEventIcon, getMatchEventClass } from '@/utils/constants'

defineProps({ events: { type: Array, required: true } })

// 创建别名以保持组件内部使用一致性
const getEventIcon = getMatchEventIcon
const getEventClass = getMatchEventClass
</script>