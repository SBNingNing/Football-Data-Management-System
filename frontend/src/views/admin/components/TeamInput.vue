<template>
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
</template>

<script>
export default {
  name: 'TeamInput',
  props: {
    matchType: String
  },
  data() {
    return {
      teamForm: {
        teamName: '',
        players: []
      }
    }
  },
  methods: {
    addPlayer() {
      this.teamForm.players.push({ name: '', number: '', studentId: '' });
    },
    removePlayer(index) {
      this.teamForm.players.splice(index, 1);
    },
    submitTeam() {
      this.$emit('submit', this.teamForm);
      this.teamForm = { teamName: '', players: [] };
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

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.player-count {
  color: #909399;
  font-size: 14px;
}

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
