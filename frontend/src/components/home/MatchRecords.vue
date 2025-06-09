<template>
  <el-card class="match-records-card">
    <template #header>
      <div class="card-header">
        <span>比赛记录</span>
        <div class="header-actions">
          <el-select
            v-model="selectedType"
            placeholder="选择比赛类型"
            @change="handleFilterChange"
            clearable
            class="type-select"
          >
            <el-option label="冠军杯" value="championsCup" />
            <el-option label="巾帼杯" value="womensCup" />
            <el-option label="八人制" value="eightASide" />
          </el-select>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索比赛名称、球队或地点"
            @input="handleSearch"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </template>

    <el-table :data="matchRecords" style="width: 100%" stripe>
      <el-table-column prop="name" label="比赛名称" width="200" />
      <el-table-column prop="type" label="赛事类型" width="100" />
      <el-table-column label="对阵球队" width="250">
        <template #default="scope">
          <span>{{ scope.row.team1 }} VS {{ scope.row.team2 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="比分" width="100" align="center">
        <template #default="scope">
          <span :class="scope.row.status === '已完赛' ? 'final-score' : 'pending-score'">
            {{ scope.row.score }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status_type" size="small">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date" label="比赛时间" width="180" />
      <el-table-column prop="location" label="比赛地点" />
    </el-table>

    <div class="pagination-wrapper" v-if="matchRecordsTotal > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="matchRecordsTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-card>
</template>

<script>
import { Search } from '@element-plus/icons-vue';

export default {
  name: 'MatchRecords',
  components: {
    Search
  },
  props: {
    matchRecords: {
      type: Array,
      default: () => []
    },
    matchRecordsTotal: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      selectedType: '',
      searchKeyword: '',
      currentPage: 1,
      pageSize: 10,
      searchTimer: null
    };
  },
  methods: {
    handleFilterChange() {
      this.currentPage = 1;
      this.$emit('filter-change', {
        type: this.selectedType,
        keyword: this.searchKeyword,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    },

    handleSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      this.searchTimer = setTimeout(() => {
        this.currentPage = 1;
        this.$emit('search', {
          type: this.selectedType,
          keyword: this.searchKeyword,
          page: this.currentPage,
          pageSize: this.pageSize
        });
      }, 500);
    },

    handleSizeChange(val) {
      this.pageSize = val;
      this.currentPage = 1;
      this.$emit('page-change', {
        type: this.selectedType,
        keyword: this.searchKeyword,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    },

    handleCurrentChange(val) {
      this.currentPage = val;
      this.$emit('page-change', {
        type: this.selectedType,
        keyword: this.searchKeyword,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    }
  }
};
</script>

<style scoped>
.match-records-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-select {
  width: 150px;
}

.search-input {
  width: 250px;
}

.search-input :deep(.el-input__wrapper) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: border-color 0.2s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: #c0c4cc;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff inset;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.final-score {
  font-weight: bold;
  color: #409eff;
}

.pending-score {
  color: #909399;
}
</style>
