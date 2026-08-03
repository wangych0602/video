import request from './request'
import type { Device, Paginated } from './types'

export interface RegisterDevicePayload {
  device_sn: string
  device_name: string
  device_type: string
  manufacturer: string
  school: number
}

export function getDevices(params: { page?: number; search?: string } = {}) {
  return request.get<Paginated<Device>>('/devices/', { params }).then((response) => response.data)
}

export function getMySchoolDevices(params: { page?: number } = {}) {
  return request.get<Paginated<Device>>('/devices/my-school/', { params }).then((response) => response.data)
}

export function registerDevice(data: RegisterDevicePayload) {
  return request
    .post<{ device_id: number; device_token: string }>('/devices/register/', data)
    .then((response) => response.data)
}

export function startLive(deviceId: number, title = '') {
  return request
    .post<{ session_id: number; stream_url: string; stream_key: string; hls_url: string }>(
      `/devices/${deviceId}/start-live/`,
      { title },
    )
    .then((response) => response.data)
}

export function stopLive(deviceId: number) {
  return request.post<{ session_id: number; status: string }>(`/devices/${deviceId}/stop-live/`).then((response) => response.data)
}
