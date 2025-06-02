<template>
  <div class="home">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div slot="header" class="clearfix">
        <span>足球管理系统欢迎您</span>
        <span @click="logout" style="float: right; margin-top: 8px; color: #409EFF; cursor: pointer;">
          退出
        </span>
      </div>

      <!-- 数据统计卡片区域 -->
      <el-row :gutter="20" class="stats-section">
        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-data-line stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.totalMatches }}</div>
                <div class="stats-label">总赛事数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-timer stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.upcomingMatches }}</div>
                <div class="stats-label">即将进行</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-card-inner">
              <i class="el-icon-finished stats-icon"></i>
              <div class="stats-info">
                <div class="stats-number">{{ statsData.completedMatches }}</div>
                <div class="stats-label">已完成赛事</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 赛事类型卡片区域 -->
      <el-row :gutter="20" class="match-types">
        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/champions-cup')">
            <div class="match-type-card">
              <i class="el-icon-trophy"></i>
              <h3>冠军杯</h3>
              <p>查看冠军杯赛事信息</p>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/womens-cup')">
            <div class="match-type-card">
              <i class="el-icon-female"></i>
              <h3>巾帼杯</h3>
              <p>查看巾帼杯赛事信息</p>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" @click.native="$router.push('/matches/eight-a-side')">
            <div class="match-type-card">
              <i class="el-icon-football"></i>
              <h3>八人制比赛</h3>
              <p>查看八人制赛事信息</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 精选比赛轮播 -->
    <el-card class="featured-matches-card">
      <div slot="header" class="clearfix">
        <span>精选比赛</span>
      </div>

      <el-carousel :interval="4000" type="card" height="200px">
        <el-carousel-item v-for="match in featuredMatches" :key="match.id">
          <div class="featured-match-item" @click="viewMatchDetails(match)">
            <div class="featured-match-header">
              <span class="match-type-tag">{{ match.type }}</span>
              <span class="match-date">{{ match.date }}</span>
            </div>
            <div class="featured-match-teams">
              <span class="team1">{{ match.team1 }}</span>
              <span class="vs">VS</span>
              <span class="team2">{{ match.team2 }}</span>
            </div>
            <div class="featured-match-footer">
              <span class="match-location"><i class="el-icon-location"></i> {{ match.location }}</span>
              <el-button size="mini" type="primary">查看详情</el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </el-card>

    <!-- 排行数据 -->
    <el-card class="rankings-card">
      <div slot="header" class="clearfix">
        <span>赛事排行</span>
        <el-select v-model="selectedCompetition" placeholder="选择赛事" style="float: right; width: 150px;" @change="onCompetitionChange">
          <el-option label="冠军杯" value="championsCup"></el-option>
          <el-option label="巾帼杯" value="womensCup"></el-option>
          <el-option label="八人制" value="eightASide"></el-option>
        </el-select>
      </div>

      <el-tabs type="card" v-model="activeRankingTab">
        <!-- 射手榜 -->
        <el-tab-pane label="射手榜" name="scorers">
          <el-row :gutter="20">
            <el-col :span="12">
              <h3>球员射手榜</h3>
              <el-table :data="currentRankings.topScorers.players" style="width: 100%">
                <el-table-column prop="name" label="球员"></el-table-column>
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="goals" label="进球数"></el-table-column>
              </el-table>
            </el-col>
            <el-col :span="12">
              <h3>球队射手榜</h3>
              <el-table :data="currentRankings.topScorers.teams" style="width: 100%">
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="goals" label="进球数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 红黄牌榜 -->
        <el-tab-pane label="红黄牌榜" name="cards">
          <el-row :gutter="20">
            <el-col :span="12">
              <h3>球员红黄牌榜</h3>
              <el-table :data="currentRankings.cards.players" style="width: 100%">
                <el-table-column prop="name" label="球员"></el-table-column>
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
                <el-table-column prop="redCards" label="红牌数"></el-table-column>
              </el-table>
            </el-col>
            <el-col :span="12">
              <h3>球队红黄牌榜</h3>
              <el-table :data="currentRankings.cards.teams" style="width: 100%">
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
                <el-table-column prop="redCards" label="红牌数"></el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 积分榜 -->
        <el-tab-pane label="积分榜" name="points">
          <el-select v-model="currentRankingsTab" placeholder="选择阶段" style="float: right; width: 150px; margin-bottom: 20px;" @change="onRankingsTabChange">
            <el-option label="常规赛" value="常规赛"></el-option>
            <el-option label="淘汰赛" value="淘汰赛"></el-option>
          </el-select>
          
          <div v-if="currentRankingsTab === '常规赛'">
            <div v-if="selectedCompetition === 'eightASide'">
              <div v-for="group in sortedGroupRankings" :key="group.name" style="margin-bottom: 30px;">
                <h3>{{ group.name }}</h3>
                <el-table :data="group.teams" style="width: 100%">
                  <el-table-column prop="team" label="球队" width="120"></el-table-column>
                  <el-table-column prop="matchesPlayed" label="比赛场次" width="100"></el-table-column>
                  <el-table-column prop="wins" label="胜" width="60"></el-table-column>
                  <el-table-column prop="draws" label="平" width="60"></el-table-column>
                  <el-table-column prop="losses" label="负" width="60"></el-table-column>
                  <el-table-column prop="goalsFor" label="进球" width="70"></el-table-column>
                  <el-table-column prop="goalsAgainst" label="失球" width="70"></el-table-column>
                  <el-table-column label="净胜" width="70">
                    <template slot-scope="scope">
                      {{ scope.row.goalsFor - scope.row.goalsAgainst }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="points" label="积分" width="70"></el-table-column>
                </el-table>
              </div>
            </div>
            <div v-else>
              <el-table :data="currentRankings.points" style="width: 100%">
                <el-table-column prop="team" label="球队"></el-table-column>
                <el-table-column prop="matchesPlayed" label="比赛场次"></el-table-column>
                <el-table-column prop="points" label="积分"></el-table-column>
              </el-table>
            </div>
          </div>
          
          <div v-else>
            <div v-for="round in currentPlayoffBracket" :key="round.round" style="margin-bottom: 20px;">
              <h3>{{ round.round }}</h3>
              <div v-for="(match, index) in round.matches" :key="index" style="padding: 10px; background: #f5f7fa; margin-bottom: 10px; border-radius: 5px;">
                {{ match }}
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 近期比赛 -->
    <el-card class="recent-matches-card">
      <div slot="header" class="clearfix">
        <span>近期比赛</span>
      </div>
      <el-table :data="recentMatches[selectedCompetition]" style="width: 100%">
        <el-table-column prop="name" label="比赛名称"></el-table-column>
        <el-table-column prop="type" label="类型"></el-table-column>
        <el-table-column prop="date" label="日期"></el-table-column>
        <el-table-column prop="location" label="地点"></el-table-column>
        <el-table-column label="对阵">
          <template slot-scope="scope">
            {{ scope.row.team1 }} vs {{ scope.row.team2 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button size="mini" type="primary" @click="viewMatchDetails(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { useUserStore } from '@/store';
import { ElMessage } from 'element-plus';

export default {
  name: 'Home',
  data() {
    return {
      selectedCompetition: 'championsCup',
      activeRankingTab: 'scorers',
      currentRankingsTab: '常规赛',
      recentMatches: {
        championsCup: [],
        womensCup: [],
        eightASide: []
      },
      featuredMatches: [],
      statsData: {
        totalMatches: 0,
        upcomingMatches: 0,
        completedMatches: 0
      },
      rankings: {
        championsCup: {
          topScorers: {
            players: [],
            teams: []
          },
          cards: {
            players: [],
            teams: []
          },
          points: []
        },
        womensCup: {
          topScorers: {
            players: [],
            teams: []
          },
          cards: {
            players: [],
            teams: []
          },
          points: []
        },
        eightASide: {
          topScorers: {
            players: [],
            teams: []
          },
          cards: {
            players: [],
            teams: []
          },
          points: []
        }
      },
      playoffBracket: {
        championsCup: [
          { round: '半决赛', matches: ['红牛队 vs 蓝狮队', '雄鹰队 vs 猛虎队'] },
          { round: '决赛', matches: ['红牛队 vs 雄鹰队'] },
          { round: '季军赛', matches: ['蓝狮队 vs 猛虎队'] }
        ],
        womensCup: [
          { round: '半决赛', matches: ['凤凰队 vs 玫瑰队', '飓风队 vs 百合队'] },
          { round: '决赛', matches: ['凤凰队 vs 百合队'] }
        ],
        eightASide: [
          { round: '1/4决赛', matches: ['闪电队 vs 雷霆队', '烈火队 vs 寒冰队'] },
          { round: '半决赛', matches: ['闪电队 vs 烈火队', '雷霆队 vs 寒冰队'] },
          { round: '决赛', matches: ['闪电队 vs 雷霆队'] }
        ]
      },
      groupRankings: {
        eightASide: {
          groups: [
            {
              name: 'A组',
              teams: [
                { team: '闪电队', group: 'A', matchesPlayed: 3, wins: 2, draws: 1, losses: 0, goalsFor: 9, goalsAgainst: 2, points: 7 },
                { team: '雷霆队', group: 'A', matchesPlayed: 3, wins: 1, draws: 2, losses: 0, goalsFor: 2, goalsAgainst: 1, points: 5 },
                { team: '烈火队', group: 'A', matchesPlayed: 3, wins: 1, draws: 0, losses: 2, goalsFor: 4, goalsAgainst: 7, points: 3 },
                { team: '寒冰队', group: 'A', matchesPlayed: 3, wins: 0, draws: 1, losses: 2, goalsFor: 1, goalsAgainst: 6, points: 1 }
              ]
            },
            {
              name: 'B组',
              teams: [
                { team: '疾风队', group: 'B', matchesPlayed: 3, wins: 3, draws: 0, losses: 0, goalsFor: 7, goalsAgainst: 1, points: 9 },
                { team: '山岳队', group: 'B', matchesPlayed: 3, wins: 2, draws: 0, losses: 1, goalsFor: 6, goalsAgainst: 5, points: 6 },
                { team: '海浪队', group: 'B', matchesPlayed: 3, wins: 1, draws: 1, losses: 1, goalsFor: 4, goalsAgainst: 4, points: 4 },
                { team: '森林队', group: 'B', matchesPlayed: 3, wins: 0, draws: 2, losses: 1, goalsFor: 2, goalsAgainst: 5, points: 2 }
              ]
            }
          ]
        }
      }
    };
  },
  computed: {
    currentRankings() {
      return this.rankings[this.selectedCompetition] || {
        topScorers: { players: [], teams: [] },
        cards: { players: [], teams: [] },
        points: []
      };
    },
    currentPlayoffBracket() {
      return this.playoffBracket[this.selectedCompetition] || [];
    },
    sortedGroupRankings() {
      if (this.selectedCompetition !== 'eightASide' || !this.groupRankings.eightASide) {
        return [];
      }
      return this.groupRankings.eightASide.groups.map(group => ({
        ...group,
        teams: group.teams.slice().sort((a, b) => {
          if (b.points !== a.points) {
            return b.points - a.points;
          }
          const aDiff = a.goalsFor - a.goalsAgainst;
          const bDiff = b.goalsFor - b.goalsAgainst;
          if (bDiff !== aDiff) {
            return bDiff - aDiff;
          }
          return b.goalsFor - a.goalsFor;
        })
      }));
    }
  },
  created() {
    this.fetchRecentMatches();
    this.fetchFeaturedMatches();
    this.fetchStats();
    this.fetchRankings();
  },
  methods: {
    fetchRecentMatches() {
      axios.get('/api/matches')
        .then(response => {
          if (response.data.status === 'success') {
            const matches = response.data.data;
            this.recentMatches.championsCup = matches.filter(match => match.type === '冠军杯').slice(0, 5);
            this.recentMatches.womensCup = matches.filter(match => match.type === '巾帼杯').slice(0, 5);
            this.recentMatches.eightASide = matches.filter(match => match.type === '八人制').slice(0, 5);
          }
        })
        .catch(error => {
          console.error('获取比赛数据失败:', error);
          this.recentMatches = {
            championsCup: [
              { id: 1, name: '冠军杯半决赛A组', type: '冠军杯', date: '2023-06-10 15:00:00', location: '主体育场', team1: '红牛队', team2: '蓝狮队' },
              { id: 2, name: '冠军杯半决赛B组', type: '冠军杯', date: '2023-06-12 14:00:00', location: '体育中心', team1: '雄鹰队', team2: '猛虎队' },
              { id: 3, name: '冠军杯决赛', type: '冠军杯', date: '2023-06-15 15:00:00', location: '主体育场', team1: '红牛队', team2: '雄鹰队' },
              { id: 4, name: '冠军杯季军赛', type: '冠军杯', date: '2023-06-14 16:00:00', location: '体育中心', team1: '蓝狮队', team2: '猛虎队' },
              { id: 5, name: '冠军杯小组赛', type: '冠军杯', date: '2023-06-08 18:30:00', location: '西区球场', team1: '飞豹队', team2: '狂狼队' }
            ],
            womensCup: [
              { id: 6, name: '巾帼杯第三轮A组', type: '巾帼杯', date: '2023-06-12 14:00:00', location: '体育中心', team1: '凤凰队', team2: '飓风队' },
              { id: 7, name: '巾帼杯第三轮B组', type: '巾帼杯', date: '2023-06-13 15:00:00', location: '主体育场', team1: '玫瑰队', team2: '百合队' },
              { id: 8, name: '巾帼杯半决赛', type: '巾帼杯', date: '2023-06-16 14:00:00', location: '体育中心', team1: '凤凰队', team2: '玫瑰队' },
              { id: 9, name: '巾帼杯小组赛', type: '巾帼杯', date: '2023-06-09 16:00:00', location: '南区球场', team1: '蝴蝶队', team2: '鸿雁队' },
              { id: 10, name: '巾帼杯决赛', type: '巾帼杯', date: '2023-06-18 15:00:00', location: '主体育场', team1: '凤凰队', team2: '百合队' }
            ],
            eightASide: [
              { id: 11, name: '八人制联赛第5轮', type: '八人制', date: '2023-06-15 18:30:00', location: '西区球场', team1: '闪电队', team2: '雷霆队' },
              { id: 12, name: '八人制联赛第6轮', type: '八人制', date: '2023-06-17 19:00:00', location: '东区球场', team1: '烈火队', team2: '寒冰队' },
              { id: 13, name: '八人制联赛第7轮', type: '八人制', date: '2023-06-19 18:00:00', location: '北区球场', team1: '疾风队', team2: '山岳队' },
              { id: 14, name: '八人制联赛第4轮', type: '八人制', date: '2023-06-13 19:30:00', location: '南区球场', team1: '海浪队', team2: '森林队' },
              { id: 15, name: '八人制联赛第8轮', type: '八人制', date: '2023-06-21 18:30:00', location: '中央球场', team1: '钢铁队', team2: '流星队' }
            ]
          };
        });
    },
    fetchFeaturedMatches() {
      this.featuredMatches = [
        { id: 1, name: '冠军杯决赛', type: '冠军杯', date: '2023-06-15 15:00', location: '主体育场', team1: '红牛队', team2: '蓝狮队' },
        { id: 2, name: '巾帼杯半决赛', type: '巾帼杯', date: '2023-06-12 14:00', location: '体育中心', team1: '凤凰队', team2: '飓风队' },
        { id: 3, name: '八人制联赛焦点战', type: '八人制', date: '2023-06-18 18:30', location: '西区球场', team1: '闪电队', team2: '雷霆队' }
      ];
    },
    fetchStats() {
      this.statsData = {
        totalMatches: 24,
        upcomingMatches: 8,
        completedMatches: 16
      };
    },
    fetchRankings() {
      axios.get('/api/rankings')
        .then(response => {
          if (response.data.status === 'success') {
            this.rankings = response.data.data;
          }
        })
        .catch(error => {
          console.error('获取排行数据失败:', error);
          this.rankings = {
            championsCup: {
              topScorers: {
                players: [
                  { name: '张三', team: '红牛队', goals: 15 },
                  { name: '李四', team: '蓝狮队', goals: 12 },
                  { name: '王五', team: '雄鹰队', goals: 10 },
                  { name: '赵六', team: '猛虎队', goals: 9 },
                  { name: '钱七', team: '飞豹队', goals: 8 }
                ],
                teams: [
                  { team: '红牛队', goals: 45 },
                  { team: '蓝狮队', goals: 38 },
                  { team: '雄鹰队', goals: 35 },
                  { team: '猛虎队', goals: 32 },
                  { team: '飞豹队', goals: 28 }
                ]
              },
              cards: {
                players: [
                  { name: '孙八', team: '狂狼队', yellowCards: 8, redCards: 2 },
                  { name: '周九', team: '红牛队', yellowCards: 6, redCards: 1 },
                  { name: '吴十', team: '蓝狮队', yellowCards: 5, redCards: 1 },
                  { name: '郑一', team: '雄鹰队', yellowCards: 4, redCards: 0 },
                  { name: '王二', team: '猛虎队', yellowCards: 3, redCards: 0 }
                ],
                teams: [
                  { team: '狂狼队', yellowCards: 25, redCards: 5 },
                  { team: '红牛队', yellowCards: 18, redCards: 3 },
                  { team: '蓝狮队', yellowCards: 15, redCards: 2 },
                  { team: '雄鹰队', yellowCards: 12, redCards: 1 },
                  { team: '猛虎队', yellowCards: 10, redCards: 1 }
                ]
              },
              points: [
                { team: '红牛队', matchesPlayed: 12, points: 30 },
                { team: '雄鹰队', matchesPlayed: 12, points: 28 },
                { team: '蓝狮队', matchesPlayed: 12, points: 25 },
                { team: '猛虎队', matchesPlayed: 12, points: 22 },
                { team: '飞豹队', matchesPlayed: 12, points: 18 }
              ]
            },
            womensCup: {
              topScorers: {
                players: [
                  { name: '小红', team: '凤凰队', goals: 12 },
                  { name: '小芳', team: '玫瑰队', goals: 10 },
                  { name: '小丽', team: '百合队', goals: 9 },
                  { name: '小美', team: '飓风队', goals: 8 },
                  { name: '小娟', team: '蝴蝶队', goals: 7 }
                ],
                teams: [
                  { team: '凤凰队', goals: 35 },
                  { team: '玫瑰队', goals: 30 },
                  { team: '百合队', goals: 28 },
                  { team: '飓风队', goals: 25 },
                  { team: '蝴蝶队', goals: 22 }
                ]
              },
              cards: {
                players: [
                  { name: '小华', team: '鸿雁队', yellowCards: 5, redCards: 1 },
                  { name: '小玲', team: '凤凰队', yellowCards: 4, redCards: 0 },
                  { name: '小燕', team: '玫瑰队', yellowCards: 3, redCards: 0 },
                  { name: '小雪', team: '百合队', yellowCards: 3, redCards: 0 },
                  { name: '小梅', team: '飓风队', yellowCards: 2, redCards: 0 }
                ],
                teams: [
                  { team: '鸿雁队', yellowCards: 15, redCards: 2 },
                  { team: '凤凰队', yellowCards: 12, redCards: 1 },
                  { team: '玫瑰队', yellowCards: 10, redCards: 1 },
                  { team: '百合队', yellowCards: 8, redCards: 0 },
                  { team: '飓风队', yellowCards: 6, redCards: 0 }
                ]
              },
              points: [
                { team: '凤凰队', matchesPlayed: 8, points: 21 },
                { team: '玫瑰队', matchesPlayed: 8, points: 18 },
                { team: '百合队', matchesPlayed: 8, points: 16 },
                { team: '飓风队', matchesPlayed: 8, points: 12 },
                { team: '蝴蝶队', matchesPlayed: 8, points: 9 }
              ]
            },
            eightASide: {
              topScorers: {
                players: [
                  { name: '阿强', team: '闪电队', goals: 18 },
                  { name: '阿明', team: '雷霆队', goals: 16 },
                  { name: '阿伟', team: '烈火队', goals: 14 },
                  { name: '阿华', team: '寒冰队', goals: 13 },
                  { name: '阿超', team: '疾风队', goals: 11 }
                ],
                teams: [
                  { team: '闪电队', goals: 52 },
                  { team: '雷霆队', goals: 48 },
                  { team: '烈火队', goals: 44 },
                  { team: '寒冰队', goals: 40 },
                  { team: '疾风队', goals: 36 }
                ]
              },
              cards: {
                players: [
                  { name: '阿龙', team: '山岳队', yellowCards: 10, redCards: 3 },
                  { name: '阿虎', team: '海浪队', yellowCards: 8, redCards: 2 },
                  { name: '阿豹', team: '森林队', yellowCards: 7, redCards: 1 },
                  { name: '阿鹰', team: '钢铁队', yellowCards: 6, redCards: 1 },
                  { name: '阿狼', team: '流星队', yellowCards: 5, redCards: 0 }
                ],
                teams: [
                  { team: '山岳队', yellowCards: 30, redCards: 6 },
                  { team: '海浪队', yellowCards: 25, redCards: 4 },
                  { team: '森林队', yellowCards: 22, redCards: 3 },
                  { team: '钢铁队', yellowCards: 18, redCards: 2 },
                  { team: '流星队', yellowCards: 15, redCards: 1 }
                ]
              },
              points: [
                { team: '疾风队', matchesPlayed: 3, points: 9 },
                { team: '山岳队', matchesPlayed: 3, points: 6 },
                { team: '海浪队', matchesPlayed: 3, points: 4 },
                { team: '森林队', matchesPlayed: 3, points: 2 }
              ]
            }
          };
        });
    },
    onCompetitionChange() {
      this.currentRankingsTab = '常规赛';
      this.activeRankingTab = 'scorers';
    },
    onRankingsTabChange() {
      // 切换积分榜阶段时的逻辑
    },
    viewMatchDetails(match) {
      this.$router.push(`/matches/detail/${match.id}`);
    },
    logout() {
      // 确认退出登录
      this.$confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const userStore = useUserStore();
        
        // 清除用户状态
        userStore.logout();
        
        // 清除本地存储
        localStorage.removeItem('userToken');
        localStorage.removeItem('userInfo');
        sessionStorage.clear();
        
        // 显示退出消息
        this.$message.success('已退出登录');
        
        // 使用页面刷新跳转到登录页
        setTimeout(() => {
          window.location.href = '/login';
        }, 500);
      }).catch(() => {
        // 取消退出，不做任何操作
      });
    }
  }
};
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card,
.featured-matches-card,
.rankings-card,
.recent-matches-card {
  margin-bottom: 20px;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  background-color: #f7f8fa;
  border: none;
  height: 100px;
}

.stats-card-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  font-size: 40px;
  color: #409EFF;
  margin-right: 15px;
}

.stats-info {
  display: flex;
  flex-direction: column;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.match-types {
  margin-top: 20px;
}

.match-type-card {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.match-type-card:hover {
  transform: translateY(-5px);
}

.match-type-card i {
  font-size: 40px;
  margin-bottom: 10px;
  color: #409EFF;
}

.match-type-card h3 {
  margin-bottom: 10px;
}

.featured-match-item {
  height: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #1e88e5, #0d47a1);
  color: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
}

.featured-match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.match-type-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
}

.featured-match-teams {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin: 20px 0;
}

.vs {
  margin: 0 15px;
  color: #ffeb3b;
}

.featured-match-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-timeline-item {
  padding-bottom: 20px;
}

.el-timeline-item h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.el-timeline-item p {
  margin-top: 10px;
  color: #606266;
}

.el-divider {
  margin: 30px 0;
}

h2 {
  margin-bottom: 20px;
}

.rankings-card {
  margin-bottom: 20px;
}

h3 {
  margin-bottom: 10px;
}
</style>