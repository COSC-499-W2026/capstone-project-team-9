<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { requestToken } from '../api/login.js'
import { setToken } from '../utils/auth.js'

const email = ref('')
const password = ref('')
const message = ref('')
const router = useRouter()

async function login() {
  message.value = ''

  try {
    const { access_token } = await requestToken(email.value, password.value)
    setToken(access_token)
  } catch {
    message.value = 'Login failed. Check your email and password.'
    return
  }

  await router.push({ name: 'play' })
}
</script>

<template>
  <h2>Login</h2>

  <form @submit.prevent="login">
    <div>
      <label for="email">Email:</label>
      <input id="email" v-model="email" type="email" required />
    </div>

    <div>
      <label for="password">Password:</label>
      <input id="password" v-model="password" type="password" required />
    </div>

    <button type="submit">Login</button>
  </form>

  <p v-if="message">{{ message }}</p>
</template>