const API_BASE = "/api";

export async function fetchStats() {
  const response = await fetch(`${API_BASE}/stats/`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
}

export async function fetchOrders(limit = 15, offset = 0) {
  const response = await fetch(`${API_BASE}/orders/?limit=${limit}&offset=${offset}`);
  if (!response.ok) throw new Error("Failed to fetch orders");
  return response.json();
}
