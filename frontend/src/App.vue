<template>
  <div class="layout-wrapper">
    <header class="app-header">
      <div class="container">
        <h1>GBC Dashboard ⚡️</h1>
        <div class="header-actions">
          <div class="stat-badge" v-if="summary">
             Total Volume: <strong>{{ summary.total_revenue.toLocaleString() }} ₸</strong>
          </div>
          <div class="stat-badge" v-if="summary">
             Orders: <strong>{{ summary.total_orders }}</strong>
          </div>
        </div>
      </div>
    </header>

    <main class="container main-content">
      <div class="grid-layout">
        <div class="chart-section">
          <OrdersChart />
        </div>
      </div>
      <div class="table-section">
        <OrdersTable />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchStats } from './services/api'
import OrdersChart from './components/OrdersChart.vue'
import OrdersTable from './components/OrdersTable.vue'

const summary = ref(null)

onMounted(async () => {
  try {
    const data = await fetchStats()
    summary.value = data.summary
  } catch(e) {
    console.error("Summary load error:", e)
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
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.app-header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.app-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.header-actions {
  display: flex;
  gap: 1rem;
}
.stat-badge {
  background-color: var(--bg-color);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
.main-content {
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.chart-section {
  width: 100%;
}
</style>
