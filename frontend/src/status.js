export const STATUS_LABELS = {
  pending: '排队中',
  claimed: '领取中',
  done: '已结案',
}

export function statusLabel(s) {
  return STATUS_LABELS[s] || s
}
