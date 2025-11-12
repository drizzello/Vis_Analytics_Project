<script setup>
import * as d3 from "d3";
import { ref, watch, onMounted, nextTick} from "vue";
import { selectedPort, selectedDate } from "@/stores/usefilters.js";
import EmptyStateMessage from "@/components/EmptyStateMessage.vue";

const chartRef = ref(null);
const data = ref([]);
const cargoIds = ref([]);
const selectedCargo = ref("");
const hasData = ref(true);

// --- Fetch vessel catch data ---
async function fetchData() {
  if (!selectedPort.value || !selectedDate.value) return;

  const res = await fetch(
    `http://127.0.0.1:8000/api/vessel_catch_view?port=${encodeURIComponent(
      selectedPort.value
    )}&date=${selectedDate.value}`
  );
  const json = await res.json();

  if (!json.vessel_catch || json.vessel_catch.length === 0) {
    hasData.value = false;
    data.value = [];
    return;
  }

  data.value = json.vessel_catch;
  cargoIds.value = [...new Set(data.value.map((d) => d.cargo_id))];
  selectedCargo.value = cargoIds.value[0];
  hasData.value = true;
  await nextTick();
  renderChart();
}

const isProhibited = (d) =>
  d.is_prohibited === true || d.is_prohibited === "True" || d.is_prohibited === "true";

function renderChart() {
  const svg = d3.select(chartRef.value);
  svg.selectAll("*").remove();

  if (!data.value.length || !selectedCargo.value) return;

  const cargoData = data.value
    .filter((d) => d.cargo_id === selectedCargo.value)
    .sort((a, b) => d3.ascending(a.share_percent, b.share_percent));

  const margin = { top: 40, right: 40, bottom: 50, left: 160 };
  const width = 800 - margin.left - margin.right;
  const height = cargoData.length * 28;

  const chart = svg
    .attr(
      "viewBox",
      [0, 0, width + margin.left + margin.right, height + margin.top + margin.bottom]
    )
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear()
    .domain([0, d3.max(cargoData, (d) => d.share_percent)])
    .nice()
    .range([0, width]);

  const y = d3.scaleBand()
    .domain(cargoData.map((d) => d.vessel_name))
    .range([height, 0])
    .padding(0.2);

  // --- Color rule ---
  const color = (d) => (isProhibited(d) ? "#e11d48" : "#2196F3");

  // --- Axes ---
  chart.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat((d) => d + "%"))
    .selectAll("text")
    .style("font-size", "12px");

  chart.append("g")
    .call(d3.axisLeft(y))
    .selectAll("text")
    .style("font-size", "12px");

  // --- Bars ---
  chart.selectAll("rect")
    .data(cargoData)
    .join("rect")
    .attr("x", 0)
    .attr("y", (d) => y(d.vessel_name))
    .attr("height", y.bandwidth())
    .attr("width", (d) => x(d.share_percent))
    .attr("fill", color)
    .attr("opacity", 0.85)
    .append("title")
    .text(
      (d) =>
        `${d.vessel_name}\n${d.fish_name}\nShare: ${d.share_percent.toFixed(1)}%\nEstimated: ${d.estimated_tons.toFixed(1)} tons\n${
          isProhibited(d)
            ? "🚫 Prohibited species"
            : "✔️ Legal species"
        }`
    );

  // --- Legend ---
  const legend = chart
    .append("g")
    .attr("transform", `translate(${width - 160}, -30)`);

  const legendItems = [
    { label: "Legal fish", color: "#2196F3" },
    { label: "Prohibited fish", color: "#e11d48" },
  ];

  legend
    .selectAll("rect")
    .data(legendItems)
    .join("rect")
    .attr("x", 0)
    .attr("y", (_, i) => i * 20)
    .attr("width", 12)
    .attr("height", 12)
    .attr("fill", (d) => d.color);

  legend
    .selectAll("text")
    .data(legendItems)
    .join("text")
    .attr("x", 18)
    .attr("y", (_, i) => i * 20 + 10)
    .text((d) => d.label)
    .style("font-size", "12px")
    .attr("fill", "#334155");

  // --- X label ---
  chart.append("text")
    .attr("x", width / 2)
    .attr("y", height + margin.bottom - 5)
    .attr("text-anchor", "middle")
    .attr("fill", "#334155")
    .style("font-size", "13px")
    .text("Share of cargo (%)");
}

onMounted(fetchData);
watch([selectedPort, selectedDate], fetchData);
watch(selectedCargo, renderChart);
</script>

<template>
  <div class="vessel-catch-bar">
    <div class="heading">
      <p class="section-eyebrow">Cargo → Vessel Distribution</p>
      <h2>How were the cargos distributed among vessels?</h2>
    </div>

    <div v-if="hasData">
      <label class="dropdown-label">Select Cargo ID:</label>
      <select v-model="selectedCargo" class="cargo-dropdown">
        <option v-for="id in cargoIds" :key="id" :value="id">
          {{ id }}
        </option>
      </select>

      <svg ref="chartRef" class="chart"></svg>
    </div>

    <EmptyStateMessage
      v-else
      title="No vessel catch data"
      :description="selectedPort && selectedDate
        ? `We couldn’t estimate any cargo shares for ${selectedPort} on ${selectedDate}.`
        : 'Select a port and date to compute catches.'"
    />
  </div>
</template>

<style scoped>
.vessel-catch-bar {
  padding: clamp(1.5rem, 2.5vw, 2.5rem);
}

.heading {
  margin-bottom: 1.2rem;
}

.section-eyebrow {
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  color: #0e7490;
  margin-bottom: 0.2rem;
}

h2 {
  margin: 0;
  font-size: clamp(1.3rem, 2vw, 1.6rem);
  color: #0f172a;
}

.chart {
  width: 100%;
  height: auto;
  margin-top: 1rem;
}

.dropdown-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #475569;
  font-size: 0.9rem;
}

.cargo-dropdown {
  margin-bottom: 1rem;
  padding: 0.4rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
}

</style>
