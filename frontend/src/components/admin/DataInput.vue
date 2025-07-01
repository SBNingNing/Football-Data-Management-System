<template>
  <div class="data-input-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h2 class="page-title">
            <el-icon class="title-icon"><EditPen /></el-icon>
            信息录入管理
          </h2>
          <p class="page-description">请先选择比赛类型，然后选择要录入的信息类型进行操作</p>
        </div>
        <div class="header-actions" v-if="currentMatchType">
          <el-button 
            type="primary" 
            @click="refreshData" 
            :icon="Refresh" 
            size="large"
            class="refresh-button"
          >
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-container">
      <el-steps :active="currentStep" align-center finish-status="success" process-status="process">
        <el-step title="选择比赛类型" :icon="Trophy"></el-step>
        <el-step title="选择录入类型" :icon="MenuIcon"></el-step>
        <el-step title="录入信息" :icon="EditPen"></el-step>
      </el-steps>
    </div>

    <!-- 比赛类型选择 -->
    <el-card class="match-type-card" shadow="hover" v-show="currentStep >= 0" ref="matchTypeCard">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Trophy /></el-icon>
            选择比赛类型
          </span>
          <div class="header-right">
            <el-tag v-if="currentMatchType" :type="getMatchTypeTagType(currentMatchType)" size="large" class="current-type-tag">
              {{ getMatchTypeLabel(currentMatchType) }}
            </el-tag>
            <el-button 
              v-if="currentMatchType" 
              type="primary" 
              @click="refreshData" 
              :icon="Refresh" 
              size="small"
              class="header-refresh-btn"
              circle
              title="刷新数据"
            />
          </div>
        </div>
      </template>
      
      <div class="match-type-content">
        <el-row :gutter="32">
          <el-col :lg="10" :md="12" :sm="24">
            <div class="type-selector-wrapper">
              <el-form-item label="选择比赛类型" class="type-select-item">
                <el-select 
                  v-model="matchTypeForm.matchType" 
                  placeholder="请选择比赛类型" 
                  @change="handleMatchTypeChange"
                  size="large"
                  style="width: 100%;"
                  clearable
                  class="type-selector"
                  popper-class="match-type-dropdown"
                >
                  <el-option 
                    label="冠军杯 - 男子组比赛" 
                    value="champions-cup"
                    class="match-option"
                  >
                    <div class="option-content">
                      <span class="option-icon">🏆</span>
                      <div class="option-info">
                        <div class="option-name">冠军杯</div>
                        <div class="option-desc">男子组比赛</div>
                      </div>
                    </div>
                  </el-option>
                  <el-option 
                    label="巾帼杯 - 女子组比赛" 
                    value="womens-cup"
                    class="match-option"
                  >
                    <div class="option-content">
                      <span class="option-icon">👑</span>
                      <div class="option-info">
                        <div class="option-name">巾帼杯</div>
                        <div class="option-desc">女子组比赛</div>
                      </div>
                    </div>
                  </el-option>
                  <el-option 
                    label="八人制比赛 - 混合组比赛" 
                    value="eight-a-side"
                    class="match-option"
                  >
                    <div class="option-content">
                      <span class="option-icon">⚽</span>
                      <div class="option-info">
                        <div class="option-name">八人制比赛</div>
                        <div class="option-desc">混合组比赛</div>
                      </div>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </div>
          </el-col>
          <el-col :lg="14" :md="12" :sm="24">
            <div class="match-type-info" v-if="currentMatchType">
              <div class="info-header">
                <h4 class="info-title">{{ getMatchTypeLabel(currentMatchType) }} 统计信息</h4>
              </div>
              <div class="info-grid">
                <div class="info-card teams-card">
                  <div class="info-icon teams-icon">
                    <el-icon><UserFilled /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-value">{{ filteredTeams.length }}</div>
                    <div class="info-label">已注册球队</div>
                  </div>
                  <div class="info-trend">
                    <el-icon class="trend-icon"><ArrowUp /></el-icon>
                  </div>
                </div>
                <div class="info-card matches-card">
                  <div class="info-icon matches-icon">
                    <el-icon><Trophy /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-value">{{ filteredMatches.length }}</div>
                    <div class="info-label">已安排比赛</div>
                  </div>
                  <div class="info-trend">
                    <el-icon class="trend-icon"><ArrowUp /></el-icon>
                  </div>
                </div>
                <div class="info-card events-card">
                  <div class="info-icon events-icon">
                    <el-icon><Flag /></el-icon>
                  </div>
                  <div class="info-content">
                    <div class="info-value">{{ getEventCount() }}</div>
                    <div class="info-label">比赛事件</div>
                  </div>
                  <div class="info-trend">
                    <el-icon class="trend-icon"><ArrowUp /></el-icon>
                  </div>
                </div>
              </div>
            </div>
            <div class="no-match-type" v-else>
              <div class="empty-illustration">
                <el-icon class="empty-icon"><Warning /></el-icon>
                <span class="empty-text">请先选择比赛类型</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 录入类型选择 -->
    <div v-if="currentMatchType" class="input-type-selection" ref="typeSelectionContainer">
      <el-card shadow="hover" class="selection-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><MenuIcon /></el-icon>
              选择录入类型
            </span>
          </div>
        </template>
        
        <div class="type-cards-container">
          <div 
            class="type-card teams-card" 
            :class="{ active: selectedInputType === 'team' }"
            @click="selectInputType('team')"
          >
            <div class="type-card-icon teams-bg">
              <el-icon><UserFilled /></el-icon>
            </div>
            <h4 class="type-card-title">球队信息</h4>
            <p class="type-card-desc">录入球队基本信息和球员名单</p>
            <div class="type-card-stats">
              <span class="stats-text">已录入 {{ filteredTeams.length }} 支球队</span>
            </div>
          </div>

          <div 
            class="type-card schedule-card" 
            :class="{ active: selectedInputType === 'schedule' }"
            @click="selectInputType('schedule')"
          >
            <div class="type-card-icon schedule-bg">
              <el-icon><Calendar /></el-icon>
            </div>
            <h4 class="type-card-title">赛程安排</h4>
            <p class="type-card-desc">安排比赛时间地点和对阵信息</p>
            <div class="type-card-stats">
              <span class="stats-text">已安排 {{ filteredMatches.length }} 场比赛</span>
            </div>
          </div>

          <div 
            class="type-card events-card" 
            :class="{ active: selectedInputType === 'event' }"
            @click="selectInputType('event')"
          >
            <div class="type-card-icon events-bg">
              <el-icon><Flag /></el-icon>
            </div>
            <h4 class="type-card-title">比赛事件</h4>
            <p class="type-card-desc">录入比赛过程中的进球、红黄牌等事件</p>
            <div class="type-card-stats">
              <span class="stats-text">已录入 {{ getEventCount() }} 个事件</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 信息录入区域 -->
    <div v-if="selectedInputType" class="input-form-container" ref="inputFormContainer">
      <transition name="slide-fade" mode="out-in">
        <!-- 球队信息录入 -->
        <el-card v-if="selectedInputType === 'team'" key="team" shadow="hover" class="form-card">
          <template #header>
            <div class="form-header">
              <h3 class="form-title">
                <el-icon class="form-icon teams-color"><UserFilled /></el-icon>
                球队信息录入
              </h3>
              <el-button @click="goBackToSelection" text>
                <el-icon><Close /></el-icon>
                返回选择
              </el-button>
            </div>
          </template>
          <TeamInput 
            :match-type="currentMatchType"
            :teams="filteredTeams"
            @submit="handleTeamSubmit"
            class="input-component"
          />
        </el-card>

        <!-- 赛程信息录入 -->
        <el-card v-else-if="selectedInputType === 'schedule'" key="schedule" shadow="hover" class="form-card">
          <template #header>
            <div class="form-header">
              <h3 class="form-title">
                <el-icon class="form-icon schedule-color"><Calendar /></el-icon>
                赛程信息录入
              </h3>
              <el-button @click="goBackToSelection" text>
                <el-icon><Close /></el-icon>
                返回选择
              </el-button>
            </div>
          </template>
          <ScheduleInput 
            :match-type="currentMatchType"
            :teams="filteredTeams"
            @submit="handleScheduleSubmit"
            class="input-component"
          />
        </el-card>

        <!-- 事件信息录入 -->
        <el-card v-else-if="selectedInputType === 'event'" key="event" shadow="hover" class="form-card">
          <template #header>
            <div class="form-header">
              <h3 class="form-title">
                <el-icon class="form-icon events-color"><Flag /></el-icon>
                比赛事件录入
              </h3>
              <el-button @click="goBackToSelection" text>
                <el-icon><Close /></el-icon>
                返回选择
              </el-button>
            </div>
          </template>
          <EventInput 
            :match-type="currentMatchType"
            :matches="filteredMatches"
            :teams="filteredTeams"
            @submit="handleEventSubmit"
            class="input-component"
          />
        </el-card>
      </transition>
    </div>

    <!-- 空状态提示 -->
    <div v-if="!currentMatchType" class="empty-state">
      <el-empty 
        description="请先选择比赛类型开始录入"
        :image-size="160"
      >
        <template #image>
          <div class="empty-icon">
            <el-icon size="160" color="#d1d5db"><Box /></el-icon>
          </div>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script>
import TeamInput from './TeamInput.vue'
import ScheduleInput from './ScheduleInput.vue'
import EventInput from './EventInput.vue'
import { 
  EditPen, 
  Trophy, 
  UserFilled, 
  Calendar, 
  Flag, 
  Warning, 
  Box,
  Menu as MenuIcon,
  Close,
  Refresh,
  ArrowUp
} from '@element-plus/icons-vue'

export default {
  name: 'DataInput',
  components: {
    TeamInput,
    ScheduleInput,
    EventInput,
    EditPen,
    Trophy,
    UserFilled,
    Calendar,
    Flag,
    Warning,
    Box,
    MenuIcon,
    Close,
    Refresh,
    ArrowUp
  },
  props: {
    teams: Array,
    matches: Array,
    events: Array
  },
  data() {
    return {
      matchTypeForm: {
        matchType: ''
      },
      currentMatchType: '',
      selectedInputType: '', // 'team', 'schedule', 'event'
      currentStep: 0
    }
  },
  computed: {
    filteredTeams() {
      return this.teams.filter(team => team.matchType === this.currentMatchType);
    },
    filteredMatches() {
      return this.matches.filter(match => match.matchType === this.currentMatchType);
    }
  },
  methods: {
    handleMatchTypeChange(value) {
      this.currentMatchType = value;
      this.selectedInputType = '';
      this.currentStep = value ? 1 : 0;
      
      // 如果选择了比赛类型，滚动到类型选择区域
      if (value) {
        this.$nextTick(() => {
          this.scrollToTypeSelectionAfterMatchType();
        });
      }
    },
    selectInputType(type) {
      this.selectedInputType = type;
      this.currentStep = 2;
      
      // 延迟滚动，等待DOM更新，滚动到页面底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    scrollToBottom() {
      // 滚动到页面底部
      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: 'smooth'
        });
      }, 100); // 稍微延迟确保DOM完全渲染
    },
    scrollToInputForm() {
      if (this.$refs.inputFormContainer) {
        // 计算滚动位置，在表单容器上方留出更大的空间
        const element = this.$refs.inputFormContainer;
        const elementTop = element.offsetTop;
        const offset = 150; // 增加距离顶部的偏移量
        
        // 平滑滚动到目标位置
        window.scrollTo({
          top: elementTop - offset,
          behavior: 'smooth'
        });
      }
    },
    scrollToTypeSelectionAfterMatchType() {
      // 当选择比赛类型后，滚动到类型选择区域
      if (this.$refs.typeSelectionContainer) {
        const element = this.$refs.typeSelectionContainer;
        const elementTop = element.offsetTop;
        const offset = 120; // 适中的偏移量
        
        window.scrollTo({
          top: elementTop - offset,
          behavior: 'smooth'
        });
      } else {
        // 如果类型选择区域还未渲染，等待一下再滚动
        setTimeout(() => {
          const typeSelectionElement = document.querySelector('.input-type-selection');
          if (typeSelectionElement) {
            const elementTop = typeSelectionElement.offsetTop;
            const offset = 120;
            
            window.scrollTo({
              top: elementTop - offset,
              behavior: 'smooth'
            });
          }
        }, 300);
      }
    },
    goBackToSelection() {
      this.selectedInputType = '';
      this.currentStep = 1;
      
      // 滚动回选择区域，使用更大的滚动距离
      this.$nextTick(() => {
        this.scrollToTypeSelection();
      });
    },
    scrollToTypeSelection() {
      if (this.$refs.typeSelectionContainer) {
        const element = this.$refs.typeSelectionContainer;
        const elementTop = element.offsetTop;
        const offset = 120; // 增加偏移量
        
        window.scrollTo({
          top: elementTop - offset,
          behavior: 'smooth'
        });
      } else {
        // 备用方案
        const typeSelectionElement = document.querySelector('.input-type-selection');
        if (typeSelectionElement) {
          const elementTop = typeSelectionElement.offsetTop;
          const offset = 120;
          
          window.scrollTo({
            top: elementTop - offset,
            behavior: 'smooth'
          });
        }
      }
    },
    // 新增：滚动到比赛类型选择区域的方法
    scrollToMatchTypeSelection() {
      if (this.$refs.matchTypeCard) {
        const element = this.$refs.matchTypeCard.$el;
        const elementTop = element.offsetTop;
        const offset = 100;
        
        window.scrollTo({
          top: elementTop - offset,
          behavior: 'smooth'
        });
      }
    },
    handleTeamSubmit(teamData) {
      this.$emit('team-submit', { ...teamData, matchType: this.currentMatchType });
      // 提交成功后返回选择界面并滚动
      setTimeout(() => {
        this.goBackToSelection();
      }, 1000);
    },
    handleScheduleSubmit(scheduleData) {
      this.$emit('schedule-submit', { ...scheduleData, matchType: this.currentMatchType });
      // 提交成功后返回选择界面并滚动
      setTimeout(() => {
        this.goBackToSelection();
      }, 1000);
    },
    handleEventSubmit(eventData) {
      this.$emit('event-submit', { ...eventData, matchType: this.currentMatchType });
      // 提交成功后返回选择界面并滚动
      setTimeout(() => {
        this.goBackToSelection();
      }, 1000);
    },
    getMatchTypeLabel(type) {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return type ? labels[type] : labels[this.currentMatchType] || '';
    },
    getMatchTypeTagType(type) {
      const types = {
        'champions-cup': 'warning',
        'womens-cup': 'danger',
        'eight-a-side': 'success'
      };
      return types[type] || 'info';
    },
    getEventCount() {
      return this.events ? this.events.filter(event => event.matchType === this.currentMatchType).length : 0;
    },
    refreshData() {
      this.$emit('refresh-data');
    }
  },
  watch: {
    currentMatchType(newVal) {
      if (!newVal) {
        this.selectedInputType = '';
        this.currentStep = 0;
      }
    }
  }
}
</script>

<style scoped>
.data-input-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 0 100px 0; /* 增加底部内边距 */
}

/* 页面头部样式 */
.page-header {
  margin-bottom: 32px;
  padding: 32px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  min-height: 80px;
}

.header-main {
  flex: 1;
  min-width: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  align-items: flex-start;
  padding-top: 8px;
}

.refresh-button {
  min-width: 120px;
  white-space: nowrap;
  font-weight: 600;
}

/* 步骤指示器 */
.steps-container {
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* 比赛类型选择卡片 */
.match-type-card {
  margin-bottom: 32px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  scroll-margin-top: 100px; /* 添加滚动偏移 */
}

.match-type-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.card-title .el-icon {
  margin-right: 10px;
  color: #f59e0b;
  font-size: 20px;
}

.current-type-tag {
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}

.header-refresh-btn {
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.header-refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.match-type-content {
  padding: 8px 0;
}

/* 类型选择器样式 */
.type-selector-wrapper {
  padding: 16px 0;
}

/* 下拉框样式优化 */
:deep(.type-selector .el-select__wrapper) {
  min-height: 48px;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.type-selector .el-select__wrapper:hover) {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

:deep(.type-selector .el-select__wrapper.is-focused) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 选择器选中值显示样式 */
:deep(.type-selector .el-select__selected-item) {
  font-weight: 500;
  color: #1f2937;
}

/* 下拉选项样式 */
.option-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
  width: 100%;
}

.option-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.option-info {
  flex: 1;
  min-width: 0;
}

.option-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
  line-height: 1.2;
}

.option-desc {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
  line-height: 1.2;
}

/* 下拉菜单样式 */
:global(.match-type-dropdown .el-select-dropdown__item) {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.2s ease;
  min-height: 48px;
  display: flex;
  align-items: center;
}

:global(.match-type-dropdown .el-select-dropdown__item:hover) {
  background: rgba(59, 130, 246, 0.05);
}

:global(.match-type-dropdown .el-select-dropdown__item.is-selected) {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  font-weight: 600;
}

/* 信息统计区域 */
.match-type-info {
  padding: 16px 0;
}

.info-header {
  margin-bottom: 16px;
}

.info-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--card-color), var(--card-color-light));
}

.teams-card {
  --card-color: #10b981;
  --card-color-light: #34d399;
}

.matches-card {
  --card-color: #f59e0b;
  --card-color-light: #fbbf24;
}

.events-card {
  --card-color: #ef4444;
  --card-color-light: #f87171;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.teams-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.matches-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.events-icon {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.info-content {
  flex: 1;
}

.info-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.info-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.info-trend {
  color: #10b981;
}

.trend-icon {
  font-size: 16px;
}

.no-match-type {
  padding: 40px;
  text-align: center;
}

.empty-illustration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-icon {
  font-size: 48px;
  color: #f59e0b;
}

.empty-text {
  color: #6b7280;
  font-size: 16px;
}

/* 录入类型选择 */
.input-type-selection {
  margin-bottom: 32px;
  scroll-margin-top: 120px; /* 添加滚动偏移 */
  position: relative;
}

.selection-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
}

.type-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 8px 0;
}

.type-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  transform-origin: center;
}

.type-card:active {
  transform: translateY(-2px) scale(0.98);
}

/* 为选择按钮添加脉冲效果 */
.type-card.active .type-card-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.type-card:hover {
  border-color: var(--card-border);
  box-shadow: 0 8px 25px var(--card-shadow);
  transform: translateY(-4px);
}

.type-card:hover::before {
  transform: scaleX(1);
}

.type-card.active {
  border-color: var(--card-border);
  box-shadow: 0 8px 25px var(--card-shadow);
  transform: translateY(-2px);
}

.type-card.active::before {
  transform: scaleX(1);
}

.type-card.teams-card {
  --card-gradient: linear-gradient(90deg, #10b981, #34d399);
  --card-border: #10b981;
  --card-shadow: rgba(16, 185, 129, 0.25);
}

.type-card.schedule-card {
  --card-gradient: linear-gradient(90deg, #f59e0b, #fbbf24);
  --card-border: #f59e0b;
  --card-shadow: rgba(245, 158, 11, 0.25);
}

.type-card.events-card {
  --card-gradient: linear-gradient(90deg, #ef4444, #f87171);
  --card-border: #ef4444;
  --card-shadow: rgba(239, 68, 68, 0.25);
}

.type-card-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
  font-size: 28px;
  transition: transform 0.3s ease;
}

.type-card:hover .type-card-icon {
  transform: scale(1.1);
}

.teams-bg {
  background: linear-gradient(135deg, #10b981, #059669);
}

.schedule-bg {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.events-bg {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.type-card-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.type-card-desc {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.type-card-stats {
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stats-text {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

/* 信息录入区域 */
.input-form-container {
  margin-bottom: 80px; /* 增加底部边距 */
  scroll-margin-top: 100px; /* 为现代浏览器提供滚动偏移 */
}

/* 表单卡片出现动画 */
@keyframes formCardAppear {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.95); /* 增加缩放效果 */
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.form-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  animation: formCardAppear 0.6s ease-out;
  scroll-margin-top: 150px; /* 增加滚动偏移 */
  margin-bottom: 40px; /* 表单卡片底部间距 */
}

/* 为选中状态添加更明显的视觉效果 */
.type-card.active {
  border-color: var(--card-border);
  box-shadow: 0 8px 25px var(--card-shadow);
  transform: translateY(-2px);
  position: relative;
  animation: selectedCardPulse 0.6s ease-out;
}

@keyframes selectedCardPulse {
  0% {
    transform: translateY(-2px) scale(1);
    box-shadow: 0 8px 25px var(--card-shadow);
  }
  50% {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 35px var(--card-shadow);
  }
  100% {
    transform: translateY(-2px) scale(1);
    box-shadow: 0 8px 25px var(--card-shadow);
  }
}

.type-card.active::after {
  content: '✓';
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: var(--card-border);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  animation: checkmarkAppear 0.3s ease-out;
}

@keyframes checkmarkAppear {
  0% {
    opacity: 0;
    transform: scale(0) rotate(-180deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

/* 为页面滚动到底部时添加一个提示效果 */
.input-form-container::after {
  content: '';
  display: block;
  height: 20px;
  background: linear-gradient(to bottom, transparent, rgba(59, 130, 246, 0.05));
  border-radius: 0 0 16px 16px;
  margin-top: 20px;
}

/* 优化滚动体验 */
html {
  scroll-behavior: smooth;
}

/* 响应式滚动优化 */
@media (max-width: 768px) {
  .input-form-container {
    scroll-margin-top: 100px; /* 移动端减少一些偏移 */
  }
  
  /* 移动端滚动偏移量调整 */
  .form-card {
    margin-top: 20px;
  }
}

@media (max-width: 576px) {
  .input-form-container {
    scroll-margin-top: 80px; /* 小屏幕进一步减少偏移 */
  }
}

/* 增强点击反馈 */
.type-card:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
