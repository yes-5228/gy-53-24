<script setup>
import { onMounted, reactive, ref } from "vue";
import { parkingApi } from "../api/parking";
import StatusBadge from "../components/StatusBadge.vue";

const cards = ref([]);
const message = ref("");
const form = reactive({
  holder_name: "",
  phone: "",
  plate_number: "",
  start_date: new Date().toISOString().slice(0, 10),
  end_date: "",
  fee: 360,
});

async function loadCards() {
  const data = await parkingApi.getCards();
  cards.value = data.items;
}

async function createCard() {
  message.value = "";
  try {
    await parkingApi.createCard(form);
    Object.assign(form, {
      holder_name: "",
      phone: "",
      plate_number: "",
      start_date: new Date().toISOString().slice(0, 10),
      end_date: "",
      fee: 360,
    });
    await loadCards();
    message.value = "月卡办理成功";
  } catch (err) {
    message.value = err.message;
  }
}

async function setStatus(card, status) {
  await parkingApi.updateCard(card.id, { status });
  await loadCards();
}

onMounted(loadCards);
</script>

<template>
  <div class="page-stack two-column">
    <section>
      <header class="page-header compact">
        <div>
          <h2>月卡办理</h2>
          <p>登记车主、车牌、有效期与费用。</p>
        </div>
      </header>
      <form class="form-panel" @submit.prevent="createCard">
        <label>车主姓名<input v-model="form.holder_name" required /></label>
        <label>手机号<input v-model="form.phone" required /></label>
        <label>车牌号<input v-model="form.plate_number" required /></label>
        <label>开始日期<input v-model="form.start_date" type="date" required /></label>
        <label>结束日期<input v-model="form.end_date" type="date" required /></label>
        <label>费用<input v-model.number="form.fee" type="number" min="0" required /></label>
        <button class="primary-button" type="submit">办理月卡</button>
        <p v-if="message" class="hint-text">{{ message }}</p>
      </form>
    </section>

    <section class="table-section">
      <h3>月卡列表</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>车主</th>
              <th>车牌</th>
              <th>有效期</th>
              <th>费用</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="card in cards" :key="card.id">
              <td>{{ card.holder_name }}</td>
              <td>{{ card.plate_number }}</td>
              <td>{{ card.start_date }} 至 {{ card.end_date }}</td>
              <td>¥{{ card.fee }}</td>
              <td><StatusBadge :status="card.status" /></td>
              <td>
                <select :value="card.status" @change="setStatus(card, $event.target.value)">
                  <option value="active">有效</option>
                  <option value="paused">暂停</option>
                  <option value="expired">到期</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
