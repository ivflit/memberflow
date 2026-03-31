import { ref, watch } from 'vue'

// Module-level singleton — all components share one reactive theme ref.
const theme = ref(localStorage.getItem('mf-theme') || 'light')

// Immediately apply to <html data-theme> so the page background is correct
// before any component mounts (prevents black flash during route transitions).
document.documentElement.dataset.theme = theme.value

watch(theme, (val) => {
  document.documentElement.dataset.theme = val
  localStorage.setItem('mf-theme', val)
})

export function useTheme() {
  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  return { theme, toggleTheme }
}
