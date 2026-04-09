<template>
  <div class="card">
    <div class="card-header">
      <h2>Sales Overview</h2>
    </div>
    <div class="chart-container" v-if="chartData.labels">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="loading">
      Loading chart...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchStats } from '../services/api'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const chartData = ref({})
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { mode: 'index', intersect: false }
  },
  scales: {
    y: { beginAtZero: true, grid: { color: '#f0f0f0' }, ticks: { precision: 0 } },
    x: { grid: { display: false } }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

onMounted(async () => {
  try {
    const data = await fetchStats()
    const perDay = data.orders_per_day || []
    chartData.value = {
      labels: perDay.map(d => d.date),
      datasets: [
        {
          label: 'Orders per Day',
          data: perDay.map(d => d.count),
          fill: true,
          borderColor: '#4f46e5',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#4f46e5'
        }
      ]
    }
  } catch (e) {
    console.error("Chart load error:", e)
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}
</style>
