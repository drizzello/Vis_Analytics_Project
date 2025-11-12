<script setup>
import * as d3 from "d3";
import { ref, onMounted, watch, nextTick } from "vue";
import { selectedPort, selectedDate } from "@/stores/usefilters.js";
import EmptyStateMessage from "@/components/EmptyStateMessage.vue";

const chartRef = ref(null);
const data = ref([]);
const hasData = ref(true);

async function fetchData() {
  if (!selectedPort.value || !selectedDate.value) return;

  const res = await fetch(
    `http://127.0.0.1:8000/api/daily_view?port=${encodeURIComponent(selectedPort.value)}&date=${selectedDate.value}`
  );
  const json = await res.json();
  data.value = json.scatter_data || [];
  hasData.value = data.value.length > 0;
  
  await nextTick(); 
  renderChart();
}

onMounted(fetchData);
watch([selectedPort, selectedDate], fetchData);

function renderChart() {
  const svgEl = chartRef.value;
  d3.select(svgEl).selectAll("*").remove();
  if (!hasData.value) return;

  const margin = { top: 70, right: 150, bottom: 100, left: 120 },
    width = 1000 - margin.left - margin.right,
    height = 700 - margin.top - margin.bottom;

  const svg = d3
    .select(svgEl)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  if (!data.value.length) return;

  const categories = ["Protected", "Non-protected", "Transit / Other"];
  const color = d3
    .scaleOrdinal()
    .domain(categories)
    .range(["#e11d48", "#2196F3", "#9E9E9E"]);

  const x = d3.scalePoint()
    .domain([...new Set(data.value.map((d) => d.vessel_name))])
    .range([0, width])
    .padding(0.5);

  const y = d3.scalePoint()
    .domain([...new Set(data.value.map((d) => d.location_name))])
    .range([height, 0])
    .padding(0.5);

  const r = d3.scaleSqrt()
    .domain([0, d3.max(data.value, (d) => d.dwell)])
    .range([3, 30]);

  // Tooltip
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

  const pointsGroup = svg.append("g").attr("class", "points");

  function updatePoints(activeCategories) {
    const filtered = data.value.filter((d) => activeCategories.has(d.area_type));

    const circles = pointsGroup
      .selectAll("circle")
      .data(filtered, (d) => d.vessel_name + d.location_name);

    circles.join(
      (enter) =>
        enter
          .append("circle")
          .attr("cx", (d) => x(d.vessel_name))
          .attr("cy", (d) => y(d.location_name))
          .attr("r", (d) => r(d.dwell))
          .attr("fill", (d) => color(d.area_type))
          .attr("opacity", 0.8)
          .on("mouseover", (event, d) => {
            tooltip.transition().duration(150).style("opacity", 1);
            tooltip
              .html(`
                <strong>${d.vessel_name}</strong><br/>
                Location: ${d.location_name}<br/>
                Dwell: ${d.dwell.toFixed(1)}<br/>
                Area: ${d.area_type}<br/>
                Tonnage: ${d.tonnage || "N/A"}<br/>
                Arrived: ${d.arrival_time}
              `)
              .style("left", `${event.pageX + 10}px`)
              .style("top", `${event.pageY - 28}px`);
          })
          .on("mouseout", () =>
            tooltip.transition().duration(200).style("opacity", 0)
          ),
      (update) => update,
      (exit) => exit.remove()
    );
  }

  const activeCategories = new Set(categories);
  updatePoints(activeCategories);

  // Axes
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "11px");

  svg
    .append("g")
    .call(d3.axisLeft(y).tickSize(0))
    .selectAll("text")
    .style("font-size", "11px");

  // Title
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", -30)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(
      `Vessels and Dwell Time — ${selectedPort.value} (${selectedDate.value})`
    );

  // --- LEGEND ---
  const legend = svg
    .append("g")
    .attr("class", "legend")
    .attr("transform", `translate(${width + 20}, 20)`);

  legend
    .selectAll("rect")
    .data(categories)
    .join("rect")
    .attr("x", 0)
    .attr("y", (_, i) => i * 25)
    .attr("width", 16)
    .attr("height", 16)
    .attr("fill", (d) => color(d))
    .attr("stroke", "#333")
    .attr("stroke-width", 0.5)
    .style("cursor", "pointer")
    .on("click", function (event, d) {
      if (activeCategories.has(d)) {
        activeCategories.delete(d);
        d3.select(this).attr("opacity", 0.3);
      } else {
        activeCategories.add(d);
        d3.select(this).attr("opacity", 1);
      }
      updatePoints(activeCategories);
    });

  legend
    .selectAll("text")
    .data(categories)
    .join("text")
    .attr("x", 25)
    .attr("y", (_, i) => i * 25 + 12)
    .text((d) => d)
    .style("font-size", "12px")
    .style("cursor", "pointer")
    .on("click", function (event, d) {
      const rect = legend.selectAll("rect").filter((dd) => dd === d);
      if (activeCategories.has(d)) {
        activeCategories.delete(d);
        rect.attr("opacity", 0.3);
      } else {
        activeCategories.add(d);
        rect.attr("opacity", 1);
      }
      updatePoints(activeCategories);
    });
}
</script>

<template>
  <div class="vessel-dwell-scatter">
    <EmptyStateMessage
      v-if="!hasData"
      title="No vessel activity"
      :description="selectedPort && selectedDate
        ? `We couldn’t find routes arriving at ${selectedPort} on ${selectedDate}.`
        : 'Select a port and date to load arrivals.'"
    />
    <svg v-else ref="chartRef"></svg>
  </div>
</template>

<style scoped>
.vessel-dwell-scatter {
  width: 100%;
  overflow-x: auto;
  text-align: center;
}

</style>
