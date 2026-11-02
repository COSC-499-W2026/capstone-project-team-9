<script setup>
import { ref } from 'vue'
import { post } from '../api/client.js'

const email = ref('')
const password = ref('')
const message = ref('')

async function login() {
  message.value = ''

  try {
    const user = await post('/login', {
      email: email.value,
      password: password.value,
    })

    message.value = `Welcome, ${user.name}!`
  } catch {
    message.value = 'Login failed. Check your email and password.'
  }
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