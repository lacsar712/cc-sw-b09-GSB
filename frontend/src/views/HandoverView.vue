<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api.js'

const STATUS_LABELS = { pending: '排队中', claimed: '领取中', done: '已结案' }

const role = ref(localStorage.getItem('role') || '')
const handovers = ref([])
const current = ref(null)
const err = ref('')
const msg = ref('')
const busy = ref(false)

const canHandover = computed(() => role.value === 'writer')

function statusLabel(s) {
  return STATUS_LABELS[s] || s
}

function fmtTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}

async function refresh() {
  try {
    handovers.value = await api('/api/handovers')
    err.value = ''
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function open(h) {
  err.value = ''
  try {
    current.value = await api(`/api/handovers/${h.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function handover() {
  if (!canHandover.value || busy.value) return
  busy.value = true
  err.value = ''
  msg.value = ''
  try {
    const created = await api('/api/handovers', { method: 'POST' })
    msg.value = `已冻结副本 #${created.id}，待处理 ${created.item_count} 笔`
    await refresh()
    current.value = created
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(() => {
  role.value = localStorage.getItem('role') || ''
  refresh()
})
</script>

<template>
  <div>
    <p v-if="err" style="color:#b00020">{{ err }}</p>

    <section style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>交班</h3>
      <button
        type="button"
        :disabled="!canHandover || busy"
        :title="canHandover ? '冻结当前全部排队中与领取中任务' : '仅校准员可交班'"
        @click="handover"
      >交班</button>
      <span v-if="!canHandover" class="hint" style="margin-left:8px;">巡检员可翻阅副本，不可交班</span>
      <p v-if="msg" style="color:#1a7f37">{{ msg }}</p>
    </section>

    <section style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>历史副本</h3>
      <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
        <thead>
          <tr>
            <th>副本号</th><th>交班时间</th><th>操作人</th><th>笔数</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="h in handovers"
            :key="h.id"
            :style="{ cursor: 'pointer', background: current && current.id === h.id ? '#e8f0fe' : '' }"
            @click="open(h)"
          >
            <td>{{ h.id }}</td>
            <td>{{ fmtTime(h.created_at) }}</td>
            <td>{{ h.created_by }}</td>
            <td>{{ h.item_count }}</td>
          </tr>
          <tr v-if="!handovers.length">
            <td colspan="4" style="color:#666;">暂无副本</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="current" style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>副本明细 #{{ current.id }}（只读）</h3>
      <p style="color:#666; font-size:13px;">
        交班时间：{{ fmtTime(current.created_at) }}　操作人：{{ current.created_by }}　冻结时共 {{ current.item_count }} 笔
      </p>
      <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
        <thead>
          <tr>
            <th>编号</th><th>灯种</th><th>标称 nm</th><th>冻结时状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="it in current.items" :key="it.job_id">
            <td>{{ it.job_id }}</td>
            <td>{{ it.lamp }}</td>
            <td>{{ it.nominal_nm }}</td>
            <td>{{ statusLabel(it.status) }}</td>
          </tr>
          <tr v-if="!current.items.length">
            <td colspan="4" style="color:#666;">交班时无待处理任务</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
