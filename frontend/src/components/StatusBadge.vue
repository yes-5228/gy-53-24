<script setup>
const props = defineProps({
  status: {
    type: String,
    required: true,
  },
});

const labels = {
  free: "空闲",
  occupied: "占用",
  reserved: "预约",
  maintenance: "维护",
  active: "有效",
  expired: "到期",
  paused: "暂停",
  parking: "停车中",
  paid: "已结算",
  issued: "已开具",
};
</script>

<template>
  <span class="status-badge" :class="`status-${props.status}`">
    {{ labels[props.status] || props.status }}
  </span>
</template>
