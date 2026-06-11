import { defineStore } from 'pinia'

type Locale = 'zh' | 'en'

const STORAGE_KEY = 'compete_locale'

function getStoredLocale(): Locale | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY)
    if (value === 'zh' || value === 'en') return value
  } catch (err) {
    return null
  }
  return null
}

export const useLocaleStore = defineStore('locale', {
  state: () => ({
    locale: (getStoredLocale() || 'zh') as Locale,
  }),
  actions: {
    setLocale(locale: Locale) {
      this.locale = locale
      try {
        localStorage.setItem(STORAGE_KEY, locale)
      } catch (err) {
        // ignore storage errors
      }
    },
  },
})
