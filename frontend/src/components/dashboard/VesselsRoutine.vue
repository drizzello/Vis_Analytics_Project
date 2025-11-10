<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as d3 from "d3";

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    selectedVessel: {
        type: String,
        default: null,
    },
    indexLoading: {
        type: Boolean,
        default: false,
    },
    indexError: {
        type: String,
        default: null,
    },
    dataLoading: {
        type: Boolean,
        default: false,
    },
    dataError: {
        type: String,
        default: null,
    },
    compareEnabled: {
        type: Boolean,
        default: false,
    },
    comparisonData: {
        type: Array,
        default: () => [],
    },
    comparisonLabel: {
        type: String,
        default: "",
    },
    comparisonError: {
        type: String,
        default: null,
    },
    comparisonLoading: {
        type: Boolean,
        default: false,
    },
});

const timeline = ref(null);
let resizeObserver = null;

const colorMap = Object.freeze({
    "Fishing Ground": "#22c55e",
    buoy: "#0ea5e9",
    city: "#6366f1",
    "Ecological Preserve": "#f97316",
    harbor: "#0ea5e9",
    default: "#9ca3af",
});

const cleanup = () => {
    if (timeline.value) {
        d3.select(timeline.value).selectAll("*").remove();
    }
};

const buildSegments = () => {
    const segments = [];

    const pushSegments = (items, series, label) => {
        (items ?? []).forEach((item) => {
            const startDate = new Date(item.start);
            const endDate = new Date(item.end);

            if (Number.isNaN(startDate.valueOf()) || Number.isNaN(endDate.valueOf())) {
                return;
            }

            segments.push({
                ...item,
                startDate,
                endDate,
                kind: item.kind || "Unknown",
                vessel: label,
                series,
            });
        });
    };

    pushSegments(props.data, "primary", props.selectedVessel ?? "Selected vessel");

    if (props.compareEnabled && !props.comparisonLoading) {
        pushSegments(props.comparisonData, "comparison", props.comparisonLabel || "Comparison vessel");
    }

    return segments.sort((a, b) => d3.ascending(a.startDate, b.startDate));
};

const renderChart = () => {
    if (!timeline.value) return;

    cleanup();

    if (!props.selectedVessel || props.dataLoading) {
        return;
    }

    const segments = buildSegments();

    if (!segments.length) {
        return;
    }

    const seriesList = [];
    const seriesLabelMap = new Map();
    for (const segment of segments) {
        if (!seriesList.includes(segment.series)) {
            seriesList.push(segment.series);
        }
        if (!seriesLabelMap.has(segment.series)) {
            seriesLabelMap.set(segment.series, segment.vessel);
        }
    }
    const seriesCount = seriesList.length;

    const legendData = Array.from(
        segments.reduce((map, item) => {
            if (!map.has(item.kind)) {
                map.set(item.kind, colorMap[item.kind] || colorMap.default);
            }
            return map;
        }, new Map())
    );

    const root = d3.select(timeline.value);

    const containerWidth = timeline.value.clientWidth || 800;
    const legendReservedWidth = legendData.length ? 220 : 0;
    const gapWidth = legendData.length ? 24 : 0;
    const chartAreaWidth = Math.max(containerWidth - legendReservedWidth - gapWidth, 320);

    const margin = { top: 56, right: 24, bottom: 60, left: 160 };
    const rowHeight = 26;
    const sources = Array.from(new Set(segments.map((d) => d.source))).sort((a, b) =>
        a.localeCompare(b)
    );
    const height = Math.max(margin.top + margin.bottom + sources.length * rowHeight, 320);
    const width = Math.max(chartAreaWidth, margin.left + margin.right + 200);

    const xDomain = d3.extent(
        segments.flatMap((d) => [d.startDate, d.endDate]),
        (d) => d
    );

    if (!xDomain[0] || !xDomain[1]) {
        return;
    }

    const xScale = d3.scaleTime().domain(xDomain).range([margin.left, width - margin.right]);

    const yScale = d3
        .scaleBand()
        .domain(sources)
        .range([margin.top, height - margin.bottom])
        .paddingInner(0.4);

    const svg = root
        .append("svg")
        .attr("class", "timeline-svg")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet");

    const chartGroup = svg.append("g");

    // Horizontal grid lines
    chartGroup
        .append("g")
        .attr("stroke", "var(--p-surface-200)")
        .attr("stroke-opacity", 0.5)
        .selectAll("line")
        .data(sources)
        .join("line")
        .attr("x1", margin.left)
        .attr("x2", width - margin.right)
        .attr("y1", (d) => (yScale(d) ?? margin.top) + yScale.bandwidth() / 2)
        .attr("y2", (d) => (yScale(d) ?? margin.top) + yScale.bandwidth() / 2);

    const offsetForSeries = (series) => {
        if (seriesCount <= 1) return 0;
        const idx = seriesList.indexOf(series);
        return ((idx - (seriesCount - 1) / 2) * yScale.bandwidth()) / 2.5;
    };

    // Timeline segments
    chartGroup
        .append("g")
        .attr("stroke-linecap", "round")
        .attr("stroke-width", 8)
        .selectAll("line")
        .data(segments)
        .join("line")
        .attr("x1", (d) => xScale(d.startDate))
        .attr("x2", (d) => xScale(d.endDate))
        .attr("y1", (d) => (yScale(d.source) ?? margin.top) + yScale.bandwidth() / 2 + offsetForSeries(d.series))
        .attr("y2", (d) => (yScale(d.source) ?? margin.top) + yScale.bandwidth() / 2 + offsetForSeries(d.series))
        .attr("stroke", (d) => colorMap[d.kind] || colorMap.default)
        .attr("stroke-dasharray", (d) => (d.series === "comparison" ? "6,3" : null))
        .attr("stroke-opacity", (d) => (d.series === "comparison" ? 0.75 : 1))
        .append("title")
        .text(
            (d) =>
                `${d.target}\n${d.kind}\n${d.startDate.toLocaleString()} → ${d.endDate.toLocaleString()}\n${d.source}\n${d.vessel}`
        );

    // X axis
    chartGroup
        .append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(
            d3
                .axisBottom(xScale)
                .ticks(Math.max(width / 130, 2))
                .tickSizeOuter(0)
        )
        .call((g) => g.selectAll("text").style("font-size", "0.75rem"))
        .call((g) =>
            g
                .append("text")
                .attr("x", width - margin.right)
                .attr("y", 40)
                .attr("fill", "currentColor")
                .attr("text-anchor", "end")
                .style("font-size", "0.85rem")
                .text("Time")
        );

    // Y axis
    chartGroup
        .append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(yScale).tickSize(0).tickPadding(10))
        .call((g) => g.select(".domain").remove())
        .call((g) => g.selectAll("text").style("font-size", "0.8rem"));

    if (legendData.length) {
        const legend = root
            .append("div")
            .attr("class", "timeline-legend");

        const typeSection = legend.append("div").attr("class", "timeline-legend-section");

        typeSection.append("span").attr("class", "timeline-legend-title").text("Activity types");

        const typeItems = typeSection
            .append("div")
            .attr("class", "timeline-legend-group")
            .selectAll("div")
            .data(legendData)
            .join("div")
            .attr("class", "timeline-legend-item");

        typeItems
            .append("span")
            .attr("class", "timeline-legend-swatch")
            .style("background-color", (d) => d[1]);

        typeItems
            .append("span")
            .attr("class", "timeline-legend-label")
            .text((d) => d[0]);

        if (seriesCount > 1) {
            const seriesSection = legend.append("div").attr("class", "timeline-legend-section");

            seriesSection.append("span").attr("class", "timeline-legend-title").text("Series");

            const seriesItems = seriesSection
                .append("div")
                .attr("class", "timeline-legend-group")
                .selectAll("div")
                .data(
                    seriesList.map((series) => ({
                        series,
                        label: seriesLabelMap.get(series) ?? (series === "primary" ? "Primary" : "Comparison"),
                    }))
                )
                .join("div")
                .attr("class", "timeline-legend-item");

            seriesItems
                .append("span")
                .attr(
                    "class",
                    (d) =>
                        [
                            "timeline-legend-series-indicator",
                            d.series === "comparison" ? "comparison" : "primary",
                        ].join(" ")
                );

            seriesItems
                .append("span")
                .attr("class", "timeline-legend-label")
                .text((d) => d.label);
        }
    }
};

const scheduleRender = () => {
    if (props.dataLoading) {
        cleanup();
        return;
    }
    nextTick(() => renderChart());
};

watch(
    () => props.data,
    () => {
        scheduleRender();
    },
    { deep: true }
);

watch(
    () => props.selectedVessel,
    (value) => {
        if (!value) {
            cleanup();
        } else {
            scheduleRender();
        }
    }
);

watch(
    () => props.dataLoading,
    (loading) => {
        if (loading) {
            cleanup();
        } else {
            scheduleRender();
        }
    }
);

watch(
    () => props.compareEnabled,
    () => {
        scheduleRender();
    }
);

watch(
    () => props.comparisonData,
    () => {
        scheduleRender();
    },
    { deep: true }
);

watch(
    () => props.comparisonLoading,
    (loading) => {
        if (!loading) {
            scheduleRender();
        }
    }
);

watch(
    () => timeline.value,
    (el, prev) => {
        if (prev && resizeObserver) {
            resizeObserver.unobserve(prev);
        }
        if (!el) {
            return;
        }

        if (typeof ResizeObserver === "undefined") {
            renderChart();
            return;
        }

        if (!resizeObserver) {
            resizeObserver = new ResizeObserver(() => renderChart());
        }
        resizeObserver.observe(el);
        renderChart();
    }
);

onMounted(() => {
    if (timeline.value) {
        renderChart();
    }
});

onBeforeUnmount(() => {
    cleanup();
    if (resizeObserver) {
        resizeObserver.disconnect();
    }
});
</script>

<template>
    <div class="layout-card layout-card-full">
        <div class="chart-header">
            <span class="chart-title">Vessel Routine</span>
        </div>

        <div class="chart-content">
            <div v-if="indexLoading" class="chart-status">Loading vessels…</div>
            <div v-else-if="indexError" class="chart-status chart-status--error">{{ indexError }}</div>
            <div v-else-if="!selectedVessel" class="chart-status">Select a vessel to view its routine.</div>
            <div v-else-if="dataLoading" class="chart-status">Loading data…</div>
            <div v-else-if="dataError" class="chart-status chart-status--error">{{ dataError }}</div>
            <div v-else-if="!data.length" class="chart-status">
                No data available for {{ selectedVessel }}.
            </div>
            <template v-else>
                <div ref="timeline" class="timeline-chart"></div>
                <div v-if="compareEnabled">
                    <div v-if="comparisonLoading" class="chart-status small">Loading comparison data…</div>
                    <div v-else-if="comparisonError" class="chart-status chart-status--error small">
                        {{ comparisonError }}
                    </div>
                    <div v-else-if="!comparisonData.length" class="chart-status small">
                        No data available for {{ comparisonLabel }}.
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>
