<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { NIcon, NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NMenu } from 'naive-ui'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const collapsed = ref(false)

const menuOptions = computed(() => [
  {
    label: t('admin.menu.dashboard'),
    key: '/admin/dashboard',
    icon: () => h(NIcon, null, { default: () => h(IconDashboard) }),
  },
  {
    label: t('admin.menu.journal'),
    key: '/admin/journal',
    icon: () => h(NIcon, null, { default: () => h(IconJournal) }),
  },
])

const selectedKeys = computed(() => {
  if (route.path.startsWith('/admin')) return [route.path]
  return []
})

function handleMenuUpdate(key: string) {
  if (key !== route.path) router.push(key)
}

const IconDashboard = {
  render() {
    return h(
      'svg',
      {
        viewBox: '0 0 24 24',
        fill: 'none',
        xmlns: 'http://www.w3.org/2000/svg',
      },
      [
        h('path', {
          d: 'M3 3h8v8H3V3zm10 0h8v5h-8V3zM13 10h8v11h-8V10zM3 13h8v8H3v-8z',
          fill: 'currentColor',
        }),
      ],
    )
  },
}

const IconJournal = {
  render() {
    return h(
      'svg',
      {
        viewBox: '0 0 24 24',
        fill: 'none',
        xmlns: 'http://www.w3.org/2000/svg',
      },
      [
        h('path', {
          d: 'M6 3h9a3 3 0 013 3v14a1 1 0 01-1.6.8L13 18l-3.4 2.8A1 1 0 018 20V6a3 3 0 00-2-2.8V3z',
          fill: 'currentColor',
        }),
      ],
    )
  },
}
</script>

<template>
  <NLayout has-sider class="admin-layout">
    <NLayoutSider
      bordered
      collapsible
      :collapsed="collapsed"
      show-trigger
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      class="admin-sider"
      @update:collapsed="collapsed = $event"
    >
      <div class="admin-brand" :class="{ compact: collapsed }">{{ t('common.brand') }}</div>
      <NMenu :value="selectedKeys[0]" :options="menuOptions" @update:value="handleMenuUpdate" />
    </NLayoutSider>

    <NLayout>
      <NLayoutHeader bordered class="admin-header">
        <div class="admin-header-title">{{ t('admin.title') }}</div>
        <LocaleSwitcher />
      </NLayoutHeader>
      <NLayoutContent class="admin-content">
        <router-view />
      </NLayoutContent>
    </NLayout>
  </NLayout>
</template>

<style scoped>
.admin-layout {
  height: 100vh;
}

.admin-sider {
  padding: 16px 8px;
}

.admin-brand {
  padding: 8px 12px 16px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.admin-brand.compact {
  display: none;
}

.admin-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.admin-header-title {
  font-weight: 600;
}

.admin-content {
  padding: 16px;
  min-height: calc(100vh - 56px);
  background: #f6f7f9;
}
</style>
