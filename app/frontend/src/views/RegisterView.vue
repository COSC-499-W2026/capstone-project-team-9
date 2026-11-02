<script setup>
import { ref } from 'vue'
import { post } from '../api/client.js'

const name = ref('')
const email = ref('')
const password = ref('')
const message = ref('')
const successful = ref(false)

async function register() {
  message.value = ''
  successful.value = false

  try {
    const user = await post('/users/register', {
      name: name.value,
      email: email.value,
      password: password.value,
    })

    successful.value = true
    message.value = `Registration successful! Welcome, ${user.name}!`

    name.value = ''
    email.value = ''
    password.value = ''
  } catch (error) {
    if (error.message.includes('(409)')) {
      message.value = 'Username or email already exists.'
    } else if (error.message.includes('(422)')) {
      message.value = 'Please check your registration details.'
    } else {
      message.value = 'Registration failed. Please try again.'
    }
  }
}
</script>

<template>
  <h2>Register</h2>

  <form @submit.prevent="register">
    <div>
      <label for="name">Username:</label>
      <input
        id="name"
        v-model="name"
        type="text"
        minlength="1"
        maxlength="100"
        required
      />
    </div>

    <div>
      <label for="email">Email:</label>
      <input
        id="email"
        v-model="email"
        type="email"
        maxlength="320"
        required
      />
    </div>

    <div>
      <label for="password">Password:</label>
      <input
        id="password"
        v-model="password"
        type="password"
        minlength="8"
        required
      />
    </div>

    <button type="submit">Register</button>
  </form>

  <p v-if="message" role="status">
    {{ message }}
  </p>
</template>