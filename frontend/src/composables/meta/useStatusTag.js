// useStatusTag (inlined)
import { MATCH_STATUS_TEXT, MATCH_STATUS_TAG_TYPE } from '@/constants/match'
export function useStatusTag(customMap){ const textMap = customMap?.textMap || MATCH_STATUS_TEXT; const tagMap = customMap?.tagMap || MATCH_STATUS_TAG_TYPE; const fallback = customMap?.fallback || { text:'未开始', type:'info' }; function resolve(status){ return { text: textMap[status] || fallback.text, type: tagMap[status] || fallback.type } } function text(status){ return resolve(status).text } function tagType(status){ return resolve(status).type } return { resolve, text, tagType } }
