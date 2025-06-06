<template>
  <el-card class="section-card">
    <div slot="header">
      <span>{{ getMatchTypeLabel() }}事件录入</span>
    </div>
    <el-form ref="eventForm" :model="eventForm" label-width="120px">
      <el-form-item label="比赛名称">
        <el-select v-model="eventForm.matchName" placeholder="请选择比赛" @change="handleMatchSelect">
          <el-option v-for="match in matches" :key="match.id" :label="match.matchName" :value="match.matchName"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="事件信息">
        <div class="event-header">
          <el-button type="primary" @click="addEvent">添加事件</el-button>
          <span class="event-count">已添加 {{ eventForm.events.length }} 个事件</span>
        </div>
        <div class="events-container">
          <div v-for="(event, index) in eventForm.events" :key="index" class="event-card">
            <div class="event-card-header">
              <span class="event-index">事件 {{ index + 1 }}</span>
              <el-button type="text" icon="el-icon-delete" @click="removeEvent(index)" class="delete-btn">删除</el-button>
            </div>
            <div class="event-inputs">
              <el-select v-model="event.eventType" placeholder="事件类型" class="event-input">
                <el-option label="进球" value="进球"></el-option>
                <el-option label="红牌" value="红牌"></el-option>
                <el-option label="黄牌" value="黄牌"></el-option>
                <el-option label="乌龙球" value="乌龙球"></el-option>
              </el-select>
              <el-select v-model="event.playerName" placeholder="选择球员" class="event-input">
                <el-option v-for="player in currentMatchPlayers" :key="player.id" :label="player.name" :value="player.name"></el-option>
              </el-select>
              <el-input v-model="event.eventTime" placeholder="事件时间（分钟）" class="event-input"></el-input>
            </div>
          </div>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitEvents">提交事件信息</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
export default {
  name: 'EventInput',
  props: {
    matchType: String,
    matches: Array,
    teams: Array
  },
  data() {
    return {
      eventForm: {
        matchName: '',
        events: []
      },
      currentMatchPlayers: []
    }
  },
  methods: {
    addEvent() {
      this.eventForm.events.push({ eventType: '', playerName: '', eventTime: '' });
    },
    removeEvent(index) {
      this.eventForm.events.splice(index, 1);
    },
    handleMatchSelect(matchName) {
      const selectedMatch = this.matches.find(match => match.matchName === matchName);
      if (selectedMatch) {
        const team1Players = this.teams.find(team => team.teamName === selectedMatch.team1)?.players || [];
        const team2Players = this.teams.find(team => team.teamName === selectedMatch.team2)?.players || [];
        this.currentMatchPlayers = [...team1Players, ...team2Players];
      }
    },
    submitEvents() {
      this.$emit('submit', this.eventForm);
      this.eventForm = { matchName: '', events: [] };
      this.currentMatchPlayers = [];
    },
    getMatchTypeLabel() {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return labels[this.matchType] || '';
    }
  }
}
</script>

<style scoped>
.section-card {
  border: 1px solid #e4e7ed;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.event-count {
  color: #909399;
  font-size: 14px;
}

.events-container {
  max-height: 400px;
  overflow-y: auto;
}

.event-card {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fff;
  transition: box-shadow 0.2s;
}

.event-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.event-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.event-index {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.delete-btn {
  color: #f56c6c;
  padding: 0;
}

.delete-btn:hover {
  color: #f78989;
}

.event-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.event-input {
  width: 100%;
}
</style>
