import i18n from '@/i18n'

export function formatDuration(duration?: string | null): string {
  if (!duration) return '--:--'
  // ISO 8601 duration: PT1H2M3S
  const match = duration.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$/)
  if (match) {
    const hours = Number(match[1] || 0)
    const minutes = Number(match[2] || 0)
    const seconds = Math.floor(Number(match[3] || 0))
    if (hours > 0) {
      return [hours, minutes, seconds].map((part) => String(part).padStart(2, '0')).join(':')
    }
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }
  // Django DurationField: HH:MM:SS.ffffff
  const tdMatch = duration.match(/^(\d{1,2}):(\d{2}):(\d{2})(?:\.\d+)?$/)
  if (tdMatch) {
    const hours = Number(tdMatch[1])
    const minutes = Number(tdMatch[2])
    const seconds = Number(tdMatch[3])
    if (hours > 0) {
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    }
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }
  return duration
}

export function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let index = 0
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const locale = i18n.global.locale.value || 'zh-CN'
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}
