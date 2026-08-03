import request from './request'
import type { Paginated, VideoAlbum, TeacherRecord, SearchResult } from './types'

export function getTeachers(params: { q?: string } = {}) {
  return request.get<TeacherRecord[]>('/teachers/', { params }).then((r) => r.data)
}

export function searchStudio(q: string) {
  return request.get<SearchResult>('/studio/search/', { params: { q } }).then((r) => r.data)
}

export function getMyTeacherProfile() {
  return request.get<TeacherRecord>('/teacher-profiles/me/').then((r) => r.data)
}

export function updateMyTeacherProfile(data: FormData) {
  return request.put<TeacherRecord>('/teacher-profiles/me/', data).then((r) => r.data)
}

export function getAlbums(params: { page?: number; mine?: string } = {}) {
  return request.get<Paginated<VideoAlbum>>('/video-albums/', { params }).then((r) => r.data)
}

export function getPopularAlbums() {
  return request.get<VideoAlbum[]>('/video-albums/popular/').then((r) => r.data)
}

export function getAlbum(id: number | string) {
  return request.get<VideoAlbum>(`/video-albums/${id}/`).then((r) => r.data)
}

export function createAlbum(data: FormData) {
  return request.post<VideoAlbum>('/video-albums/', data).then((r) => r.data)
}

export function updateAlbum(id: number, data: FormData) {
  return request.patch<VideoAlbum>(`/video-albums/${id}/`, data).then((r) => r.data)
}

export function deleteAlbum(id: number) {
  return request.delete(`/video-albums/${id}/`)
}
