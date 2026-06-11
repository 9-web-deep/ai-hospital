<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NDropdown } from 'naive-ui'
import { useLocaleStore } from '@/stores/locale'

const localeStore = useLocaleStore()
const active = computed(() => localeStore.locale)

const options = [
  { label: '中文', key: 'zh' },
  { label: 'English', key: 'en' },
]

function setLocale(lang: 'en' | 'zh') {
  localeStore.setLocale(lang)
}
</script>

<template>
  <NDropdown :options="options" @select="setLocale">
    <NButton size="small">{{ active === 'zh' ? '中文' : 'English' }}</NButton>
  </NDropdown>
</template>
