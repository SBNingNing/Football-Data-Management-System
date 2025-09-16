<template>
  <transition name="fade" mode="out-in">
    <el-card v-if="type==='team'" key="team" shadow="hover" class="form-card">
      <template #header>
        <div class="form-header">
          <h3 class="form-title">
            <el-icon class="form-icon teams-color"><UserFilled /></el-icon>
            队伍信息录入
          </h3>
          <el-button @click="$emit('back')" text><el-icon><Close /></el-icon>返回选择</el-button>
        </div>
      </template>
      <TeamInput :match-type="matchType" :teams="teams" @submit="$emit('team-submit', $event)" class="input-component" />
    </el-card>
    <el-card v-else-if="type==='schedule'" key="schedule" shadow="hover" class="form-card">
      <template #header>
        <div class="form-header">
          <h3 class="form-title">
            <el-icon class="form-icon schedule-color"><Calendar /></el-icon>
            赛程信息录入
          </h3>
          <el-button @click="$emit('back')" text><el-icon><Close /></el-icon>返回选择</el-button>
        </div>
      </template>
      <ScheduleInput :match-type="matchType" :teams="teams" @submit="$emit('schedule-submit', $event)" class="input-component" />
    </el-card>
    <el-card v-else-if="type==='event'" key="event" shadow="hover" class="form-card">
      <template #header>
        <div class="form-header">
          <h3 class="form-title">
            <el-icon class="form-icon events-color"><Flag /></el-icon>
            比赛事件录入
          </h3>
          <el-button @click="$emit('back')" text><el-icon><Close /></el-icon>返回选择</el-button>
        </div>
      </template>
      <EventInput :match-type="matchType" :matches="matches" :teams="teams" @submit="$emit('event-submit', $event)" class="input-component" />
    </el-card>
  </transition>
</template>
<script setup>
import { UserFilled, Calendar, Flag, Close } from '@element-plus/icons-vue'
import TeamInput from '../TeamInput.vue'
import ScheduleInput from '../ScheduleInput.vue'
import EventInput from '../EventInput.vue'
defineProps({
  type: { type: String, default: '' },
  matchType: { type: String, default: '' },
  teams: { type: Array, default: () => [] },
  matches: { type: Array, default: () => [] }
})
defineEmits(['back','team-submit','schedule-submit','event-submit'])
</script>
