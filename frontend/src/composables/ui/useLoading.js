// useLoading (inlined)
import { ref } from 'vue'
export function useLoading(){ const loading = ref(false); async function run(factory){ loading.value=true; try { return await factory() } finally { loading.value=false } } return { loading, run } }
