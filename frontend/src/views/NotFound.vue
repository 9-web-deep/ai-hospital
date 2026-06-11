<script setup lang="ts">
import { NButton, NResult } from 'naive-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/admin/dashboard')
}
</script>

<template>
  <div class="not-found">
    <NResult status="404" title="404" description="Page not found">
      <template #footer>
        <NButton type="primary" @click="goHome">Back to Dashboard</NButton>
      </template>
    </NResult>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f7f9;
}
</style>
