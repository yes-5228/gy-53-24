<script setup>
import { computed, onMounted, ref } from "vue";
import StatGrid from "../components/StatGrid.vue";
import { parkingApi } from "../api/parking";

const dailyRevenue = ref([]);
const loading = ref(false);
const error = ref("");

const summaryStats = computed(() => {
  const total = dailyRevenue.value.reduce(
    (acc, item) => ({
      amount: acc.amount + item.total_amount,
      orders: acc.orders + item.order_count,
      free: acc.free + item.free_count,
    }),
    { amount: 0, orders: 0, free: 0 },
  );
  return [
    { label: "累计结算金额", value: `¥${total.amount.toFixed(2)}` },
    { label: "累计订单数", value: total.orders },
    { label: "累计免费车辆", value: total.free },
    { label: "统计天数", value: dailyRevenue.value.length },
  ];
});

async function loadRevenue() {
  loading.value = true;
  error.value = "";
  try {
    const data = await parkingApi.getDailyRevenue();
    dailyRevenue.value = data.items;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadRevenue);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <h2>日营收看板</h2>
        <p>按日期查看结算金额、免费车辆、订单数量和高峰时段。</p>
      </div>
      <button class="primary-button" type="button" @click="loadRevenue">刷新</button>
    </header>

    <StatGrid :stats="summaryStats" />
    <p v-if="error" class="error-text">{{ error }}</p>

    <section class="table-section">
      <h3>每日营收明细</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>结算金额</th>
              <th>免费车辆</th>
              <th>订单数量</th>
              <th>高峰时段</th>
            </tr>
          </thead>
          <tbody :class="{ muted: loading }">
            <tr v-for="item in dailyRevenue" :key="item.date">
              <td>{{ item.date }}</td>
              <td><strong>¥{{ item.total_amount.toFixed(2) }}</strong></td>
              <td>{{ item.free_count }} 辆</td>
              <td>{{ item.order_count }} 单</td>
              <td>{{ item.peak_hour }}</td>
            </tr>
            <tr v-if="dailyRevenue.length === 0 && !loading">
              <td colspan="5" style="text-align: center; color: #65746e;">暂无结算数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
