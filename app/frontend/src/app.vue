<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getCurrentUser } from './api/course'
import { getToken } from './utils/auth'
import BackendStatus from './components/BackendStatus.vue'
import UserStatus from './components/UserStatus.vue'

const route = useRoute()
const showHeader = computed(() => route.name !== 'landing')

// Guests can't use courses, so hide the link for them (the router guard blocks the pages too)
const isGuest = ref(false)
watch(
  () => route.fullPath,
  async () => {
    if (!getToken()) {
      isGuest.value = false
      return
    }
    try {
      isGuest.value = (await getCurrentUser()).role === 'guest'
    } catch {
      isGuest.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <header v-if="showHeader">
    <h1>Language Game</h1>
    <nav>
    <!-- add links as screens are added -->
      <RouterLink to="/">Home</RouterLink>
      |
      <RouterLink to="/play">Play</RouterLink>
      |
      <template v-if="!isGuest">
        <RouterLink to="/courses">Courses</RouterLink>
        |
      </template>
      <RouterLink to="/login">Login</RouterLink>
      |
      <RouterLink to="/register">Register</RouterLink>
    </nav>
    <UserStatus />
    <hr>
  </header>

  <main>
    <RouterView />
  </main>

  <footer>
    <!-- <BackendStatus /> -->
  </footer>
</template>