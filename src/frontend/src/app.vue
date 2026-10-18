<script setup>
import BackendStatus from './components/BackendStatus.vue'
</script>

<template>
  <header>
    <h1>Language Game</h1>
    <nav>
      <RouterLink to="/">Play</RouterLink>
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