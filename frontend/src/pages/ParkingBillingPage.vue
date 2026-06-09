<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { parkingApi } from "../api/parking";
import StatusBadge from "../components/StatusBadge.vue";

const spaces = ref([]);
const orders = ref([]);
const message = ref("");
const quote = ref(null);
const entryForm = reactive({
  plate_number: "",
  space_code: "",
});
const calcForm = reactive({
  entry_time: new Date(Date.now() - 90 * 60 * 1000).toISOString().slice(0, 16),
  exit_time: new Date().toISOString().slice(0, 16),
});

const freeSpaces = computed(() => spaces.value.filter((space) => ["free", "reserved"].includes(space.status)));
const parkingOrders = computed(() => orders.value.filter((order) => order.status === "parking"));

async function loadData() {
  const [spaceData, orderData] = await Promise.all([parkingApi.getSpaces(), parkingApi.getOrders()]);
  spaces.value = spaceData.items;
  orders.value = orderData.items;
  if (!entryForm.space_code && freeSpaces.value[0]) entryForm.space_code = freeSpaces.value[0].code;
}

async function createEntry() {
  message.value = "";
  try {
    await parkingApi.entry(entryForm);
    entryForm.plate_number = "";
    await loadData();
    message.value = "入场登记成功";
  } catch (err) {
    message.value = err.message;
  }
}

async function calculate() {
  quote.value = await parkingApi.calculate(calcForm);
}

async function closeOrder(order) {
  const result = await parkingApi.exit(order.id, { exit_time: new Date().toISOString().slice(0, 16) });
  message.value = `${order.plate_number} 已结算，金额 ¥${result.amount}`;
  await loadData();
}

onMounted(loadData);
</script>

<template>
  <div class="page-stack">
    <header class="page-header">
      <div>
        <h2>临时停车计费</h2>
        <p>登记入场、试算费用并完成离场结算。</p>
      </div>
    </header>

    <div class="billing-grid">
      <form class="form-panel" @submit.prevent="createEntry">
        <h3>车辆入场</h3>
        <label>车牌号<input v-model="entryForm.plate_number" required /></label>
        <label>
          车位
          <select v-model="entryForm.space_code" required>
            <option v-for="space in freeSpaces" :key="space.id" :value="space.code">{{ space.code }}</option>
          </select>
        </label>
        <button class="primary-button" type="submit">登记入场</button>
        <p v-if="message" class="hint-text">{{ message }}</p>
      </form>

      <form class="form-panel" @submit.prevent="calculate">
        <h3>费用试算</h3>
        <label>入场时间<input v-model="calcForm.entry_time" type="datetime-local" required /></label>
        <label>离场时间<input v-model="calcForm.exit_time" type="datetime-local" required /></label>
        <button class="secondary-button" type="submit">计算费用</button>
        <p v-if="quote" class="quote-text">停车 {{ quote.duration_hours }} 小时，应收 ¥{{ quote.amount }}</p>
      </form>
    </div>

    <section class="table-section">
      <h3>在场车辆</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>订单</th>
              <th>车牌</th>
              <th>车位</th>
              <th>入场时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in parkingOrders" :key="order.id">
              <td>#{{ order.id }}</td>
              <td>{{ order.plate_number }}</td>
              <td>{{ order.space_code }}</td>
              <td>{{ order.entry_time }}</td>
              <td><StatusBadge :status="order.status" /></td>
              <td><button class="small-button" type="button" @click="closeOrder(order)">离场结算</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
