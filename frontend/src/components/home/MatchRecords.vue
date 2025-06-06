<template>
  <el-card class="recent-matches-card">
    <template #header>
      <div class="clearfix">
        <span>比赛记录</span>
        <div style="float: right;">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索比赛名称/球队/地点"
            size="small"
            style="width: 200px; margin-right: 10px;"
            @input="onSearch"
            clearable
          />
          <el-select
            v-model="filterType"
            placeholder="筛选类型"
            size="small"
            style="width: 120px; margin-right: 10px;"
            @change="onFilterChange"
            clearable
          >
            <el-option label="全部" value=""></el-option>
            <el-option label="冠军杯" value="championsCup"></el-option>
            <el-option label="巾帼杯" value="womensCup"></el-option>
            <el-option label="八人制" value="eightASide"></el-option>
          </el-select>
        </div>
      </div>
    </template>
    <el-table :data="matchRecords" border style="width: 100%" table-layout="fixed">
      <el-table-column prop="name" label="比赛名称" min-width="180" show-overflow-tooltip></el-table-column>
      <el-table-column label="比赛类型" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row">{{ getMatchTypeLabel(row.type) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="match_time" label="比赛时间" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row">{{ formatDate(row.match_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="对阵" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row">{{ row.team1 }} vs {{ row.team2 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="比赛地点" min-width="120" show-overflow-tooltip></el-table-column>
      <el-table-column label="操作" width="110" align="center" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="viewMatchDetails(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 16px; text-align: right;">
      <el-pagination
        background
        layout="prev, pager, next, jumper"
        :total="matchRecordsTotal"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        @current-change="onPageChange"
      />
    </div>
  </el-card>
</template>

<script>
import { ElMessage } from 'element-plus';

export default {
  name: 'MatchRecords',
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
      searchKeyword: '',
      filterType: '',
      currentPage: 1,
      pageSize: 10
    };
  },
  methods: {
    getMatchTypeLabel(type) {
      const labels = {
        'championsCup': '冠军杯',
        'womensCup': '巾帼杯',
        'eightASide': '八人制',
        'champions-cup': '冠军杯',
        'womens-cup': '巾帼杯',
        'eight-a-side': '八人制'
      };
      return labels[type] || type || '';
    },
    formatDate(dateInput) {
      if (!dateInput) return '';
      
      try {
        let date;
        
        if (typeof dateInput === 'string') {
          const cleanDate = dateInput.replace(/[TZ]/g, ' ').replace(/\.\d{3}/, '').trim();
          date = new Date(cleanDate);
        } else {
          date = new Date(dateInput);
        }
        
        if (isNaN(date.getTime())) {
          console.warn('Invalid date:', dateInput);
          return '';
        }
        
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } catch (error) {
        console.error('Date formatting error:', error, dateInput);
        return '';
      }
    },
    viewMatchDetails(match) {
      if (match.id) {
        this.$router.push(`/matches/detail/${match.id}`);
      } else {
        ElMessage.error('未找到比赛ID');
      }
    },
    onSearch() {
      this.currentPage = 1;
      this.$emit('search', {
        keyword: this.searchKeyword,
        type: this.filterType,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    },
    onFilterChange() {
      this.currentPage = 1;
      this.$emit('filter-change', {
        keyword: this.searchKeyword,
        type: this.filterType,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    },
    onPageChange(page) {
      this.currentPage = page;
      this.$emit('page-change', {
        keyword: this.searchKeyword,
        type: this.filterType,
        page: this.currentPage,
        pageSize: this.pageSize
      });
    }
  }
};
</script>

<style scoped>
.recent-matches-card {
  margin-bottom: 20px;
}

.clearfix::after {
  content: "";
  display: table;
  clear: both;
}
</style>
