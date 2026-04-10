<template>
  <div class="layout-wrapper">
    <header class="app-header">
      <div class="container">
        <div class="header-brand">
          <h1>Панель GBC ⚡️</h1>
          <div class="live-status" :class="{ syncing: isRefreshing }">
            <span class="live-dot"></span>
            <span>{{ statusLabel }}</span>
          </div>
        </div>
        <div class="header-actions">
          <div class="stat-badge" v-if="summary">
             Выручка: <strong>{{ summary.total_revenue.toLocaleString() }} ₸</strong>
          </div>
          <div class="stat-badge" v-if="summary">
             Заказы: <strong>{{ summary.total_orders }}</strong>
          </div>
        </div>
      </div>
    </header>

    <main class="container main-content">
      <section class="hero-strip">
        <div class="hero-copy">
          <span class="hero-label">Операционный обзор</span>
          <h2>Продажи, статусы и каналы в одном окне</h2>
          <p>
            Дашборд обновляется автоматически и показывает текущую картину без ручной перезагрузки.
          </p>
        </div>
        <div class="hero-stats" v-if="dashboardMetrics">
          <div class="hero-stat">
            <span>Средний чек</span>
            <strong>{{ dashboardMetrics.averageCheck }}</strong>
          </div>
          <div class="hero-stat">
            <span>Крупных заказов</span>
            <strong>{{ dashboardMetrics.highValueOrders }}</strong>
          </div>
          <div class="hero-stat">
            <span>Топ город</span>
            <strong>{{ dashboardMetrics.topCity }}</strong>
          </div>
        </div>
      </section>

      <DashboardInsights :orders="orders" />

      <div class="grid-layout">
        <div class="chart-section">
          <OrdersChart :stats="stats" />
        </div>
      </div>
      <div class="table-section">
        <OrdersTable :orders="orders" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { fetchOrders, fetchStats } from './services/api'
import DashboardInsights from './components/DashboardInsights.vue'
import OrdersChart from './components/OrdersChart.vue'
import OrdersTable from './components/OrdersTable.vue'

const REFRESH_INTERVAL_MS = 15000

const stats = ref(null)
const orders = ref([])
const summary = ref(null)
const lastUpdatedAt = ref(null)
const isRefreshing = ref(false)
let refreshTimer = null

const statusLabel = computed(() => {
  if (!lastUpdatedAt.value) {
    return 'Подключение'
  }

  const time = lastUpdatedAt.value.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  })

  return isRefreshing.value ? 'Обновление...' : `Онлайн • ${time}`
})

const dashboardMetrics = computed(() => {
  if (!summary.value) {
    return null
  }

  const average = summary.value.total_orders
    ? Math.round(summary.value.total_revenue / summary.value.total_orders)
    : 0

  const highValueOrders = orders.value.filter((order) => Number(order.total) > 50000).length
  const cityCounts = orders.value.reduce((acc, order) => {
    const key = order.city || 'Не указан'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  const topCityEntry = Object.entries(cityCounts).sort((a, b) => b[1] - a[1])[0]

  return {
    averageCheck: `${average.toLocaleString()} ₸`,
    highValueOrders,
    topCity: topCityEntry ? topCityEntry[0] : 'Нет данных'
  }
})

async function refreshDashboard({ silent = false } = {}) {
  if (isRefreshing.value) {
    return
  }

  if (!silent) {
    isRefreshing.value = true
  }

  try {
    const [statsData, ordersData] = await Promise.all([
      fetchStats(),
      fetchOrders(15)
    ])

    stats.value = statsData
    summary.value = statsData.summary
    orders.value = ordersData
    lastUpdatedAt.value = new Date()
  } catch (e) {
    console.error('Dashboard refresh error:', e)
  } finally {
    isRefreshing.value = false
  }
}

onMounted(async () => {
  await refreshDashboard()
  refreshTimer = window.setInterval(() => {
    refreshDashboard({ silent: true })
  }, REFRESH_INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.layout-wrapper {
  min-height: 100vh;
  background-color: var(--bg-color);
}
.app-header {
  background-color: #ffffff;
  border-bottom: 1px solid var(--border-color);
  padding: 1.15rem 0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.app-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-brand {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.app-header h1 {
  font-size: 1.65rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.live-status {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.9rem;
  color: var(--text-muted);
  transition: opacity 0.2s ease;
}
.live-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: #14b8a6;
  box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.35);
}
.live-status.syncing .live-dot {
  animation: pulse 1.8s infinite;
}
.header-actions {
  display: flex;
  gap: 1rem;
}
.stat-badge {
  background-color: var(--bg-color);
  padding: 0.7rem 1.15rem;
  border-radius: 12px;
  font-size: 0.98rem;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
.main-content {
  padding: 2.4rem 0 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-strip {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.9rem 2rem;
  border: 1px solid rgba(15, 118, 110, 0.12);
  border-radius: 24px;
  background:
    radial-gradient(circle at right top, rgba(45, 212, 191, 0.16), transparent 25%),
    linear-gradient(135deg, #f8fffd 0%, #ffffff 50%, #f8fafc 100%);
}

.hero-copy h2 {
  margin: 0 0 0.55rem;
  font-size: 2.2rem;
  line-height: 1.15;
}

.hero-copy p {
  margin: 0;
  max-width: 44rem;
  color: var(--text-muted);
  line-height: 1.6;
  font-size: 1.02rem;
}

.hero-label {
  display: inline-block;
  margin-bottom: 0.65rem;
  padding: 0.45rem 0.82rem;
  border-radius: 9999px;
  background: rgba(20, 184, 166, 0.1);
  color: #0f766e;
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
  min-width: 420px;
}

.hero-stat {
  padding: 1.2rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.hero-stat span {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.hero-stat strong {
  font-size: 1.45rem;
}

.chart-section {
  width: 100%;
}

@media (max-width: 980px) {
  .app-header .container,
  .hero-strip {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions,
  .hero-stats {
    width: 100%;
  }

  .hero-stats {
    min-width: 0;
    grid-template-columns: 1fr;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.35);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(20, 184, 166, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0);
  }
}
</style>
