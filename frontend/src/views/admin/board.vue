<template>
  <div class="admin">
    <!-- 管理员欢迎卡片 -->
    <el-card class="welcome-card">
      <div slot="header" class="clearfix">
        <span>足球管理系统管理员界面</span>
        <div style="float: right;">
          <el-button type="text" @click="goToHome">查看前台</el-button>
          <el-button type="text" @click="logout">退出登录</el-button>
        </div>
      </div>
      <p>欢迎管理员，您可以通过以下功能管理比赛信息。</p>
    </el-card>

    <!-- 功能标签页 -->
    <el-card class="main-content-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 信息录入标签页 -->
        <el-tab-pane label="信息录入" name="input">
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
            <el-card class="section-card">
              <div slot="header">
                <span>{{ getMatchTypeLabel() }}球队信息录入</span>
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

            <!-- 赛程信息录入 -->
            <el-card class="section-card">
              <div slot="header">
                <span>{{ getMatchTypeLabel() }}赛程录入</span>
              </div>
              <el-form ref="scheduleForm" :model="scheduleForm" label-width="120px">
                <el-form-item label="比赛名称">
                  <el-input v-model="scheduleForm.matchName" placeholder="请输入比赛名称"></el-input>
                </el-form-item>
                <el-form-item label="参赛球队1">
                  <el-select v-model="scheduleForm.team1" placeholder="请选择球队1">
                    <el-option v-for="team in filteredTeams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="参赛球队2">
                  <el-select v-model="scheduleForm.team2" placeholder="请选择球队2">
                    <el-option v-for="team in filteredTeams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
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

            <!-- 事件信息录入 -->
            <el-card class="section-card">
              <div slot="header">
                <span>{{ getMatchTypeLabel() }}事件录入</span>
              </div>
              <el-form ref="eventForm" :model="eventForm" label-width="120px">
                <el-form-item label="比赛名称">
                  <el-select v-model="eventForm.matchName" placeholder="请选择比赛">
                    <el-option v-for="match in filteredMatches" :key="match.id" :label="match.matchName" :value="match.matchName"></el-option>
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
                    <el-option v-for="player in filteredPlayers" :key="player.id" :label="player.name" :value="player.name"></el-option>
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
        </el-tab-pane>

        <!-- 信息管理标签页 -->
        <el-tab-pane label="信息管理" name="manage">
          <el-tabs v-model="manageActiveTab" type="card">
            <!-- 球队管理 -->
            <el-tab-pane label="球队管理" name="teams">
              <div class="manage-header">
                <el-select v-model="manageMatchType" placeholder="请选择比赛类型" @change="filterManageData" style="width: 200px;">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="冠军杯" value="champions-cup"></el-option>
                  <el-option label="巾帼杯" value="womens-cup"></el-option>
                  <el-option label="八人制比赛" value="eight-a-side"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchTeams" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayTeams" border style="width: 100%">
                <el-table-column prop="teamName" label="球队名称" width="200"></el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="150">
                  <template slot-scope="scope">
                    {{ getMatchTypeLabel(scope.row.matchType) }}
                  </template>
                </el-table-column>
                <el-table-column label="球员数量" width="120">
                  <template slot-scope="scope">
                    {{ scope.row.players ? scope.row.players.length : 0 }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <el-button size="mini" type="primary" @click="editTeam(scope.row)">编辑</el-button>
                    <el-button size="mini" type="danger" @click="deleteTeam(scope.row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 赛事管理 -->
            <el-tab-pane label="赛事管理" name="matches">
              <div class="manage-header">
                <el-select v-model="manageMatchType" placeholder="请选择比赛类型" @change="filterManageData" style="width: 200px;">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="冠军杯" value="champions-cup"></el-option>
                  <el-option label="巾帼杯" value="womens-cup"></el-option>
                  <el-option label="八人制比赛" value="eight-a-side"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchMatches" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayMatches" border style="width: 100%">
                <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
                <el-table-column prop="team1" label="球队1" width="150"></el-table-column>
                <el-table-column prop="team2" label="球队2" width="150"></el-table-column>
                <el-table-column prop="date" label="比赛时间" width="180">
                  <template slot-scope="scope">
                    {{ formatDate(scope.row.date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="location" label="比赛地点" width="150"></el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="120">
                  <template slot-scope="scope">
                    {{ getMatchTypeLabel(scope.row.matchType) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <el-button size="mini" type="primary" @click="editMatch(scope.row)">编辑</el-button>
                    <el-button size="mini" type="danger" @click="deleteMatch(scope.row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 事件管理 -->
            <el-tab-pane label="事件管理" name="events">
              <div class="manage-header">
                <el-select v-model="manageMatchType" placeholder="请选择比赛类型" @change="filterManageData" style="width: 200px;">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="冠军杯" value="champions-cup"></el-option>
                  <el-option label="巾帼杯" value="womens-cup"></el-option>
                  <el-option label="八人制比赛" value="eight-a-side"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchEvents" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayEvents" border style="width: 100%">
                <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
                <el-table-column prop="eventType" label="事件类型" width="120">
                  <template slot-scope="scope">
                    {{ getEventTypeLabel(scope.row.eventType) }}
                  </template>
                </el-table-column>
                <el-table-column prop="playerName" label="球员" width="150"></el-table-column>
                <el-table-column prop="eventTime" label="事件时间" width="120">
                  <template slot-scope="scope">
                    {{ scope.row.eventTime }}分钟
                  </template>
                </el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="120">
                  <template slot-scope="scope">
                    {{ getMatchTypeLabel(scope.row.matchType) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <el-button size="mini" type="primary" @click="editEvent(scope.row)">编辑</el-button>
                    <el-button size="mini" type="danger" @click="deleteEvent(scope.row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 编辑球队对话框 -->
    <el-dialog title="编辑球队信息" :visible.sync="editTeamDialog" width="600px">
      <el-form ref="editTeamForm" :model="editTeamForm" label-width="120px">
        <el-form-item label="球队名称">
          <el-input v-model="editTeamForm.teamName"></el-input>
        </el-form-item>
        <el-form-item label="比赛类型">
          <el-select v-model="editTeamForm.matchType" disabled>
            <el-option label="冠军杯" value="champions-cup"></el-option>
            <el-option label="巾帼杯" value="womens-cup"></el-option>
            <el-option label="八人制比赛" value="eight-a-side"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="球员信息">
          <el-button type="primary" @click="addEditPlayer">添加球员</el-button>
          <div v-for="(player, index) in editTeamForm.players" :key="index" class="player-item">
            <el-input v-model="player.name" placeholder="球员姓名"></el-input>
            <el-input v-model="player.number" placeholder="球员号码"></el-input>
            <el-button type="danger" @click="removeEditPlayer(index)">删除</el-button>
          </div>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="editTeamDialog = false">取消</el-button>
        <el-button type="primary" @click="updateTeam">确定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑比赛对话框 -->
    <el-dialog title="编辑比赛信息" :visible.sync="editMatchDialog" width="600px">
      <el-form ref="editMatchForm" :model="editMatchForm" label-width="120px">
        <el-form-item label="比赛名称">
          <el-input v-model="editMatchForm.matchName"></el-input>
        </el-form-item>
        <el-form-item label="参赛球队1">
          <el-select v-model="editMatchForm.team1">
            <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参赛球队2">
          <el-select v-model="editMatchForm.team2">
            <el-option v-for="team in teams" :key="team.id" :label="team.teamName" :value="team.teamName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="比赛日期">
          <el-date-picker v-model="editMatchForm.date" type="datetime"></el-date-picker>
        </el-form-item>
        <el-form-item label="比赛地点">
          <el-input v-model="editMatchForm.location"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="editMatchDialog = false">取消</el-button>
        <el-button type="primary" @click="updateMatch">确定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑事件对话框 -->
    <el-dialog title="编辑事件信息" :visible.sync="editEventDialog" width="500px">
      <el-form ref="editEventForm" :model="editEventForm" label-width="120px">
        <el-form-item label="比赛名称">
          <el-select v-model="editEventForm.matchName">
            <el-option v-for="match in matches" :key="match.id" :label="match.matchName" :value="match.matchName"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件类型">
          <el-select v-model="editEventForm.eventType">
            <el-option label="进球" value="goal"></el-option>
            <el-option label="红牌" value="redCard"></el-option>
            <el-option label="黄牌" value="yellowCard"></el-option>
            <el-option label="乌龙球" value="ownGoal"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件球员">
          <el-select v-model="editEventForm.playerName">
            <el-option v-for="player in players" :key="player.id" :label="player.name" :value="player.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="事件时间">
          <el-input v-model="editEventForm.eventTime" placeholder="分钟"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="editEventDialog = false">取消</el-button>
        <el-button type="primary" @click="updateEvent">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import { useUserStore } from '@/store';

export default {
  name: 'Admin',
  data() {
    return {
      activeTab: 'input',
      manageActiveTab: 'teams',
      manageMatchType: '',
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
      players: [],
      events: [],
      // 编辑相关数据
      editTeamDialog: false,
      editMatchDialog: false,
      editEventDialog: false,
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
      }
    };
  },
  computed: {
    // ...existing computed properties...
    filteredTeams() {
      return this.teams.filter(team => team.matchType === this.currentMatchType);
    },
    filteredMatches() {
      return this.matches.filter(match => match.matchType === this.currentMatchType);
    },
    filteredPlayers() {
      return this.players.filter(player => player.matchType === this.currentMatchType);
    },
    displayTeams() {
      return this.manageMatchType ? 
        this.teams.filter(team => team.matchType === this.manageMatchType) : 
        this.teams;
    },
    displayMatches() {
      return this.manageMatchType ? 
        this.matches.filter(match => match.matchType === this.manageMatchType) : 
        this.matches;
    },
    displayEvents() {
      return this.manageMatchType ? 
        this.events.filter(event => event.matchType === this.manageMatchType) : 
        this.events;
    }
  },
  methods: {
    // ...existing methods...
    handleMatchTypeChange(value) {
      this.currentMatchType = value;
      this.teamForm = { teamName: '', players: [] };
      this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
      this.eventForm = { matchName: '', eventType: '', playerName: '', eventTime: '' };
    },
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '' });
    },
    removePlayer(index) {
      this.teamForm.players.splice(index, 1);
    },
    submitTeam() {
      const teamData = {
        ...this.teamForm,
        matchType: this.currentMatchType
      };
      
      axios.post('/api/auth/teams', teamData)
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
      const scheduleData = {
        ...this.scheduleForm,
        matchType: this.currentMatchType
      };
      
      axios.post('/api/matches', scheduleData)
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
      const eventData = {
        ...this.eventForm,
        matchType: this.currentMatchType
      };
      
      axios.post('/api/events', eventData)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('事件信息录入成功');
            this.eventForm = { matchName: '', eventType: '', playerName: '', eventTime: '' };
            this.fetchEvents();
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
      axios.get('/api/auth/teams')
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
      axios.get('/api/auth/players')
        .then(response => {
          if (response.data.status === 'success') {
            this.players = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取球员信息失败:', error);
        });
    },
    fetchEvents() {
      axios.get('/api/events')
        .then(response => {
          if (response.data.status === 'success') {
            this.events = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取事件信息失败:', error);
        });
    },
    // 新增方法
    handleTabClick(tab) {
      if (tab.name === 'manage') {
        this.fetchTeams();
        this.fetchMatches();
        this.fetchEvents();
      }
    },
    filterManageData() {
      // 筛选数据的方法，通过计算属性实现
    },
    getMatchTypeLabel(type) {
      const labels = {
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制比赛'
      };
      return type ? labels[type] : labels[this.currentMatchType] || '';
    },
    getEventTypeLabel(type) {
      const labels = {
        'goal': '进球',
        'redCard': '红牌',
        'yellowCard': '黄牌',
        'ownGoal': '乌龙球'
      };
      return labels[type] || type;
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleString('zh-CN');
    },
    // 编辑球队
    editTeam(team) {
      this.editTeamForm = {
        id: team.id,
        teamName: team.teamName,
        matchType: team.matchType,
        players: team.players ? [...team.players] : []
      };
      this.editTeamDialog = true;
    },
    addEditPlayer() {
      this.editTeamForm.players.push({ name: '', number: '' });
    },
    removeEditPlayer(index) {
      this.editTeamForm.players.splice(index, 1);
    },
    updateTeam() {
      axios.put(`/api/auth/teams/${this.editTeamForm.id}`, this.editTeamForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('球队信息更新成功');
            this.editTeamDialog = false;
            this.fetchTeams();
          } else {
            this.$message.error('球队信息更新失败');
          }
        })
        .catch(error => {
          console.error('更新球队信息失败:', error);
          this.$message.error('球队信息更新失败');
        });
    },
    deleteTeam(teamId) {
      this.$confirm('此操作将永久删除该球队, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete(`/api/auth/teams/${teamId}`)
          .then(response => {
            if (response.data.status === 'success') {
              this.$message.success('删除成功');
              this.fetchTeams();
            } else {
              this.$message.error('删除失败');
            }
          })
          .catch(error => {
            console.error('删除球队失败:', error);
            this.$message.error('删除失败');
          });
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
    updateMatch() {
      axios.put(`/api/matches/${this.editMatchForm.id}`, this.editMatchForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('比赛信息更新成功');
            this.editMatchDialog = false;
            this.fetchMatches();
          } else {
            this.$message.error('比赛信息更新失败');
          }
        })
        .catch(error => {
          console.error('更新比赛信息失败:', error);
          this.$message.error('比赛信息更新失败');
        });
    },
    deleteMatch(matchId) {
      this.$confirm('此操作将永久删除该比赛, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete(`/api/matches/${matchId}`)
          .then(response => {
            if (response.data.status === 'success') {
              this.$message.success('删除成功');
              this.fetchMatches();
            } else {
              this.$message.error('删除失败');
            }
          })
          .catch(error => {
            console.error('删除比赛失败:', error);
            this.$message.error('删除失败');
          });
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
    updateEvent() {
      axios.put(`/api/events/${this.editEventForm.id}`, this.editEventForm)
        .then(response => {
          if (response.data.status === 'success') {
            this.$message.success('事件信息更新成功');
            this.editEventDialog = false;
            this.fetchEvents();
          } else {
            this.$message.error('事件信息更新失败');
          }
        })
        .catch(error => {
          console.error('更新事件信息失败:', error);
          this.$message.error('事件信息更新失败');
        });
    },
    deleteEvent(eventId) {
      this.$confirm('此操作将永久删除该事件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete(`/api/events/${eventId}`)
          .then(response => {
            if (response.data.status === 'success') {
              this.$message.success('删除成功');
              this.fetchEvents();
            } else {
              this.$message.error('删除失败');
            }
          })
          .catch(error => {
            console.error('删除事件失败:', error);
            this.$message.error('删除失败');
          });
      });
    },
    goToHome() {
      // 使用页面刷新来跳转到前台
      window.location.href = '/home';
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
        // 使用页面刷新跳转到登录页
        setTimeout(() => {
          window.location.href = '/login';
        }, 500);
      }).catch(() => {
        // 取消退出
      });
    }
  },
  created() {
    this.fetchTeams();
    this.fetchMatches();
    this.fetchPlayers();
    this.fetchEvents();
  }
};
</script>

<style scoped>
.admin {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.main-content-card {
  min-height: 600px;
}

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

.section-card {
  border: 1px solid #e4e7ed;
}

.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.player-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  gap: 10px;
}

.player-item .el-input {
  flex: 1;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-table {
  margin-top: 20px;
}

.el-tabs--card > .el-tabs__header {
  margin: 0 0 15px;
}

@media (max-width: 768px) {
  .admin {
    padding: 10px;
  }
  
  .manage-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .player-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>