<script setup>
import { ref } from 'vue'
import { checkHealth } from '../api/health'

const status = ref('not checked')

async function check() {
  try {
    status.value = (await checkHealth()).status
  } catch (err) {
    status.value = err.message
  }
}
</script>

<template>
  <button @click="check">Check backend</button>
  <span> Backend: {{ status }}</span>
</template>