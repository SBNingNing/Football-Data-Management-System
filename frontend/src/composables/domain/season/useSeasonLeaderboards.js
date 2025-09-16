/** useSeasonLeaderboards (inlined) */
import { computed } from 'vue'
export function useSeasonLeaderboards(seasonRef){
	const topScorers = computed(()=>{ const season=seasonRef?.value; if(!season||!Array.isArray(season.teams)) return []; const list=[]; season.teams.forEach(team=>{ if(!Array.isArray(team.players)) return; team.players.forEach(p=>{ if((p.goals||0)>0) list.push({ ...p, team_name: team.name }) }) }); return list.sort((a,b)=>(b.goals||0)-(a.goals||0)).slice(0,10) })
	const topCards = computed(()=>{ const season=seasonRef?.value; if(!season||!Array.isArray(season.teams)) return []; const list=[]; season.teams.forEach(team=>{ if(!Array.isArray(team.players)) return; team.players.forEach(p=>{ if((p.yellowCards||0)>0 || (p.redCards||0)>0) list.push({ ...p, team_name: team.name }) }) }); return list.sort((a,b)=> ((b.redCards||0)+(b.yellowCards||0)) - ((a.redCards||0)+(a.yellowCards||0)) ).slice(0,10) })
	return { topScorers, topCards }
}
