/** 比赛类型元数据 / 统计 (inlined) */
import { computed } from 'vue'
const MATCH_TYPE_LABELS = Object.freeze({ 'champions-cup':'冠军杯','womens-cup':'巾帼杯','eight-a-side':'八人制比赛' })
const MATCH_TYPE_TAG_TYPES = Object.freeze({ 'champions-cup':'warning','womens-cup':'danger','eight-a-side':'success' })
export default function useMatchTypeMeta(){
	const getMatchTypeLabel = (type)=> MATCH_TYPE_LABELS[type] || type || '未知'
	const getMatchTypeTagType = (type)=> MATCH_TYPE_TAG_TYPES[type] || 'info'
	const getMatchTypeStats = (type, {teams=[],matches=[],events=[]}={})=>{ if(!type) return {teams:0,matches:0,events:0}; const tc=teams.filter(t=>t&&(t.matchType===type||t.type===type)).length; const mc=matches.filter(m=>m&&(m.matchType===type||m.type===type)).length; const ec=events.filter(e=>e&&(e.matchType===type||e.type===type)).length; return { teams:tc, matches:mc, events:ec } }
	const createReactiveStats = (matchTypeRef, sources)=> computed(()=> getMatchTypeStats(matchTypeRef.value, sources))
	return { getMatchTypeLabel, getMatchTypeTagType, getMatchTypeStats, createReactiveStats }
}
