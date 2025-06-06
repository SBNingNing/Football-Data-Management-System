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
                  <template #default="{ row }">
                    {{ row.goalsFor - row.goalsAgainst }}
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
</template>

<script>
export default {
  name: 'RankingsSection',
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
  methods: {
    onCompetitionChange() {
      this.currentRankingsTab = '常规赛';
      this.activeRankingTab = 'scorers';
      this.$emit('competition-change', this.selectedCompetition);
    },
    onRankingsTabChange() {
      this.$emit('rankings-tab-change', this.currentRankingsTab);
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
</style>
