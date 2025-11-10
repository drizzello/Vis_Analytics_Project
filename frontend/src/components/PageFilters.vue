<script setup>
import { onMounted } from "vue";
import {
  ports,
  dates,
  selectedPort,
  selectedDate,
  fetchFilters,
} from "@/stores/usefilters.js";
import VesselSelect from "@/components/VesselSelect.vue";

defineProps({
  showPort: { type: Boolean, default: true },
  showDate: { type: Boolean, default: true },
  showVessel: { type: Boolean, default: false },
});

onMounted(fetchFilters);
</script>

<template>
  <div class="page-filters">
    <label v-if="showPort">
      <span>Port:</span>
      <select v-model="selectedPort">
        <option disabled value="">Select Port</option>
        <option v-for="p in ports" :key="p" :value="p">{{ p }}</option>
      </select>
    </label>

    <label v-if="showDate">
      <span>Date:</span>
      <input
        type="date"
        v-model="selectedDate"
        :min="dates[0]"
        :max="dates[dates.length - 1]"
      />
    </label>

    <VesselSelect v-if="showVessel" />
  </div>
</template>

<style scoped>
.page-filters {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-items: stretch;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 0.85rem;
  background: #f8fafc;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.95rem;
  color: #0f172a;
  min-width: 220px;
  flex: 1 1 220px;
}

select,
input[type="date"] {
  width: 100%;
  padding: 0.55rem 0.85rem;
  border-radius: 0.6rem;
  border: 1px solid #cbd5f5;
  font-size: 0.95rem;
  background: #ffffff;
}

@media (max-width: 640px) {
  .page-filters {
    flex-direction: column;
    gap: 0.85rem;
  }

  label {
    width: 100%;
    min-width: 0;
  }
}
</style>
