<template>
  <div class="welcome-card float-shadow">
    <div class="welcome-header">
      <div class="welcome-title">
        <el-icon size="24" class="welcome-icon"><UserFilled /></el-icon>
        <h2>管理员控制台</h2>
      </div>
      <div class="welcome-actions">
        <el-button type="success" size="small" class="btn-hover" @click="fetchStats" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button type="primary" size="small" class="btn-hover" @click="$emit('go-to-home')">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button type="danger" size="small" class="btn-hover" @click="$emit('logout')">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </div>
    <div class="welcome-content">
      <div class="welcome-stats">
        <div v-if="loading" class="stat-item float-shadow">
          <el-skeleton :rows="1" animated />
        </div>
        <div v-else class="stat-item float-shadow">
          <div class="stat-number">{{ teamsCount }}</div>
          <div class="stat-label">球队数量</div>
        </div>
        
        <div v-if="loading" class="stat-item float-shadow">
          <el-skeleton :rows="1" animated />
        </div>
        <div v-else class="stat-item float-shadow">
          <div class="stat-number">{{ matchesCount }}</div>
          <div class="stat-label">比赛数量</div>
        </div>
        
        <div v-if="loading" class="stat-item float-shadow">
          <el-skeleton :rows="1" animated />
        </div>
        <div v-else class="stat-item float-shadow">
          <div class="stat-number">{{ playersCount }}</div>
          <div class="stat-label">球员数量</div>
        </div>
      </div>
      <div class="welcome-message">
        <p>欢迎使用足球管理系统管理员控制台！您可以在这里管理球队、比赛、球员和赛事信息。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { UserFilled, House, SwitchButton, Refresh } from '@element-plus/icons-vue'
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/modules/auth'
import http from '@/utils/httpClient'
import logger from '@/utils/logger'
import '@/assets/styles/welcome-card.css'

const authStore = useAuthStore()

// 统计数据
const teamsCount = ref(0)
const matchesCount = ref(0)
const playersCount = ref(0)
const loading = ref(false)

// 获取统计数据
async function fetchStats() {
  loading.value = true
  try {
    const result = await http.get('/stats', {
      retry: {
        times: 2,
        delay: (attempt) => attempt * 1000
      }
    })
    
    if (result.ok) {
      const stats = result.data
      // 根据实际API响应结构更新数据
      teamsCount.value = stats.teams_count || stats.totalTeams || 0
      matchesCount.value = stats.matches_count || stats.totalMatches || 0
      playersCount.value = stats.players_count || stats.totalPlayers || 0
      logger.info('统计数据获取成功:', stats)
    } else {
      logger.error('获取统计数据失败:', result.error)
      // 如果API失败，从用户信息中获取备用数据
      teamsCount.value = authStore.user?.teamsCount || 0
      matchesCount.value = authStore.user?.matchesCount || 0
      playersCount.value = authStore.user?.playersCount || 0
    }
  } catch (error) {
    logger.error('获取统计数据异常:', error)
    // 出错时使用备用数据
    teamsCount.value = authStore.user?.teamsCount || 0
    matchesCount.value = authStore.user?.matchesCount || 0
    playersCount.value = authStore.user?.playersCount || 0
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取统计数据
onMounted(() => {
  fetchStats()
})

defineEmits(['go-to-home', 'logout'])
</script>