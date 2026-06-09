<script setup>
defineProps({
  stats: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <div class="stat-grid">
    <section v-for="item in stats" :key="item.label" class="stat-card">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </section>
  </div>
</template>
