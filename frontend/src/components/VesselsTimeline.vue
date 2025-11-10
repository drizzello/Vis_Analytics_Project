<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">PrimeVue UI Test</h1>

    <div class="flex gap-4 mb-4">
      <Dropdown
        v-model="selectedVessel"
        :options="vessels"
        placeholder="Select Vessel"
        class="w-60"
        showClear
      />
    </div>

    <Card>
      <template #title>Selected Values</template>
      <p><b>Vessel:</b> {{ selectedVessel }}</p>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'

const vessels = ['ship_a', 'ship_b', 'ship_c']
const selectedVessel = ref(null)
</script>
