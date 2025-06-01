<template>
  <div class="admin">
    <!-- 管理员欢迎卡片 -->
    <el-card class="welcome-card">
      <div slot="header" class="clearfix">
        <span>足球管理系统管理员界面</span>
      </div>
      <p>欢迎管理员，您可以通过以下功能管理比赛信息。</p>
    </el-card>

    <!-- 比赛信息录入区域 -->
    <el-card class="match-input-card">
      <div slot="header" class="clearfix">
        <span>比赛信息录入</span>
      </div>

      <!-- 比赛类型选择 -->
      <el-form ref="matchTypeForm" :model="matchTypeForm" label-width="120px">
        <el-form-item label="比赛类型">
          <el-select v-model="matchTypeForm.matchType" placeholder="请选择比赛类型" @change="handleMatchTypeChange">
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 参赛球队名称录入 -->
    <el-card v-if="currentMatchType === 'champions-cup'" class="team-input-card">
      <div slot="header" class="clearfix">
        <span>冠军杯球队信息录入</span>
      </div>
      <el-form ref="teamForm" :model="teamForm" label-width="120px">
        <el-form-item label="球队名称">
          <el-input v-model="teamForm.teamName" placeholder="请输入球队名称"></el-input>
        </el-form-item>
        <el-form-item label="球员信息">
          <el-button type="primary" @click="addPlayer">添加球员</el-button>
          <div v-for="(player, index) in teamForm.players" :key="index" class="player-item">
            <el-input v-model="player.name" placeholder="球员姓名"></el-input>
            <el-input v-model="player.number" placeholder="球员号码"></el-input>
            <el-button type="danger" @click="removePlayer(index)">删除</el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitTeam">提交球队信息</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 比赛赛程录入 -->
    <el-card v-if="currentMatchType === 'champions-cup'" class="schedule-input-card">
      <div slot="header" class="clearfix">
        <span>冠军杯赛程录入</span>
      </div>
      <el-form ref="scheduleForm" :model="scheduleForm" label-width="120px">
        <el-form-item label="比赛名称">
          <el-input v-model="scheduleForm.matchName" placeholder="请输入比赛名称"></el-input>
        </el-form-item>
        <el-form-item label="参赛球队1">
          <el-select v-model="scheduleForm.team1" placeholder="请选择球队1">
            <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参赛球队2">
          <el-select v-model="scheduleForm.team2" placeholder="请选择球队2">
            <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="比赛日期">
          <el-date-picker v-model="scheduleForm.date" type="datetime" placeholder="选择日期时间"></el-date-picker>
        </el-form-item>
        <el-form-item label="比赛地点">
          <el-input v-model="scheduleForm.location" placeholder="请输入比赛地点"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitSchedule">提交赛程信息</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 比赛事件录入 -->
    <el-card v-if="currentMatchType === 'champions-cup'" class="event-input-card">
      <div slot="header" class="clearfix">
        <span>冠军杯事件录入</span>
      </div>
      <el-form ref="eventForm" :model="eventForm" label-width="120px">
        <el-form-item label="比赛名称">
          <el-select v-model="eventForm.matchName" placeholder="请选择比赛">
            <el-option v-for="match in matches" :key="match.id" :label="match.matchName" :value="match.matchName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型">
          <el-select v-model="eventForm.eventType" placeholder="请选择事件类型">
            <el-option label="进球" value="goal"></el-option>
            <el-option label="红牌" value="redCard"></el-option>
            <el-option label="黄牌" value="yellowCard"></el-option>
            <el-option label="乌龙球" value="ownGoal"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件球员">
          <el-select v-model="eventForm.playerName" placeholder="请选择球员">
            <el-option v-for="player in players" :key="player.id" :label="player.name" :value="player.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件时间">
          <el-input v-model="eventForm.eventTime" placeholder="请输入事件发生时间（分钟）"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitEvent">提交事件信息</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Admin',
  data() {
    return {
      matchTypeForm: {
        matchType: ''
      },
      currentMatchType: '',
      teamForm: {
        teamName: '',
        players: []
      },
      scheduleForm: {
        matchName: '',
        team1: '',
        team2: '',
        date: '',
        location: ''
      },
      eventForm: {
        matchName: '',
        eventType: '',
        playerName: '',
        eventTime: ''
      },
      teams: [],
      matches: [],
      players: []
    };
  },
  methods: {
    handleMatchTypeChange(value) {
      this.currentMatchType = value;
    },
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '' });
    },
    removePlayer(index) {
      this.teamForm.players.splice(index, 1);
    },
    submitTeam() {
      axios.post('/api/teams', this.teamForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('球队信息录入成功');
            this.teamForm = { teamName: '', players: [] };
            this.fetchTeams();
          } else {
            this.$message.error('球队信息录入失败');
          }
        })
        .catch(error => {
          console.error('球队信息录入失败:', error);
          this.$message.error('球队信息录入失败');
        });
    },
    submitSchedule() {
      axios.post('/api/schedules', this.scheduleForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('赛程信息录入成功');
            this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
            this.fetchMatches();
          } else {
            this.$message.error('赛程信息录入失败');
          }
        })
        .catch(error => {
          console.error('赛程信息录入失败:', error);
          this.$message.error('赛程信息录入失败');
        });
    },
    submitEvent() {
      axios.post('/api/events', this.eventForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('事件信息录入成功');
            this.eventForm = { matchName: '', eventType: '', playerName: '', eventTime: '' };
          } else {
            this.$message.error('事件信息录入失败');
          }
        })
        .catch(error => {
          console.error('事件信息录入失败:', error);
          this.$message.error('事件信息录入失败');
        });
    },
    fetchTeams() {
      axios.get('/api/teams')
        .then(response => {
          if (response.data.status === 'success') {
            this.teams = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取球队信息失败:', error);
        });
    },
    fetchMatches() {
      axios.get('/api/matches')
        .then(response => {
          if (response.data.status === 'success') {
            this.matches = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取比赛信息失败:', error);
        });
    },
    fetchPlayers() {
      axios.get('/api/players')
        .then(response => {
          if (response.data.status === 'success') {
            this.players = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取球员信息失败:', error);
        });
    }
  },
  created() {
    this.fetchTeams();
    this.fetchMatches();
    this.fetchPlayers();
  }
};
</script>

<style scoped>
.admin {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card,
.match-input-card,
.team-input-card,
.schedule-input-card,
.event-input-card {
  margin-bottom: 20px;
}

.player-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.player-item .el-input {
  margin-right: 10px;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>