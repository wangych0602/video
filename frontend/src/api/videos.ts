import request from './request'
import type { Paginated, SiteSettings, Video, VideoCategory } from './types'

export interface VideoListParams {
  page?: number
  search?: string
  category?: number | undefined
  status?: string
}

export function getVideos(params: VideoListParams = {}) {
  return request.get<Paginated<Video>>('/videos/', { params }).then((response) => response.data)
}

export function getVideo(id: number | string) {
  return request.get<Video>(`/videos/${id}/`).then((response) => response.data)
}

export function getMyVideos(page = 1) {
  return request.get<Paginated<Video>>('/videos/my/', { params: { page } }).then((response) => response.data)
}

export function getPendingVideos(page = 1) {
  return request.get<Paginated<Video>>('/videos/pending/', { params: { page } }).then((response) => response.data)
}

export function uploadVideo(data: FormData) {
  return request.post<Video>('/videos/upload/', data).then((response) => response.data)
}

export function updateVideo(id: number, data: FormData) {
  return request.patch<Video>(`/videos/${id}/`, data).then((response) => response.data)
}

export function deleteVideo(id: number) {
  return request.delete(`/videos/${id}/`)
}

export function approveVideo(id: number) {
  return request.post<Video>(`/videos/${id}/approve/`).then((response) => response.data)
}

export function rejectVideo(id: number, comment: string) {
  return request.post<Video>(`/videos/${id}/reject/`, { comment }).then((response) => response.data)
}

export function getPopularVideos() {
  return request.get<Video[]>('/videos/popular/').then((response) => response.data)
}

export function getVideoCategories() {
  return request.get<Paginated<VideoCategory>>('/video-categories/').then((response) => response.data)
}

export function getSiteSettings() {
  return request.get<SiteSettings>('/site-settings/').then((response) => response.data)
}
