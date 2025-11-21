// useScrollRestore (inlined, formatted)
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, onBeforeRouteLeave } from 'vue-router'

const memoryStore = new Map()

export function useScrollRestore(options = {}) {
	const route = useRoute()
	const restoring = ref(false)
	const key = options.key || route.fullPath
	const targetGetter = options.target || (() => document.scrollingElement || document.documentElement)
	const throttle = options.throttle ?? 150
	const debug = !!options.debug
	let lastSave = 0
	let abortRestore = false

	function log(...a) { if (debug) console.warn('[useScrollRestore]', ...a) }

	function save() {
		const el = targetGetter()
		if (!el) return
		memoryStore.set(key, { top: el.scrollTop, ts: Date.now() })
		log('save', key, el.scrollTop)
	}

	async function restore(_force = false) { // _force 保留以便未来条件控制
		const state = memoryStore.get(key)
		if (!state) { log('no state for', key); return }
		const el = targetGetter()
		if (!el) return
		restoring.value = true
		abortRestore = false
		let tries = 0
		const maxTries = 10
		const desired = state.top

		function attempt() {
			if (abortRestore) return done()
			el.scrollTop = desired
			tries++
			if (Math.abs(el.scrollTop - desired) < 2 || tries >= maxTries) {
				done()
				return
			}
			const raf = typeof window !== 'undefined' && window.requestAnimationFrame
				? window.requestAnimationFrame
				: (fn) => setTimeout(fn, 16)
			raf(attempt)
		}

		function done() {
			restoring.value = false
			log('restore done', key, el.scrollTop)
		}

		attempt()
		log('restore start', key, desired)
	}

	function clear() { memoryStore.delete(key) }

	function onScroll() {
		const now = Date.now()
		if (now - lastSave < throttle) return
		lastSave = now
		save()
	}

	onMounted(() => {
		try {
			const el = targetGetter()
			if (el) el.addEventListener('scroll', onScroll, { passive: true })
			restore()
		} catch (error) {
			console.warn('滚动恢复初始化失败:', error.message)
		}
	})

	onBeforeUnmount(() => {
		try {
			const el = targetGetter()
			if (el) el.removeEventListener('scroll', onScroll)
			save()
		} catch (error) {
			console.warn('滚动恢复清理失败:', error.message)
		}
	})

	onBeforeRouteLeave(() => { save() })

	// 打断还原的用户交互监听 - 使用安全的事件监听器
	try {
		document.addEventListener('wheel', () => { abortRestore = true }, { passive: true })
		document.addEventListener('touchmove', () => { abortRestore = true }, { passive: true })
	} catch (error) {
		console.warn('用户交互监听器添加失败:', error.message)
	}

	return { restoring, save, restore, clear }
}
