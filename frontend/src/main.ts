import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/router'
import i18n from '@/i18n'
import { useLocaleStore } from '@/stores/locale'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

const localeStore = useLocaleStore(pinia)
i18n.global.locale.value = localeStore.locale
localeStore.$subscribe((_mutation, state) => {
  i18n.global.locale.value = state.locale
})

app.mount('#app')
