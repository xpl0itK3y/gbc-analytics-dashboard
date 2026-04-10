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

      <div class="table-footer" v-if="orders.length">
        <button 
          class="load-more-btn" 
          @click="$emit('load-more')"
          :disabled="isLoadingMore"
        >
          <span v-if="isLoadingMore" class="spinner"></span>
          {{ isLoadingMore ? 'Загрузка...' : 'Показать больше' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  orders: {
    type: Array,
    default: () => []
  },
  isLoadingMore: {
    type: Boolean,
    default: false
  }
})

defineEmits(['load-more'])

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
.table-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
}
.load-more-btn {
  padding: 0.75rem 1.5rem;
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f766e;
  background-color: #ffffff;
  border: 1px solid rgba(15, 118, 110, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.load-more-btn:hover:not(:disabled) {
  background-color: #f0fdfa;
  border-color: #0f766e;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(15, 118, 110, 0.08);
}
.load-more-btn:active:not(:disabled) {
  transform: translateY(0);
}
.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(15, 118, 110, 0.2);
  border-top-color: #0f766e;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
