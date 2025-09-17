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
                <el-icon><IconSearch /></el-icon>
                选择现有球员
              </el-button>
              <el-button type="primary" @click="addPlayer" size="large" class="add-player-btn">
                <el-icon><Plus /></el-icon>
                添加新球员
              </el-button>
            </div>
          </div>

          <div class="players-container" v-if="teamForm.players.length > 0">
            <transition-group name="player-list" tag="div" class="entity-grid grid-cols-2 grid-collapse-sm">
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
                    <el-icon><IconClose /></el-icon>
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
                  <el-icon><IconSearch /></el-icon>
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

      <el-form-item class="submit-form-item entity-submit-zone">
        <el-button 
          type="primary" 
          @click="submitTeam"
          size="large"
          class="submit-btn btn-entity-submit"
          :disabled="!canSubmit || submitting"
          :loading="submitting"
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
              <el-icon><IconSearch /></el-icon>
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
import { User, UserFilled, Plus, Close as IconClose, StarFilled, Postcard, Check, Search as IconSearch, Refresh } from '@element-plus/icons-vue'
import logger from '@/utils/logger';
import { getMatchTypeLabel } from '@/constants/domain';
import { fetchPlayers } from '@/domain/player/playerService';
import { createTeam } from '@/domain/team/teamService';

export default {
  name: 'TeamInput',
  components: {
    User,
    UserFilled,
    Plus,
  IconClose,
    StarFilled,
    Postcard,
    Check,
  IconSearch,
    Refresh
  },
  props: {
    matchType: {
      type: String,
      default: ''
    }
  },
  emits: ['submit'],
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
      loadingPlayers: false,
      submitting: false
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
    async submitTeam() {
      if (this.submitting) return;
      if (!this.canSubmit) {
        this.$message.warning('请填写球队名称并至少添加一名球员');
        return;
      }
      const payload = { ...this.teamForm };
      try {
        this.submitting = true;
        const { ok, data, error } = await createTeam(payload);
        if (!ok) {
          this.$message.error(error?.message || '创建球队失败');
          return;
        }
        try {
          import('@/utils/httpClient').then(m=>{
            m.default.cache.invalidate('teams:list')
            m.default.cache.invalidate('stats:dashboard')
          })
  } catch { /* ignore cache invalidation error */ }
        this.$message.success('球队创建成功');
        this.$emit('submit', data || payload);
        this.teamForm = { teamName: '', players: [] };
      } catch (err) {
        logger.error('创建球队异常', err);
        this.$message.error('创建球队异常');
      } finally {
        this.submitting = false;
      }
    },
    getMatchTypeLabel() {
      return getMatchTypeLabel(this.matchType);
    },
    async fetchExistingPlayers() {
      this.loadingPlayers = true;
      try {
        const { ok, data: playersData, error } = await fetchPlayers();
        if (!ok) {
          logger.warn('获取球员列表失败(标准化层)', error);
          this.existingPlayers = [];
          return;
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
        
  logger.debug('处理后的球员数据:', this.existingPlayers.length, '名有效球员');
        
      } catch (err) {
        logger.error('获取球员列表异常:', err);
        this.$message.error('获取球员列表失败');
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
  logger.info('球员列表为空，重新获取数据');
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
  logger.debug('当前选中的球员ID:', this.selectedPlayers);
    },
    confirmSelectPlayers() {
      const playersToAdd = this.existingPlayers.filter(player => 
        this.selectedPlayers.includes(player.id)
      );
      
  logger.debug('准备添加的球员:', playersToAdd);
      
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
/* 样式已迁移至 admin-management.css (.team-input-wrapper...) */
</style>
