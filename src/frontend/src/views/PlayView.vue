<script setup>
import { ref } from 'vue'
import { verifyLocation } from '../api/location'
import { getCurrentCoords } from '../utils/geolocation'

const result = ref(null)
const error = ref('')
const loading = ref(false)

async function play() {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const { latitude, longitude } = await getCurrentCoords()
    result.value = await verifyLocation(latitude, longitude)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section>
    <button :disabled="loading" @click="play">Play</button>
    <p v-if="result">{{ result.allowed ? '✅' : '🚫' }} {{ result.message }}</p>
    <p v-if="error">Error: {{ error }}</p>
  </section>
</template>