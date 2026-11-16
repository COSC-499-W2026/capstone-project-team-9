<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { get } from '../api/client'
import { clearToken, getToken } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const userName = ref('')

// Re-check on every navigation, so the header updates right after logging in
watch(
  () => route.fullPath,
  async () => {
    if (!getToken()) {
      userName.value = ''
      return
    }
    try {
      userName.value = (await get('/login/me')).name
    } catch {
      userName.value = '' // token missing, expired or invalid
    }
  },
  { immediate: true },
)

async function logout() {
  clearToken()
  userName.value = ''
  await router.push({ name: 'login' })
}
</script>

<template>
  <p v-if="userName">
    Logged in as: {{ userName }}
    <button type="button" @click="logout">Log out</button>
  </p>
  <p v-else>Not logged in</p>
</template>