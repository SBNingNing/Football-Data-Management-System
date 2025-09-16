// useHomeDashboard (inlined)
import { ref } from 'vue'
import { useMatchRecords } from '../match/useMatchRecords.js'
import logger from '@/utils/logger'
import { fetchDashboardStats, fetchGroupRankings, fetchPlayoffBracket, fetchRankings, processRankingDataBlock } from '@/domain/stats/statsService'
import { fetchRecentMatches } from '@/domain/match/matchService'
export function useHomeDashboard({ feedback }) {
	const statsData = ref({ totalMatches:0, upcomingMatches:0, completedMatches:0 })
	const rankings = ref({ championsCup:{ topScorers:{ players:[], teams:[] }, cards:{ players:[], teams:[] }, points:[] }, womensCup:{ topScorers:{ players:[], teams:[] }, cards:{ players:[], teams:[] }, points:[] }, eightASide:{ topScorers:{ players:[], teams:[] }, cards:{ players:[], teams:[] }, points:[] } })
	const playoffBracket = ref({ championsCup:[], womensCup:[], eightASide:[] })
	const groupRankings = ref({ eightASide:{ groups:[] } })
	const recentMatches = ref([]); const retryCount = ref(0); const maxRetries = 3
	const isPageRefresh = ref(!!(window.performance && window.performance.navigation && window.performance.navigation.type === 1))
	const matchRecordsC = useMatchRecords(); const matchRecords = matchRecordsC.records; const matchRecordsTotal = matchRecordsC.total
	function setDefaultRankings(){ const def={ topScorers:{ players:[], teams:[] }, cards:{ players:[], teams:[] }, points:[] }; rankings.value={ championsCup:{...def}, womensCup:{...def}, eightASide:{...def} } }
	async function loadStats(){ const token = localStorage.getItem('token') || sessionStorage.getItem('token'); if(!token){ statsData.value={ totalMatches:0, upcomingMatches:0, completedMatches:0 }; return } const { ok, data } = await fetchDashboardStats({ token }); if(ok) statsData.value = data }
	async function loadGroupRankings(){ const { ok, data, error } = await fetchGroupRankings(); if(!ok) return logger.warn('group rankings fail', error); groupRankings.value = data || groupRankings.value }
	async function loadPlayoffBracket(){ const { ok, data, error } = await fetchPlayoffBracket(); if(!ok) return logger.warn('playoff bracket fail', error); playoffBracket.value = data || playoffBracket.value }
	async function loadRankings(){ const token = localStorage.getItem('token') || sessionStorage.getItem('token'); if(!token) return setDefaultRankings(); const { ok, data, error } = await fetchRankings({ token }); if(!ok){ logger.warn('rankings fail', error); return setDefaultRankings() } rankings.value = { championsCup: processRankingDataBlock(data?.championsCup,'冠军杯'), womensCup: processRankingDataBlock(data?.womensCup,'女子杯'), eightASide: processRankingDataBlock(data?.eightASide,'八人制') } }
	async function fetchMatchRecords(params={}){
		const key = 'svc:match:records';
		feedback?.begin(key)
		try {
			await matchRecordsC.setFilter({ ...params })
		} catch(e){
			feedback?.pushError(e)
		} finally {
			feedback?.end(key)
		}
	}
	async function fetchRecent(){
		const key = 'svc:recent-matches'
		feedback?.begin(key)
		try {
			const token = localStorage.getItem('token') || sessionStorage.getItem('token');
			if(!token){ recentMatches.value = []; return }
			const { ok, data, error } = await fetchRecentMatches({ token });
			if(!ok){ logger.warn('recent matches fail', error); recentMatches.value = []; return }
			recentMatches.value = Array.isArray(data) ? data : []
		} finally {
			feedback?.end(key)
		}
	}
	function handleMatchSearch(p){ fetchMatchRecords(p) } function handleMatchFilter(p){ fetchMatchRecords(p) } function handleMatchPageChange(p){ fetchMatchRecords(p) }
	async function loadAllData(){
		const key = 'view:home:init'
		feedback?.begin(key)
		try {
			await Promise.all([
				loadStats(),
				loadGroupRankings(),
				loadPlayoffBracket(),
				loadRankings(),
				fetchMatchRecords({}),
				fetchRecent()
			])
			retryCount.value=0
		} catch(e){
			logger.error('loadAllData error', e)
			feedback?.pushError(e)
			handleLoadError()
		} finally {
			feedback?.end(key)
		}
	}
	function handleLoadError(){ if(retryCount.value < maxRetries){ retryCount.value++; setTimeout(()=> loadAllData(), 600) } }
	function refreshData(){ loadAllData() }
	function onCompetitionChange(){ /* placeholder for future filter logic */ }
	function onRankingsTabChange(){ /* placeholder */ }
	function fetchRecentMatchesWrapper(){ fetchRecent() }
	function handleVisibilityChange(){ if(document.visibilityState==='visible'){ fetchRecent() } }
	return { statsData, rankings, playoffBracket, groupRankings, recentMatches, retryCount, isPageRefresh, matchRecords, matchRecordsTotal, loadAllData, fetchMatchRecords, fetchRecent: fetchRecentMatchesWrapper, handleMatchSearch, handleMatchFilter, handleMatchPageChange, refreshData, onCompetitionChange, onRankingsTabChange, handleVisibilityChange }
}
