<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { NCard, NTag, NButton } from 'naive-ui'

const { t } = useI18n()

type HealthStatus = 'unknown' | 'healthy' | 'unhealthy'

interface ServiceItem {
  key: string
  label: string
  baseUrl: string
  status: HealthStatus
  lastChecked?: string
}

const services = ref<ServiceItem[]>([])

const isChecking = ref(false)

const statusLabel = computed(() => {
  return {
    unknown: t('admin.dashboard.health.unknown'),
    healthy: t('admin.dashboard.health.healthy'),
    unhealthy: t('admin.dashboard.health.unhealthy'),
  }
})

function getTagType(status: HealthStatus) {
  if (status === 'healthy') return 'success'
  if (status === 'unhealthy') return 'error'
  return 'warning'
}

async function checkService(service: ServiceItem) {
  try {
    await axios.get(`${service.baseUrl}/health`, { timeout: 5000 })
    service.status = 'healthy'
  } catch (err) {
    service.status = 'unhealthy'
  } finally {
    service.lastChecked = new Date().toLocaleString()
  }
}

async function checkAll() {
  isChecking.value = true
  await Promise.all(services.value.map((service) => checkService(service)))
  isChecking.value = false
}

onMounted(checkAll)

watchEffect(() => {
  const prev = new Map(services.value.map((item) => [item.key, item]))
  const next = [
    {
      key: 'administrator',
      label: t('admin.dashboard.services.administrator'),
      baseUrl: import.meta.env.VITE_BACKEND_ADMINISTRATOR,
    },
    {
      key: 'nurse',
      label: t('admin.dashboard.services.nurse'),
      baseUrl: import.meta.env.VITE_BACKEND_NURSE,
    },
    {
      key: 'customer',
      label: t('admin.dashboard.services.customer'),
      baseUrl: import.meta.env.VITE_BACKEND_CUSTOMER,
    },
    {
      key: 'doctor',
      label: t('admin.dashboard.services.doctor'),
      baseUrl: import.meta.env.VITE_BACKEND_DOCTOR,
    },
  ]
  services.value = next.map((item) => {
    const existing = prev.get(item.key)
    return {
      ...item,
      status: existing?.status ?? 'unknown',
      lastChecked: existing?.lastChecked,
    }
  })
})
</script>

<template>
  <NCard :title="t('admin.dashboard.title')">
    <div class="dashboard-section">
      <div class="dashboard-section-header">
        <div class="dashboard-section-title">{{ t('admin.dashboard.health.title') }}</div>
        <NButton size="small" :loading="isChecking" @click="checkAll">
          {{ t('admin.dashboard.health.refresh') }}
        </NButton>
      </div>

      <div class="health-list">
        <div v-for="service in services" :key="service.key" class="health-item">
          <div class="health-info">
            <div class="health-name">{{ service.label }}</div>
            <div class="health-url">{{ service.baseUrl }}</div>
          </div>
          <div class="health-status">
            <NTag :type="getTagType(service.status)">
              {{ statusLabel[service.status] }}
            </NTag>
            <div class="health-time">
              {{ service.lastChecked || t('admin.dashboard.health.notChecked') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </NCard>
</template>

<style scoped>
.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dashboard-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dashboard-section-title {
  font-weight: 600;
}

.health-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.health-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.health-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.health-name {
  font-weight: 600;
}

.health-url {
  font-size: 12px;
  color: #6b7280;
}

.health-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.health-time {
  font-size: 12px;
  color: #9ca3af;
}

@media (max-width: 720px) {
  .health-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .health-status {
    align-items: flex-start;
  }
}
</style>
