<template>
  <div class="team-input-wrapper">
    <el-form ref="teamForm" :model="teamForm" label-width="120px" class="team-form">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="球队名称" required>
            <el-select
              v-model="teamForm.team_name"
              placeholder="请选择或输入球队名称"
              size="large"
              clearable
              filterable
              allow-create
              default-first-option
              class="w-full"
            >
              <el-option
                v-for="team in availableTeams"
                :key="team.id"
                :label="team.team_name"
                :value="team.team_name"
              />
            </el-select>
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
                      v-model="player.student_id" 
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
            
            <div class="append-players-actions">
              <el-button type="success" @click="showPlayerSelector">
                <el-icon><IconSearch /></el-icon>
                选择现有球员
              </el-button>
              <el-button type="primary" @click="addPlayer">
                <el-icon><Plus /></el-icon>
                添加新球员
              </el-button>
            </div>
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
      append-to-body
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
          <div class="players-grid" v-if="filteredExistingPlayers.length > 0">
            <div 
              v-for="player in filteredExistingPlayers" 
              :key="player.id"
              class="player-card-item"
              :class="{ 'selected': selectedPlayers.includes(player.id) }"
              @click="togglePlayerSelection(player)"
            >
              <div class="card-header">
                <span class="player-name">{{ player.name }}</span>
                <el-icon v-if="selectedPlayers.includes(player.id)" class="check-icon"><Check /></el-icon>
              </div>
              <div class="card-body">
                <div class="info-row">
                  <el-icon><Postcard /></el-icon>
                  <span class="info-text">{{ player.student_id }}</span>
                </div>
                <div class="info-row" v-if="player.team_name">
                  <el-icon><UserFilled /></el-icon>
                  <span class="info-text">{{ player.team_name }}</span>
                </div>
                <div class="status-row">
                   <el-tag v-if="!player.number" type="warning" size="small" effect="dark">号码待分配</el-tag>
                   <el-tag v-else type="success" size="small">{{ player.number }}号</el-tag>
                </div>
              </div>
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
import { getMatchTypeLabel } from '@/utils/constants';
import { fetchPlayers } from '@/api/players';
import { createTeam } from '@/api/teams';

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
      type: [String, Number],
      default: ''
    },
    tournamentId: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['submit'],
  data() {
    return {
      teamForm: {
        team_name: '',
        players: []
      },
      playerSelectorVisible: false,
      searchKeyword: '',
      selectedPlayers: [],
      existingPlayers: [],
      availableTeams: [], // 新增：可用球队列表
      loadingPlayers: false,
      submitting: false
    }
  },
  computed: {
    canSubmit() {
      return this.teamForm.team_name.trim() && this.teamForm.players.length > 0
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
    this.fetchAvailableTeams(); // 新增：获取可用球队
  },
  methods: {
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '', student_id: '' });
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
      // 构造 payload，包含 competition_id (传入的 matchType 即为 competition_id) 和 tournament_id
      const payload = { 
        ...this.teamForm,
        competition_id: this.matchType,
        tournament_id: this.tournamentId
      };
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
        this.teamForm = { team_name: '', players: [] };
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
        const { ok, data, error } = await fetchPlayers();
        if (!ok) {
          logger.warn('获取球员列表失败(标准化层)', error);
          this.existingPlayers = [];
          return;
        }
        
        const rawList = data?.data || data || []
        // 处理球员数据，确保字段映射正确
        this.existingPlayers = rawList.map(player => ({
          id: player.id || player.student_id, // 球员ID
          name: player.name || '', // 球员姓名
          number: player.number || '', // 当前球衣号码
          student_id: player.id || player.student_id, // 学号
          team_name: player.team_name || null, // 当前队伍
          match_type: player.match_type || '' // 赛事类型
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
    async fetchAvailableTeams() {
      try {
        // 假设有一个获取所有基础球队的API，或者复用 fetchTeams 获取所有参赛球队并去重
        // 这里暂时复用 fetchTeams，实际可能需要专门的 API 获取 TeamBase
        const { fetchTeams } = await import('@/api/teams');
        const { ok, data } = await fetchTeams();
        if (ok && data) {
          // 去重逻辑
          const uniqueTeams = new Map();
          data.forEach(t => {
            if (!uniqueTeams.has(t.team_name)) {
              uniqueTeams.set(t.team_name, { id: t.team_id, team_name: t.team_name });
            }
          });
          this.availableTeams = Array.from(uniqueTeams.values());
        }
      } catch (e) {
        logger.error('获取可用球队失败', e);
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
      const existingPlayerIds = this.teamForm.players.map(p => p.student_id);
      const validPlayersToAdd = playersToAdd.filter(player => 
        !existingPlayerIds.includes(player.student_id)
      );
      
      if (validPlayersToAdd.length !== playersToAdd.length) {
        const duplicateCount = playersToAdd.length - validPlayersToAdd.length;
        this.$message.warning(`已过滤 ${duplicateCount} 名重复的球员`);
      }
      
      validPlayersToAdd.forEach(player => {
        this.teamForm.players.push({
          name: player.name,
          number: '', // 允许用户后续填写新的球衣号码
          student_id: player.student_id
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
/* 样式已迁移至 input-management.css */
.append-players-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px;
  border-top: 1px dashed #dcdfe6;
}

.player-card {
  min-height: 280px; /* 增加卡片高度以容纳所有信息 */
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.player-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
}

.compact-form-item {
  margin-bottom: 15px;
}
</style>