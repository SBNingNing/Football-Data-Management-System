<template>
  <div class="schedule-input-wrapper">
    <el-form ref="scheduleForm" :model="scheduleForm" label-width="120px" class="schedule-form">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="比赛名称" required>
            <el-input 
              v-model="scheduleForm.matchName" 
              placeholder="请输入比赛名称"
              size="large"
              clearable
              maxlength="100"
              show-word-limit
            >
              <template #prefix>
                <el-icon><Trophy /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :md="12" :span="24">
          <el-form-item label="参赛球队1" required>
            <el-select 
              v-model="scheduleForm.team1" 
              placeholder="请选择球队1"
              size="large"
              style="width: 100%;"
              filterable
              clearable
              no-data-text="暂无可选球队"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
              <el-option 
                v-for="team in teams" 
                :key="team.id" 
                :label="team.teamName" 
                :value="team.teamName"
                :disabled="scheduleForm.team2 === team.teamName"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.teamName }}</span>
                  <span class="team-players">{{ team.players?.length || 0 }}名球员</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :md="12" :span="24">
          <el-form-item label="参赛球队2" required>
            <el-select 
              v-model="scheduleForm.team2" 
              placeholder="请选择球队2"
              size="large"
              style="width: 100%;"
              filterable
              clearable
              no-data-text="暂无可选球队"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
              <el-option 
                v-for="team in teams" 
                :key="team.id" 
                :label="team.teamName" 
                :value="team.teamName"
                :disabled="scheduleForm.team1 === team.teamName"
              >
                <div class="team-option">
                  <span class="team-name">{{ team.teamName }}</span>
                  <span class="team-players">{{ team.players?.length || 0 }}名球员</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :md="12" :span="24">
          <el-form-item label="比赛日期" required>
            <el-date-picker 
              v-model="scheduleForm.date" 
              type="datetime" 
              placeholder="选择日期时间"
              size="large"
              style="width: 100%;"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              :disabled-date="disabledDate"
            >
              <template #prefix>
                <el-icon><Calendar /></el-icon>
              </template>
            </el-date-picker>
          </el-form-item>
        </el-col>
        <el-col :md="12" :span="24">
          <el-form-item label="比赛地点" required>
            <el-input 
              v-model="scheduleForm.location" 
              placeholder="请输入比赛地点"
              size="large"
              clearable
              maxlength="50"
            >
              <template #prefix>
                <el-icon><MapLocation /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 比赛预览卡片 -->
      <div v-if="isFormValid" class="match-preview">
        <div class="preview-header">
          <h4 class="preview-title">
            <el-icon><View /></el-icon>
            比赛预览
          </h4>
        </div>
        <div class="preview-content">
          <div class="match-info">
            <div class="match-title">{{ scheduleForm.matchName }}</div>
            <div class="match-teams">
              <div class="team">
                <el-avatar :size="40" class="team-avatar">{{ scheduleForm.team1?.charAt(0) }}</el-avatar>
                <span class="team-name">{{ scheduleForm.team1 }}</span>
              </div>
              <div class="vs">VS</div>
              <div class="team">
                <el-avatar :size="40" class="team-avatar">{{ scheduleForm.team2?.charAt(0) }}</el-avatar>
                <span class="team-name">{{ scheduleForm.team2 }}</span>
              </div>
            </div>
            <div class="match-details">
              <div class="detail-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatDate(scheduleForm.date) }}</span>
              </div>
              <div class="detail-item">
                <el-icon><MapLocation /></el-icon>
                <span>{{ scheduleForm.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-form-item class="submit-form-item">
        <el-button 
          type="primary" 
          @click="submitSchedule"
          size="large"
          class="submit-btn"
          :disabled="!isFormValid"
        >
          <el-icon><Check /></el-icon>
          提交赛程信息
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { Trophy, UserFilled, Calendar, MapLocation, View, Check } from '@element-plus/icons-vue'

export default {
  name: 'ScheduleInput',
  components: {
    Trophy,
    UserFilled,
    Calendar,
    MapLocation,
    View,
    Check
  },
  props: {
    matchType: String,
    teams: Array
  },
  data() {
    return {
      scheduleForm: {
        matchName: '',
        team1: '',
        team2: '',
        date: '',
        location: ''
      }
    }
  },
  computed: {
    isFormValid() {
      return this.scheduleForm.matchName.trim() && 
             this.scheduleForm.team1 && 
             this.scheduleForm.team2 && 
             this.scheduleForm.date && 
             this.scheduleForm.location.trim() &&
             this.scheduleForm.team1 !== this.scheduleForm.team2
    }
  },
  methods: {
    submitSchedule() {
      if (!this.isFormValid) {
        this.$message.warning('请填写完整的赛程信息');
        return;
      }

      // 修正：将日期转为字符串并加上时区（北京时间），避免时区丢失
      let form = { ...this.scheduleForm };
      if (form.date instanceof Date) {
        // 转为北京时间字符串
        const pad = n => n < 10 ? '0' + n : n;
        const dt = new Date(form.date.getTime()); 
        form.date = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
      }
      this.$emit('submit', form);
      this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
    },
    getMatchTypeLabel() {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return labels[this.matchType] || '';
    },
    disabledDate(time) {
      // 禁用过去的日期
      return time.getTime() < Date.now() - 8.64e7; // 24小时前
    },
    formatDate(date) {
      if (!date) return '';
      try {
        return new Date(date).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          weekday: 'long'
        });
      } catch (error) {
        return date;
      }
    }
  }
}
</script>

<style scoped>
.schedule-input-wrapper {
  padding: 24px;
  background: white;
}

.schedule-form {
  max-width: none;
}

/* 球队选项样式 */
.team-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.team-name {
  font-weight: 500;
  color: #1f2937;
}

.team-players {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 比赛预览卡片 */
.match-preview {
  margin: 24px 0;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  overflow: hidden;
}

.preview-header {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.preview-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.preview-title .el-icon {
  margin-right: 8px;
  color: #3b82f6;
}

.preview-content {
  padding: 20px;
}

.match-info {
  text-align: center;
}

.match-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.match-teams {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
}

.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.team-avatar {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  font-weight: 600;
}

.team .team-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
}

.vs {
  font-size: 16px;
  font-weight: 700;
  color: #ef4444;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  border: 2px solid #fee2e2;
}

.match-details {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-size: 14px;
}

.detail-item .el-icon {
  color: #6b7280;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .match-teams {
    flex-direction: column;
    gap: 16px;
  }

  .vs {
    transform: rotate(90deg);
    font-size: 14px;
    padding: 6px 12px;
  }

  .match-details {
    flex-direction: column;
    gap: 12px;
    align-items: center;
  }
}

/* 表单控件样式优化 */
:deep(.el-input__wrapper),
:deep(.el-select .el-select__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-select__wrapper:hover) {
  border-color: #3b82f6;
}

:deep(.el-date-editor.el-input) {
  width: 100%;
}
</style>
