<template>
  <div class="competition-history">
    <!-- 赛事基本信息卡片 -->
    <el-card class="competition-basic-info">
      <div class="competition-name-header">
        <div class="back-button-container">
          <el-button 
            type="primary" 
            :icon="ArrowLeft" 
            plain
            @click="goToHomePage"
            class="back-button"
          >
            返回主页
          </el-button>
        </div>
        <h1 class="tournament-title">{{ competition.tournamentName }}</h1>
        <div class="tournament-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            总赛季数: {{ competition.totalSeasons }}
          </span>
        </div>
      </div>
    </el-card>

    <!-- 赛事历史数据 -->
    <el-card class="competition-history-stats">
      <template #header>
        <div class="clearfix">
          <span>赛事历史数据</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Finished /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #f39c12; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #e74c3c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalRedCards }}</div>
              <div class="stat-label">红牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item" style="background-color: #27ae60; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ competition.totalSeasons }}</div>
              <div class="stat-label">赛季数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 赛事赛季表现 -->
    <el-card class="competition-seasons">
      <template #header>
        <div class="clearfix">
          <span>赛事赛季表现</span>
        </div>
      </template>
      <el-collapse v-model="activeSeason">
        <el-collapse-item v-for="season in competition.records" :key="season.id" :name="season.id">
          <template #title>
            <div class="season-title">
              <span>{{ season.seasonName }} ({{ season.seasonStartTime ? new Date(season.seasonStartTime).getFullYear() : '' }})</span>
              <span class="season-info">球队数: {{ season.teamCount }} | 总进球: {{ season.totalGoals }}</span>
            </div>
          </template>
          
          <!-- 射手榜 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="24">
              <h4>射手榜</h4>
              <el-table :data="getTopScorers(season)" style="width: 100%" max-height="300">
                <el-table-column prop="player_name" label="球员"></el-table-column>
                <el-table-column prop="team_name" label="球队"></el-table-column>
                <el-table-column prop="player_number" label="球衣号码"></el-table-column>
                <el-table-column prop="goals" label="进球数" sortable></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          
          <!-- 红黄牌榜 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="24">
              <h4>红黄牌榜</h4>
              <el-table :data="getTopCards(season)" style="width: 100%" max-height="300">
                <el-table-column prop="player_name" label="球员"></el-table-column>
                <el-table-column prop="team_name" label="球队"></el-table-column>
                <el-table-column prop="player_number" label="球衣号码"></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数" sortable></el-table-column>
                <el-table-column prop="redCards" label="红牌数" sortable></el-table-column>
              </el-table>
            </el-col>
          </el-row>
          
          <!-- 赛季积分榜 -->
          <el-row :gutter="20">
            <el-col :span="24">
              <h4>赛季积分榜</h4>
              <el-table :data="season.teams" style="width: 100%">
                <el-table-column prop="rank" label="排名" sortable></el-table-column>
                <el-table-column prop="name" label="球队"></el-table-column>
                <el-table-column prop="points" label="积分" sortable></el-table-column>
                <el-table-column prop="goals" label="进球数" sortable></el-table-column>
                <el-table-column prop="goalsConceded" label="失球数" sortable></el-table-column>
                <el-table-column prop="goalDifference" label="净胜球" sortable></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数" sortable></el-table-column>
                <el-table-column prop="redCards" label="红牌数" sortable></el-table-column>
                <el-table-column prop="playerCount" label="球员数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Finished, Warning, CircleClose, User, Calendar, ArrowLeft } from '@element-plus/icons-vue'
import { getTournamentStats } from '@/api/tournaments'

const route = useRoute()
const router = useRouter()

const activeSeason = ref(null)
const competition = ref({
  tournamentName: '',
  totalGoals: 0,
  totalYellowCards: 0,
  totalRedCards: 0,
  totalSeasons: 0,
  records: []
})

onMounted(async () => {
  await loadTournamentData()
})

const loadTournamentData = async () => {
  try {
    const tournamentName = route.params.tournamentName
    if (!tournamentName) {
      ElMessage.error('缺少赛事名称参数')
      return
    }

    console.log('原始赛事名称:', tournamentName)
    console.log('解码后的赛事名称:', decodeURIComponent(tournamentName))
    console.log('当前路由:', route.fullPath)
    
    // 添加loading状态
    ElMessage.info('正在加载赛事数据...')
    
    const response = await getTournamentStats(tournamentName)
    console.log('完整API响应:', response)
    
    if (response && response.data && response.data.status === 'success') {
      const tournamentData = response.data.data
      console.log('解析的赛事数据:', tournamentData)
      
      competition.value = {
        tournamentName: tournamentData.tournamentName || decodeURIComponent(tournamentName),
        totalGoals: 0,
        totalYellowCards: 0,
        totalRedCards: 0,
        totalSeasons: tournamentData.totalSeasons || 0,
        records: tournamentData.records || []
      }
      
      console.log('设置的competition数据:', competition.value)
      calculateTotalStats()
      ElMessage.success('赛事数据加载成功')
    } else {
      const errorMsg = response?.data?.message || '获取赛事数据失败'
      console.error('API返回错误:', errorMsg)
      console.error('可用的赛事:', response?.data?.available_tournaments)
      console.error('调试信息:', response?.data?.debug_info)
      
      if (response?.data?.available_tournaments) {
        ElMessage.error(`${errorMsg}。可用的赛事: ${response.data.available_tournaments.join(', ')}`)
      } else {
        ElMessage.error(errorMsg)
      }
    }
  } catch (error) {
    console.error('加载赛事数据失败:', error)
    console.error('错误详情:', {
      message: error.message,
      code: error.code,
      response: error.response,
      stack: error.stack
    })
    
    if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    } else if (error.response) {
      const status = error.response.status
      const data = error.response.data
      console.error(`服务器响应错误 ${status}:`, data)
      ElMessage.error(`服务器错误 (${status}): ${data?.message || '未知错误'}`)
    } else {
      ElMessage.error('加载赛事数据失败，请稍后重试')
    }
  }
}

const calculateTotalStats = () => {
  // 计算总统计数据
  let totalGoals = 0
  let totalYellowCards = 0
  let totalRedCards = 0
  
  if (competition.value.records && Array.isArray(competition.value.records)) {
    competition.value.records.forEach(season => {
      totalGoals += season.totalGoals || 0
      if (season.teams && Array.isArray(season.teams)) {
        season.teams.forEach(team => {
          totalYellowCards += team.yellowCards || 0
          totalRedCards += team.redCards || 0
        })
      }
    })
  }
  
  competition.value.totalGoals = totalGoals
  competition.value.totalYellowCards = totalYellowCards
  competition.value.totalRedCards = totalRedCards
}

const getTopScorers = (season) => {
  // 获取射手榜数据
  const allPlayers = []
  if (season.teams && Array.isArray(season.teams)) {
    season.teams.forEach(team => {
      if (team.players && Array.isArray(team.players)) {
        team.players.forEach(player => {
          if (player.goals > 0) {
            allPlayers.push({
              ...player,
              team_name: team.name
            })
          }
        })
      }
    })
  }
  return allPlayers.sort((a, b) => (b.goals || 0) - (a.goals || 0)).slice(0, 10)
}

const getTopCards = (season) => {
  // 获取红黄牌榜数据
  const allPlayers = []
  if (season.teams && Array.isArray(season.teams)) {
    season.teams.forEach(team => {
      if (team.players && Array.isArray(team.players)) {
        team.players.forEach(player => {
          if ((player.yellowCards || 0) > 0 || (player.redCards || 0) > 0) {
            allPlayers.push({
              ...player,
              team_name: team.name
            })
          }
        })
      }
    })
  }
  return allPlayers.sort((a, b) => 
    ((b.redCards || 0) + (b.yellowCards || 0)) - ((a.redCards || 0) + (a.yellowCards || 0))
  ).slice(0, 10)
}

const goToHomePage = () => {
  router.push('/home')
}
</script>

<style scoped>
.competition-history {
  max-width: 1200px;
  margin: 0 auto;
}

.competition-basic-info,
.competition-history-stats,
.competition-seasons {
  margin-bottom: 20px;
}

.competition-name-header {
  background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
  color: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
  position: relative;
}

.back-button-container {
  position: absolute;
  top: 20px;
  left: 20px;
}

.back-button {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

.tournament-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0 0 15px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.tournament-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.meta-item .el-icon {
  font-size: 18px;
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-info {
  display: flex;
  flex-direction: column;
  margin-left: 15px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
}

.season-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.season-info {
  font-size: 12px;
  color: #909399;
  margin-left: 20px;
}

.season-stat {
  display: flex;
  flex-direction: column;
}

.season-label {
  font-size: 14px;
  color: #909399;
}

.season-number {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
</style>