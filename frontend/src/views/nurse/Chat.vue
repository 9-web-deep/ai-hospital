<script setup lang="ts">
import { ref } from 'vue'
import { NAlert, NButton, NCard, NInput } from 'naive-ui'

const message = ref('')
const streamingText = ref('')
const conversationId = ref('')
const sending = ref(false)
const errorMsg = ref('')

const onSend = async () => {
  if (sending.value) return
  errorMsg.value = ''
  streamingText.value = ''

  const trimmed = message.value.trim()
  if (!trimmed) {
    errorMsg.value = '请输入消息内容'
    return
  }

  const payload: Record<string, string> = { message: trimmed }
  if (conversationId.value) {
    payload.conversation_id = conversationId.value
  }

  sending.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_BACKEND_NURSE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 1',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok || !response.body) {
      throw new Error(`请求失败: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const processEvent = (rawEvent: string) => {
      let eventType: string | null = null
      const dataLines: string[] = []

      for (const line of rawEvent.split(/\r?\n/)) {
        if (line.startsWith('event:')) {
          eventType = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          dataLines.push(line.slice(5).replace(/^\s/, ''))
        }
      }

      if (dataLines.length === 0) return
      const dataStr = dataLines.join('\n').trim()
      if (!dataStr || dataStr === '[DONE]') return

      let payloadObj: any = null
      try {
        payloadObj = JSON.parse(dataStr)
      } catch {
        payloadObj = { event: eventType ?? 'message', message: dataStr }
      }

      const payloadEvent = payloadObj?.event ?? eventType

      if (payloadEvent === 'message' && typeof payloadObj?.message === 'string') {
        streamingText.value += payloadObj.message
        return
      }

      if (payloadEvent === 'conversation_id') {
        let nextId = payloadObj?.conversation_id
        if (!nextId && payloadObj && typeof payloadObj === 'object') {
          const keys = Object.keys(payloadObj).filter((key) => key !== 'event')
          if (keys.length === 1) {
            nextId = payloadObj[keys[0]]
          }
        }
        if (nextId) {
          conversationId.value = String(nextId)
        }
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      let splitIndex = buffer.indexOf('\n\n')
      while (splitIndex !== -1) {
        const rawEvent = buffer.slice(0, splitIndex).trim()
        buffer = buffer.slice(splitIndex + 2)
        if (rawEvent) {
          processEvent(rawEvent)
        }
        splitIndex = buffer.indexOf('\n\n')
      }
    }

    if (buffer.trim()) {
      processEvent(buffer.trim())
    }
  } catch (error: any) {
    errorMsg.value = error?.message || '请求失败'
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <NCard title="（测试用）护士方智能体">
    <div class="chat-layout">
      <div class="chat-input">
        <NInput v-model:value="message" type="textarea" placeholder="Input message"
          :autosize="{ minRows: 3, maxRows: 6 }" :disabled="sending" />
        <div class="chat-actions">
          <NButton type="primary" :loading="sending" @click="onSend">
            发送
          </NButton>
        </div>
      </div>
      <NAlert v-if="errorMsg" type="error">
        {{ errorMsg }}
      </NAlert>
      <div class="chat-stream">
        <div class="chat-meta">
          <span>conversation_id:</span>
          <span>{{ conversationId || '-' }}</span>
        </div>
        <pre v-if="streamingText">{{ streamingText }}</pre>
        <div v-else class="chat-empty">等待输出...</div>
      </div>
    </div>
  </NCard>
</template>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-actions {
  display: flex;
  justify-content: flex-end;
}

.chat-stream {
  min-height: 220px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  padding: 12px;
  color: #6b7280;
  font-size: 14px;
}

.chat-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.chat-empty {
  color: #9ca3af;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: #111827;
}
</style>
