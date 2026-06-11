<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NAlert, NButton, NCard, NDataTable, NSwitch, useMessage, type DataTableColumns } from 'naive-ui'
import { nurseHttp } from '@/lib/http'

type DispensingTask = {
  task_id: string
  time: string
  user_id: string
  user_role: string
  medicines: any[]
  is_completed: boolean
}

const message = useMessage()
const loading = ref(false)
const errorMsg = ref('')
const showCompleted = ref(false)
const items = ref<DispensingTask[]>([])

const fetchTasks = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const resp = await nurseHttp.get('/dispensing_tasks', {
      params: {
        is_completed: showCompleted.value ? undefined : false,
        limit: 200,
        offset: 0,
      },
      headers: {
        Authorization: 'Bearer 1',
      },
    })
    items.value = (resp.data?.items ?? []) as DispensingTask[]
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const formatMedicines = (medicines: any[]) => {
  if (!Array.isArray(medicines) || medicines.length === 0) return '-'
  return medicines
    .map((m) => {
      const name = String(m?.medicine ?? '').trim()
      const spec = String(m?.specification ?? '').trim()
      const amt = m?.amount != null ? String(m.amount) : ''
      const parts = [name]
      if (spec) parts.push(spec)
      if (amt) parts.push(`x${amt}`)
      return parts.filter(Boolean).join(' ')
    })
    .filter(Boolean)
    .join('\n')
}

const onComplete = async (taskId: string) => {
  try {
    await nurseHttp.post(
      `/dispensing_tasks/${encodeURIComponent(taskId)}/complete`,
      {},
      {
        headers: { Authorization: 'Bearer 1' },
      },
    )
    message.success('已完成')
    await fetchTasks()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

const columns = computed<DataTableColumns<DispensingTask>>(() => [
  {
    title: 'task_id',
    key: 'task_id',
    ellipsis: true,
  },
  {
    title: 'time',
    key: 'time',
    width: 190,
  },
  {
    title: 'user_role',
    key: 'user_role',
    width: 110,
  },
  {
    title: 'user_id',
    key: 'user_id',
    ellipsis: true,
  },
  {
    title: 'medicines',
    key: 'medicines',
    render: (row) => {
      return formatMedicines(row.medicines)
    },
  },
  {
    title: 'is_completed',
    key: 'is_completed',
    width: 120,
    render: (row) => (row.is_completed ? 'YES' : 'NO'),
  },
  {
    title: 'action',
    key: 'action',
    width: 140,
    render: (row) => {
      if (row.is_completed) return null
      return h(
        NButton,
        {
          size: 'small',
          type: 'primary',
          onClick: () => onComplete(row.task_id),
        },
        { default: () => '完成' },
      )
    },
  },
])

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <NCard title="护士端: 配药任务列表">
    <div class="toolbar">
      <div class="toggle">
        <span>显示已完成</span>
        <NSwitch v-model:value="showCompleted" @update:value="fetchTasks" />
      </div>
      <NButton :loading="loading" @click="fetchTasks">刷新</NButton>
    </div>

    <NAlert v-if="errorMsg" type="error" class="block">{{ errorMsg }}</NAlert>

    <NDataTable
      class="block"
      :loading="loading"
      :columns="columns"
      :data="items"
      :row-key="(row) => row.task_id"
      :max-height="560"
    />
  </NCard>
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #374151;
  font-size: 14px;
}

.block {
  margin-top: 12px;
  white-space: pre-wrap;
}
</style>
