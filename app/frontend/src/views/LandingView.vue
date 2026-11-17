<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { requestGuestToken } from '../api/login.js'
import { setToken } from '../utils/auth.js'

const router = useRouter()
const loading = ref(false)
const error = ref('')

async function playAsGuest() {
  error.value = ''
  loading.value = true
  try {
    const { access_token } = await requestGuestToken()
    setToken(access_token)
  } catch {
    error.value = "Couldn't start a guest session. Try again."
    loading.value = false
    return
  }
  await router.push({ name: 'play' })
}
</script>

<template>
  <section>
    <h2>Welcome to Language Game</h2>

    <p><RouterLink to="/login">Log in</RouterLink></p>
    <p><RouterLink to="/register">Register</RouterLink></p>
    <p><button type="button" :disabled="loading" @click="playAsGuest">Play as guest</button></p>

    <p v-if="error">{{ error }}</p>
  </section>
</template>