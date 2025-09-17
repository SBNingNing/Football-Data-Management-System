<template>
  <el-card class="selection-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <el-icon><EditPen /></el-icon>
          选择录入信息类型
        </div>
      </div>
    </template>
    <div class="type-cards-container">
      <div class="type-card teams-card" :class="{ active: modelValue==='team' }" @click="select('team')">
        <div class="type-card-icon teams-bg"><el-icon><UserFilled /></el-icon></div>
        <h3 class="type-card-title">队伍信息</h3>
        <p class="type-card-desc">添加或维护队伍，设置基础资料</p>
        <div class="type-card-stats"><span class="stats-text">当前 {{ teamCount }} 支队伍</span></div>
      </div>
      <div class="type-card schedule-card" :class="{ active: modelValue==='schedule' }" @click="select('schedule')">
        <div class="type-card-icon schedule-bg"><el-icon><Calendar /></el-icon></div>
        <h3 class="type-card-title">赛程信息</h3>
        <p class="type-card-desc">录入比赛安排与对阵</p>
        <div class="type-card-stats"><span class="stats-text">已登记 {{ matchCount }} 场比赛</span></div>
      </div>
      <div class="type-card events-card" :class="{ active: modelValue==='event' }" @click="select('event')">
        <div class="type-card-icon events-bg"><el-icon><Flag /></el-icon></div>
        <h3 class="type-card-title">比赛事件</h3>
        <p class="type-card-desc">记录进球、牌、换人等事件</p>
        <div class="type-card-stats"><span class="stats-text">当前 {{ eventCount }} 条事件</span></div>
      </div>
    </div>
  </el-card>
</template>
<script setup>
import { EditPen, UserFilled, Calendar, Flag } from '@element-plus/icons-vue'
const props = defineProps({
  modelValue: { type: String, default: '' },
  teamCount: { type: Number, default: 0 },
  matchCount: { type: Number, default: 0 },
  eventCount: { type: Number, default: 0 }
})
const emit = defineEmits(['update:modelValue','select'])
function select(type){ emit('update:modelValue', type); emit('select', type) }
// 访问一次 props 以满足 eslint no-unused-vars（模板已用，但有的配置无法静态检测）
void props.modelValue
</script>
