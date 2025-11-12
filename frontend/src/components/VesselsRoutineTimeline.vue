<script setup>
import * as d3 from "d3";
import { ref, onMounted, watch } from "vue";
import { selectedVessel } from "@/stores/usefilters.js";
import EmptyStateMessage from "@/components/EmptyStateMessage.vue";

const chartRef = ref(null);
const data = ref([]);
const comparisonData = ref([]);
const hasData = ref(true);
const compareMode = ref(false);

const comparisonVessel = "snappersnatcher7be";

async function fetchData(vessel) {
  const res = await fetch(
    `http://127.0.0.1:8000/api/vessel_routine_view?vessel=${encodeURIComponent(vessel)}`
  );
  const json = await res.json();
  return (json.segments || []).map((d) => ({
    source: d.source,
    kind: d.kind,
    start: new Date(d.start),
    end: new Date(d.end),
  }));
}

async function refreshData() {
  if (!selectedVessel.value) return;

  data.value = await fetchData(selectedVessel.value);
  hasData.value = data.value.length > 0;

  if (compareMode.value) {
    comparisonData.value = await fetchData(comparisonVessel);
  } else {
    comparisonData.value = [];
  }

  renderChart();
}

// === D3 Visualization ===
function renderChart() {
  const svgEl = chartRef.value;
  d3.select(svgEl).selectAll("*").remove();
  if (!hasData.value) return;

  const margin = { top: 50, right: 160, bottom: 80, left: 180 },
    width = 1000 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

  const svg = d3
    .select(svgEl)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const allData = compareMode.value
    ? [
        ...data.value.map((d) => ({ ...d, series: "selected" })),
        ...comparisonData.value.map((d) => ({ ...d, series: "comparison" })),
      ]
    : data.value.map((d) => ({ ...d, series: "selected" }));

  const kinds = (() => {
    const detected = Array.from(new Set(allData.map((d) => d.kind))).filter(Boolean);
    return detected.length ? detected : ["Other"];
  })();
  const fixedColors = {
    Protected: "#ef4444",
    "Transit / Other": "#94a3b8",
  };
  const palette = ["#22c55e", "#0ea5e9", "#6366f1", "#f97316", "#10b981"];
  const assignedColors = kinds.map(
    (kind, idx) => fixedColors[kind] || palette[idx % palette.length]
  );
  const color = d3
    .scaleOrdinal()
    .domain(kinds)
    .range(assignedColors);

  const activeKinds = new Set(kinds);

  const xDomain = d3.extent(allData.flatMap((d) => [d.start, d.end]));
  if (!xDomain[0] || !xDomain[1]) return;

  const baseX = d3.scaleTime().domain(xDomain).range([0, width]);
  const xScale = baseX.copy();

  const y = d3
    .scaleBand()
    .domain([...new Set(allData.map((d) => d.source))])
    .range([0, height])
    .padding(0.2);

  const gBars = svg.append("g").attr("class", "bars");
  const xAxisGroup = svg.append("g").attr("transform", `translate(0,${height})`);

  function drawXAxis(scale = xScale) {
    xAxisGroup.call(d3.axisBottom(scale).ticks(6));
    xAxisGroup
      .selectAll("text")
      .attr("transform", "rotate(-35)")
      .style("text-anchor", "end")
      .style("font-size", "11px");
  }

  function updateBars(scale = xScale) {
    const filtered = allData.filter((d) => activeKinds.has(d.kind));

    const bars = gBars
      .selectAll("rect")
      .data(filtered, (d) => d.source + d.start + d.series);

    bars.join(
      (enter) =>
        enter
          .append("rect")
          .attr("x", (d) => scale(d.start))
          .attr("y", (d) => y(d.source))
          .attr("width", (d) => scale(d.end) - scale(d.start))
          .attr("height", y.bandwidth())
          .attr("fill", (d) =>
            d.series === "comparison" ? d3.color(color(d.kind)).brighter(1.2) : color(d.kind)
          )
          .attr("stroke", (d) => (d.series === "comparison" ? color(d.kind) : "none"))
          .attr("stroke-dasharray", (d) => (d.series === "comparison" ? "4,2" : null))
          .attr("rx", 2)
          .attr("ry", 2)
          .attr("opacity", (d) => (d.series === "comparison" ? 0.6 : 1))
          .append("title")
          .text(
            (d) =>
              `${d.source}\n${d.kind}\n${d.start.toLocaleString()} → ${d.end.toLocaleString()}`
          ),
      (update) =>
        update
          .attr("x", (d) => scale(d.start))
          .attr("width", (d) => scale(d.end) - scale(d.start)),
      (exit) => exit.remove()
    );
  }

  updateBars();
  drawXAxis();

  svg.append("g").call(d3.axisLeft(y)).selectAll("text").style("font-size", "11px");

  const zoomBehavior = d3
    .zoom()
    .scaleExtent([1, 24])
    .translateExtent([
      [0, 0],
      [width, height],
    ])
    .extent([
      [0, 0],
      [width, height],
    ])
    .filter((event) => {
      const [xPos, yPos] = d3.pointer(event, svgEl);
      return (
        xPos >= margin.left &&
        xPos <= margin.left + width &&
        yPos >= margin.top &&
        yPos <= margin.top + height
      );
    })
    .on("zoom", (event) => {
      const newX = event.transform.rescaleX(baseX);
      xScale.domain(newX.domain());
      updateBars(xScale);
      drawXAxis(xScale);
    });

  d3.select(svgEl).call(zoomBehavior);

  // Title
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", -15)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(
      compareMode.value
        ? `Routine Comparison — ${selectedVessel.value} vs ${comparisonVessel}`
        : `Routine Timeline — ${selectedVessel.value}`
    );

  // === LEGEND ===
  const legend = svg.append("g").attr("transform", `translate(${width + 25}, 10)`);

  const legendItems = legend
    .selectAll("g")
    .data(kinds)
    .join("g")
    .attr("transform", (_, i) => `translate(0, ${i * 26})`)
    .style("cursor", "pointer")
    .on("click", function (_, kind) {
      if (activeKinds.has(kind)) {
        activeKinds.delete(kind);
        d3.select(this).select("rect").attr("opacity", 0.3);
      } else {
        activeKinds.add(kind);
        d3.select(this).select("rect").attr("opacity", 1);
      }
      updateBars(xScale);
    });

  legendItems
    .append("rect")
    .attr("width", 16)
    .attr("height", 16)
    .attr("rx", 3)
    .attr("ry", 3)
    .attr("fill", (d) => color(d))
    .attr("opacity", 1);

  legendItems
    .append("text")
    .attr("x", 22)
    .attr("y", 12)
    .text((d) => d)
    .style("font-size", "12px")
    .style("fill", "#334155");
}

onMounted(refreshData);
watch([selectedVessel, compareMode], refreshData);
</script>

<template>
  <div class="vessel-timeline">
    <div class="timeline-header">
      <label>
        <input type="checkbox" v-model="compareMode" />
        Compare with <strong>snappersnatcher7be (SouthSeafood Express Corp)</strong>
      </label>
    </div>

    <EmptyStateMessage
      v-if="!hasData"
      title="No vessel activity"
      :description="selectedVessel
        ? `We couldn’t reconstruct a route for ${selectedVessel}.`
        : 'Select a vessel to inspect its timeline.'"
    />
    <svg v-else ref="chartRef"></svg>
  </div>
</template>

<style scoped>
.vessel-timeline {
  width: 100%;
  text-align: center;
  overflow-x: auto;
}

.timeline-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
  color: #334155;
}

.timeline-header input[type="checkbox"] {
  transform: scale(1.1);
  accent-color: #0e7490;
}
</style>
