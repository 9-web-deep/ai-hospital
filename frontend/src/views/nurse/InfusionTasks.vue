<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NAlert, NButton, NCard, NDataTable, NSwitch, useMessage, type DataTableColumns } from 'naive-ui'
import { nurseHttp } from '@/lib/http'

type FluidItem = {
  medicine?: string
  specification?: string
  amount?: number
}

type InfusionTask = {
  task_id: string
  time: string
  target_id: string
  target_role: string
  fluids: FluidItem[]
  current_fluid: FluidItem | null
  is_completed: boolean
  status: string
  status_updated_at: string
}

const message = useMessage()
const loading = ref(false)
const errorMsg = ref('')
const showCompleted = ref(false)
const items = ref<InfusionTask[]>([])

const sameFluid = (a: FluidItem | null | undefined, b: FluidItem | null | undefined) => {
  const am = String(a?.medicine ?? '').trim()
  const bm = String(b?.medicine ?? '').trim()
  const as = String(a?.specification ?? '').trim()
  const bs = String(b?.specification ?? '').trim()
  const aa = a?.amount ?? null
  const ba = b?.amount ?? null
  return am === bm && as === bs && aa === ba
}

const formatFluid = (f: FluidItem | null | undefined) => {
  if (!f) return '-'
  const name = String(f.medicine ?? '').trim()
  const spec = String(f.specification ?? '').trim()
  const amt = f.amount != null ? String(f.amount) : ''
  const parts = [name]
  if (spec) parts.push(spec)
  if (amt) parts.push(`x${amt}`)
  return parts.filter(Boolean).join(' ')
}

const formatFluids = (fluids: FluidItem[]) => {
  if (!Array.isArray(fluids) || fluids.length === 0) return '-'
  return fluids.map((f) => formatFluid(f)).filter(Boolean).join('\n')
}

const nextFluidOf = (task: InfusionTask): FluidItem | null => {
  const fluids = Array.isArray(task.fluids) ? task.fluids : []
  if (fluids.length === 0) return null
  const current = task.current_fluid
  if (!current) return fluids[0]
  const idx = fluids.findIndex((f) => sameFluid(f, current))
  if (idx < 0) return fluids[0]
  if (idx + 1 >= fluids.length) return null
  return fluids[idx + 1]
}

const fetchTasks = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const resp = await nurseHttp.get('/infusion_tasks', {
      params: {
        is_completed: showCompleted.value ? undefined : false,
        limit: 200,
        offset: 0,
      },
      headers: {
        Authorization: 'Bearer 1',
      },
    })
    items.value = (resp.data?.items ?? []) as InfusionTask[]
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const onStart = async (task: InfusionTask) => {
  try {
    await nurseHttp.post(
      `/infusion_tasks/${encodeURIComponent(task.task_id)}/start`,
      {},
      { headers: { Authorization: 'Bearer 1' } },
    )
    message.success('已开始')
    await fetchTasks()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

const onNext = async (task: InfusionTask) => {
  const next = nextFluidOf(task)
  if (!next || !String(next.medicine ?? '').trim()) {
    message.warning('没有下一袋液体了')
    return
  }
  try {
    await nurseHttp.post(
      `/infusion_tasks/${encodeURIComponent(task.task_id)}/change`,
      {
        medicine: String(next.medicine ?? '').trim(),
        specification: String(next.specification ?? '').trim() || undefined,
        amount: typeof next.amount === 'number' ? next.amount : undefined,
      },
      { headers: { Authorization: 'Bearer 1' } },
    )
    message.success('已换液')
    await fetchTasks()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

const onComplete = async (task: InfusionTask) => {
  try {
    await nurseHttp.post(
      `/infusion_tasks/${encodeURIComponent(task.task_id)}/complete`,
      {},
      { headers: { Authorization: 'Bearer 1' } },
    )
    message.success('已完成')
    await fetchTasks()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

const columns = computed<DataTableColumns<InfusionTask>>(() => [
  { title: 'task_id', key: 'task_id', ellipsis: true },
  { title: 'target_id', key: 'target_id', ellipsis: true },
  { title: 'status', key: 'status', width: 110 },
  { title: 'updated_at', key: 'status_updated_at', width: 190 },
  {
    title: 'current_fluid',
    key: 'current_fluid',
    render: (row) => formatFluid(row.current_fluid),
  },
  {
    title: 'fluids',
    key: 'fluids',
    render: (row) => formatFluids(row.fluids),
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
    width: 220,
    render: (row) => {
      if (row.is_completed) return null
      return h(
        'div',
        { style: { display: 'flex', gap: '8px' } },
        [
          h(
            NButton,
            { size: 'small', onClick: () => onStart(row) },
            { default: () => '开始' },
          ),
          h(
            NButton,
            { size: 'small', type: 'primary', onClick: () => onNext(row) },
            { default: () => '换液' },
          ),
          h(
            NButton,
            { size: 'small', type: 'success', onClick: () => onComplete(row) },
            { default: () => '完成' },
          ),
        ],
      )
    },
  },
])

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <NCard title="护士端: 输液任务列表">
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

