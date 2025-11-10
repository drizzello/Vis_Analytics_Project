<script setup>
const props = defineProps({
  title: {
    type: String,
    default: "No data available",
  },
  description: {
    type: String,
    default: "",
  },
  icon: {
    type: String,
    default: "⚠️",
  },
});
</script>

<template>
  <div class="empty-state" role="status" aria-live="polite">
    <span class="empty-state__icon" aria-hidden="true">{{ icon }}</span>
    <div class="empty-state__content">
      <p class="empty-state__title">{{ title }}</p>
      <p v-if="description" class="empty-state__description">
        {{ description }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  width: 100%;
  padding: 1.75rem;
  border: 1px dashed rgba(15, 23, 42, 0.2);
  border-radius: 0.85rem;
  background: #f8fafc;
  color: #475569;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  text-align: left;
  box-sizing: border-box;
}

.empty-state__icon {
  font-size: 1.5rem;
  line-height: 1;
}

.empty-state__title {
  margin: 0;
  font-weight: 600;
  color: #0f172a;
}

.empty-state__description {
  margin: 0.3rem 0 0;
  font-size: 0.95rem;
  color: #475569;
}
</style>
