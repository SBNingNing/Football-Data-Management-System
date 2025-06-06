<template>
  <el-card class="rankings-card">
    <template #header>
      <div class="clearfix">
        <span>赛事排行</span>
        <el-select v-model="selectedCompetition" placeholder="选择赛事" style="float: right; width: 150px;" @change="onCompetitionChange">
          <el-option label="冠军杯" value="championsCup"></el-option>
          <el-option label="巾帼杯" value="womensCup"></el-option>
          <el-option label="八人制" value="eightASide"></el-option>
        </el-select>
      </div>
    </template>

    <!-- 加载状态 -->
    <div v-if="loading" style="text-align: center; padding: 20px;">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在加载赛事数据...</p>
    </div>

    <!-- 无数据状态 -->
    <div v-else-if="!hasData" style="text-align: center; padding: 20px;">
      <el-icon><Warning /></el-icon>
      <p>暂无{{ getCompetitionName(selectedCompetition) }}数据</p>
    </div>

    <!-- 数据展示 -->
    <el-tabs v-else type="card" v-model="activeRankingTab">
      <!-- 射手榜 -->
      <el-tab-pane label="射手榜" name="scorers">
        <el-row :gutter="20">
          <el-col :span="12">
            <h3>球员射手榜</h3>
            <el-table :data="currentRankings.topScorers.players" style="width: 100%" v-loading="loading">
              <el-table-column label="球员">
                <template #default="{ row }">
                  <div class="player-name-cell">
                    <span 
                      class="clickable-player" 
                      @click="navigateToPlayer(row)"
                      :title="点击查看球员详情"
                    >
                      <el-icon class="player-icon"><User /></el-icon>
                      {{ row.name }}
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="team" label="球队"></el-table-column>
              <el-table-column prop="goals" label="进球数"></el-table-column>
            </el-table>
          </el-col>
          <el-col :span="12">
            <h3>球队射手榜</h3>
            <el-table :data="currentRankings.topScorers.teams" style="width: 100%" v-loading="loading">
              <el-table-column label="球队">
                <template #default="{ row }">
                  <div class="team-name-cell">
                    <span 
                      class="clickable-team" 
                      @click="navigateToTeam(row)"
                      :title="点击查看球队详情"
                    >
                      <el-icon class="team-icon"><Trophy /></el-icon>
                      {{ row.team }}
                    </span>
                  </div>
                </template>
              </el-table-column>
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
            <el-table :data="currentRankings.cards.players" style="width: 100%" v-loading="loading">
              <el-table-column label="球员">
                <template #default="{ row }">
                  <div class="player-name-cell">
                    <span 
                      class="clickable-player" 
                      @click="navigateToPlayer(row)"
                      :title="点击查看球员详情"
                    >
                      <el-icon class="player-icon"><User /></el-icon>
                      {{ row.name }}
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="team" label="球队"></el-table-column>
              <el-table-column prop="yellowCards" label="黄牌数"></el-table-column>
              <el-table-column prop="redCards" label="红牌数"></el-table-column>
            </el-table>
          </el-col>
          <el-col :span="12">
            <h3>球队红黄牌榜</h3>
            <el-table :data="currentRankings.cards.teams" style="width: 100%" v-loading="loading">
              <el-table-column label="球队">
                <template #default="{ row }">
                  <div class="team-name-cell">
                    <span 
                      class="clickable-team" 
                      @click="navigateToTeam(row)"
                      :title="点击查看球队详情"
                    >
                      <el-icon class="team-icon"><Trophy /></el-icon>
                      {{ row.team }}
                    </span>
                  </div>
                </template>
              </el-table-column>
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
              <el-table :data="group.teams" style="width: 100%" v-loading="loading">
                <el-table-column prop="team" label="球队" width="120"></el-table-column>
                <el-table-column prop="matchesPlayed" label="比赛场次" width="100"></el-table-column>
                <el-table-column prop="wins" label="胜" width="60"></el-table-column>
                <el-table-column prop="draws" label="平" width="60"></el-table-column>
                <el-table-column prop="losses" label="负" width="60"></el-table-column>
                <el-table-column prop="goalsFor" label="进球" width="70"></el-table-column>
                <el-table-column prop="goalsAgainst" label="失球" width="70"></el-table-column>
                <el-table-column label="净胜" width="70">
                  <template #default="{ row }">
                    {{ row.goalsFor - row.goalsAgainst }}
                  </template>
                </el-table-column>
                <el-table-column prop="points" label="积分" width="70"></el-table-column>
              </el-table>
            </div>
          </div>
          <div v-else>
            <el-table :data="currentRankings.points" style="width: 100%" v-loading="loading">
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
</template>

<script>
import { User, Trophy, Loading, Warning } from '@element-plus/icons-vue'

export default {
  name: 'RankingsSection',
  components: {
    User,
    Trophy,
    Loading,
    Warning
  },
  props: {
    rankings: {
      type: Object,
      default: () => ({})
    },
    playoffBracket: {
      type: Object,
      default: () => ({})
    },
    groupRankings: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedCompetition: 'championsCup',
      activeRankingTab: 'scorers',
      currentRankingsTab: '常规赛'
    };
  },
  computed: {
    currentRankings() {
      const rankings = this.rankings[this.selectedCompetition] || {
        topScorers: { players: [], teams: [] },
        cards: { players: [], teams: [] },
        points: []
      };
      console.log(`当前赛事 ${this.selectedCompetition} 的排行数据:`, rankings);
      return rankings;
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
    },
    hasData() {
      const current = this.currentRankings;
      return (
        (current.topScorers && (current.topScorers.players.length > 0 || current.topScorers.teams.length > 0)) ||
        (current.cards && (current.cards.players.length > 0 || current.cards.teams.length > 0)) ||
        (current.points && current.points.length > 0) ||
        (this.selectedCompetition === 'eightASide' && this.sortedGroupRankings.length > 0)
      );
    }
  },
  methods: {
    onCompetitionChange() {
      console.log('赛事类型切换到:', this.selectedCompetition);
      this.currentRankingsTab = '常规赛';
      this.activeRankingTab = 'scorers';
      
      // 触发父组件重新获取数据
      this.$emit('competition-change', this.selectedCompetition);
      
      // 添加延迟确保数据获取完成后再检查
      this.$nextTick(() => {
        console.log('切换后的排行数据:', this.currentRankings);
      });
    },
    onRankingsTabChange() {
      console.log('排行榜标签切换到:', this.currentRankingsTab);
      this.$emit('rankings-tab-change', this.currentRankingsTab);
    },
    getCompetitionName(competition) {
      const nameMap = {
        championsCup: '冠军杯',
        womensCup: '巾帼杯',
        eightASide: '八人制'
      };
      return nameMap[competition] || '未知赛事';
    },
    navigateToPlayer(player) {
      console.log('点击了球员:', player) // 调试用
      
      // 确保有ID数据再跳转
      const playerId = player.id || player.studentId || player.playerId
      if (!playerId) {
        console.error('球员ID不存在:', player)
        this.$message.error('球员信息不完整，无法查看详情')
        return
      }
      
      // 跳转到球员历史页面，只传递球员ID
      this.$router.push({
        name: 'PlayerHistory',
        query: {
          playerId: playerId
        }
      }).catch(err => {
        console.error('路由跳转失败:', err)
        this.$message.error('页面跳转失败')
      })
    },
    navigateToTeam(team) {
      console.log('点击了球队:', team)
      
      const teamName = team.team || team.name
      if (!teamName) {
        console.error('球队名称不存在:', team)
        this.$message.error('球队信息不完整，无法查看详情')
        return
      }
      
      this.$router.push({
        name: 'TeamHistory',
        query: {
          teamName: teamName
        }
      }).catch(err => {
        console.error('路由跳转失败:', err)
        this.$message.error('页面跳转失败')
      })
    }
  }
};
</script>

<style scoped>
.rankings-card {
  margin-bottom: 20px;
}

h3 {
  margin-bottom: 10px;
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}

.player-name-cell,
.team-name-cell {
  display: flex;
  align-items: center;
}

.clickable-player,
.clickable-team {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409EFF;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.clickable-player:hover,
.clickable-team:hover {
  color: #ffffff;
  background-color: #409EFF;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
}

.player-icon,
.team-icon {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.clickable-player:hover .player-icon,
.clickable-team:hover .team-icon {
  transform: scale(1.1);
}
</style>
