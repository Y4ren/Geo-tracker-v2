<template>
  <div>
    <Navbar class="fixed top-0 left-0 w-full z-50" />

    <main class="pt-16 p-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>