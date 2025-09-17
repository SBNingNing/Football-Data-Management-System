<template>
  <el-card class="form-card event-input-card">
    <template #header>
      <div class="form-header">
        <h3 class="form-title">
          <el-icon class="form-icon events-color"><Flag /></el-icon>
          {{ matchTypeLabel }}事件录入
        </h3>
      </div>
    </template>
    <el-form ref="eventFormRef" :model="eventForm" label-width="120px" class="event-form">
      <el-form-item label="比赛名称">
        <el-select v-model="eventForm.matchName" placeholder="请选择比赛" @change="handleMatchSelect" class="w-full">
          <el-option v-for="match in matches" :key="match.id" :label="match.matchName" :value="match.matchName" />
        </el-select>
      </el-form-item>
      <el-form-item label="事件信息">
        <div class="event-section-header">
          <el-button type="primary" @click="addEvent" class="add-event-btn">添加事件</el-button>
          <span class="event-count-text">已添加 {{ eventForm.events.length }} 个事件</span>
        </div>
        <div class="event-list-container" v-if="eventForm.events.length">
          <transition-group name="player-list" tag="div">
            <div v-for="(ev, index) in eventForm.events" :key="`event-${index}`" class="event-item-card player-card">
              <div class="event-item-header player-card-header">
                <span class="event-index-badge player-number-badge">事件 {{ index + 1 }}</span>
                <el-button type="primary" link @click="removeEvent(index)" class="delete-btn" size="small">删除</el-button>
              </div>
              <div class="event-item-inputs player-form entity-grid grid-cols-3 compact-gap grid-collapse-sm">
                <el-select v-model="ev.eventType" placeholder="事件类型" class="event-field">
                  <el-option label="进球" value="进球" />
                  <el-option label="红牌" value="红牌" />
                  <el-option label="黄牌" value="黄牌" />
                  <el-option label="乌龙球" value="乌龙球" />
                </el-select>
                <el-select v-model="ev.playerName" placeholder="选择球员" class="event-field">
                  <el-option v-for="player in currentMatchPlayers" :key="player.id" :label="player.name" :value="player.name" />
                </el-select>
                <el-input v-model="ev.eventTime" placeholder="事件时间（分钟）" class="event-field" />
              </div>
            </div>
          </transition-group>
        </div>
        <div v-else class="empty-players empty-events">
          <el-empty description="暂无事件" :image-size="80">
            <el-button type="primary" @click="addEvent">添加第一个事件</el-button>
          </el-empty>
        </div>
      </el-form-item>
      <el-form-item class="entity-submit-zone">
        <el-button type="primary" @click="submitEvents" :disabled="!canSubmit" :loading="submitting" class="submit-btn btn-entity-submit">提交事件信息</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Flag } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getMatchTypeLabel } from '@/constants/domain'
import { createEventsBatch } from '@/domain/event/eventService'

const props = defineProps({
  matchType: { type: String, default: '' },
  matches: { type: Array, default: () => [] },
  teams: { type: Array, default: () => [] }
})
const emit = defineEmits(['submit'])

const eventFormRef = ref(null)
const eventForm = reactive({ matchName: '', events: [] })
const currentMatchPlayers = ref([])
const submitting = ref(false)

const matchTypeLabel = computed(() => getMatchTypeLabel(props.matchType))
const canSubmit = computed(() => !!eventForm.matchName && eventForm.events.length > 0 && !submitting.value)

const addEvent = () => {
  eventForm.events.push({ eventType: '', playerName: '', eventTime: '' })
}
const removeEvent = (index) => {
  eventForm.events.splice(index, 1)
}
const handleMatchSelect = (matchName) => {
  const selectedMatch = props.matches.find(m => m.matchName === matchName)
  if (selectedMatch) {
    const team1Players = props.teams.find(t => t.teamName === selectedMatch.team1)?.players || []
    const team2Players = props.teams.find(t => t.teamName === selectedMatch.team2)?.players || []
    currentMatchPlayers.value = [...team1Players, ...team2Players]
  } else {
    currentMatchPlayers.value = []
  }
}
const submitEvents = () => {
  if (!canSubmit.value || submitting.value) return
  const clone = JSON.parse(JSON.stringify(eventForm))
  submitting.value = true
  createEventsBatch(clone.events.map(e => ({
    matchName: clone.matchName,
    eventType: e.eventType,
    playerName: e.playerName,
    eventTime: e.eventTime
  }))).then(({ ok, data, error }) => {
    if(!ok){
      ElMessage.error(error?.message || '批量创建事件失败')
      return
    }
    try {
      import('@/utils/httpClient').then(m => {
        // 失效相关缓存（简单容错）
        m.default.cache.invalidate('events:list')
        m.default.cache.invalidate('stats:dashboard')
        m.default.cache.invalidate('stats:rankings')
      })
  } catch { /* ignore invalidate error */ }
    const success = data?.success || 0
    const total = data?.total || clone.events.length
    ElMessage.success(`事件提交完成：成功 ${success}/${total}`)
    emit('submit', clone)
    eventForm.matchName = ''
    eventForm.events = []
    currentMatchPlayers.value = []
  }).catch(_err => {
    ElMessage.error('事件提交异常')
  }).finally(()=>{ submitting.value = false })
}
</script>

<style scoped>
/* 已迁移特有样式到全局 admin-management.css，保留空块占位，后续可彻底移除 */
</style>
