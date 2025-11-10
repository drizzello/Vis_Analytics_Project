<script setup>
import * as d3 from "d3";
import { ref, onMounted, watch, nextTick } from "vue";
import { selectedPort, selectedDate } from "@/stores/usefilters.js";
import EmptyStateMessage from "@/components/EmptyStateMessage.vue";

const chartRef = ref(null);
const data = ref([]);
const hasData = ref(true);

// --- Fetch chart data for current port/date ---
async function fetchData() {
  if (!selectedPort.value || !selectedDate.value) return;

  const res = await fetch(
    `http://127.0.0.1:8000/api/daily_exports_view?port=${encodeURIComponent(selectedPort.value)}&date=${selectedDate.value}`
  );
  const json = await res.json();
  data.value = json.daily_exports || [];
  hasData.value = data.value.length > 0;

  await nextTick();
  renderChart();
}

// --- Draw the D3 bar chart ---
function renderChart() {
  const svgEl = chartRef.value;
  d3.select(svgEl).selectAll("*").remove(); // clear previous chart

  if (!hasData.value) return;

  const margin = { top: 50, right: 40, bottom: 100, left: 80 },
    width = 800 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  const svg = d3
    .select(svgEl)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // --- X scale ---
  let xDomain = data.value.map((d) => d.fish_id);
  if (xDomain.length === 1) xDomain = ["", ...xDomain, ""]; // pad for single bar

  const x = d3.scaleBand().domain(xDomain).range([0, width]).padding(0.3);
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data.value, (d) => d.exports_tons)])
    .nice()
    .range([height, 0]);

  // --- Axes ---
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).tickFormat((d) => d || ""))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "11px");

  svg.append("g").call(d3.axisLeft(y).ticks(6));

  // --- Tooltip ---
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("background", "white")
    .style("padding", "6px 10px")
    .style("border", "1px solid #ccc")
    .style("border-radius", "6px")
    .style("pointer-events", "none")
    .style("opacity", 0);

  // --- Color function ---
  const color = (d) => (d.is_prohibited ? "#e11d48" : "#2196F3");

  // --- Bars ---
  svg
    .selectAll("rect")
    .data(data.value)
    .join("rect")
    .attr("x", (d) => x(d.fish_id))
    .attr("y", (d) => y(d.exports_tons))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.exports_tons))
    .attr("fill", color)
    .attr("opacity", 0.85)
    .on("mouseover", (event, d) => {
      tooltip.transition().duration(150).style("opacity", 1);
      tooltip
        .html(`
        <strong>${d.fish_id}</strong><br/>
        Export: ${d.exports_tons.toFixed(2)} tons<br/>
        ${
          d.is_prohibited
            ? `<span style="color:#e11d48;font-weight:bold;">🚫 Prohibited species</span>`
            : `<span style="color:#16a34a;">✔️ Legal species</span>`
        }
      `)
        .style("left", `${event.pageX + 10}px`)
        .style("top", `${event.pageY - 28}px`);
    })
    .on("mouseout", () =>
      tooltip.transition().duration(200).style("opacity", 0)
    );

  // --- Legend ---
  const legend = svg.append("g").attr("transform", `translate(${width - 160}, -20)`);

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

  // --- Title & Labels ---
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", -15)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(
      `Daily Exports by Fish Species — ${selectedPort.value} (${selectedDate.value})`
    );

  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", height + margin.bottom - 40)
    .attr("text-anchor", "middle")
    .style("font-size", "13px");

  svg
    .append("text")
    .attr("x", -height / 2)
    .attr("y", -55)
    .attr("transform", "rotate(-90)")
    .attr("text-anchor", "middle")
    .style("font-size", "13px")
    .text("Exported Tons");
}

// --- Lifecycle ---
onMounted(fetchData);
watch([selectedPort, selectedDate], fetchData);
</script>

<template>
  <div class="daily-export-bar">
    <EmptyStateMessage
      v-if="!hasData"
      title="No daily exports"
      :description="selectedPort && selectedDate
        ? `We couldn’t find declared exports for ${selectedPort} on ${selectedDate}.`
        : 'Select a port and date to view export data.'"
    />
    <svg v-else ref="chartRef"></svg>
  </div>
</template>

<style scoped>
.daily-export-bar {
  width: 100%;
  overflow-x: auto;
  text-align: center;
  margin-top: 1rem;
}

</style>
