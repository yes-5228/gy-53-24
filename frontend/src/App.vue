<script setup>
import { computed, ref } from "vue";
import { BadgeDollarSign, Car, FileText, IdCard } from "lucide-vue-next";
import InvoicePage from "./pages/InvoicePage.vue";
import MonthlyCardPage from "./pages/MonthlyCardPage.vue";
import ParkingBillingPage from "./pages/ParkingBillingPage.vue";
import SpaceMonitorPage from "./pages/SpaceMonitorPage.vue";

const current = ref("spaces");
const tabs = [
  { key: "spaces", label: "车位监控", icon: Car, component: SpaceMonitorPage },
  { key: "cards", label: "月卡办理", icon: IdCard, component: MonthlyCardPage },
  { key: "billing", label: "临停计费", icon: BadgeDollarSign, component: ParkingBillingPage },
  { key: "invoices", label: "电子发票", icon: FileText, component: InvoicePage },
];

const currentComponent = computed(() => tabs.find((tab) => tab.key === current.value).component);
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar">
      <div>
        <h1>停车场收费系统</h1>
        <p>车位、月卡、计费与开票</p>
      </div>
      <nav>
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="{ active: current === tab.key }"
          type="button"
          @click="current = tab.key"
        >
          <component :is="tab.icon" :size="18" />
          <span>{{ tab.label }}</span>
        </button>
      </nav>
    </aside>
    <section class="content-panel">
      <component :is="currentComponent" />
    </section>
  </main>
</template>
