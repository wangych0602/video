import request from './request'
import type { LiveRoom, LiveSession, Paginated } from './types'

export function getLiveRooms() {
  return request.get<Paginated<LiveRoom>>('/live-rooms/').then((response) => response.data)
}

export function getLiveSessions(params: { status?: string; mine?: string } = {}) {
  return request.get<Paginated<LiveSession>>('/live-sessions/', { params }).then((response) => response.data)
}

export interface PersonalLiveResult {
  session_id: number
  title: string
  stream_url: string
  stream_key: string
  push_token: string
  hls_url: string
}

export function startPersonalLive(title: string) {
  return request.post<PersonalLiveResult>('/live/personal-start/', { title }).then((response) => response.data)
}

export function stopPersonalLive(sessionId: number) {
  return request.post<{ session_id: number; status: string }>('/live/personal-stop/', { session_id: sessionId }).then((response) => response.data)
}

export function deletePersonalLive(sessionId: number) {
  return request.post<{ session_id: number }>('/live/personal-delete/', { session_id: sessionId }).then((response) => response.data)
}
