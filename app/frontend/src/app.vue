<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BackendStatus from './components/BackendStatus.vue'
import UserStatus from './components/UserStatus.vue'

const route = useRoute()
const showHeader = computed(() => route.name !== 'landing')
</script>

<template>
  <header v-if="showHeader">
    <h1>Language Game</h1>
    <UserStatus />
    <nav>
      <RouterLink to="/">Home</RouterLink>
      |
      <RouterLink to="/play">Play</RouterLink>
      <!-- add links as screens are added -->
    </nav>
  </header>

  <main>
    <RouterView />
  </main>

  <footer>
    <BackendStatus />
  </footer>
</template>