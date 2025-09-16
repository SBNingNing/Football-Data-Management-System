// useFeedback (inlined)
import { ref, reactive, computed } from 'vue'
export function normalizeError(err){ if(!err) return { message:'未知错误', ts:Date.now(), scope:'local' }; if(err.isNormalized) return err; let message = err.message || '请求失败'; const code = err.code || err.statusCode; return { message, code, cause:err, ts:Date.now(), scope:'local', isNormalized:true } }
export function useFeedback(){ const pendings = reactive(new Map());
const errors = ref([]); 
function begin(key){ pendings.set(key,(pendings.get(key)||0)+1) } function end(key){ const c=pendings.get(key); if(!c) return; c<=1?pendings.delete(key):pendings.set(key,c-1) } function pushError(err){ errors.value.push(normalizeError(err)) } function clearError(index){ if(index==null){ errors.value=[]; return } errors.value.splice(index,1) } const isLoading = computed(()=> pendings.size>0);
async function trackPromise(key,p){ begin(key);
try { return await p } finally { end(key) } } return { isLoading, pendings, errors, begin, end, pushError, clearError, trackPromise } }
