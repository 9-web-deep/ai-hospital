<script setup lang="ts">
import { ref } from 'vue'
import { NAlert, NButton, NCard, NDynamicInput, NForm, NFormItem, NInput, NInputNumber } from 'naive-ui'
import { doctorHttp } from '@/lib/http'

type MedicineItem = {
  medicine: string
  specification?: string
  amount?: number
}

const medicines = ref<MedicineItem[]>([{ medicine: '', specification: '', amount: 1 }])
const submitting = ref(false)
const errorMsg = ref('')
const taskId = ref('')

const onSubmit = async () => {
  errorMsg.value = ''
  taskId.value = ''

  const trimmed = (medicines.value ?? [])
    .filter((m): m is MedicineItem => !!m && typeof m === 'object')
    .map((m) => ({
      medicine: (m.medicine ?? '').trim(),
      specification: (m.specification ?? '').trim() || undefined,
      amount: typeof m.amount === 'number' ? m.amount : undefined,
    }))
    .filter((m) => m.medicine)

  if (trimmed.length === 0) {
    errorMsg.value = '请至少填写 1 个药品（medicine）'
    return
  }

  submitting.value = true
  try {
    const resp = await doctorHttp.post(
      '/dispensing_tasks',
      { medicines: trimmed },
      {
        headers: {
          Authorization: 'Bearer 1',
        },
      },
    )
    taskId.value = String(resp.data?.task_id ?? '')
    if (!taskId.value) {
      errorMsg.value = '请求成功但未返回 task_id'
    }
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || e?.message || '请求失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <NCard title="医生端: 发出配药任务">
    <NForm label-placement="left" label-width="120">
      <NFormItem label="要配的药列表">
        <NDynamicInput
          v-model:value="medicines"
          :min="1"
          item-style="margin-bottom: 12px;"
          :on-create="() => ({ medicine: '', specification: '', amount: 1 })"
        >
          <template #default="{ value }">
            <div class="row">
              <NInput v-model:value="value.medicine" placeholder="medicine (必填)" />
              <NInput v-model:value="value.specification" placeholder="specification (可选)" />
              <NInputNumber v-model:value="value.amount" :min="1" placeholder="amount (可选)" />
            </div>
          </template>
        </NDynamicInput>
      </NFormItem>

      <div class="actions">
        <NButton type="primary" :loading="submitting" @click="onSubmit">发送配药任务</NButton>
      </div>
    </NForm>

    <NAlert v-if="errorMsg" type="error" class="block">{{ errorMsg }}</NAlert>
    <NAlert v-if="taskId" type="success" class="block">
      已发送，task_id: <span class="mono">{{ taskId }}</span>
    </NAlert>
  </NCard>
</template>

<style scoped>
.row {
  display: grid;
  grid-template-columns: 1fr 1fr 140px;
  gap: 10px;
  width: 100%;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.block {
  margin-top: 12px;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

@media (max-width: 720px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
