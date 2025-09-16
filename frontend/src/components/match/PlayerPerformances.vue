<template>
  <el-card class="player-performances">
    <template #header>
      <div class="clearfix">
        <span>球员表现详情</span>
        <div class="header-controls">
          <div class="search-stats">共 {{ filteredPlayers.length }} 名球员</div>
          <el-radio-group v-model="selectedTeamLocal" class="team-filter">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button :label="match.homeTeam">{{ match.homeTeam }}</el-radio-button>
            <el-radio-button :label="match.awayTeam">{{ match.awayTeam }}</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </template>
    <div class="players-section">
      <div v-if="filteredPlayers.length===0" class="no-players">
        <el-icon class="no-data-icon"><UserFilled /></el-icon>
        <p>{{ selectedTeamLocal==='all' ? '暂无球员数据' : `${selectedTeamLocal} 队暂无球员数据` }}</p>
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="player in paginatedPlayers" :key="player.playerId" class="player-col">
          <el-card shadow="hover" class="player-card" @click="$emit('view-player', player.playerId)">
            <div class="player-info">
              <div class="player-avatar"><el-icon class="avatar-icon"><User /></el-icon></div>
              <div class="player-details">
                <div class="player-name">{{ player.playerName || '未知球员' }}</div>
                <div class="player-meta">
                  <div class="meta-item"><el-icon><Trophy /></el-icon><span>{{ player.teamName || '未知球队' }}</span></div>
                  <div class="meta-item" v-if="player.playerNumber"><el-icon><Tickets /></el-icon><span>{{ player.playerNumber }}号</span></div>
                </div>
                <div class="player-stats">
                  <span class="stat-badge goals"><el-icon><Football /></el-icon>{{ player.goals || 0 }}球</span>
                  <span class="stat-badge own-goals"><el-icon><Football /></el-icon>{{ player.ownGoals || 0 }}乌龙</span>
                  <span class="stat-badge yellow-cards"><el-icon><Warning /></el-icon>{{ player.yellowCards || 0 }}黄</span>
                  <span class="stat-badge red-cards"><el-icon><CircleClose /></el-icon>{{ player.redCards || 0 }}红</span>
                </div>
              </div>
            </div>
            <div class="player-card-overlay"><el-icon><IconView /></el-icon><span>查看详情</span></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <div class="pagination-wrapper" v-if="filteredPlayers.length > pageSizeLocal">
      <el-pagination
        v-model:current-page="currentPageLocal"
        v-model:page-size="pageSizeLocal"
        :page-sizes="[12,24,48]"
        :total="filteredPlayers.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="onSizeChange"
        @current-change="onPageChange"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed, watch, ref } from 'vue'
import { UserFilled, User, Trophy, Tickets, Football, Warning, CircleClose, View as IconView } from '@element-plus/icons-vue'
const props = defineProps({
  match: { type:Object, required:true },
  players: { type:Array, required:true },
  selectedTeam: { type:String, required:true },
  currentPage: { type:Number, required:true },
  pageSize: { type:Number, required:true }
})
const emits = defineEmits(['update:selectedTeam','update:currentPage','update:pageSize','view-player'])
const selectedTeamLocal = ref(props.selectedTeam)
const currentPageLocal = ref(props.currentPage)
const pageSizeLocal = ref(props.pageSize)
watch(()=>props.selectedTeam, v=>{ if(v!==selectedTeamLocal.value) selectedTeamLocal.value = v })
watch(()=>props.currentPage, v=>{ if(v!==currentPageLocal.value) currentPageLocal.value = v })
watch(()=>props.pageSize, v=>{ if(v!==pageSizeLocal.value) pageSizeLocal.value = v })
watch(selectedTeamLocal, v=>{ emits('update:selectedTeam', v); currentPageLocal.value = 1; emits('update:currentPage',1) })
function onSizeChange(size){ pageSizeLocal.value = size; emits('update:pageSize', size); currentPageLocal.value = 1; emits('update:currentPage',1) }
function onPageChange(p){ currentPageLocal.value = p; emits('update:currentPage', p) }
const filteredPlayers = computed(()=> selectedTeamLocal.value==='all' ? props.players : props.players.filter(p=>p.teamName===selectedTeamLocal.value))
const paginatedPlayers = computed(()=> { const start = (currentPageLocal.value-1)*pageSizeLocal.value; return filteredPlayers.value.slice(start, start+pageSizeLocal.value) })
</script>