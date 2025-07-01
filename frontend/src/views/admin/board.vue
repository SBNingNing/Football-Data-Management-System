<template>
  <div class="admin-container">
    <!-- 管理员欢迎卡片 -->
    <WelcomeCard 
      @go-to-home="goToHome"
      @logout="logout"
    />

    <!-- 功能标签页 -->
    <div class="main-content">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="admin-tabs">
        <!-- 信息管理标签页 -->
        <el-tab-pane name="manage">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon>
              信息管理
            </span>
          </template>
          <div class="tab-content">
            <DataManagement 
              :teams="teams"
              :matches="matches"
              :events="events"
              :players="players"
              :manage-match-type="manageMatchType"
              @filter-change="handleFilterChange"
              @refresh="loadAllData"
              @edit-team="editTeam"
              @delete-team="deleteTeam"
              @edit-match="editMatch"
              @delete-match="deleteMatch"
              @edit-event="editEvent"
              @delete-event="deleteEvent"
              @edit-player="editPlayer"
              @delete-player="deletePlayer"
              @complete-match="completeMatch"
            />
          </div>
        </el-tab-pane>

        <!-- 信息录入标签页 -->
        <el-tab-pane name="input">
          <template #label>
            <span class="tab-label">
              <el-icon><EditPen /></el-icon>
              信息录入
            </span>
          </template>
          <div class="tab-content">
            <DataInput 
              ref="dataInputRef"
              :teams="teams"
              :matches="matches"
              :events="events"
              @team-submit="handleTeamSubmit"
              @schedule-submit="handleScheduleSubmit"
              @event-submit="handleEventSubmit"
              @refresh-data="loadAllData"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 编辑对话框组件 -->
    <EditDialogs
      :edit-team-dialog="editTeamDialog"
      :edit-match-dialog="editMatchDialog"
      :edit-event-dialog="editEventDialog"
      :edit-player-dialog="editPlayerDialog"
      :edit-team-form="editTeamForm"
      :edit-match-form="editMatchForm"
      :edit-event-form="editEventForm"
      :edit-player-form="editPlayerForm"
      :teams="teams"
      :matches="matches"
      :players="players"
      @close-team-dialog="editTeamDialog = false"
      @close-match-dialog="editMatchDialog = false"
      @close-event-dialog="editEventDialog = false"
      @close-player-dialog="editPlayerDialog = false"
      @update-team="updateTeam"
      @update-match="updateMatch"
      @update-event="updateEvent"
      @update-player="updatePlayer"
      @add-edit-player="addEditPlayer"
      @remove-edit-player="removeEditPlayer"
    />

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <el-icon class="loading-icon is-loading"><Loading /></el-icon>
        <p class="loading-text">正在加载数据...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '@/store';
import WelcomeCard from '@/components/admin/WelcomeCard.vue';
import DataInput from '@/components/admin/DataInput.vue';
import DataManagement from '@/components/admin/DataManagement.vue';
import EditDialogs from '@/components/admin/EditDialogs.vue';
import { Setting, EditPen, Loading } from '@element-plus/icons-vue';

export default {
  name: 'Admin',
  components: {
    WelcomeCard,
    DataInput,
    DataManagement,
    EditDialogs,
    Setting,
    EditPen,
    Loading
  },
  data() {
    return {
      activeTab: 'manage',
      manageMatchType: '',
      // 编辑相关数据
      editTeamDialog: false,
      editMatchDialog: false,
      editEventDialog: false,
      editPlayerDialog: false,
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
      },
      editPlayerForm: {
        id: '',
        name: '',
        number: '',
        studentId: '',
        teamName: '',
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
      } else if (tab.name === 'input') {
        // 切换到录入页面时也刷新数据，确保数据是最新的
        await this.loadAllData();
      }
    },

    // 滚动到指定的录入模块
    scrollToInputModule(moduleType) {
      if (this.$refs.dataInputRef && this.$refs.dataInputRef.scrollToModule) {
        this.$refs.dataInputRef.scrollToModule(moduleType);
      }
    },

    // 添加一个处理录入类型点击的方法
    handleInputTypeClick(inputType) {
      // 如果当前不在录入标签页，先切换到录入标签页
      if (this.activeTab !== 'input') {
        this.activeTab = 'input';
        // 等待DOM更新后再滚动
        this.$nextTick(() => {
          this.scrollToInputModule(inputType);
        });
      } else {
        // 如果已经在录入标签页，直接滚动
        this.scrollToInputModule(inputType);
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
            this.$message.warning(`加载${names[index]}数据失败: ${result.reason?.message || '未知错误'}`);
          } else if (result.value && !result.value.success) {
            console.error(`加载${names[index]}数据失败:`, result.value.error);
            this.$message.warning(`加载${names[index]}数据失败: ${result.value.error}`);
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
      try {
        const result = await this.userStore.createTeam(teamData);
        if (result.success) {
          this.$message.success('球队信息录入成功');
          // 重新加载球队数据
          await this.userStore.fetchTeams();
        } else {
          this.$message.error(result.error || '球队信息录入失败');
        }
      } catch (error) {
        console.error('录入球队失败:', error);
        this.$message.error('球队信息录入失败');
      }
    },
    
    async handleScheduleSubmit(scheduleData) {
      try {
        const result = await this.userStore.createMatch(scheduleData);
        if (result.success) {
          this.$message.success('赛程信息录入成功');
          // 重新加载比赛数据
          await this.userStore.fetchMatches();
        } else {
          this.$message.error(result.error || '赛程信息录入失败');
        }
      } catch (error) {
        console.error('录入赛程失败:', error);
        this.$message.error('赛程信息录入失败');
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

      try {
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

        const results = await Promise.all(eventPromises);
        const successCount = results.filter(result => result.success).length;
        
        if (successCount === eventData.events.length) {
          this.$message.success(`成功录入 ${successCount} 个事件`);
          // 重新加载事件数据
          await this.userStore.fetchEvents();
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
    // 编辑球员
    editPlayer(player) {
      console.log('编辑球员:', player);
      this.editPlayerForm = {
        id: player.id || player.studentId,
        name: player.name,
        number: player.number,
        studentId: player.studentId || player.id,
        teamName: player.teamName,
        matchType: player.matchType
      };
      this.editPlayerDialog = true;
    },
    async updatePlayer() {
      try {
        const playerId = this.editPlayerForm.id || this.editPlayerForm.studentId;
        const result = await this.userStore.updatePlayer(playerId, this.editPlayerForm);
        if (result.success) {
          this.$message.success('球员信息更新成功');
          this.editPlayerDialog = false;
          // 重新加载球员数据
          await this.userStore.fetchPlayers();
        } else {
          this.$message.error(result.error || '球员信息更新失败');
        }
      } catch (error) {
        console.error('更新球员失败:', error);
        this.$message.error('球员信息更新失败');
      }
    },
    deletePlayer(playerId) {
      this.$confirm('此操作将永久删除该球员, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const result = await this.userStore.deletePlayer(playerId);
          if (result.success) {
            this.$message.success('删除成功');
          } else {
            this.$message.error(result.error || '删除失败');
          }
        } catch (error) {
          console.error('删除球员失败:', error);
          this.$message.error('删除失败');
        }
      });
    },
    // 完赛处理函数
    completeMatch(matchId) {
      this.$confirm('确定要标记该比赛为已完赛吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const result = await this.userStore.completeMatch(matchId);
          if (result.success) {
            this.$message.success('比赛已标记为完赛');
            // 重新加载比赛数据
            await this.userStore.fetchMatches();
          } else {
            this.$message.error(result.error || '操作失败');
          }
        } catch (error) {
          console.error('完赛操作失败:', error);
          this.$message.error('操作失败，请重试');
        }
      }).catch(() => {
        // 取消操作
      });
    },
    goToHome() {
      // 使用路由跳转到前台主页
      this.$router.push('/home');
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
        // 使用路由跳转到登录页
        setTimeout(() => {
          this.$router.push('/login');
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
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
  position: relative;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 20px;
}

/* 标签页样式优化 */
.admin-tabs {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #e5e7eb;
  backdrop-filter: blur(10px);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.tab-content {
  padding: 0;
  background: linear-gradient(135deg, #fafbfc 0%, #f8fafc 100%);
  min-height: 600px;
}

/* 标签页头部样式 */
:deep(.el-tabs__header) {
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-bottom: 1px solid #e5e7eb;
  padding: 8px 0;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0 32px;
}

:deep(.el-tabs__item) {
  height: 64px;
  line-height: 64px;
  padding: 0 28px;
  font-size: 15px;
  color: #6b7280;
  border: none;
  position: relative;
  transition: all 0.3s ease;
  border-radius: 12px;
  margin: 0 4px;
}

:deep(.el-tabs__item:hover) {
  color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.05));
  transform: translateY(-1px);
}

:deep(.el-tabs__item.is-active) {
  color: #3b82f6;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(59, 130, 246, 0.08));
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transform: translateY(-1px);
}

:deep(.el-tabs__active-bar) {
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border-radius: 2px;
  bottom: 8px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  padding: 32px;
}

/* 移除信息录入标签页下方间隔 */
:deep(.el-tab-pane[aria-labelledby="tab-input"]) {
  padding: 32px 32px 0 32px;
}

/* DataInput 组件底部无间距 */
:deep(.el-tab-pane[aria-labelledby="tab-input"] > .tab-content) {
  padding: 0;
  margin: 0;
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.loading-icon {
  font-size: 48px;
  color: #3b82f6;
  margin-bottom: 16px;
}

.loading-text {
  margin: 0;
  color: #6b7280;
  font-size: 16px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    max-width: 100%;
    padding: 0 16px 16px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 0 12px 12px;
  }
  
  :deep(.el-tabs__nav-wrap) {
    padding: 0 16px;
  }
  
  :deep(.el-tabs__item) {
    padding: 0 20px;
    font-size: 14px;
    height: 56px;
    line-height: 56px;
  }
  
  :deep(.el-tab-pane) {
    padding: 20px;
  }
  
  .tab-label {
    gap: 4px;
    padding: 4px 8px;
  }

  .loading-content {
    margin: 20px;
    padding: 32px 24px;
  }
  
  .loading-icon {
    font-size: 40px;
  }
  
  .loading-text {
    font-size: 14px;
  }
}

/* 全局样式优化 */
:deep(.el-card) {
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

:deep(.el-card__header) {
  border-bottom: 1px solid #f0f2f5;
  background: linear-gradient(135deg, #fafbfc 0%, #f8fafc 100%);
  border-radius: 16px 16px 0 0;
}

:deep(.el-button) {
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #2563eb, #1e40af);
}

/* 滚动条样式 */
:deep(::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: #f1f5f9;
  border-radius: 4px;
}

:deep(::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  border-radius: 4px;
  transition: background 0.3s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, #94a3b8, #64748b);
}
</style>