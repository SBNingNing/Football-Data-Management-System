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
                  <div class="player-header">
                    <el-button type="primary" @click="addPlayer">添加球员</el-button>
                    <span class="player-count">已添加 {{ teamForm.players.length }} 名球员</span>
                  </div>
                  <div class="players-container">
                    <div v-for="(player, index) in teamForm.players" :key="index" class="player-card">
                      <div class="player-card-header">
                        <span class="player-index">球员 {{ index + 1 }}</span>
                        <el-button type="text" icon="el-icon-delete" @click="removePlayer(index)" class="delete-btn">删除</el-button>
                      </div>
                      <div class="player-inputs">
                        <el-input v-model="player.name" placeholder="球员姓名" class="player-input"></el-input>
                        <el-input v-model="player.number" placeholder="球员号码" class="player-input"></el-input>
                        <el-input v-model="player.studentId" placeholder="学号" class="player-input"></el-input>
                      </div>
                    </div>
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
                  <el-select v-model="eventForm.matchName" placeholder="请选择比赛" @change="handleMatchSelect">
                    <el-option v-for="match in filteredMatches" :key="match.id" :label="match.matchName" :value="match.matchName"></el-option>
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
                          <el-option label="进球" value="goal"></el-option>
                          <el-option label="红牌" value="redCard"></el-option>
                          <el-option label="黄牌" value="yellowCard"></el-option>
                          <el-option label="乌龙球" value="ownGoal"></el-option>
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
                <el-button type="primary" @click="loadAllData" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayTeams" border style="width: 100%">
                <el-table-column prop="teamName" label="球队名称" width="200"></el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="150">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ getMatchTypeLabel(scope.row.matchType) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="球员数量" width="120">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ scope.row.players ? scope.row.players.length : 0 }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="球员信息" min-width="200">
                  <template slot-scope="scope">
                    <div v-if="scope && scope.row && scope.row.players && scope.row.players.length > 0" class="players-preview">
                      <el-tag v-for="player in scope.row.players.slice(0, 3)" :key="player.name" size="mini" class="player-tag">
                        {{ player.name }}({{ player.number }})
                      </el-tag>
                      <span v-if="scope.row.players.length > 3" class="more-players">+{{ scope.row.players.length - 3 }}人</span>
                    </div>
                    <span v-else class="no-players">暂无球员</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <div v-if="scope && scope.row">
                      <el-button size="mini" type="primary" @click="editTeam(scope.row)">编辑</el-button>
                      <el-button size="mini" type="danger" @click="deleteTeam(scope.row.id)">删除</el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 比赛管理 -->
            <el-tab-pane label="比赛管理" name="matches">
              <div class="manage-header">
                <el-select v-model="manageMatchType" placeholder="请选择比赛类型" @change="filterManageData" style="width: 200px;">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="冠军杯" value="champions-cup"></el-option>
                  <el-option label="巾帼杯" value="womens-cup"></el-option>
                  <el-option label="八人制比赛" value="eight-a-side"></el-option>
                </el-select>
                <el-button type="primary" @click="loadAllData" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayMatches" border style="width: 100%">
                <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
                <el-table-column prop="team1" label="球队1" width="150"></el-table-column>
                <el-table-column prop="team2" label="球队2" width="150"></el-table-column>
                <el-table-column prop="date" label="比赛时间" width="180">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ formatDate(scope.row.date) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="location" label="比赛地点" width="150"></el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="120">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ getMatchTypeLabel(scope.row.matchType) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <div v-if="scope && scope.row">
                      <el-button size="mini" type="primary" @click="editMatch(scope.row)">编辑</el-button>
                      <el-button size="mini" type="danger" @click="deleteMatch(scope.row.id)">删除</el-button>
                    </div>
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
                <el-button type="primary" @click="loadAllData" icon="el-icon-refresh">刷新</el-button>
              </div>
              <el-table :data="displayEvents" border style="width: 100%">
                <el-table-column prop="matchName" label="比赛名称" width="200"></el-table-column>
                <el-table-column prop="eventType" label="事件类型" width="120">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ getEventTypeLabel(scope.row.eventType) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="playerName" label="球员" width="150"></el-table-column>
                <el-table-column prop="eventTime" label="事件时间" width="120">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ scope.row.eventTime }}分钟</span>
                  </template>
                </el-table-column>
                <el-table-column prop="matchType" label="比赛类型" width="120">
                  <template slot-scope="scope">
                    <span v-if="scope && scope.row">{{ getMatchTypeLabel(scope.row.matchType) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template slot-scope="scope">
                    <div v-if="scope && scope.row">
                      <el-button size="mini" type="primary" @click="editEvent(scope.row)">编辑</el-button>
                      <el-button size="mini" type="danger" @click="deleteEvent(scope.row.id)">删除</el-button>
                    </div>
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
          <div class="players-container">
            <div v-for="(player, index) in editTeamForm.players" :key="index" class="player-card">
              <div class="player-card-header">
                <span class="player-index">球员 {{ index + 1 }}</span>
                <el-button type="text" icon="el-icon-delete" @click="removeEditPlayer(index)" class="delete-btn">删除</el-button>
              </div>
              <div class="player-inputs">
                <el-input v-model="player.name" placeholder="球员姓名" class="player-input"></el-input>
                <el-input v-model="player.number" placeholder="球员号码" class="player-input"></el-input>
                <el-input v-model="player.studentId" placeholder="学号" class="player-input"></el-input>
              </div>
            </div>
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
        events: []
      },
      currentMatchPlayers: [],
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
    userStore() {
      return useUserStore();
    },
    // 使用 Store 中的数据
    teams() {
      return this.userStore.teams;
    },
    matches() {
      return this.userStore.matches;
    },
    players() {
      return this.userStore.players;
    },
    events() {
      return this.userStore.events;
    },
    loading() {
      return this.userStore.loading;
    },
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
    async handleTabClick(tab) {
      if (tab.name === 'manage') {
        await this.loadAllData();
      }
    },
    // 统一加载所有数据的方法 - 使用 Store 方法
    async loadAllData() {
      this.userStore.loading = true;
      try {
        console.log('开始加载数据...');
        const results = await Promise.allSettled([
          this.userStore.fetchTeams(),
          this.userStore.fetchMatches(),
          this.userStore.fetchEvents(),
          this.userStore.fetchPlayers()
        ]);
        
        // 检查加载结果
        results.forEach((result, index) => {
          const names = ['球队', '比赛', '事件', '球员'];
          if (result.status === 'rejected') {
            console.error(`加载${names[index]}数据失败:`, result.reason);
          } else {
            console.log(`加载${names[index]}数据成功:`, result.value);
          }
        });
        
        console.log('数据加载完成，当前数据状态:', {
          teams: this.teams.length,
          matches: this.matches.length,
          events: this.events.length,
          players: this.players.length
        });
      } catch (error) {
        console.error('加载数据失败:', error);
        this.$message.error('数据加载失败，请刷新页面重试');
      } finally {
        this.userStore.loading = false;
      }
    },
    filterManageData() {
      // 筛选数据的方法，通过计算属性实现
      console.log('筛选数据，当前筛选条件:', this.manageMatchType);
    },
    // 添加缺失的 editTeam 方法
    editTeam(team) {
      console.log('编辑球队:', team);
      this.editTeamForm = {
        id: team.id,
        teamName: team.teamName,
        matchType: team.matchType,
        players: team.players ? [...team.players] : []
      };
      this.editTeamDialog = true;
    },
    addEditPlayer() {
      this.editTeamForm.players.push({ name: '', number: '', studentId: '' });
    },
    removeEditPlayer(index) {
      this.editTeamForm.players.splice(index, 1);
    },
    async updateTeam() {
      const result = await this.userStore.updateTeam(this.editTeamForm.id, this.editTeamForm);
      if (result.success) {
        this.$message.success('球队信息更新成功');
        this.editTeamDialog = false;
      } else {
        this.$message.error(result.error || '球队信息更新失败');
      }
    },
    deleteTeam(teamId) {
      this.$confirm('此操作将永久删除该球队, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteTeam(teamId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
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
    async updateMatch() {
      const result = await this.userStore.updateMatch(this.editMatchForm.id, this.editMatchForm);
      if (result.success) {
        this.$message.success('比赛信息更新成功');
        this.editMatchDialog = false;
      } else {
        this.$message.error(result.error || '比赛信息更新失败');
      }
    },
    deleteMatch(matchId) {
      this.$confirm('此操作将永久删除该比赛, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteMatch(matchId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
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
    async updateEvent() {
      const result = await this.userStore.updateEvent(this.editEventForm.id, this.editEventForm);
      if (result.success) {
        this.$message.success('事件信息更新成功');
        this.editEventDialog = false;
      } else {
        this.$message.error(result.error || '事件信息更新失败');
      }
    },
    deleteEvent(eventId) {
      this.$confirm('此操作将永久删除该事件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const result = await this.userStore.deleteEvent(eventId);
        if (result.success) {
          this.$message.success('删除成功');
        } else {
          this.$message.error(result.error || '删除失败');
        }
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
    },
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '', studentId: '' });
    },
    removePlayer(index) {
      this.teamForm.players.splice(index, 1);
    },
    async submitTeam() {
      const teamData = {
        ...this.teamForm,
        matchType: this.currentMatchType
      };
      
      const result = await this.userStore.createTeam(teamData);
      if (result.success) {
        this.$message.success('球队信息录入成功');
        this.teamForm = { teamName: '', players: [] };
      } else {
        this.$message.error(result.error || '球队信息录入失败');
      }
    },
    async submitSchedule() {
      const scheduleData = {
        ...this.scheduleForm,
        matchType: this.currentMatchType
      };
      
      const result = await this.userStore.createMatch(scheduleData);
      if (result.success) {
        this.$message.success('赛程信息录入成功');
        this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
      } else {
        this.$message.error(result.error || '赛程信息录入失败');
      }
    },
    addEvent() {
      this.eventForm.events.push({ eventType: '', playerName: '', eventTime: '' });
    },
    removeEvent(index) {
      this.eventForm.events.splice(index, 1);
    },
    handleMatchSelect(matchName) {
      // 根据选择的比赛获取相关球员
      const selectedMatch = this.filteredMatches.find(match => match.matchName === matchName);
      if (selectedMatch) {
        // 获取参赛两队的所有球员
        const team1Players = this.teams.find(team => team.teamName === selectedMatch.team1)?.players || [];
        const team2Players = this.teams.find(team => team.teamName === selectedMatch.team2)?.players || [];
        this.currentMatchPlayers = [...team1Players, ...team2Players];
      }
    },
    async submitEvents() {
      if (!this.eventForm.matchName) {
        this.$message.error('请选择比赛');
        return;
      }
      if (this.eventForm.events.length === 0) {
        this.$message.error('请至少添加一个事件');
        return;
      }

      const eventPromises = this.eventForm.events.map(event => {
        const eventData = {
          matchName: this.eventForm.matchName,
          eventType: event.eventType,
          playerName: event.playerName,
          eventTime: event.eventTime,
          matchType: this.currentMatchType
        };
        return this.userStore.createEvent(eventData);
      });

      try {
        const results = await Promise.all(eventPromises);
        const successCount = results.filter(result => result.success).length;
        if (successCount === this.eventForm.events.length) {
          this.$message.success(`成功录入 ${successCount} 个事件`);
          this.eventForm = { matchName: '', events: [] };
          this.currentMatchPlayers = [];
        } else {
          this.$message.warning(`录入了 ${successCount}/${this.eventForm.events.length} 个事件`);
        }
      } catch (error) {
        console.error('事件信息录入失败:', error);
        this.$message.error('事件信息录入失败');
      }
    },
    handleMatchTypeChange(value) {
      this.currentMatchType = value;
      this.teamForm = { teamName: '', players: [] };
      this.scheduleForm = { matchName: '', team1: '', team2: '', date: '', location: '' };
      this.eventForm = { matchName: '', events: [] };
      this.currentMatchPlayers = [];
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
      try {
        return new Date(date).toLocaleString('zh-CN');
      } catch (error) {
        return date;
      }
    }
  },
  async created() {
    // 页面创建时加载所有数据
    console.log('管理员页面创建，开始加载数据...');
    await this.loadAllData();
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

.player-header,
.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.player-count,
.event-count {
  color: #909399;
  font-size: 14px;
}

.players-container,
.events-container {
  max-height: 400px;
  overflow-y: auto;
}

.player-card,
.event-card {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fff;
  transition: box-shadow 0.2s;
}

.player-card:hover,
.event-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.player-card-header,
.event-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.player-index,
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

.player-inputs,
.event-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.player-input,
.event-input {
  width: 100%;
}

.players-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.player-tag {
  margin: 0;
}

.more-players {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.no-players {
  color: #c0c4cc;
  font-style: italic;
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

@media (max-width: 1024px) {
  .player-inputs,
  .event-inputs {
    grid-template-columns: 1fr 1fr;
  }
}
</style>