<template>
  <div class="admin">
    <!-- 管理员欢迎卡片 -->
    <WelcomeCard 
      @go-to-home="goToHome"
      @logout="logout"
    />

    <!-- 功能标签页 -->
    <el-card class="main-content-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 信息录入标签页 -->
        <el-tab-pane label="信息录入" name="input">
          <DataInput 
            :teams="teams"
            :matches="matches"
            @team-submit="handleTeamSubmit"
            @schedule-submit="handleScheduleSubmit"
            @event-submit="handleEventSubmit"
          />
        </el-tab-pane>

        <!-- 信息管理标签页 -->
        <el-tab-pane label="信息管理" name="manage">
          <DataManagement 
            :teams="teams"
            :matches="matches"
            :events="events"
            :manage-match-type="manageMatchType"
            @filter-change="handleFilterChange"
            @refresh="loadAllData"
            @edit-team="editTeam"
            @delete-team="deleteTeam"
            @edit-match="editMatch"
            @delete-match="deleteMatch"
            @edit-event="editEvent"
            @delete-event="deleteEvent"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 编辑对话框组件 -->
    <EditDialogs
      :edit-team-dialog="editTeamDialog"
      :edit-match-dialog="editMatchDialog"
      :edit-event-dialog="editEventDialog"
      :edit-team-form="editTeamForm"
      :edit-match-form="editMatchForm"
      :edit-event-form="editEventForm"
      :teams="teams"
      :matches="matches"
      :players="players"
      @close-team-dialog="editTeamDialog = false"
      @close-match-dialog="editMatchDialog = false"
      @close-event-dialog="editEventDialog = false"
      @update-team="updateTeam"
      @update-match="updateMatch"
      @update-event="updateEvent"
      @add-edit-player="addEditPlayer"
      @remove-edit-player="removeEditPlayer"
    />
  </div>
</template>

<script>
import { useUserStore } from '@/store';
import WelcomeCard from './components/WelcomeCard.vue';
import DataInput from './components/DataInput.vue';
import DataManagement from './components/DataManagement.vue';
import EditDialogs from './components/EditDialogs.vue';

export default {
  name: 'Admin',
  components: {
    WelcomeCard,
    DataInput,
    DataManagement,
    EditDialogs
  },
  data() {
    return {
      activeTab: 'input',
      manageMatchType: '',
      // 编辑相关数据
      editTeamDialog: false,
      editMatchDialog: false,
      editEventDialog: false,
      editTeamForm: {
        id: '',
        teamName: '',
        matchType: '',
        players: []
      },
      editMatchForm: {
        id: '',
        matchName: '',
        team1: '',
        team2: '',
        date: '',
        location: '',
        matchType: ''
      },
      editEventForm: {
        id: '',
        matchName: '',
        eventType: '',
        playerName: '',
        eventTime: '',
        matchType: ''
      }
    };
  },
  computed: {
    userStore() {
      return useUserStore();
    },
    teams() {
      return this.userStore.teams;
    },
    matches() {
      return this.userStore.matches;
    },
    players() {
      return this.userStore.players;
    },
    events() {
      return this.userStore.events;
    },
    loading() {
      return this.userStore.loading;
    }
  },
  methods: {
    async handleTabClick(tab) {
      if (tab.name === 'manage') {
        await this.loadAllData();
      }
    },
    // 统一加载所有数据的方法 - 使用 Store 方法
    async loadAllData() {
      this.userStore.loading = true;
      try {
        console.log('开始加载数据...');
        const results = await Promise.allSettled([
          this.userStore.fetchTeams(),
          this.userStore.fetchMatches(),
          this.userStore.fetchEvents(),
          this.userStore.fetchPlayers()
        ]);
        
        // 检查加载结果
        results.forEach((result, index) => {
          const names = ['球队', '比赛', '事件', '球员'];
          if (result.status === 'rejected') {
            console.error(`加载${names[index]}数据失败:`, result.reason);
          } else {
            console.log(`加载${names[index]}数据成功:`, result.value);
          }
        });
        
        console.log('数据加载完成，当前数据状态:', {
          teams: this.teams.length,
          matches: this.matches.length,
          events: this.events.length,
          players: this.players.length
        });
      } catch (error) {
        console.error('加载数据失败:', error);
        this.$message.error('数据加载失败，请刷新页面重试');
      } finally {
        this.userStore.loading = false;
      }
    },
    handleFilterChange(matchType) {
      this.manageMatchType = matchType;
    },
    async handleTeamSubmit(teamData) {
      const result = await this.userStore.createTeam(teamData);
      if (result.success) {
        this.$message.success('球队信息录入成功');
      } else {
        this.$message.error(result.error || '球队信息录入失败');
      }
    },
    async handleScheduleSubmit(scheduleData) {
      const result = await this.userStore.createMatch(scheduleData);
      if (result.success) {
        this.$message.success('赛程信息录入成功');
      } else {
        this.$message.error(result.error || '赛程信息录入失败');
      }
    },
    async handleEventSubmit(eventData) {
      if (!eventData.matchName) {
        this.$message.error('请选择比赛');
        return;
      }
      if (eventData.events.length === 0) {
        this.$message.error('请至少添加一个事件');
        return;
      }

      const eventPromises = eventData.events.map(event => {
        const newEventData = {
          matchName: eventData.matchName,
          eventType: event.eventType,
          playerName: event.playerName,
          eventTime: event.eventTime,
          matchType: eventData.matchType
        };
        return this.userStore.createEvent(newEventData);
      });

      try {
        const results = await Promise.all(eventPromises);
        const successCount = results.filter(result => result.success).length;
        if (successCount === eventData.events.length) {
          this.$message.success(`成功录入 ${successCount} 个事件`);
        } else {
          this.$message.warning(`录入了 ${successCount}/${eventData.events.length} 个事件`);
        }
      } catch (error) {
        console.error('事件信息录入失败:', error);
        this.$message.error('事件信息录入失败');
      }
    },
    // 编辑球队
    editTeam(team) {
      console.log('编辑球队:', team);
      this.editTeamForm = {
        id: team.id,
        teamName: team.teamName,
        matchType: team.matchType,
        players: team.players ? [...team.players] : []
      };
      this.editTeamDialog = true;
    },
    addEditPlayer() {
      this.editTeamForm.players.push({ name: '', number: '', studentId: '' });
    },
    removeEditPlayer(index) {
      this.editTeamForm.players.splice(index, 1);
    },
    async updateTeam() {
      const result = await this.userStore.updateTeam(this.editTeamForm.id, this.editTeamForm);
      if (result.success) {
        this.$message.success('球队信息更新成功');
        this.editTeamDialog = false;
      } else {
        this.$message.error(result.error || '球队信息更新失败');
      }
    },
    deleteTeam(teamId) {
      this.$confirm('此操作将永久删除该球队, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteTeam(teamId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
      });
    },
    // 编辑比赛
    editMatch(match) {
      this.editMatchForm = {
        id: match.id,
        matchName: match.matchName,
        team1: match.team1,
        team2: match.team2,
        date: match.date,
        location: match.location,
        matchType: match.matchType
      };
      this.editMatchDialog = true;
    },
    async updateMatch() {
      const result = await this.userStore.updateMatch(this.editMatchForm.id, this.editMatchForm);
      if (result.success) {
        this.$message.success('比赛信息更新成功');
        this.editMatchDialog = false;
      } else {
        this.$message.error(result.error || '比赛信息更新失败');
      }
    },
    deleteMatch(matchId) {
      this.$confirm('此操作将永久删除该比赛, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteMatch(matchId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
      });
    },
    // 编辑事件
    editEvent(event) {
      this.editEventForm = {
        id: event.id,
        matchName: event.matchName,
        eventType: event.eventType,
        playerName: event.playerName,
        eventTime: event.eventTime,
        matchType: event.matchType
      };
      this.editEventDialog = true;
    },
    async updateEvent() {
      const result = await this.userStore.updateEvent(this.editEventForm.id, this.editEventForm);
      if (result.success) {
        this.$message.success('事件信息更新成功');
        this.editEventDialog = false;
      } else {
        this.$message.error(result.error || '事件信息更新失败');
      }
    },
    deleteEvent(eventId) {
      this.$confirm('此操作将永久删除该事件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteEvent(eventId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
      });
    },
    goToHome() {
      // 使用页面刷新来跳转到前台
      window.location.href = '/home';
    },
    logout() {
      // 确认退出登录
      this.$confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const userStore = useUserStore();
        userStore.logout();
        // 清除本地存储
        localStorage.removeItem('userToken');
        localStorage.removeItem('userInfo');
        sessionStorage.clear();
        this.$message.success('已退出登录');
        // 使用页面刷新跳转到登录页
        setTimeout(() => {
          window.location.href = '/login';
        }, 500);
      }).catch(() => {
        // 取消退出
      });
    }
  },
  async created() {
    // 页面创建时加载所有数据
    console.log('管理员页面创建，开始加载数据...');
    await this.loadAllData();
  }
};
</script>

<style scoped>
.admin {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.main-content-card {
  min-height: 600px;
}

@media (max-width: 768px) {
  .admin {
    padding: 10px;
  }
}
</style>