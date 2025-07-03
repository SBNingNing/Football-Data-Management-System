<template>
  <div class="match-detail">
    <!-- 比赛基本信息卡片 -->
    <el-card class="match-basic-info">
      <div class="match-header">
        <div class="back-button-container">
          <el-button 
            type="primary" 
            :icon="ArrowLeft" 
            plain
            @click="goBack"
            class="back-button"
          >
            返回
          </el-button>
        </div>
        <div class="status-container">
          <span class="match-status" :class="getMatchStatusClass()">{{ getMatchStatusText() }}</span>
        </div>
        <h1 class="match-title">{{ match.homeTeam }} VS {{ match.awayTeam }}</h1>
        <div class="match-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            比赛时间: {{ match.matchDate }}
          </span>
          <span class="meta-item">
            <el-icon><Trophy /></el-icon>
            赛事: {{ match.tournament }}
          </span>
          <span class="meta-item">
            <el-icon><Location /></el-icon>
            赛季: {{ match.season }}
          </span>
        </div>
        <div class="match-score">
          <span class="score">{{ match.homeScore }} : {{ match.awayScore }}</span>
        </div>
      </div>
    </el-card>

    <!-- 比赛统计数据 -->
    <el-card class="match-stats">
      <template #header>
        <div class="clearfix">
          <span>比赛统计数据</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="5">
          <div class="stat-item" style="background-color: #1e88e5; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Finished /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ match.totalGoals }}</div>
              <div class="stat-label">总进球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-item" style="background-color: #ff9800; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Football /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ match.totalOwnGoals }}</div>
              <div class="stat-label">乌龙球数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-item" style="background-color: #f39c12; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ match.totalYellowCards }}</div>
              <div class="stat-label">黄牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-item" style="background-color: #e74c3c; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ match.totalRedCards }}</div>
              <div class="stat-label">红牌数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item" style="background-color: #27ae60; color: white;">
            <el-icon style="color: #ffffff; font-size: 40px;"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ match.totalPlayers }}</div>
              <div class="stat-label">参赛球员</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 球队表现对比 -->
    <el-card class="team-comparison">
      <template #header>
        <div class="clearfix">
          <span>球队表现对比</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="team-stats">
            <h3>{{ match.homeTeam }}</h3>
            <el-row :gutter="10">
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.homeTeamStats.goals }}</div>
                  <div class="team-stat-label">进球</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.homeTeamStats.ownGoals }}</div>
                  <div class="team-stat-label">乌龙球</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.homeTeamStats.yellowCards }}</div>
                  <div class="team-stat-label">黄牌</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.homeTeamStats.redCards }}</div>
                  <div class="team-stat-label">红牌</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="team-stats">
            <h3>{{ match.awayTeam }}</h3>
            <el-row :gutter="10">
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.awayTeamStats.goals }}</div>
                  <div class="team-stat-label">进球</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.awayTeamStats.ownGoals }}</div>
                  <div class="team-stat-label">乌龙球</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.awayTeamStats.yellowCards }}</div>
                  <div class="team-stat-label">黄牌</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="team-stat-item">
                  <div class="team-stat-number">{{ match.awayTeamStats.redCards }}</div>
                  <div class="team-stat-label">红牌</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 球员表现详情 -->
    <el-card class="player-performances">
      <template #header>
        <div class="clearfix">
          <span>球员表现详情</span>
          <div class="header-controls">
            <div class="search-stats">
              共 {{ filteredPlayers.length }} 名球员
            </div>
            <el-radio-group v-model="selectedTeam" class="team-filter">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button :label="match.homeTeam">{{ match.homeTeam }}</el-radio-button>
              <el-radio-button :label="match.awayTeam">{{ match.awayTeam }}</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      
      <!-- 球员卡片展示 -->
      <div class="players-section" v-loading="playersLoading" element-loading-text="正在加载球员数据...">
        <div v-if="filteredPlayers.length === 0 && !playersLoading" class="no-players">
          <el-icon class="no-data-icon"><UserFilled /></el-icon>
          <p>{{ selectedTeam === 'all' ? '暂无球员数据' : `${selectedTeam} 队暂无球员数据` }}</p>
        </div>
        
        <el-row :gutter="20" v-else>
          <el-col 
            :span="8" 
            v-for="player in paginatedPlayers" 
            :key="player.playerId"
            class="player-col"
          >
            <el-card 
              shadow="hover" 
              class="player-card"
              @click="viewPlayerHistory(player.playerId)"
            >
              <div class="player-info">
                <div class="player-avatar">
                  <el-icon class="avatar-icon"><User /></el-icon>
                </div>
                <div class="player-details">
                  <div class="player-name">{{ player.playerName || '未知球员' }}</div>
                  <div class="player-meta">
                    <div class="meta-item">
                      <el-icon><Trophy /></el-icon>
                      <span>{{ player.teamName || '未知球队' }}</span>
                    </div>
                    <div class="meta-item" v-if="player.playerNumber">
                      <el-icon><Tickets /></el-icon>
                      <span>{{ player.playerNumber }}号</span>
                    </div>
                  </div>
                  <div class="player-stats">
                    <span class="stat-badge goals">
                      <el-icon><Football /></el-icon>
                      {{ player.goals || 0 }}球
                    </span>
                    <span class="stat-badge own-goals">
                      <el-icon><Football /></el-icon>
                      {{ player.ownGoals || 0 }}乌龙
                    </span>
                    <span class="stat-badge yellow-cards">
                      <el-icon><Warning /></el-icon>
                      {{ player.yellowCards || 0 }}黄
                    </span>
                    <span class="stat-badge red-cards">
                      <el-icon><CircleClose /></el-icon>
                      {{ player.redCards || 0 }}红
                    </span>
                  </div>
                </div>
              </div>
              <div class="player-card-overlay">
                <el-icon><View /></el-icon>
                <span>查看详情</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="filteredPlayers.length > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 48]"
          :total="filteredPlayers.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handleCurrentPageChange"
        />
      </div>
    </el-card>

    <!-- 比赛事件时间轴 -->
    <el-card class="match-events">
      <template #header>
        <div class="clearfix">
          <span>比赛事件时间轴</span>
          <div class="events-stats">
            共 {{ events.length }} 个事件
          </div>
        </div>
      </template>
      
      <div class="events-timeline" v-loading="playersLoading" element-loading-text="正在加载事件数据...">
        <div v-if="events.length === 0 && !playersLoading" class="no-events">
          <el-icon class="no-data-icon"><Clock /></el-icon>
          <p>暂无比赛事件记录</p>
        </div>
        
        <div v-else class="timeline-container">
          <div 
            v-for="event in events" 
            :key="event.id"
            class="timeline-item"
            :class="getEventTypeClass(event.event_type)"
          >
            <div class="timeline-marker">
              <el-icon class="event-icon">
                <component :is="getEventIcon(event.event_type)" />
              </el-icon>
            </div>
            <div class="timeline-content">
              <div class="event-header">
                <span class="event-time">{{ event.event_time }}'</span>
                <span class="event-type">{{ event.event_type_text }}</span>
              </div>
              <div class="event-details">
                <div class="player-info">
                  <el-icon><User /></el-icon>
                  <span class="player-name">{{ event.player_name }}</span>
                </div>
                <div class="team-info">
                  <el-icon><Trophy /></el-icon>
                  <span class="team-name">{{ event.team_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { useUserStore } from '@/store'
import { 
  Finished, 
  Warning, 
  CircleClose, 
  User, 
  UserFilled,
  Trophy, 
  ArrowLeft, 
  Calendar, 
  Location, 
  Tickets, 
  Football, 
  View,
  Clock
} from '@element-plus/icons-vue'

export default {
  name: 'MatchDetail',
  components: {
    Finished,
    Warning,
    CircleClose,
    User,
    UserFilled,
    Trophy,
    ArrowLeft,
    Calendar,
    Location,
    Tickets,
    Football,
    View,
    Clock
  },
  data() {
    return {
      selectedTeam: 'all',
      playersLoading: false,
      currentPage: 1,
      pageSize: 12,
      events: [],
      match: {
        id: '',
        homeTeam: '',
        awayTeam: '',
        homeScore: 0,
        awayScore: 0,
        matchDate: '',
        tournament: '',
        season: '',
        status: '',
        totalGoals: 0,
        totalOwnGoals: 0, // 添加乌龙球统计
        totalYellowCards: 0,
        totalRedCards: 0,
        totalPlayers: 0,
        homeTeamStats: {
          goals: 0,
          ownGoals: 0, // 添加乌龙球统计
          yellowCards: 0,
          redCards: 0
        },
        awayTeamStats: {
          goals: 0,
          ownGoals: 0, // 添加乌龙球统计
          yellowCards: 0,
          redCards: 0
        }
      },
      players: [],
      store: null
    };
  },
  computed: {
    filteredPlayers() {
      if (this.selectedTeam === 'all') {
        return this.players;
      }
      return this.players.filter(player => player.teamName === this.selectedTeam);
    },
    paginatedPlayers() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredPlayers.slice(start, end);
    }
  },
  async mounted() {
    this.store = useUserStore();
    await this.loadMatchData();
  },
  methods: {
    async loadMatchData() {
      try {
        // 获取 matchId 的多种方式
        const matchId = this.$route.params.matchId || 
                       this.$route.query.matchId || 
                       this.$route.params.id;
        
        console.log('=== 路由调试信息 ===');
        console.log('完整路由对象:', this.$route);
        console.log('路由参数 params:', this.$route.params);
        console.log('查询参数 query:', this.$route.query);
        console.log('获取到的 matchId:', matchId);
        console.log('==================');
        
        if (!matchId) {
          this.$message.error('未指定比赛ID');
          console.error('无法获取比赛ID，返回上级页面');
          this.goBack();
          return;
        }
        
        const loading = this.$loading({
          lock: true,
          text: '正在加载比赛数据...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        
        this.playersLoading = true;
        
        try {
          // 获取token
          const token = localStorage.getItem('token') || sessionStorage.getItem('token');
          if (!token) {
            loading.close();
            this.playersLoading = false;
            this.$message.error('用户未登录');
            this.$router.push('/login');
            return;
          }

          console.log(`正在请求比赛详情: /api/matches/${matchId}`);
          
          // 调用后端API获取比赛详情
          const response = await fetch(`/api/matches/${matchId}`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          const result = await response.json();
          
          loading.close();
          this.playersLoading = false;
          
          if (response.ok && result.status === 'success') {
            this.formatMatchData(result.data);
            this.$message.success('比赛数据加载成功');
          } else {
            console.error('API返回错误:', result.message);
            this.$message.error(`加载失败: ${result.message || '未知错误'}`);
            this.goBack();
          }
        } catch (fetchError) {
          loading.close();
          this.playersLoading = false;
          console.error('API调用失败:', fetchError);
          this.$message.error('网络错误，无法获取比赛数据');
          this.goBack();
        }
      } catch (error) {
        this.playersLoading = false;
        console.error('加载比赛数据异常:', error);
        this.$message.error('系统错误，无法获取比赛数据');
        this.goBack();
      }
    },

    // 简化获取所有参与球员的方法
    async loadAllParticipatingPlayers() {
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (!token) return;

        console.log('尝试从事件API获取球员数据...');
        
        // 尝试从事件API获取球员信息
        const eventsResponse = await fetch(`/api/events/match/${this.match.id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (eventsResponse.ok) {
          const eventsResult = await eventsResponse.json();
          if (eventsResult.status === 'success' && eventsResult.data && eventsResult.data.length > 0) {
            console.log('从事件API获取到事件数据:', eventsResult.data);
            
            // 统计每个球员的数据
            const playerStats = new Map();
            
            eventsResult.data.forEach(event => {
              if (event.player_id) {
                if (!playerStats.has(event.player_id)) {
                  playerStats.set(event.player_id, {
                    playerId: event.player_id,
                    playerName: event.player_name || '未知球员',
                    teamName: event.team_name || '未知球队',
                    playerNumber: event.player_number || 0,
                    goals: 0,
                    ownGoals: 0, // 添加乌龙球统计
                    yellowCards: 0,
                    redCards: 0
                  });
                }
                
                const playerData = playerStats.get(event.player_id);
                
                // 统计各类事件 - 进球和乌龙球分开统计
                switch (event.event_type) {
                  case '进球':
                    playerData.goals++;
                    break;
                  case '乌龙球':
                    playerData.ownGoals++;
                    break;
                  case '黄牌':
                    playerData.yellowCards++;
                    break;
                  case '红牌':
                    playerData.redCards++;
                    break;
                }
              }
            });

            // 更新球员数据
            this.players = Array.from(playerStats.values());
            
            // 同时更新比赛统计数据
            this.updateMatchStats(eventsResult.data);
            
            console.log('统计后的球员数据:', this.players);
          }
        } else {
          console.log('无法从事件API获取数据，使用比赛详情API的数据');
        }
      } catch (error) {
        console.error('获取球员数据失败:', error);
      }
    },

    // 更新比赛统计数据方法 - 处理乌龙球逻辑和参赛球员数量
    updateMatchStats(events) {
      if (!events || events.length === 0) return;
      
      let totalGoals = 0;
      let totalOwnGoals = 0;
      let totalYellowCards = 0;
      let totalRedCards = 0;
      let homeGoals = 0;
      let awayGoals = 0;
      let homeOwnGoals = 0;
      let awayOwnGoals = 0;
      let homeYellowCards = 0;
      let awayYellowCards = 0;
      let homeRedCards = 0;
      let awayRedCards = 0;
      
      // 统计参与事件的球员数量
      const uniquePlayers = new Set();
      
      events.forEach(event => {
        // 统计参与的球员
        if (event.player_id) {
          uniquePlayers.add(event.player_id);
        }
        
        // 使用中文事件类型进行统计
        switch (event.event_type) {
          case '进球':
            totalGoals++;
            // 正常进球，计入对应球队
            if (event.team_name === this.match.homeTeam) {
              homeGoals++;
            } else if (event.team_name === this.match.awayTeam) {
              awayGoals++;
            }
            break;
          case '乌龙球':
            totalOwnGoals++; // 乌龙球单独统计
            // 乌龙球记录在对应球队，但不影响进球数
            if (event.team_name === this.match.homeTeam) {
              homeOwnGoals++; // 主队乌龙球
            } else if (event.team_name === this.match.awayTeam) {
              awayOwnGoals++; // 客队乌龙球
            }
            break;
          case '黄牌':
            totalYellowCards++;
            if (event.team_name === this.match.homeTeam) {
              homeYellowCards++;
            } else if (event.team_name === this.match.awayTeam) {
              awayYellowCards++;
            }
            break;
          case '红牌':
            totalRedCards++;
            if (event.team_name === this.match.homeTeam) {
              homeRedCards++;
            } else if (event.team_name === this.match.awayTeam) {
              awayRedCards++;
            }
            break;
        }
      });
      
      // 更新比赛统计数据
      this.match.totalGoals = totalGoals;
      this.match.totalOwnGoals = totalOwnGoals;
      this.match.totalYellowCards = totalYellowCards;
      this.match.totalRedCards = totalRedCards;
      this.match.homeTeamStats.goals = homeGoals;
      this.match.homeTeamStats.ownGoals = homeOwnGoals;
      this.match.homeTeamStats.yellowCards = homeYellowCards;
      this.match.homeTeamStats.redCards = homeRedCards;
      this.match.awayTeamStats.goals = awayGoals;
      this.match.awayTeamStats.ownGoals = awayOwnGoals;
      this.match.awayTeamStats.yellowCards = awayYellowCards;
      this.match.awayTeamStats.redCards = awayRedCards;
      
      console.log('更新后的比赛统计数据:', {
        totalGoals,
        totalOwnGoals,
        totalYellowCards,
        totalRedCards,
        totalPlayers: this.match.totalPlayers,
        homeStats: this.match.homeTeamStats,
        awayStats: this.match.awayTeamStats
      });
    },

    formatMatchData(data) {
      // 格式化比赛数据
      this.match = {
        id: data.id,
        homeTeam: data.home_team_name || '主队',
        awayTeam: data.away_team_name || '客队',
        homeScore: data.home_score || 0,
        awayScore: data.away_score || 0,
        matchDate: this.formatDateDisplay(data.match_date),
        tournament: data.tournament_name || '',
        season: data.season_name || '',
        status: this.mapStatusFromBackend(data.status),
        totalGoals: data.total_goals || 0,
        totalOwnGoals: data.total_own_goals || 0, // 添加乌龙球统计
        totalYellowCards: data.total_yellow_cards || 0,
        totalRedCards: data.total_red_cards || 0,
        totalPlayers: data.total_players || 0,
        homeTeamStats: {
          goals: data.home_goals || 0,
          ownGoals: data.home_own_goals || 0, // 添加乌龙球统计
          yellowCards: data.home_yellow_cards || 0,
          redCards: data.home_red_cards || 0
        },
        awayTeamStats: {
          goals: data.away_goals || 0,
          ownGoals: data.away_own_goals || 0, // 添加乌龙球统计
          yellowCards: data.away_yellow_cards || 0,
          redCards: data.away_red_cards || 0
        }
      };

      // 格式化球员数据 - 确保正确映射字段
      this.players = (data.players || []).map(player => ({
        playerId: player.player_id,
        playerName: player.player_name || '未知球员',
        teamName: player.team_name || '未知球队',
        playerNumber: player.player_number || 0,
        goals: player.goals || 0,
        ownGoals: player.own_goals || 0, // 添加乌龙球统计
        yellowCards: player.yellow_cards || 0,
        redCards: player.red_cards || 0
      }));

      // 格式化事件数据
      this.events = (data.events || []).map(event => ({
        id: event.id,
        event_type: event.event_type,
        event_time: event.event_time || 0,
        player_id: event.player_id,
        player_name: event.player_name || '未知球员',
        team_id: event.team_id,
        team_name: event.team_name || '未知球队',
        event_type_text: event.event_type_text || event.event_type  // 直接使用中文
      }));

      console.log('格式化后的比赛数据:', this.match);
      console.log('格式化后的球员数据:', this.players);
      console.log('格式化后的事件数据:', this.events);
      console.log('参赛球员总数:', this.match.totalPlayers);
      
      // 验证数据完整性
      if (this.players.length === 0) {
        console.log('没有球员数据，尝试重新获取...');
        this.loadAllParticipatingPlayers();
      }
    },

    // 获取事件类型对应的图标 - 支持中文事件类型
    getEventIcon(eventType) {
      const iconMap = {
        '进球': 'Football',
        '黄牌': 'Warning',
        '红牌': 'CircleClose',
        '换人': 'User',
        '点球': 'Trophy',
        '乌龙球': 'Football',
        // 英文兼容
        'goal': 'Football',
        'yellow_card': 'Warning',
        'red_card': 'CircleClose',
        'substitution': 'User',
        'penalty': 'Trophy',
        'own_goal': 'Football'
      };
      return iconMap[eventType] || 'Clock';
    },

    // 获取事件类型的样式类 - 支持中文事件类型
    getEventTypeClass(eventType) {
      const classMap = {
        '进球': 'event-goal',
        '黄牌': 'event-yellow-card',
        '红牌': 'event-red-card',
        '换人': 'event-substitution',
        '点球': 'event-penalty',
        '乌龙球': 'event-own-goal',
        // 英文兼容
        'goal': 'event-goal',
        'yellow_card': 'event-yellow-card',
        'red_card': 'event-red-card',
        'substitution': 'event-substitution',
        'penalty': 'event-penalty',
        'own_goal': 'event-own-goal'
      };
      return classMap[eventType] || 'event-default';
    },

    // 添加日期格式化方法
    formatDateDisplay(dateStr) {
      if (!dateStr) return '时间待定';
      
      try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
          return '时间待定';
        }
        
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } catch (error) {
        console.error('Date formatting error:', error);
        return '时间待定';
      }
    },

    // 添加状态映射方法
    mapStatusFromBackend(status) {
      const statusMap = {
        'P': 'upcoming',
        'O': 'ongoing',
        'F': 'completed'
      };
      return statusMap[status] || 'completed';
    },

    getMatchStatusClass() {
      switch (this.match.status) {
        case 'completed':
          return 'status-completed';
        case 'ongoing':
          return 'status-ongoing';
        case 'upcoming':
          return 'status-upcoming';
        default:
          return 'status-completed';
      }
    },

    getMatchStatusText() {
      switch (this.match.status) {
        case 'completed':
          return '已结束';
        case 'ongoing':
          return '进行中';
        case 'upcoming':
          return '未开始';
        default:
          return '已结束';
      }
    },

    viewPlayerHistory(playerId) {
      // 跳转到球员详情页面
      if (playerId) {
        this.$router.push({
          name: 'PlayerDetail',
          params: { playerId }
        });
      } else {
        this.$message.info('球员信息不完整，无法查看详情');
      }
    },

    goBack() {
      // 返回上一页或首页
      if (window.history.length > 1) {
        this.$router.back();
      } else {
        this.$router.push('/');
      }
    },

    handlePageSizeChange(newSize) {
      this.pageSize = newSize;
      this.currentPage = 1;
    },

    handleCurrentPageChange(newPage) {
      this.currentPage = newPage;
    }
  }
};
</script>

<style scoped>
.match-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.match-basic-info,
.match-stats,
.team-comparison,
.player-performances {
  margin-bottom: 20px;
}

.match-header {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
  position: relative;
}

.back-button-container {
  position: absolute;
  top: 20px;
  left: 20px;
}

.back-button {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

.status-container {
  position: absolute;
  top: 20px;
  right: 20px;
}

.match-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0 0 15px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.match-meta {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  opacity: 1;
  background-color: rgba(255, 255, 255, 0.15);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.meta-item:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.meta-item .el-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.match-score {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.score {
  font-size: 48px;
  font-weight: bold;
  text-align: center;
}

.match-status {
  font-size: 16px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
}

.status-completed {
  background-color: rgba(255, 255, 255, 0.2);
}

.status-ongoing {
  background-color: #f39c12;
}

.status-upcoming {
  background-color: #3498db;
}

.match-stats {
  margin-bottom: 20px;
}

.match-stats .el-row {
  margin: 0 -10px;
}

.match-stats .el-col {
  padding: 0 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  width: 100%;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-info {
  display: flex;
  flex-direction: column;
  margin-left: 15px;
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
}

.team-stats {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.team-stats h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 24px;
}

.team-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.team-stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.team-stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-top: 5px;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

.player-performances .clearfix {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.search-stats {
  color: #909399;
  font-size: 14px;
  white-space: nowrap;
}

.team-filter {
  flex-shrink: 0;
}

.players-section {
  min-height: 300px;
  margin-top: 20px;
}

.no-players {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #e0e0e0;
}

.player-col {
  margin-bottom: 20px;
}

.player-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 180px;
  background: white;
  border: 1px solid #ebeef5;
}

.player-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.player-card:hover .player-card-overlay {
  opacity: 1;
}

.player-info {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  height: 100%;
  padding: 15px;
}

.player-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 55px;
  height: 55px;
  background: linear-gradient(135deg, #409EFF, #36A3FF);
  border-radius: 50%;
  color: white;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 26px;
}

.player-details {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.player-meta .meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.player-meta .meta-item .el-icon {
  font-size: 14px;
  color: #909399;
}

.player-stats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.stat-badge.goals {
  background-color: #e8f5e8;
  color: #67c23a;
}

.stat-badge.own-goals {
  background-color: #fff3e0;
  color: #ff9800;
}

.stat-badge.yellow-cards {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-badge.red-cards {
  background-color: #fef0f0;
  color: #f56c6c;
}

.player-card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(64, 158, 255, 0.9);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-weight: 500;
}

.player-card-overlay .el-icon {
  font-size: 28px;
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.match-events {
  margin-bottom: 20px;
}

.match-events .clearfix {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.events-stats {
  color: #909399;
  font-size: 14px;
}

.events-timeline {
  min-height: 200px;
  margin-top: 20px;
}

.no-events {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.timeline-container {
  position: relative;
}

.timeline-container::before {
  content: '';
  position: absolute;
  left: 30px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #e4e7ed;
}

.timeline-item {
  position: relative;
  padding: 15px 0 15px 70px;
  margin-bottom: 10px;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: 20px;
  top: 15px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border: 2px solid #e4e7ed;
  z-index: 1;
}

.event-icon {
  font-size: 12px;
  color: #606266;
}

.timeline-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #e4e7ed;
}

.event-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.event-time {
  background-color: #409eff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  min-width: 35px;
  text-align: center;
}

.event-type {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.event-details {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.player-info,
.team-info {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
}

.player-name,
.team-name {
  font-weight: 500;
}

/* 不同事件类型的样式 */
.event-goal .timeline-marker {
  border-color: #67c23a;
}

.event-goal .event-icon {
  color: #67c23a;
}

.event-goal .timeline-content {
  border-left-color: #67c23a;
}

.event-yellow-card .timeline-marker {
  border-color: #e6a23c;
}

.event-yellow-card .event-icon {
  color: #e6a23c;
}

.event-yellow-card .timeline-content {
  border-left-color: #e6a23c;
}

.event-red-card .timeline-marker {
  border-color: #f56c6c;
}

.event-red-card .event-icon {
  color: #f56c6c;
}

.event-red-card .timeline-content {
  border-left-color: #f56c6c;
}

.event-substitution .timeline-marker {
  border-color: #409eff;
}

.event-substitution .event-icon {
  color: #409eff;
}

.event-substitution .timeline-content {
  border-left-color: #409eff;
}

.event-penalty .timeline-marker {
  border-color: #9c27b0;
}

.event-penalty .event-icon {
  color: #9c27b0;
}

.event-penalty .timeline-content {
  border-left-color: #9c27b0;
}

.event-own-goal .timeline-marker {
  border-color: #ff9800;
}

.event-own-goal .event-icon {
  color: #ff9800;
}

.event-own-goal .timeline-content {
  border-left-color: #ff9800;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .timeline-container::before {
    left: 15px;
  }
  
  .timeline-item {
    padding-left: 50px;
  }
  
  .timeline-marker {
    left: 5px;
  }
  
  .event-details {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
