<template>
  <el-card class="manage-card">
    <template #header>
      <div class="card-header">
        <span>球队管理</span>
        <div class="header-stats">共 {{ total }} 支球队</div>
      </div>
    </template>

    <div class="search-section">
      <slot name="search" />
    </div>

    <div class="cards-container">
      <div v-if="items.length === 0" class="no-data">
        <el-empty description="暂无球队数据" />
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="12" v-for="team in items" :key="team.id || team.teamId">
          <slot name="card" :team="team" />
        </el-col>
      </el-row>
    </div>

    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPageProxy"
        v-model:page-size="pageSizeProxy"
        :page-sizes="[6,12,24]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
/**
 * TeamsTab 组件
 * Props: items(球队数组), total, currentPage, pageSize
 * Emits: update:currentPage, update:pageSize
 * Slots:
 *  - search: 搜索与筛选区域
 *  - card:   单个球队卡片 (作用域 { team })
 * 仅负责布局与分页逻辑。
 */
const props = defineProps({
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 6 }
})
const emit = defineEmits(['update:currentPage','update:pageSize'])
const currentPageProxy = computed({ get:()=>props.currentPage, set:v=>emit('update:currentPage', v) })
const pageSizeProxy = computed({ get:()=>props.pageSize, set:v=>emit('update:pageSize', v) })
</script>
