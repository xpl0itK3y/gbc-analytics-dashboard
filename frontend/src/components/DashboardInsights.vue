<template>
  <section class="insights-grid">
    <div class="card insight-card accent-cyan">
      <div class="card-header insight-header">
        <div>
          <p class="section-kicker">Срез по городам</p>
          <h2>Где чаще покупают</h2>
        </div>
        <span class="section-note">Топ-4</span>
      </div>
      <div class="insight-content">
        <div v-if="topCities.length" class="rank-list">
          <div v-for="city in topCities" :key="city.name" class="rank-item">
            <div>
              <strong>{{ city.name }}</strong>
              <span>{{ city.share }}</span>
            </div>
            <b>{{ city.count }}</b>
          </div>
        </div>
        <p v-else class="empty-copy">Города появятся после загрузки заказов.</p>
      </div>
    </div>

    <div class="card insight-card accent-sand">
      <div class="card-header insight-header">
        <div>
          <p class="section-kicker">Статусы заказов</p>
          <h2>Что происходит сейчас</h2>
        </div>
        <span class="section-note">Текущий срез</span>
      </div>
      <div class="insight-content">
        <div v-if="topStatuses.length" class="status-grid">
          <div v-for="status in topStatuses" :key="status.name" class="status-tile">
            <span>{{ status.name }}</span>
            <strong>{{ status.count }}</strong>
          </div>
        </div>
        <p v-else class="empty-copy">Статусы пока не рассчитаны.</p>
      </div>
    </div>

    <div class="card insight-card accent-rose">
      <div class="card-header insight-header">
        <div>
          <p class="section-kicker">Маркетинг</p>
          <h2>Откуда пришли клиенты</h2>
        </div>
        <span class="section-note">UTM</span>
      </div>
      <div class="insight-content">
        <div v-if="topSources.length" class="source-list">
          <div v-for="source in topSources" :key="source.name" class="source-row">
            <div class="source-meta">
              <strong>{{ source.name }}</strong>
              <span>{{ source.orders }} заказов</span>
            </div>
            <div class="source-bar">
              <div class="source-fill" :style="{ width: source.width }"></div>
            </div>
          </div>
        </div>
        <p v-else class="empty-copy">UTM-источники пока не заполнены.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  orders: {
    type: Array,
    default: () => []
  }
})

const topCities = computed(() => {
  const total = props.orders.length || 1
  const grouped = props.orders.reduce((acc, order) => {
    const key = order.city || 'Не указан'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  return Object.entries(grouped)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([name, count]) => ({
      name,
      count,
      share: `${Math.round((count / total) * 100)}% от списка`
    }))
})

const topStatuses = computed(() => {
  const grouped = props.orders.reduce((acc, order) => {
    const key = formatStatus(order.status)
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  return Object.entries(grouped)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([name, count]) => ({ name, count }))
})

const topSources = computed(() => {
  const grouped = props.orders.reduce((acc, order) => {
    const key = order.utm_source || 'Без метки'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  const max = Math.max(...Object.values(grouped), 1)

  return Object.entries(grouped)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([name, orders]) => ({
      name,
      orders,
      width: `${Math.max((orders / max) * 100, 16)}%`
    }))
})

function formatStatus(value) {
  if (!value) {
    return 'Без статуса'
  }

  return value
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}
</script>

<style scoped>
.insights-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

.insight-card {
  position: relative;
}

.insight-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 4px;
}

.accent-cyan::before {
  background: linear-gradient(90deg, #14b8a6, #2dd4bf);
}

.accent-sand::before {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.accent-rose::before {
  background: linear-gradient(90deg, #ef4444, #fb7185);
}

.insight-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.section-kicker {
  margin: 0 0 0.35rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.section-note {
  padding: 0.45rem 0.75rem;
  border-radius: 9999px;
  background: #f8fafc;
  border: 1px solid var(--border-color);
  font-size: 0.82rem;
  color: var(--text-muted);
}

.insight-content {
  padding: 1.25rem 1.8rem 1.7rem;
}

.rank-list,
.source-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.rank-item,
.source-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.rank-item strong,
.source-meta strong {
  display: block;
  margin-bottom: 0.2rem;
}

.rank-item span,
.source-meta span {
  font-size: 0.92rem;
  color: var(--text-muted);
}

.rank-item b {
  font-size: 1.4rem;
  color: var(--text-primary);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.status-tile {
  padding: 1.15rem;
  border-radius: 16px;
  background: #fffaf0;
  border: 1px solid #fde68a;
}

.status-tile span {
  display: block;
  margin-bottom: 0.35rem;
  color: #92400e;
  font-size: 0.92rem;
}

.status-tile strong {
  font-size: 1.5rem;
  color: #78350f;
}

.source-row {
  align-items: flex-start;
  flex-direction: column;
}

.source-bar {
  width: 100%;
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: #ffe4e6;
}

.source-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #ef4444, #fb7185);
}

.empty-copy {
  margin: 0;
  color: var(--text-muted);
}

@media (max-width: 1024px) {
  .insights-grid {
    grid-template-columns: 1fr;
  }
}
</style>
