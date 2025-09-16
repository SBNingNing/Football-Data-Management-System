// useMetaData.js: 管理赛季与赛事元数据加载、刷新与快速赛事实例反馈
import { ref } from 'vue'
import { fetchSeasons } from '@/domain/season/seasonsService'
import { fetchCompetitions } from '@/domain/competition/competitionsService'
import notify from '@/utils/notify'

export function useMetaData(){
  const seasons = ref([])
  const competitions = ref([])
  const loadingMeta = ref(false)

  async function reloadSeasons(){
    const { ok, data, error } = await fetchSeasons()
    if(ok) seasons.value = data
    else notify.error(error?.message || '获取赛季失败')
  }
  async function reloadCompetitions(){
    const { ok, data, error } = await fetchCompetitions()
    if(ok) competitions.value = data.competitions || data
    else notify.error(error?.message || '获取赛事失败')
  }
  async function reloadAll(){
    loadingMeta.value = true
    try { await Promise.all([reloadSeasons(), reloadCompetitions()]) } finally { loadingMeta.value = false }
  }
  function handleTournamentQuick(){ reloadAll() }

  return { seasons, competitions, loadingMeta, reloadSeasons, reloadCompetitions, reloadAll, handleTournamentQuick }
}

export default useMetaData
