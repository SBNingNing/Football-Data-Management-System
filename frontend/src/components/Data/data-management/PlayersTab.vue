<template>
  <el-card class="manage-card">
    <template #header>
      <div class="card-header">
        <span>球员管理</span>
        <div class="header-stats">共 {{ total }} 名球员</div>
      </div>
    </template>

    <div class="search-section">
      <slot name="search" />
    </div>


    <div class="cards-container">
      <div v-if="items.length === 0" class="no-data">
        <el-empty description="暂无球员数据" />
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="player in items" :key="player.id || player.studentId">
          <slot name="card" :player="player" />
        </el-col>
      </el-row>
    </div>

    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPageProxy"
        v-model:page-size="pageSizeProxy"
        :page-sizes="[9,18,36]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
/**
 * PlayersTab 组件
 * Props: items(球员数组), total, currentPage, pageSize
 * Emits: update:currentPage, update:pageSize
 * Slots:
 *  - search: 搜索与筛选区域
 *  - card:   单个球员卡片 (作用域 { player })
 * 纯展示 + 分页容器。
 */
const props = defineProps({
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 9 }
})
const emit = defineEmits(['update:currentPage','update:pageSize'])
const currentPageProxy = computed({ get:()=>props.currentPage, set:v=>emit('update:currentPage', v) })
const pageSizeProxy = computed({ get:()=>props.pageSize, set:v=>emit('update:pageSize', v) })
</script>
