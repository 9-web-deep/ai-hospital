<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { adminHttp } from '@/lib/http'
import {
  NButton,
  NCard,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NPagination,
  NPopconfirm,
  NSelect,
  NSpin,
  NTag,
  NVirtualList,
  useMessage,
} from 'naive-ui'

interface OperationJournal {
  id: number | null
  trace_id: string
  source: string
  user_id: string
  user_role: string
  action_code: string
  time?: string
  status: number
  is_deleted?: boolean
  target_id: string
  target_role: string
  payload?: Record<string, unknown>
}

interface PaginatedResult<T> {
  total_count: number
  page_count: number
  page: number
  page_size: number
  data: T[]
}

const { t } = useI18n()
const message = useMessage()

const loading = ref(false)
const list = ref<OperationJournal[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  keyword: '',
  keywordField: 'trace_id_eq',
  status: null as number | null,
  timeRange: null as [number, number] | null,
  userRole: '',
  targetRole: '',
  traceId: '',
  userId: '',
  targetId: '',
  actionCode: '',
})

const advancedOpen = ref(false)

const keywordOptions = [
  { label: 'Trace ID', value: 'trace_id_eq' },
  { label: 'User ID', value: 'user_id_eq' },
  { label: 'Target ID', value: 'target_id_eq' },
  { label: 'Action Code', value: 'action_code_eq' },
]

const hasFilters = computed(() =>
  Boolean(
    form.keyword ||
      form.status !== null ||
      form.timeRange ||
      form.userRole ||
      form.targetRole ||
      form.traceId ||
      form.userId ||
      form.targetId ||
      form.actionCode,
  ),
)

function buildParams() {
  const params: Record<string, string | number> = {
    page: page.value,
    page_size: pageSize.value,
  }

  if (form.keyword) params[form.keywordField] = form.keyword
  if (form.status !== null) params.status_eq = form.status
  if (form.userRole) params.user_role_eq = form.userRole
  if (form.targetRole) params.target_role_eq = form.targetRole
  if (form.traceId) params.trace_id_eq = form.traceId
  if (form.userId) params.user_id_eq = form.userId
  if (form.targetId) params.target_id_eq = form.targetId
  if (form.actionCode) params.action_code_eq = form.actionCode
  if (form.timeRange) {
    params.time_gte = new Date(form.timeRange[0]).toISOString()
    params.time_lte = new Date(form.timeRange[1]).toISOString()
  }

  params.sort_by = '-time'

  return params
}

async function fetchList() {
  loading.value = true
  try {
    const { data } = await adminHttp.get<PaginatedResult<OperationJournal>>(
      '/operation-journals/',
      { params: buildParams() },
    )
    list.value = data.data
    total.value = data.total_count
  } catch (err) {
    message.error(t('admin.journal.fetchFailed'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchList()
}

function handleReset() {
  form.keyword = ''
  form.keywordField = 'trace_id_eq'
  form.status = null
  form.timeRange = null
  form.userRole = ''
  form.targetRole = ''
  form.traceId = ''
  form.userId = ''
  form.targetId = ''
  form.actionCode = ''
  page.value = 1
  fetchList()
}

async function handleDelete(item: OperationJournal) {
  if (item.id == null) {
    message.warning(t('admin.journal.deleteNoId'))
    return
  }
  try {
    await adminHttp.delete(`/operation-journals/${item.id}`)
    message.success(t('admin.journal.deleteSuccess'))
    fetchList()
  } catch (err) {
    message.error(t('admin.journal.deleteFailed'))
  }
}

function formatTime(value?: string) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function formatPayload(payload?: Record<string, unknown>) {
  if (!payload || Object.keys(payload).length === 0) return '-'
  try {
    return JSON.stringify(payload)
  } catch (err) {
    return String(payload)
  }
}

onMounted(fetchList)
</script>

<template>
  <NCard :title="t('admin.journal.title')">
    <div class="journal-toolbar">
      <div class="journal-search">
        <NSelect v-model:value="form.keywordField" :options="keywordOptions" size="small" class="journal-select" />
        <NInput v-model:value="form.keyword" :placeholder="t('admin.journal.searchPlaceholder')" clearable />
      </div>
      <div class="journal-quick">
        <NDatePicker v-model:value="form.timeRange" type="datetimerange" size="small" clearable />
        <NInputNumber v-model:value="form.status" size="small" clearable :min="0" :placeholder="t('admin.journal.filters.status')" />
        <NButton type="primary" :loading="loading" @click="handleSearch">
          {{ t('admin.journal.search') }}
        </NButton>
        <NButton :disabled="!hasFilters" @click="handleReset">
          {{ t('admin.journal.reset') }}
        </NButton>
        <NButton quaternary @click="advancedOpen = true">
          {{ t('admin.journal.advanced') }}
        </NButton>
      </div>
    </div>

    <NSpin :show="loading">
      <div class="journal-list">
        <NVirtualList :items="list" :item-size="96" class="journal-virtual">
          <template #default="{ item }">
            <div class="journal-item">
              <div class="journal-top">
                <div class="journal-title">
                  <span class="journal-code">{{ item.action_code }}</span>
                  <NTag size="small" type="info">{{ item.status }}</NTag>
                </div>
                <div class="journal-time">{{ formatTime(item.time) }}</div>
              </div>
              <div class="journal-meta">
                <span>{{ t('admin.journal.user') }}: {{ item.user_role }} / {{ item.user_id }}</span>
                <span>{{ t('admin.journal.target') }}: {{ item.target_role }} / {{ item.target_id }}</span>
              </div>
              <div class="journal-meta">
                <span>{{ t('admin.journal.trace') }}: {{ item.trace_id }}</span>
                <span>{{ t('admin.journal.source') }}: {{ item.source }}</span>
              </div>
              <div class="journal-payload">
                {{ t('admin.journal.payload') }}: {{ formatPayload(item.payload) }}
              </div>
              <div class="journal-ops">
                <NPopconfirm @positive-click="handleDelete(item)">
                  <template #trigger>
                    <NButton size="tiny" type="error" tertiary>
                      {{ t('admin.journal.delete') }}
                    </NButton>
                  </template>
                  {{ t('admin.journal.deleteConfirm') }}
                </NPopconfirm>
              </div>
            </div>
          </template>
        </NVirtualList>
        <div v-if="list.length === 0 && !loading" class="journal-empty">
          {{ t('admin.journal.empty') }}
        </div>
      </div>
    </NSpin>

    <div class="journal-pagination">
      <NPagination
        v-model:page="page"
        v-model:page-size="pageSize"
        :item-count="total"
        :page-sizes="[10, 20, 50, 100]"
        show-size-picker
        @update:page="fetchList"
        @update:page-size="fetchList"
      />
    </div>
  </NCard>

  <NDrawer v-model:show="advancedOpen" placement="right" :width="360">
    <NDrawerContent :title="t('admin.journal.advanced')">
      <NForm label-placement="left" label-width="auto" :show-feedback="false" class="journal-advanced-form">
        <NFormItem :label="t('admin.journal.filters.traceId')">
          <NInput v-model:value="form.traceId" clearable />
        </NFormItem>
        <NFormItem :label="t('admin.journal.filters.userId')">
          <NInput v-model:value="form.userId" clearable />
        </NFormItem>
        <NFormItem :label="t('admin.journal.filters.userRole')">
          <NInput v-model:value="form.userRole" clearable />
        </NFormItem>
        <NFormItem :label="t('admin.journal.filters.targetId')">
          <NInput v-model:value="form.targetId" clearable />
        </NFormItem>
        <NFormItem :label="t('admin.journal.filters.targetRole')">
          <NInput v-model:value="form.targetRole" clearable />
        </NFormItem>
        <NFormItem :label="t('admin.journal.filters.actionCode')">
          <NInput v-model:value="form.actionCode" clearable />
        </NFormItem>
      </NForm>
      <div class="journal-advanced-actions">
        <NButton type="primary" :loading="loading" @click="handleSearch">
          {{ t('admin.journal.search') }}
        </NButton>
        <NButton :disabled="!hasFilters" @click="handleReset">
          {{ t('admin.journal.reset') }}
        </NButton>
      </div>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped>
.journal-toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.journal-search {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px;
  align-items: center;
}

.journal-select {
  min-width: 160px;
}

.journal-quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.journal-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.journal-virtual {
  height: 420px;
}

.journal-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eef0f3;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #fff;
}

.journal-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.journal-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.journal-code {
  font-size: 14px;
}

.journal-time {
  font-size: 12px;
  color: #6b7280;
}

.journal-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  gap: 12px;
}

.journal-payload {
  font-size: 12px;
  color: #4b5563;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.journal-ops {
  display: flex;
  justify-content: flex-end;
}

.journal-empty {
  padding: 24px;
  text-align: center;
  color: #9ca3af;
}

.journal-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 720px) {
  .journal-search {
    grid-template-columns: 1fr;
  }

  .journal-meta {
    flex-direction: column;
  }
}

.journal-advanced-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.journal-advanced-form :deep(.n-form-item) {
  margin-bottom: 12px;
}
</style>
