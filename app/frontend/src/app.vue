<script setup>
import BackendStatus from './components/BackendStatus.vue'
import UserStatus from './components/UserStatus.vue';
</script>

<template>
  <header>
    <h1>Language Game</h1>
    <UserStatus />
    <nav>
      <RouterLink to="/">Play</RouterLink>
      |
      <RouterLink to="/login">Login</RouterLink>
      |
      <RouterLink to="/register">Register</RouterLink>
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