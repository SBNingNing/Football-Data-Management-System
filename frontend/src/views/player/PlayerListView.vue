<template>
  <div class="player-list">
    <el-card class="page-header">
      <div class="header-content">
        <h1>球员管理</h1>
        <el-button 
          v-if="hasPermission" 
          type="primary" 
          @click="addPlayer"
        >
          添加球员
        </el-button>
      </div>
    </el-card>

    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.teamId" clearable placeholder="选择球队">
            <el-option 
              v-for="team in teams" 
              :key="team.teamId" 
              :label="team.teamName" 
              :value="team.teamId"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.seasonId" clearable placeholder="选择赛季">
            <el-option 
              v-for="season in seasons" 
              :key="season.seasonId" 
              :label="season.seasonName" 
              :value="season.seasonId"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="players"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="playerId" label="ID" width="80" />
        <el-table-column prop="playerName" label="姓名" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            {{ scope.row.gender === 'M' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="teamName" label="所属球队" />
        <el-table-column prop="seasonName" label="赛季" />
        <el-table-column prop="seasonGoals" label="赛季进球" />
        <el-table-column prop="seasonCards" label="赛季红黄牌" />
        <el-table-column prop="historicalGoals" label="历史进球" />
        <el-table-column prop="historicalCards" label="历史红黄牌" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              v-if="hasPermission"
              size="small"
              @click="editPlayer(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="isAdmin"
              size="small"
              type="danger"
              @click="confirmDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../store/modules/user';
import playerService from '../../services/playerService';
import teamService from '../../services/teamService';
import seasonService from '../../services/seasonService';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();

const players = ref([]);
const teams = ref([]);
const seasons = ref([]);
const loading = ref(false);
const filters = ref({
  teamId: null,
  seasonId: null
});

const hasPermission = computed(() => {
  const role = userStore.userRole;
  return role === 'ADMIN' || role === 'RECORDER';
});

const isAdmin = computed(() => userStore.userRole === 'ADMIN');

onMounted(async () => {
  try {
    loading.value = true;
    await Promise.all([loadPlayers(), loadTeams(), loadSeasons()]);
  } catch (error) {
    console.error('Error loading data:', error);
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
});

async function loadPlayers() {
  try {
    const response = await playerService.getAllPlayers();
    players.value = response.data;
  } catch (error) {
    console.error('Error loading players:', error);
    throw error;
  }
}

async function loadTeams() {
  try {
    const response = await teamService.getAllTeams();
    teams.value = response.data;
  } catch (error) {
    console.error('Error loading teams:', error);
    throw error;
  }
}

async function loadSeasons() {
  try {
    const response = await seasonService.getAllSeasons();
    seasons.value = response.data;
  } catch (error) {
    console.error('Error loading seasons:', error);
    throw error;
  }
}

async function applyFilters() {
  try {
    loading.value = true;
    const { teamId, seasonId } = filters.value;
    
    if (teamId && seasonId) {
      const response = await playerService.getPlayersByTeamAndSeason(teamId, seasonId);
      players.value = response.data;
    } else if (teamId) {
      const response = await playerService.getPlayersByTeam(teamId);
      players.value = response.data;
    } else if (seasonId) {
      const response = await playerService.getPlayersBySeason(seasonId);
      players.value = response.data;
    } else {
      await loadPlayers();
    }
  } catch (error) {
    console.error('Error applying filters:', error);
    ElMessage.error('筛选数据失败');
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.value = {
    teamId: null,
    seasonId: null
  };
  loadPlayers();
}

function addPlayer() {
  router.push({ name: 'AddPlayer' });
}

function editPlayer(player) {
  router.push({ 
    name: 'EditPlayer', 
    params: { id: player.playerId } 
  });
}

function confirmDelete(player) {
  ElMessageBox.confirm(
    `确定要删除球员 ${player.playerName} 吗?`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await playerService.deletePlayer(player.playerId);
      ElMessage.success('删除成功');
      await loadPlayers();
    } catch (error) {
      console.error('Delete error:', error);
      ElMessage.error('删除失败');
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}
</script>

<style scoped>
.player-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}
</style>
