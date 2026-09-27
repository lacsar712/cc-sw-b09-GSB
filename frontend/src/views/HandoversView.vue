<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'

const router = useRouter()
const role = ref(localStorage.getItem('role') || '')
const handovers = ref([])
const err = ref('')
let timer

async function refresh() {
  if (!localStorage.getItem('tok')) return
  try {
    handovers.value = await api('/api/handovers')
    err.value = ''
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function handover() {
  err.value = ''
  try {
    await api('/api/handovers', { method: 'POST' })
    await refresh()
  } catch (e) {
    err.value = String(e.message || e)
  }
}

function goDetail(id) {
  router.push(`/handovers/${id}`)
}

onMounted(() => {
  role.value = localStorage.getItem('role') || ''
  refresh()
  timer = setInterval(refresh, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div>
    <p v-if="err" style="color:#b00020">{{ err }}</p>
    <section v-if="role === 'writer'" style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>交班</h3>
      <p style="color:#666; font-size:13px;">冻结当前全部排队中与领取中任务的编号、灯种、标称，生成只读副本。</p>
      <button @click="handover">交班</button>
    </section>
    <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
      <thead>
        <tr>
          <th>副本号</th><th>交班人</th><th>交班时间</th><th>未结笔数</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="h in handovers"
          :key="h.id"
          style="cursor:pointer"
          @click="goDetail(h.id)"
        >
          <td>{{ h.id }}</td>
          <td>{{ h.created_by }}</td>
          <td>{{ new Date(h.created_at).toLocaleString() }}</td>
          <td>{{ h.item_count }}</td>
        </tr>
        <tr v-if="!handovers.length">
          <td colspan="4">暂无交班副本</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
