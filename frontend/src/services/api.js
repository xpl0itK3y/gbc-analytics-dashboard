const API_BASE = "http://localhost:8000";

export async function fetchStats() {
  const response = await fetch(`${API_BASE}/stats/`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
}

export async function fetchOrders(limit = 100) {
  const response = await fetch(`${API_BASE}/orders/?limit=${limit}`);
  if (!response.ok) throw new Error("Failed to fetch orders");
  return response.json();
}
