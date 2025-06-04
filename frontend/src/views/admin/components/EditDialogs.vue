<template>
  <div>
    <!-- 编辑球队对话框 -->
    <el-dialog title="编辑球队信息" :visible.sync="editTeamDialogVisible" width="600px">
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
          <el-button type="primary" @click="$emit('add-edit-player')">添加球员</el-button>
          <div class="players-container">
            <div v-for="(player, index) in editTeamForm.players" :key="index" class="player-card">
              <div class="player-card-header">
                <span class="player-index">球员 {{ index + 1 }}</span>
                <el-button type="text" icon="el-icon-delete" @click="$emit('remove-edit-player', index)" class="delete-btn">删除</el-button>
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
        <el-button @click="$emit('close-team-dialog')">取消</el-button>
        <el-button type="primary" @click="$emit('update-team')">确定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑比赛对话框 -->
    <el-dialog title="编辑比赛信息" :visible.sync="editMatchDialogVisible" width="600px">
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
        <el-button @click="$emit('close-match-dialog')">取消</el-button>
        <el-button type="primary" @click="$emit('update-match')">确定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑事件对话框 -->
    <el-dialog title="编辑事件信息" :visible.sync="editEventDialogVisible" width="500px">
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
        <el-button @click="$emit('close-event-dialog')">取消</el-button>
        <el-button type="primary" @click="$emit('update-event')">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'EditDialogs',
  props: {
    editTeamDialog: Boolean,
    editMatchDialog: Boolean,
    editEventDialog: Boolean,
    editTeamForm: Object,
    editMatchForm: Object,
    editEventForm: Object,
    teams: Array,
    matches: Array,
    players: Array
  },
  computed: {
    editTeamDialogVisible: {
      get() {
        return this.editTeamDialog;
      },
      set(val) {
        if (!val) {
          this.$emit('close-team-dialog');
        }
      }
    },
    editMatchDialogVisible: {
      get() {
        return this.editMatchDialog;
      },
      set(val) {
        if (!val) {
          this.$emit('close-match-dialog');
        }
      }
    },
    editEventDialogVisible: {
      get() {
        return this.editEventDialog;
      },
      set(val) {
        if (!val) {
          this.$emit('close-event-dialog');
        }
      }
    }
  }
}
</script>

<style scoped>
.players-container {
  max-height: 400px;
  overflow-y: auto;
}

.player-card {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fff;
  transition: box-shadow 0.2s;
}

.player-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.player-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.player-index {
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

.player-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.player-input {
  width: 100%;
}
</style>
