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
                {{ formatStatus(order.status) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <p>Заказы пока не загружены. Дождитесь синхронизации.</p>
      </div>

      <div class="load-more-container" v-if="orders.length > 0">
        <button 
          class="btn-load-more" 
          @click="$emit('load-more')" 
          :disabled="isLoadingMore || !hasMore"
          :class="{ 'btn-complete': !hasMore }"
        >
          <span v-if="isLoadingMore" class="spinner"></span>
          <span>{{ buttonText }}</span>
        </button>
        <div v-if="!hasMore" class="pagination-info">
          Показано {{ orders.length }} из {{ totalOrders }} заказов. Все данные загружены.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  orders: {
    type: Array,
    required: true
  },
  totalOrders: {
    type: Number,
    default: 0
  },
  isLoadingMore: {
    type: Boolean,
    default: false
  }
})

const hasMore = computed(() => props.orders.length < props.totalOrders)

const buttonText = computed(() => {
  if (props.isLoadingMore) return 'Загрузка...'
  return hasMore.value ? 'Показать больше' : 'Все заказы загружены'
})

defineEmits(['load-more'])

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr)
  return `${d.getMonth()+1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const STATUS_LABELS = {
  'new': 'Новый',
  'offer-analog': 'Предложить аналог',
  'prepay-await': 'Ожидает предоплату',
  'prepay-success': 'Предоплата получена',
  'send-to-delivery': 'Передан в доставку',
  'delivering': 'Доставляется',
  'complete': 'Выполнен',
  'cancelled': 'Отменен',
  'return': 'Возврат'
}

function formatStatus(value) {
  if (!value) return '—'
  const techValue = value.toLowerCase()
  return STATUS_LABELS[techValue] || value
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
.load-more-container {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-top: 1px solid var(--border-color);
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
}
.btn-load-more {
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
.btn-load-more:hover:not(:disabled) {
  background-color: #f0fdfa;
  border-color: #0f766e;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(15, 118, 110, 0.08);
}
.btn-load-more:active:not(:disabled) {
  transform: translateY(0);
}
.btn-load-more.btn-complete {
  background: #f1f5f9;
  border-color: #e2e8f0;
  color: #94a3b8;
  cursor: default;
}
.btn-load-more.btn-complete:hover {
  background: #f1f5f9;
  transform: none;
  box-shadow: none;
}
.pagination-info {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
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
