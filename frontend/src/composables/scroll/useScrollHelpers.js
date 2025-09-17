// useScrollHelpers (inlined)
import { nextTick } from 'vue'

export function useScrollHelpers(options = {}) {
  const { typeSelectionSelector = '.input-type-selection', offsets = {} } = options
  const typeSelectionOffset = offsets.typeSelection ?? 120
  const matchTypeOffset = offsets.matchType ?? 100
  
  const scrollTo = (top, behavior = 'smooth') => window.scrollTo({ top, behavior })
  
  const safeOffsetTop = (el) => (el?.$el ? el.$el.offsetTop : el?.offsetTop) || 0
  
  const scrollToBottom = (delay = 100) => setTimeout(() => scrollTo(document.documentElement.scrollHeight), delay)
  
  const scrollToElement = (target, extraOffset = 0) => {
    if (!target) return
    const top = safeOffsetTop(target) - extraOffset
    scrollTo(top < 0 ? 0 : top)
  }
  
  const scrollToTypeSelection = (refEl) => {
    if (refEl?.value) return scrollToElement(refEl.value, typeSelectionOffset)
    const el = document.querySelector(typeSelectionSelector)
    if (el) scrollToElement(el, typeSelectionOffset)
  }
  
  const scrollToTypeSelectionAfterMatchType = (refEl) => {
    if (refEl?.value) {
      scrollToElement(refEl.value, typeSelectionOffset)
    } else {
      setTimeout(() => {
        const el = document.querySelector(typeSelectionSelector)
        if (el) scrollToElement(el, typeSelectionOffset)
      }, 300)
    }
  }
  
  const scrollToMatchTypeSelection = (matchTypeRef) => {
    if (matchTypeRef?.value) {
      scrollToElement(matchTypeRef.value, matchTypeOffset)
    } else {
      // 如果ref不存在，直接滚动到页面顶部
      scrollTo(0)
    }
  }
  
  const nextTickScroll = (fn) => nextTick(() => fn())
  
  return {
    scrollTo,
    scrollToBottom,
    scrollToElement,
    scrollToTypeSelection,
    scrollToTypeSelectionAfterMatchType,
    scrollToMatchTypeSelection,
    nextTickScroll
  }
}