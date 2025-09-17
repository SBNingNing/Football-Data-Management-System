<template>
  <el-card class="manage-card">
    <template #header>
      <div class="card-header">
        <span>事件管理</span>
        <div class="header-stats">共 {{ total }} 个事件</div>
      </div>
    </template>

    <div class="search-section">
      <slot name="search" />
    </div>

    <div class="cards-container">
      <div v-if="items.length === 0" class="no-data">
        <el-empty description="暂无事件数据" />
      </div>
      <el-row :gutter="20" v-else>
        <el-col :span="6" v-for="event in items" :key="event.id || event.eventId">
          <slot name="card" :event="event" />
        </el-col>
      </el-row>
    </div>

    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPageProxy"
        v-model:page-size="pageSizeProxy"
        :page-sizes="[12,24,48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </el-card>
</template>
<script setup>
import { computed } from 'vue'
/**
 * EventsTab 组件
 * Props: items(事件数组), total(总数), currentPage, pageSize
 * Emits: update:currentPage, update:pageSize
 * Slots:
 *  - search: 搜索与筛选区域
 *  - card:   单个事件卡片 (作用域 { event })
 * 仅负责布局与分页，不处理业务逻辑。
 */
const props = defineProps({
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 12 }
})
const emit = defineEmits(['update:currentPage','update:pageSize'])
const currentPageProxy = computed({ get:()=>props.currentPage, set:v=>emit('update:currentPage', v) })
const pageSizeProxy = computed({ get:()=>props.pageSize, set:v=>emit('update:pageSize', v) })
</script>
