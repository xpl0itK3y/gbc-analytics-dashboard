<template>
  <section class="insights-grid">
    <!-- Cities Insight -->
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

    <!-- Statuses Insight -->
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
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: null
  }
})

const topCities = computed(() => {
  const data = props.stats?.insights?.cities || []
  const total = props.stats?.summary?.total_orders || 1
  return data.slice(0, 4).map(item => ({
    name: item.name,
    count: item.count,
    share: `${Math.round((item.count / total) * 100)}% от всех`
  }))
})

const topStatuses = computed(() => {
  const data = props.stats?.insights?.statuses || []
  return data.slice(0, 4).map(item => ({
    name: formatStatus(item.name),
    count: item.count
  }))
})

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
  if (!value) return 'Без статуса'
  const techValue = value.toLowerCase()
  if (STATUS_LABELS[techValue]) return STATUS_LABELS[techValue]
  return value.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ')
}
</script>

<style scoped>
.insights-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
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

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.rank-item strong {
  display: block;
  margin-bottom: 0.2rem;
}

.rank-item span {
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
