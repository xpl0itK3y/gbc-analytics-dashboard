<template>
  <div class="card">
    <div class="card-header">
      <h2>Recent Orders</h2>
    </div>
    <div class="table-responsive">
      <table v-if="orders.length">
        <thead>
          <tr>
            <th>Order Number</th>
            <th>M/D</th>
            <th>Customer</th>
            <th>City</th>
            <th>Total Sum</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td class="font-medium">#{{ order.number }}</td>
            <td class="text-muted">{{ formatDate(order.created_at) }}</td>
            <td>{{ order.first_name }} {{ order.last_name }}</td>
            <td>{{ order.city || '—' }}</td>
            <td class="font-medium">{{ order.total.toLocaleString() }} ₸</td>
            <td>
              <span class="badge" :class="order.status.toLowerCase()">
                {{ order.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <p>No orders currently available. Wait for a sync!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchOrders } from '../services/api'

const orders = ref([])

onMounted(async () => {
  try {
    orders.value = await fetchOrders(15) // fetch 15 most recent
  } catch(e) {
    console.error("Orders load error:", e)
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr)
  return `${d.getMonth()+1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.table-responsive {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
th, td {
  padding: 1rem 1.2rem;
  border-bottom: 1px solid var(--border-color);
}
th {
  font-weight: 500;
  color: var(--text-muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
tbody tr:last-child td {
  border-bottom: none;
}
tbody tr {
  transition: background-color 0.2s ease;
}
tbody tr:hover {
  background-color: var(--hover-bg);
}
.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}
</style>
