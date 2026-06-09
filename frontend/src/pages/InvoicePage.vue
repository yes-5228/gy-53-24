<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { parkingApi } from "../api/parking";
import StatusBadge from "../components/StatusBadge.vue";

const orders = ref([]);
const invoices = ref([]);
const message = ref("");
const form = reactive({
  order_id: "",
  buyer_name: "",
  tax_number: "",
  email: "",
});

const paidOrders = computed(() => orders.value.filter((order) => order.status === "paid"));

async function loadData() {
  const [orderData, invoiceData] = await Promise.all([parkingApi.getOrders(), parkingApi.getInvoices()]);
  orders.value = orderData.items;
  invoices.value = invoiceData.items;
  if (!form.order_id && paidOrders.value[0]) form.order_id = paidOrders.value[0].id;
}

async function createInvoice() {
  message.value = "";
  try {
    await parkingApi.createInvoice(form);
    Object.assign(form, { order_id: "", buyer_name: "", tax_number: "", email: "" });
    await loadData();
    message.value = "电子发票已开具";
  } catch (err) {
    message.value = err.message;
  }
}

onMounted(loadData);
</script>

<template>
  <div class="page-stack two-column">
    <section>
      <header class="page-header compact">
        <div>
          <h2>电子发票开具</h2>
          <p>选择已结算订单生成电子发票记录。</p>
        </div>
      </header>

      <form class="form-panel" @submit.prevent="createInvoice">
        <label>
          订单
          <select v-model="form.order_id" required>
            <option v-for="order in paidOrders" :key="order.id" :value="order.id">
              #{{ order.id }} {{ order.plate_number }} ¥{{ order.amount }}
            </option>
          </select>
        </label>
        <label>抬头名称<input v-model="form.buyer_name" required /></label>
        <label>税号<input v-model="form.tax_number" /></label>
        <label>接收邮箱<input v-model="form.email" type="email" required /></label>
        <button class="primary-button" type="submit">开具发票</button>
        <p v-if="message" class="hint-text">{{ message }}</p>
      </form>
    </section>

    <section class="table-section">
      <h3>发票记录</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>发票号</th>
              <th>订单</th>
              <th>抬头</th>
              <th>金额</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in invoices" :key="invoice.id">
              <td>{{ invoice.invoice_no }}</td>
              <td>#{{ invoice.order_id }}</td>
              <td>{{ invoice.buyer_name }}</td>
              <td>¥{{ invoice.amount }}</td>
              <td><StatusBadge :status="invoice.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
