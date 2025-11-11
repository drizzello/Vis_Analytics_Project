<script setup>
import { vessels, selectedVessel } from "@/stores/usefilters.js";
</script>

<template>
  <label class="filter-field" for="vessel">
    <span>Select vessel:</span>
    <select id="vessel" v-model="selectedVessel">
      <option v-for="v in vessels" :key="v" :value="v">
        {{ v }}
      </option>
    </select>
  </label>
</template>

<style scoped>
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.95rem;
  color: #0f172a;
  min-width: 220px;
  flex: 1 1 220px;
}

select {
  width: 100%;
  padding: 0.55rem 0.85rem;
  border-radius: 0.6rem;
  border: 1px solid #cbd5f5;
  font-size: 0.95rem;
  background: #ffffff;
}
</style>
