<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";

const sankeyContainer = ref(null);
const rawData = ref([]);
const loading = ref(true);
const error = ref(null);

let resizeObserver = null;

const fetchData = async () => {
    loading.value = true;
    error.value = null;

    try {
        const response = await fetch(`${import.meta.env.BASE_URL}data/fish_locations.json`);
        if (!response.ok) {
            throw new Error(`Failed to load fish locations (${response.status})`);
        }

        const payload = await response.json();
        rawData.value = Array.isArray(payload) ? payload : [];
    } catch (err) {
        console.error(err);
        error.value = err instanceof Error ? err.message : "Unexpected error while loading data.";
        rawData.value = [];
    } finally {
        loading.value = false;
    }
};

const sankeyData = computed(() => {
    if (!rawData.value.length) {
        return { nodes: [], links: [] };
    }

    const entries = rawData.value.map((item) => ({
        entity: item.entity_name,
        locationLabel: `${item.location_id} (${item.kind})`,
    }));

    const counts = entries.reduce((map, item) => {
        const key = `${item.entity}__${item.locationLabel}`;
        map.set(key, (map.get(key) || 0) + 1);
        return map;
    }, new Map());

    const nodeNames = Array.from(
        new Set(entries.flatMap((item) => [item.entity, item.locationLabel]))
    );
    const nodeIndex = new Map(nodeNames.map((name, idx) => [name, idx]));

    const links = Array.from(counts.entries()).map(([key, value]) => {
        const [entity, locationLabel] = key.split("__");
        return {
            source: nodeIndex.get(entity),
            target: nodeIndex.get(locationLabel),
            value,
        };
    });

    return {
        nodes: nodeNames.map((name) => ({ name })),
        links,
    };
});

const cleanup = () => {
    if (sankeyContainer.value) {
        sankeyContainer.value.innerHTML = "";
    }
};

const renderSankey = () => {
    if (!sankeyContainer.value || !sankeyData.value.nodes.length) {
        cleanup();
        return;
    }

    cleanup();

    const containerWidth = sankeyContainer.value.clientWidth || 800;
    const height = 600;
    const margin = { top: 24, right: 24, bottom: 24, left: 24 };

    const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

    const sankeyGenerator = sankey()
        .nodeWidth(18)
        .nodePadding(16)
        .extent([
            [margin.left, margin.top],
            [containerWidth - margin.right, height - margin.bottom],
        ]);

    const graph = sankeyGenerator({
        nodes: sankeyData.value.nodes.map((node) => ({ ...node })),
        links: sankeyData.value.links.map((link) => ({ ...link })),
    });

    const svg = d3
        .select(sankeyContainer.value)
        .append("svg")
        .attr("viewBox", `0 0 ${containerWidth} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .attr("class", "sankey-svg");

    const linkGroup = svg.append("g").attr("fill", "none");

    linkGroup
        .selectAll("path")
        .data(graph.links)
        .join("path")
        .attr("d", sankeyLinkHorizontal())
        .attr("stroke", (d) => colorScale(d.source.name))
        .attr("stroke-opacity", 0.35)
        .attr("stroke-width", (d) => Math.max(1, d.width))
        .append("title")
        .text((d) => `${d.source.name} → ${d.target.name}\n${d.value}`);

    const nodeGroup = svg.append("g");

    const node = nodeGroup
        .selectAll("g")
        .data(graph.nodes)
        .join("g")
        .attr("transform", (d) => `translate(${d.x0}, ${d.y0})`);

    node
        .append("rect")
        .attr("height", (d) => Math.max(1, d.y1 - d.y0))
        .attr("width", (d) => Math.max(1, d.x1 - d.x0))
        .attr("fill", (d) => colorScale(d.name))
        .attr("fill-opacity", 0.8)
        .append("title")
        .text((d) => `${d.name}\n${d.value}`);

    node
        .append("text")
        .attr("x", (d) => (d.x0 < containerWidth / 2 ? d.x1 - d.x0 + 6 : -6))
        .attr("y", (d) => (d.y1 - d.y0) / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", (d) => (d.x0 < containerWidth / 2 ? "start" : "end"))
        .attr("fill", "currentColor")
        .style("font-size", "0.75rem")
        .text((d) => d.name);
};

const scheduleRender = () => {
    nextTick(() => {
        renderSankey();
    });
};

watch(
    () => sankeyData.value,
    () => {
        if (!loading.value) {
            scheduleRender();
        }
    },
    { deep: true }
);

watch(
    () => sankeyContainer.value,
    (el, prev) => {
        if (prev && resizeObserver) {
            resizeObserver.unobserve(prev);
        }

        if (!el) {
            return;
        }

        if (typeof ResizeObserver === "undefined") {
            renderSankey();
            return;
        }

        if (!resizeObserver) {
            resizeObserver = new ResizeObserver(() => renderSankey());
        }

        resizeObserver.observe(el);
        renderSankey();
    }
);

onMounted(async () => {
    await fetchData();
    scheduleRender();
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
            <span class="chart-title">Which Fish are illegals? Fish → Locations Sankey</span>
        </div>
        <div class="chart-content">
            <div v-if="loading" class="chart-status">Loading sankey data…</div>
            <div v-else-if="error" class="chart-status chart-status--error">{{ error }}</div>
            <div v-else-if="!sankeyData.nodes.length" class="chart-status">
                No data available for the sankey visualization.
            </div>
            <div v-else ref="sankeyContainer" class="sankey-chart"></div>
        </div>
    </div>
</template>
