<script setup lang="ts">
import { ref } from 'vue'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput } from 'naive-ui'
import { doctorHttp } from '@/lib/http'

const opdId = ref('')
const targetId = ref('')
const doctorNote = ref('')
const imageFile = ref<File | null>(null)
const submitting = ref(false)
const result = ref('')
const errorMsg = ref('')

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  imageFile.value = input.files?.[0] ?? null
}

const onSubmit = async () => {
  errorMsg.value = ''
  result.value = ''

  if (!opdId.value || !targetId.value || !imageFile.value) {
    errorMsg.value = '请填写 opd_id、target_id 并选择 image 文件'
    return
  }

  const payload = new FormData()
  payload.append('opd_id', opdId.value)
  payload.append('target_id', targetId.value)
  payload.append('doctor_note', doctorNote.value)
  payload.append('image', imageFile.value)

  submitting.value = true
  try {
    const response = await doctorHttp.post('/ai-report', payload, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': 'Bearer 1'
      },
    })

    const traceId = response.data['trace_id'];
    let count = 0;
    const intervalId = setInterval(async () => {
      count++;

      const traceResult = await doctorHttp.get('/poll?trace_id=' + traceId, {
        headers: {
          'Authorization': 'Bearer 1'
        },
      })

      const data = traceResult.data['data'];

      if (count > 180 / 5 || data) {
        result.value = data
        clearInterval(intervalId);
      }
    }, 5000);

  } catch (error: any) {
    errorMsg.value = error?.response?.data?.message || error?.message || '请求失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <NCard title="CT 智能分析">
    <div class="ct-layout">
      <NForm label-placement="left" label-width="90">
        <NFormItem label="opd_id">
          <NInput v-model:value="opdId" placeholder="请输入 opd_id" />
        </NFormItem>
        <NFormItem label="target_id">
          <NInput v-model:value="targetId" placeholder="请输入 target_id" />
        </NFormItem>
        <NFormItem label="doctor_note">
          <NInput v-model:value="doctorNote" type="textarea" placeholder="请输入 doctor_note" />
        </NFormItem>
        <NFormItem label="image">
          <input class="file-input" type="file" accept="image/*" @change="onFileChange" />
        </NFormItem>
        <div class="form-actions">
          <NButton type="primary" :loading="submitting" @click="onSubmit">
            提交分析
          </NButton>
        </div>
      </NForm>

      <NAlert v-if="errorMsg" type="error" class="alert-block">
        {{ errorMsg }}
      </NAlert>

      <div v-if="result" class="result-block">
        <pre>{{ result }}</pre>
      </div>
    </div>
  </NCard>
</template>

<style scoped>
.ct-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.file-input {
  width: 100%;
}

.alert-block {
  margin-top: 8px;
}

.result-block {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: #fff;
  font-size: 13px;
  color: #1f2937;
  white-space: pre-wrap;
}
</style>
