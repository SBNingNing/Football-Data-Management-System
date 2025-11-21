import { ref, computed } from 'vue'
import { fetchCompetitions as fetchCompetitionsService } from '@/domain/competition/competitionsService'
import logger from '@/utils/logger'

// Shared state to avoid fetching multiple times if used in multiple components
const competitions = ref([])
const loading = ref(false)
const loaded = ref(false)

export default function useCompetitions() {
  
  /**
   * Fetch competitions from the backend
   * @param {boolean} force - Force refresh
   */
  const fetchCompetitions = async (force = false) => {
    if (loaded.value && !force && competitions.value.length > 0) return

    loading.value = true
    try {
      const res = await fetchCompetitionsService({}, { force })
      if (res.ok) {
        // The service returns { competitions: [...], statistics: ... }
        competitions.value = res.data.competitions || []
        loaded.value = true
      } else {
        logger.error('Failed to fetch competitions:', res.error)
      }
    } catch (e) {
      logger.error('Error fetching competitions:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * Get options for el-select
   * Returns array of { label: string, value: string }
   * We use the competition name as the value because the backend
   * often expects a string "matchType" which corresponds to the name
   * (or a code that is mapped from the name).
   * 
   * Ideally, we should use ID, but the current system relies heavily on string codes.
   * We will use the Name as the value, and rely on the backend's normalization
   * or the existing "champions-cup" codes if they are present in the name.
   * 
   * Actually, to maintain compatibility with the existing hardcoded "champions-cup",
   * we might need to map known names to those codes, or just use the name
   * and hope the backend handles it (it does have a "normalize" function).
   */
  const competitionOptions = computed(() => {
    return competitions.value.map(comp => ({
      label: comp.name,
      value: comp.name, // Use Name as value to match backend expectation
      id: comp.id
    }))
  })

  /**
   * Get label for a given value (ID or name)
   */
  const getCompetitionLabel = (value) => {
    if (!value) return ''
    
    // Check dynamic list first
    const found = competitionOptions.value.find(c => c.value === value || c.label === value || c.id === value)
    if (found) return found.label
    
    return value
  }

  return {
    competitions,
    loading,
    fetchCompetitions,
    competitionOptions,
    getCompetitionLabel
  }
}
