// src/services/api.js
const API_BASE_URL = "http://127.0.0.1:8000";

export async function getDailyView(port, date) {
  const res = await fetch(`${API_BASE_URL}/api/daily_view?port=${encodeURIComponent(port)}&date=${date}`);
  if (!res.ok) throw new Error("API request failed");
  return await res.json();
}

export async function getPorts() {
  const res = await fetch(`${API_BASE_URL}/api/ports`);
  return await res.json();
}

export async function getDates() {
  const res = await fetch(`${API_BASE_URL}/api/dates`);
  return await res.json();
}
