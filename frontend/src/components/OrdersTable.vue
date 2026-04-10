<template>
  <div class="card">
    <div class="card-header">
      <h2>Последние заказы</h2>
    </div>
    <div class="table-responsive">
      <table v-if="orders.length">
        <thead>
          <tr>
            <th>Номер</th>
            <th>Дата</th>
            <th>Клиент</th>
            <th>Город</th>
            <th>Сумма</th>
            <th>Статус</th>
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
        <p>Заказы пока не загружены. Дождитесь синхронизации.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  orders: {
    type: Array,
    default: () => []
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
  padding: 1.15rem 1.45rem;
  border-bottom: 1px solid var(--border-color);
}
th {
  font-weight: 500;
  color: var(--text-muted);
  font-size: 0.92rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
td {
  font-size: 1rem;
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
  padding: 2.5rem;
  text-align: center;
  color: var(--text-muted);
}
</style>
