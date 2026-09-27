<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api.js'
import { statusLabel } from '../status.js'

const route = useRoute()
const router = useRouter()
const handover = ref(null)
const err = ref('')

async function load() {
  err.value = ''
  handover.value = null
  try {
    handover.value = await api(`/api/handovers/${route.params.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <div>
    <p>
      <button type="button" @click="router.push('/handovers')">返回交班台</button>
    </p>
    <p v-if="err" style="color:#b00020">{{ err }}</p>
    <section v-if="handover" style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>交班副本 #{{ handover.id }}（只读）</h3>
      <p>交班人：{{ handover.created_by }}</p>
      <p>交班时间：{{ new Date(handover.created_at).toLocaleString() }}</p>
      <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
        <thead>
          <tr>
            <th>编号</th><th>灯种</th><th>标称</th><th>冻结时状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="it in handover.items" :key="it.job_id">
            <td>{{ it.job_id }}</td>
            <td>{{ it.lamp }}</td>
            <td>{{ it.nominal_nm }}</td>
            <td>{{ statusLabel(it.status) }}</td>
          </tr>
          <tr v-if="!handover.items.length">
            <td colspan="4">交班时无未结任务</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
