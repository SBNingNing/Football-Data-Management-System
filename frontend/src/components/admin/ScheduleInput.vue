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
            <el-icon><IconView /></el-icon>
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

      <el-form-item class="submit-form-item entity-submit-zone">
        <el-button 
          type="primary" 
          @click="submitSchedule"
          size="large"
          class="submit-btn btn-entity-submit"
          :disabled="!isFormValid || submitting"
          :loading="submitting"
        >
          <el-icon><Check /></el-icon>
          提交赛程信息
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { Trophy, UserFilled, Calendar, MapLocation, View as IconView, Check } from '@element-plus/icons-vue'
import { createMatch } from '@/domain/match/matchService'

export default {
  name: 'ScheduleInput',
  components: {
    Trophy,
    UserFilled,
    Calendar,
    MapLocation,
  IconView,
    Check
  },
  props: {
    matchType: {
      type: String,
      default: ''
    },
    teams: {
      type: Array,
      default: () => []
    }
  },
  // 声明组件可触发的事件，便于类型与 Lint 校验
  emits: ['submit'],
  data() {
    return {
      scheduleForm: {
        matchName: '',
        team1: '',
        team2: '',
        date: '',
        location: ''
      },
      submitting: false
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
    async submitSchedule() {
      if (this.submitting) return;
      if (!this.isFormValid) {
        this.$message.warning('请填写完整的赛程信息');
        return;
      }
      let form = { ...this.scheduleForm };
      if (form.date instanceof Date) {
        const pad = n => n < 10 ? '0' + n : n;
        const dt = new Date(form.date.getTime());
        form.date = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;
      }
      try {
        this.submitting = true;
        const { ok, data, error } = await createMatch(form)
        if(!ok){
          this.$message.error(error?.message || '创建比赛失败')
          return
        }
        try {
          import('@/utils/httpClient').then(m=>{
            m.default.cache.invalidate('matches:records')
            m.default.cache.invalidate('stats:dashboard')
          })
  } catch { /* ignore cache invalidation errors */ }
        this.$message.success('比赛创建成功')
        this.$emit('submit', data || form)
        this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
  } catch{ 
        this.$message.error('创建比赛异常')
      } finally {
        this.submitting = false;
      }
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
      } catch {
        return date;
      }
    }
  }
}
</script>

<style scoped>
/* 样式已迁移至 admin-management.css (.schedule-input-wrapper...) */
</style>
