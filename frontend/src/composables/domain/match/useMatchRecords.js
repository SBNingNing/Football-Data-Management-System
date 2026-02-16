/**
 * 比赛记录组合函数
 * 提供统一的比赛记录分页加载与过滤状态
 */
import { ref, reactive } from 'vue'
import { fetchMatchRecords } from '@/api/matches'
import logger from '@/utils/logger'

/**
 * 比赛记录组合函数
 * @param {Object} initialQuery - 初始查询参数
 * @returns {Object} 比赛记录相关的响应式数据和方法
 */
export function useMatchRecords(initialQuery = {}) {
  // =========================
  // 响应式状态定义
  // =========================
  
  // 比赛记录列表
  const records = ref([])
  
  // 总记录数
  const total = ref(0)
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)
  
  // 查询参数（响应式）
  const query = reactive({
    type: '',
    status: '',
    keyword: '',
    page: 1,
    pageSize: 4, // 默认为4，与首页展示保持一致
    ...initialQuery
  })


  /**
   * 加载比赛记录数据
   * @param {Object} overrides - 覆盖参数
   */
  async function load(overrides = {}) {
    loading.value = true
    error.value = null

    try {
      // 获取认证token (可选，如果后端允许公开访问)
      const token = localStorage.getItem('token') || sessionStorage.getItem('token')
      
      // 处理参数
      const { force = false, ...restOverrides } = overrides
      const baseQuery = { ...query }
      
      // 清理非查询参数
      if ('force' in baseQuery) {
        delete baseQuery.force
      }
      
      const params = { ...baseQuery, ...restOverrides }
      if (force) {
        params._ts = Date.now()
      }

      // 调用API
      const { ok, data, error: err } = await fetchMatchRecords(params)

      if (!ok) {
        error.value = err
        records.value = []
        total.value = 0
        return
      }

      // 更新数据
      const rawData = data?.data || data || {}
      const rawRecords = Array.isArray(rawData) ? rawData : (rawData.records || [])
      const totalCount = rawData.total || rawRecords.length

      records.value = rawRecords.map(r => ({
        ...r,
        type: r.matchType, // Alias for component
        score: (r.home_score !== undefined && r.away_score !== undefined) 
          ? `${r.home_score}:${r.away_score}` 
          : '-:-'
      }))
      total.value = totalCount
      
    } catch (e) {
      error.value = e
      logger.error('[useMatchRecords] 加载失败', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置过滤条件
   * 返回Promise以便调用方可以await，配合反馈统一pending
   * @param {Object} partial - 部分更新的查询参数
   * @returns {Promise} 加载操作的Promise
   */
  function setFilter(partial = {}) {
    const { force, ...rest } = partial
    
    // 清理旧的force参数
    if ('force' in query) {
      Reflect.deleteProperty(query, 'force')
    }
    
    // 更新查询参数
    // 只有在非翻页操作（如筛选、搜索）时才重置页码
    if (rest.page) {
      Object.assign(query, rest)
    } else {
      Object.assign(query, rest, { page: 1 })
    }
    
    return load({ force })
  }

  /**
   * 设置当前页码
   * @param {number} page - 页码
   * @returns {Promise} 加载操作的Promise
   */
  function setPage(page) {
    query.page = page
    return load()
  }

  /**
   * 重置查询条件
   * @returns {Promise} 加载操作的Promise
   */
  function reset() {
    Object.assign(query, {
      type: '',
      status: '',
      keyword: '',
      page: 1,
      pageSize: 10
    })
    
    return load()
  }

  return {
    // 响应式数据
    records,
    total,
    loading,
    error,
    query,
    
    // 方法
    load,
    setFilter,
    setPage,
    reset
  }
}

export default useMatchRecords
