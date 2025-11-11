// src/stores/useFilters.js
import { ref } from "vue";

export const ports = ref([]);
export const dates = ref([]);
export const vessels = ref([]);        // 🆕 available vessels
export const selectedPort = ref("");
export const selectedDate = ref("");
export const selectedVessel = ref(""); // 🆕 current vessel

export async function fetchFilters() {
  const [pRes, dRes, vRes] = await Promise.all([
    fetch("http://127.0.0.1:8000/api/ports"),
    fetch("http://127.0.0.1:8000/api/dates"),
    fetch("http://127.0.0.1:8000/api/vessels") // 🆕 endpoint for vessel list
  ]);

  const portsJson = await pRes.json();
  const datesJson = await dRes.json();
  const vesselsJson = await vRes.json();

  ports.value = portsJson.ports || [];
  dates.value = datesJson.dates || [];
  vessels.value = vesselsJson.vessels || [];

  // --- Default values ---
  selectedPort.value = ports.value[0] || "";
  selectedDate.value = dates.value[0] || "";
  selectedVessel.value = vessels.value[0] || ""; 
}
