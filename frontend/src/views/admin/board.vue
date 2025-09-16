<template>
  <div class="admin-container">
    <WelcomeCard @go-to-home="goToHome" @logout="logout" />
    <div class="main-content">
      <el-tabs v-model="activeTab" class="admin-tabs">
        <el-tab-pane name="manage">
          <template #label>
            <span class="tab-label"><el-icon><Setting /></el-icon>信息管理</span>
          </template>
          <AdminManageSection
            :teams="teams"
            :matches="matches"
            :events="events"
            :players="players"
            :manage-match-type="manageMatchType"
            :loading="loading"
            @refresh="loadAllData"
            @filter-change="handleFilterChange"
            @edit-team="editTeam"
            @delete-team="deleteTeam"
            @edit-match="editMatch"
            @delete-match="deleteMatch"
            @edit-event="editEvent"
            @delete-event="deleteEvent"
            @edit-player="editPlayer"
            @delete-player="deletePlayer"
            @complete-match="completeMatch"
          />
        </el-tab-pane>
        <el-tab-pane name="input">
          <template #label>
            <span class="tab-label"><el-icon><EditPen /></el-icon>信息录入</span>
          </template>
          <AdminInputSection
            :teams="teams"
            :matches="matches"
            :events="events"
            @team-submit="handleTeamSubmit"
            @schedule-submit="handleScheduleSubmit"
            @event-submit="handleEventSubmit"
            @refresh-data="loadAllData"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
    <EditDialogs
      :edit-team-dialog="editTeamDialog"
      :edit-match-dialog="editMatchDialog"
      :edit-event-dialog="editEventDialog"
      :edit-player-dialog="editPlayerDialog"
      :edit-team-form="editTeamForm"
      :edit-match-form="editMatchForm"
      :edit-event-form="editEventForm"
      :edit-player-form="editPlayerForm"
      :teams="teams"
      :matches="matches"
      :players="players"
      @close-team-dialog="editTeamDialog = false"
      @close-match-dialog="editMatchDialog = false"
      @close-event-dialog="editEventDialog = false"
      @close-player-dialog="editPlayerDialog = false"
      @update-team="updateTeam"
      @update-match="updateMatch"
      @update-event="updateEvent"
      @update-player="updatePlayer"
      @add-edit-player="addEditPlayer"
      @remove-edit-player="removeEditPlayer"
    />
    <AdminLoadingOverlay :loading="loading" />
  </div>
</template>

<script setup>
import WelcomeCard from '@/components/admin/WelcomeCard.vue'
import EditDialogs from '@/components/admin/EditDialogs.vue'
import AdminManageSection from '@/components/admin/AdminManageSection.vue'
import AdminInputSection from '@/components/admin/AdminInputSection.vue'
import AdminLoadingOverlay from '@/components/admin/AdminLoadingOverlay.vue'
import { Setting, EditPen } from '@element-plus/icons-vue'
import { onMounted } from 'vue'
import { useAdminBoardPage } from '@/composables/admin'
import '@/styles/admin-board.css'

const {
  activeTab, manageMatchType, loading,
  editTeamDialog, editMatchDialog, editEventDialog, editPlayerDialog,
  editTeamForm, editMatchForm, editEventForm, editPlayerForm,
  teams, matches, events, players,
  loadAllData, handleFilterChange,
  handleTeamSubmit, handleScheduleSubmit, handleEventSubmit,
  editTeam, addEditPlayer, removeEditPlayer, updateTeam, deleteTeam,
  editMatch, updateMatch, deleteMatch,
  editEvent, updateEvent, deleteEvent,
  editPlayer, updatePlayer, deletePlayer,
  completeMatch, logout,
} = useAdminBoardPage()

onMounted(() => { loadAllData() })

function goToHome(){ window.location.href = '/home' }
</script>

<!-- 样式集中管理: src/styles/admin-board.css -->