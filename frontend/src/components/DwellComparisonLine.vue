<script setup>
import * as d3 from "d3";
import { ref, onMounted, watch } from "vue";
import { selectedVessel } from "@/stores/usefilters.js";

const chartRef = ref(null);
const data = ref([]);
const hasData = ref(true);

async function fetchData() {
  const res = await fetch(
    `http://127.0.0.1:8000/api/dwell_comparison_view?vessel=${encodeURIComponent(selectedVessel.value || "")}`
  );
  const json = await res.json();
  data.value = json.dwell_comparison || [];
  hasData.value = data.value.length > 0;
  renderChart();
}

function renderChart() {
  const svgEl = chartRef.value;
  d3.select(svgEl).selectAll("*").remove();
  if (!hasData.value) return;

  const margin = { top: 60, right: 50, bottom: 80, left: 80 },
    width = 900 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  const svg = d3
    .select(svgEl)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleBand()
    .domain(data.value.map((d) => d.location_name))
    .range([0, width])
    .padding(0.3);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data.value, (d) => d.safe_high)])
    .nice()
    .range([height, 0]);

  // === SAFE ZONE AREA ===
  svg
    .append("path")
    .datum(data.value)
    .attr("fill", "#cbd5e1")
    .attr("opacity", 0.4)
    .attr(
      "d",
      d3
        .area()
        .x((d) => x(d.location_name) + x.bandwidth() / 2)
        .y0((d) => y(d.safe_low))
        .y1((d) => y(d.safe_high))
    );

  // === BASELINE LINE ===
  const baselineLine = d3
    .line()
    .x((d) => x(d.location_name) + x.bandwidth() / 2)
    .y((d) => y(d.mean_dwell))
    .curve(d3.curveMonotoneX);

  svg
    .append("path")
    .datum(data.value)
    .attr("fill", "none")
    .attr("stroke", "#475569")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4,2")
    .attr("d", baselineLine);

  // === VESSEL LINE ===
  if (data.value.some((d) => d.vessel_dwell)) {
    const vesselLine = d3
      .line()
      .x((d) => x(d.location_name) + x.bandwidth() / 2)
      .y((d) => y(d.vessel_dwell || 0))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(data.value.filter((d) => d.vessel_dwell))
      .attr("fill", "none")
      .attr("stroke", "#0ea5e9")
      .attr("stroke-width", 2.5)
      .attr("d", vesselLine);
  }

  // === Axes ===
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-40)")
    .style("text-anchor", "end")
    .style("font-size", "11px");

  svg.append("g").call(d3.axisLeft(y));

  // === Title ===
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", -20)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(`Average Dwell by Zone — ${selectedVessel.value || "All Vessels"}`);

  // === Legend ===
  const legend = svg.append("g").attr("transform", `translate(${width - 200}, 0)`);

  const legendItems = [
    { label: "All vessels (avg)", color: "#475569", dash: "4,2" },
    { label: "Safe zone (±1σ)", color: "#cbd5e1", area: true },
    { label: `${selectedVessel.value || "Selected vessel"}`, color: "#0ea5e9" },
  ];

  legendItems.forEach((item, i) => {
    const yPos = i * 24;
    if (item.area) {
      legend
        .append("rect")
        .attr("x", 0)
        .attr("y", yPos - 8)
        .attr("width", 20)
        .attr("height", 12)
        .attr("fill", item.color)
        .attr("opacity", 0.4);
    } else {
      legend
        .append("line")
        .attr("x1", 0)
        .attr("x2", 20)
        .attr("y1", yPos - 2)
        .attr("y2", yPos - 2)
        .attr("stroke", item.color)
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", item.dash || null);
    }
    legend
      .append("text")
      .attr("x", 28)
      .attr("y", yPos)
      .attr("alignment-baseline", "middle")
      .style("font-size", "12px")
      .text(item.label);
  });
}

onMounted(fetchData);
watch(selectedVessel, fetchData);
</script>

<template>
  <div class="dwell-comparison-line">
    <div v-if="!hasData" class="no-data">
      ⚠️ No dwell data available.
    </div>
    <svg v-else ref="chartRef"></svg>
  </div>
</template>

<style scoped>
.dwell-comparison-line {
  width: 100%;
  overflow-x: auto;
  text-align: center;
  margin-top: 1rem;
}
.no-data {
  padding: 2rem;
  color: #555;
  background-color: #f8fafc;
  border: 1px dashed #ccc;
  border-radius: 8px;
  font-style: italic;
}
</style>
