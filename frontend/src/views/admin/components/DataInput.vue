<template>
  <div>
    <!-- 比赛类型选择 -->
    <el-form ref="matchTypeForm" :model="matchTypeForm" label-width="120px" class="match-type-form">
      <el-form-item label="比赛类型">
        <el-select v-model="matchTypeForm.matchType" placeholder="请选择比赛类型" @change="handleMatchTypeChange">
          <el-option label="冠军杯" value="champions-cup"></el-option>
          <el-option label="巾帼杯" value="womens-cup"></el-option>
          <el-option label="八人制比赛" value="eight-a-side"></el-option>
        </el-select>
      </el-form-item>
    </el-form>

    <div v-if="currentMatchType" class="input-sections">
      <!-- 球队信息录入 -->
      <TeamInput 
        :match-type="currentMatchType"
        :teams="filteredTeams"
        @submit="handleTeamSubmit"
      />

      <!-- 赛程信息录入 -->
      <ScheduleInput 
        :match-type="currentMatchType"
        :teams="filteredTeams"
        @submit="handleScheduleSubmit"
      />

      <!-- 事件信息录入 -->
      <EventInput 
        :match-type="currentMatchType"
        :matches="filteredMatches"
        :teams="filteredTeams"
        @submit="handleEventSubmit"
      />
    </div>
  </div>
</template>

<script>
import TeamInput from './TeamInput.vue'
import ScheduleInput from './ScheduleInput.vue'
import EventInput from './EventInput.vue'

export default {
  name: 'DataInput',
  components: {
    TeamInput,
    ScheduleInput,
    EventInput
  },
  props: {
    teams: Array,
    matches: Array
  },
  data() {
    return {
      matchTypeForm: {
        matchType: ''
      },
      currentMatchType: ''
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
    },
    handleTeamSubmit(teamData) {
      this.$emit('team-submit', { ...teamData, matchType: this.currentMatchType });
    },
    handleScheduleSubmit(scheduleData) {
      this.$emit('schedule-submit', { ...scheduleData, matchType: this.currentMatchType });
    },
    handleEventSubmit(eventData) {
      this.$emit('event-submit', { ...eventData, matchType: this.currentMatchType });
    },
    getMatchTypeLabel(type) {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return type ? labels[type] : labels[this.currentMatchType] || '';
    }
  }
}
</script>

<style scoped>
.match-type-form {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.input-sections {
  display: grid;
  gap: 20px;
}
</style>
