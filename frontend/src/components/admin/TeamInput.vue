<template>
  <div class="team-input-wrapper">
    <el-form ref="teamForm" :model="teamForm" label-width="120px" class="team-form">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="球队名称" required>
            <el-input 
              v-model="teamForm.teamName" 
              placeholder="请输入球队名称"
              size="large"
              clearable
              maxlength="50"
              show-word-limit
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="球员信息" class="players-form-item">
        <div class="player-management">
          <div class="player-header">
            <div class="header-left">
              <h4 class="players-title">
                <el-icon><User /></el-icon>
                球员管理
              </h4>
              <span class="player-count">
                已添加 <strong>{{ teamForm.players.length }}</strong> 名球员
              </span>
            </div>
            <div class="header-actions">
              <el-button type="success" @click="showPlayerSelector" size="large" class="select-player-btn">
                <el-icon><Search /></el-icon>
                选择现有球员
              </el-button>
              <el-button type="primary" @click="addPlayer" size="large" class="add-player-btn">
                <el-icon><Plus /></el-icon>
                添加新球员
              </el-button>
            </div>
          </div>

          <div class="players-container" v-if="teamForm.players.length > 0">
            <transition-group name="player-list" tag="div" class="players-grid-two-columns">
              <div 
                v-for="(player, index) in teamForm.players" 
                :key="`player-${index}`" 
                class="player-card"
              >
                <div class="player-card-header">
                  <div class="player-number-badge">
                    <span class="badge-text">#{{ index + 1 }}</span>
                  </div>
                  <el-button 
                    type="primary" 
                    link
                    @click="removePlayer(index)" 
                    class="delete-btn"
                    size="small"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
                
                <div class="player-form">
                  <el-form-item label="姓名" class="compact-form-item">
                    <el-input 
                      v-model="player.name" 
                      placeholder="球员姓名"
                      maxlength="20"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item label="号码" class="compact-form-item">
                    <el-input 
                      v-model="player.number" 
                      placeholder="球衣号码"
                      type="number"
                      min="1"
                      max="99"
                    >
                      <template #prefix>
                        <el-icon><StarFilled /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item label="学号" class="compact-form-item">
                    <el-input 
                      v-model="player.studentId" 
                      placeholder="学号"
                      maxlength="20"
                    >
                      <template #prefix>
                        <el-icon><Postcard /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </div>
              </div>
            </transition-group>
          </div>

          <div v-else class="empty-players">
            <el-empty 
              description="暂无球员信息"
              :image-size="80"
            >
              <template #image>
                <el-icon size="80" color="#c0c4cc"><UserFilled /></el-icon>
              </template>
              <div class="empty-actions">
                <el-button type="success" @click="showPlayerSelector">
                  <el-icon><Search /></el-icon>
                  选择现有球员
                </el-button>
                <el-button type="primary" @click="addPlayer">
                  <el-icon><Plus /></el-icon>
                  添加新球员
                </el-button>
              </div>
            </el-empty>
          </div>
        </div>
      </el-form-item>

      <el-form-item class="submit-form-item">
        <el-button 
          type="primary" 
          @click="submitTeam"
          size="large"
          class="submit-btn"
          :disabled="!canSubmit"
        >
          <el-icon><Check /></el-icon>
          提交球队信息
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 选择现有球员对话框 -->
    <el-dialog 
      v-model="playerSelectorVisible" 
      title="选择现有球员" 
      width="800px"
      class="player-selector-dialog"
    >
      <div class="player-selector-content">
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索球员姓名或学号"
            clearable
            size="large"
            class="search-input"
            :disabled="loadingPlayers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button 
            @click="fetchExistingPlayers" 
            :loading="loadingPlayers"
            type="primary"
            class="refresh-btn"
          >
            <el-icon v-if="!loadingPlayers"><Refresh /></el-icon>
            刷新列表
          </el-button>
        </div>
        
        <div class="existing-players-list" v-loading="loadingPlayers">
          <div 
            v-for="player in filteredExistingPlayers" 
            :key="player.id"
            class="existing-player-item"
            :class="{ 'selected': selectedPlayers.includes(player.id) }"
            @click="togglePlayerSelection(player)"
          >
            <div class="player-info">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-details">
                <span class="player-student-id">学号: {{ player.studentId }}</span>
                <span class="player-note" v-if="!player.number">球衣号码待分配</span>
              </div>
            </div>
            <div class="selection-indicator">
              <el-icon v-if="selectedPlayers.includes(player.id)" color="#67c23a">
                <Check />
              </el-icon>
            </div>
          </div>
          
          <div v-if="!loadingPlayers && filteredExistingPlayers.length === 0" class="no-players">
            <el-empty description="暂无匹配的球员" :image-size="60">
              <el-button @click="fetchExistingPlayers" type="primary">
                重新加载
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="playerSelectorVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmSelectPlayers"
            :disabled="selectedPlayers.length === 0 || loadingPlayers"
          >
            确认选择 ({{ selectedPlayers.length }})
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { User, UserFilled, Plus, Close, StarFilled, Postcard, Check, Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'TeamInput',
  components: {
    User,
    UserFilled,
    Plus,
    Close,
    StarFilled,
    Postcard,
    Check,
    Search,
    Refresh
  },
  props: {
    matchType: String
  },
  data() {
    return {
      teamForm: {
        teamName: '',
        players: []
      },
      playerSelectorVisible: false,
      searchKeyword: '',
      selectedPlayers: [],
      existingPlayers: [],
      loadingPlayers: false
    }
  },
  computed: {
    canSubmit() {
      return this.teamForm.teamName.trim() && this.teamForm.players.length > 0
    },
    filteredExistingPlayers() {
      if (!this.searchKeyword) {
        return this.existingPlayers;
      }
      return this.existingPlayers.filter(player => 
        player.name.includes(this.searchKeyword) || 
        player.id.includes(this.searchKeyword)
      );
    }
  },
  mounted() {
    this.fetchExistingPlayers();
  },
  methods: {
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '', studentId: '' });
    },
    removePlayer(index) {
      this.teamForm.players.splice(index, 1);
    },
    submitTeam() {
      if (!this.canSubmit) {
        this.$message.warning('请填写球队名称并至少添加一名球员');
        return;
      }
      
      this.$emit('submit', this.teamForm);
      this.teamForm = { teamName: '', players: [] };
    },
    getMatchTypeLabel() {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return labels[this.matchType] || '';
    },
    async fetchExistingPlayers() {
      this.loadingPlayers = true;
      try {
        const response = await axios.get('/api/players');
        
        // 检查响应数据格式
        let playersData = [];
        if (response.data?.status === 'success') {
          playersData = response.data.data || [];
          console.log('成功获取球员列表 (success格式):', playersData.length, '名球员');
        } else if (Array.isArray(response.data)) {
          playersData = response.data;
          console.log('成功获取球员列表 (数组格式):', playersData.length, '名球员');
        } else if (response.data && Array.isArray(response.data.data)) {
          playersData = response.data.data;
          console.log('成功获取球员列表 (嵌套格式):', playersData.length, '名球员');
        } else {
          console.warn('意外的响应格式:', response.data);
          playersData = [];
        }
        
        // 处理球员数据，确保字段映射正确
        this.existingPlayers = playersData.map(player => ({
          id: player.id || player.studentId, // 球员ID
          name: player.name || '', // 球员姓名
          number: player.number || '', // 当前球衣号码
          studentId: player.id || player.studentId, // 学号
          teamName: player.teamName || null, // 当前队伍
          matchType: player.matchType || 'champions-cup' // 赛事类型
        })).filter(player => player.id && player.name); // 过滤掉无效数据
        
        console.log('处理后的球员数据:', this.existingPlayers.length, '名有效球员');
        
      } catch (error) {
        console.error('获取球员列表失败:', error);
        
        // 更详细的错误处理
        let errorMessage = '获取球员列表失败';
        if (error.response) {
          if (error.response.status === 404) {
            errorMessage = '球员接口不存在，请检查后端服务';
          } else if (error.response.status === 500) {
            errorMessage = `服务器内部错误: ${error.response.data?.message || '请联系管理员'}`;
          } else {
            errorMessage = `服务器错误 (${error.response.status}): ${error.response.data?.message || '未知错误'}`;
          }
        } else if (error.request) {
          errorMessage = '网络连接失败，请检查网络设置';
        } else {
          errorMessage = `请求失败: ${error.message}`;
        }
        
        this.$message.error(errorMessage);
        this.existingPlayers = [];
      } finally {
        this.loadingPlayers = false;
      }
    },
    async showPlayerSelector() {
      this.playerSelectorVisible = true;
      this.selectedPlayers = [];
      this.searchKeyword = '';
      
      // 如果球员列表为空或数据可能过时，重新获取
      if (this.existingPlayers.length === 0) {
        console.log('球员列表为空，重新获取数据');
        await this.fetchExistingPlayers();
      }
    },
    togglePlayerSelection(player) {
      const index = this.selectedPlayers.indexOf(player.id);
      if (index > -1) {
        this.selectedPlayers.splice(index, 1);
      } else {
        this.selectedPlayers.push(player.id);
      }
      console.log('当前选中的球员ID:', this.selectedPlayers);
    },
    confirmSelectPlayers() {
      const playersToAdd = this.existingPlayers.filter(player => 
        this.selectedPlayers.includes(player.id)
      );
      
      console.log('准备添加的球员:', playersToAdd);
      
      // 检查是否有重复的球员
      const existingPlayerIds = this.teamForm.players.map(p => p.studentId);
      const validPlayersToAdd = playersToAdd.filter(player => 
        !existingPlayerIds.includes(player.studentId)
      );
      
      if (validPlayersToAdd.length !== playersToAdd.length) {
        const duplicateCount = playersToAdd.length - validPlayersToAdd.length;
        this.$message.warning(`已过滤 ${duplicateCount} 名重复的球员`);
      }
      
      validPlayersToAdd.forEach(player => {
        this.teamForm.players.push({
          name: player.name,
          number: '', // 允许用户后续填写新的球衣号码
          studentId: player.studentId
        });
      });
      
      this.playerSelectorVisible = false;
      
      if (validPlayersToAdd.length > 0) {
        this.$message.success(`已添加 ${validPlayersToAdd.length} 名球员`);
      } else {
        this.$message.info('没有新球员被添加');
      }
    }
  }
}
</script>

<style scoped>
.team-input-wrapper {
  padding: 24px 24px 0 24px;
  background: white;
}

.team-form {
  max-width: none;
}

/* 球员管理区域 */
.players-form-item {
  margin-bottom: 32px;
}

.player-management {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fafbfc;
  overflow: hidden;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.players-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.players-title .el-icon {
  margin-right: 8px;
  color: #3b82f6;
}

.player-count {
  padding: 4px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 16px;
  font-size: 13px;
  color: #6b7280;
}

.player-count strong {
  color: #1f2937;
  font-weight: 600;
}

.add-player-btn {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.add-player-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 球员管理头部 */
.header-actions {
  display: flex;
  gap: 12px;
}

.select-player-btn {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.2);
  transition: all 0.3s ease;
}

.select-player-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

/* 球员卡片网格 */
.players-container {
  padding: 24px;
  max-height: 500px;
  overflow-y: auto;
}

.players-grid-two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.player-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
  min-width: 0; /* 防止内容溢出 */
}

.player-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.player-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.player-number-badge {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-text {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.delete-btn {
  color: #ef4444;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background: #fef2f2;
  color: #dc2626;
  transform: scale(1.1);
}

/* 紧凑表单项 */
.compact-form-item {
  margin-bottom: 16px;
}

.compact-form-item :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 6px;
}

.compact-form-item :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.compact-form-item :deep(.el-input__wrapper:hover) {
  border-color: #3b82f6;
}

/* 空状态 */
.empty-players {
  padding: 40px 24px;
  text-align: center;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
}

/* 提交按钮 */
.submit-form-item {
  margin-bottom: 0;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.submit-btn {
  min-width: 160px;
  height: 44px;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(34, 197, 94, 0.2);
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 选择球员对话框样式 */
.player-selector-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.player-selector-content {
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.refresh-btn {
  border-radius: 8px;
  min-width: 100px;
}

.player-note {
  color: #f56c6c;
  font-size: 12px;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.existing-players-list {
  flex: 1;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  position: relative;
}

.existing-player-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.existing-player-item:hover {
  background: #f8fafc;
}

.existing-player-item.selected {
  background: #ecfdf5;
  border-color: #22c55e;
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.player-details {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
}

.player-student-id {
  color: #4b5563;
}

.selection-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-players {
  padding: 40px;
  text-align: center;
}

/* 动画效果 */
.player-list-enter-active,
.player-list-leave-active {
  transition: all 0.3s ease;
}

.player-list-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

.player-list-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}

.player-list-move {
  transition: transform 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .player-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-left {
    justify-content: space-between;
  }

  .header-actions {
    justify-content: center;
  }

  .players-grid-two-columns {
    grid-template-columns: 1fr;
  }

  .empty-actions {
    flex-direction: column;
    align-items: center;
  }

  .player-selector-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto;
  }

  .player-details {
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 1200px) and (min-width: 769px) {
  .players-grid-two-columns {
    gap: 16px;
  }
  
  .player-card {
    padding: 16px;
  }
}
</style>
