<template>
  <div class="card analytics-card">
    <div class="card-header analytics-header">
      <div>
        <p class="eyebrow">Analytics</p>
        <h2>Обзор заказов</h2>
        <p class="chart-subtitle">
          Динамика заказов по дням с аккуратным отображением даже при небольшом объёме данных.
        </p>
      </div>
      <div v-if="summary" class="header-metrics">
        <div class="metric-pill">
          <span class="metric-label">Дней в выборке</span>
          <strong>{{ summary.daysTracked }}</strong>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Среднее в день</span>
          <strong>{{ summary.avgPerDay }}</strong>
        </div>
      </div>
    </div>

    <div v-if="ordersChartData.labels?.length" class="analytics-body">
      <div class="insight-panel">
        <div class="insight-stat">
          <span>Всего заказов</span>
          <strong>{{ summary.totalOrders }}</strong>
        </div>
        <div class="insight-stat">
          <span>Выручка</span>
          <strong>{{ summary.totalRevenue }}</strong>
        </div>
        <div class="insight-message">
          <strong>{{ insight.title }}</strong>
          <p>{{ insight.description }}</p>
        </div>
      </div>

      <div class="chart-stage">
        <div class="chart-grid">
          <div class="chart-card">
            <div class="chart-card-head">
              <span>Количество заказов</span>
              <strong>{{ orderPeak }}</strong>
            </div>
            <div class="chart-container">
              <Bar v-if="isSinglePoint" :data="ordersChartData" :options="ordersBarChartOptions" />
              <Line v-else :data="ordersChartData" :options="ordersLineChartOptions" />
            </div>
          </div>

          <div class="chart-card revenue-card">
            <div class="chart-card-head">
              <span>Выручка по дням</span>
              <strong>{{ revenuePeak }}</strong>
            </div>
            <div class="chart-container">
              <Bar :data="revenueChartData" :options="revenueBarChartOptions" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      Загрузка графика...
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  BarElement
} from 'chart.js'
import { Bar, Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  stats: {
    type: Object,
    default: null
  }
})

const perDay = computed(() => props.stats?.orders_per_day || [])
const revenuePerDay = computed(() => props.stats?.revenue_per_day || [])

const ordersChartData = computed(() => ({
  labels: perDay.value.map((item) => item.date),
  datasets: [
    {
      label: 'Заказы по дням',
      data: perDay.value.map((item) => item.count),
      fill: perDay.value.length > 1,
      borderColor: '#0f766e',
      backgroundColor: perDay.value.length <= 1 ? '#14b8a6' : 'rgba(20, 184, 166, 0.14)',
      borderWidth: 3,
      tension: 0.35,
      pointRadius: perDay.value.length <= 1 ? 0 : 4,
      pointHoverRadius: 6,
      pointBackgroundColor: '#0f766e',
      borderRadius: 10,
      maxBarThickness: 64
    }
  ]
}))

const revenueChartData = computed(() => ({
  labels: revenuePerDay.value.map((item) => item.date),
  datasets: [
    {
      label: 'Выручка по дням',
      data: revenuePerDay.value.map((item) => item.revenue),
      backgroundColor: 'rgba(249, 115, 22, 0.82)',
      borderColor: '#ea580c',
      borderWidth: 1,
      borderRadius: 12,
      maxBarThickness: 56
    }
  ]
}))

const isSinglePoint = computed(() => perDay.value.length <= 1)
const orderPeak = computed(() => {
  const peak = Math.max(...perDay.value.map((item) => item.count), 0)
  return peak ? `${peak} в пике` : 'Нет данных'
})

const revenuePeak = computed(() => {
  const peak = Math.max(...revenuePerDay.value.map((item) => item.revenue), 0)
  return peak ? `${Math.round(peak).toLocaleString()} ₸` : 'Нет данных'
})

const summary = computed(() => {
  const dayCount = perDay.value.length
  const totalOrders = props.stats?.summary?.total_orders || 0
  const totalRevenue = props.stats?.summary?.total_revenue || 0
  const avgPerDay = dayCount ? (totalOrders / dayCount).toFixed(dayCount === 1 ? 0 : 1) : '0'

  return {
    daysTracked: dayCount || 0,
    avgPerDay,
    totalOrders: totalOrders.toLocaleString(),
    totalRevenue: `${totalRevenue.toLocaleString()} ₸`
  }
})

const insight = computed(() => {
  if (isSinglePoint.value) {
    return {
      title: 'Single-day snapshot',
      description: 'Сейчас все импортированные заказы относятся к одной дате, поэтому дашборд показывает объём без пустой линии.'
    }
  }

  return {
    title: 'Динамика активна',
    description: 'В выборке несколько дат, поэтому график показывает движение и темп заказов во времени.'
  }
})

const sharedOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      displayColors: false,
      backgroundColor: '#0f172a',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      padding: 12
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#e2e8f0' },
      ticks: { precision: 0, color: '#64748b' },
      border: { display: false }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#64748b' },
      border: { display: false }
    }
  }
}

const ordersLineChartOptions = {
  ...sharedOptions,
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

const ordersBarChartOptions = {
  ...sharedOptions,
  plugins: {
    ...sharedOptions.plugins,
    tooltip: {
      ...sharedOptions.plugins.tooltip,
      callbacks: {
        label: (context) => `${context.parsed.y} заказов`
      }
    }
  }
}

const revenueBarChartOptions = {
  ...sharedOptions,
  plugins: {
    ...sharedOptions.plugins,
    tooltip: {
      ...sharedOptions.plugins.tooltip,
      callbacks: {
        label: (context) => `${Math.round(context.parsed.y).toLocaleString()} ₸`
      }
    }
  },
  scales: {
    ...sharedOptions.scales,
    y: {
      ...sharedOptions.scales.y,
      ticks: {
        color: '#64748b',
        callback: (value) => `${Math.round(Number(value) / 1000)}k`
      }
    }
  }
}
</script>

<style scoped>
.analytics-card {
  overflow: hidden;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: flex-start;
  background:
    radial-gradient(circle at top right, rgba(20, 184, 166, 0.12), transparent 32%),
    linear-gradient(180deg, #fcfffe 0%, #ffffff 100%);
}

.eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #0f766e;
}

.chart-subtitle {
  margin: 0.45rem 0 0;
  max-width: 42rem;
  color: var(--text-muted);
  line-height: 1.5;
  font-size: 1rem;
}

.header-metrics {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.metric-pill {
  min-width: 110px;
  padding: 1rem 1.15rem;
  border: 1px solid rgba(15, 118, 110, 0.14);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.metric-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.86rem;
  color: var(--text-muted);
}

.metric-pill strong {
  font-size: 1.2rem;
}

.analytics-body {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 1rem;
  padding: 1rem;
}

.insight-panel {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.2rem;
  border-radius: 20px;
  background: linear-gradient(180deg, #0f172a 0%, #162033 100%);
  color: #e2e8f0;
}

.insight-stat {
  padding-bottom: 0.85rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.insight-stat span {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
  color: #94a3b8;
}

.insight-stat strong {
  font-size: 1.55rem;
  font-weight: 700;
}

.insight-message strong {
  display: block;
  margin-bottom: 0.45rem;
  font-size: 1.08rem;
}

.insight-message p {
  margin: 0;
  line-height: 1.55;
  color: #cbd5e1;
  font-size: 1rem;
}

.chart-stage {
  min-width: 0;
  padding: 1rem 1rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(255, 255, 255, 1) 100%);
}

.chart-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1rem;
}

.chart-card {
  padding: 1.1rem;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, 0.82);
}

.revenue-card {
  background: linear-gradient(180deg, #fffaf5 0%, #ffffff 100%);
}

.chart-card-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0 0.15rem 0.85rem;
}

.chart-card-head span {
  color: var(--text-muted);
  font-size: 0.96rem;
}

.chart-card-head strong {
  color: var(--text-primary);
  font-size: 1.12rem;
}

.chart-container {
  position: relative;
  height: 360px;
  width: 100%;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .analytics-header,
  .analytics-body {
    grid-template-columns: 1fr;
    display: grid;
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }

  .header-metrics {
    justify-content: flex-start;
  }
}
</style>
