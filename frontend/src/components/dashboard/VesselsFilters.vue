<script setup>
import Dropdown from "primevue/dropdown";
import Calendar from "primevue/calendar";
import InputSwitch from "primevue/inputswitch";

const props = defineProps({
    vesselOptions: {
        type: Array,
        default: () => [],
    },
    selectedVessel: {
        type: String,
        default: null,
    },
    startDate: {
        type: Date,
        default: null,
    },
    endDate: {
        type: Date,
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
    hasData: {
        type: Boolean,
        default: false,
    },
    compareEnabled: {
        type: Boolean,
        default: false,
    },
    comparisonLabel: {
        type: String,
        default: "",
    },
});

const emit = defineEmits([
    "update:selectedVessel",
    "update:startDate",
    "update:endDate",
    "update:compareEnabled",
]);

const onVesselChange = (value) => {
    emit("update:selectedVessel", value);
};

const onStartDateChange = (value) => {
    emit("update:startDate", value ?? null);
};

const onEndDateChange = (value) => {
    emit("update:endDate", value ?? null);
};

const onCompareChange = (value) => {
    emit("update:compareEnabled", value ?? false);
};
</script>

<template>
    <div class="chart-filters layout-card-full">
        <Dropdown
            :modelValue="selectedVessel"
            :options="vesselOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select a vessel"
            class="chart-dropdown"
            showClear
            :disabled="indexLoading"
            @update:modelValue="onVesselChange"
        />
        <div class="chart-calendar-group">
            <Calendar
                :modelValue="startDate"
                showIcon
                iconDisplay="input"
                dateFormat="yy-mm-dd"
                class="chart-calendar"
                :disabled="dataLoading || !hasData"
                :maxDate="endDate"
                placeholder="Start date"
                showButtonBar
                @update:modelValue="onStartDateChange"
            />
            <Calendar
                :modelValue="endDate"
                showIcon
                iconDisplay="input"
                dateFormat="yy-mm-dd"
                class="chart-calendar"
                :disabled="dataLoading || !hasData"
                :minDate="startDate"
                placeholder="End date"
                showButtonBar
                @update:modelValue="onEndDateChange"
            />
        </div>
        <div class="chart-toggle-group">
            <span class="chart-toggle-label">Compare with {{ comparisonLabel }}</span>
            <InputSwitch
                :modelValue="compareEnabled"
                :disabled="!selectedVessel"
                @update:modelValue="onCompareChange"
            />
        </div>
        <span v-if="indexError" class="chart-status chart-status--error small">
            {{ indexError }}
        </span>
    </div>
</template>
