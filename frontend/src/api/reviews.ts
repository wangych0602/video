import request from './request'
import type { Paginated, Review } from './types'

export function getReviews(params: { video?: number } = {}) {
  return request.get<Paginated<Review>>('/reviews/', { params }).then((r) => r.data)
}

export function createReview(data: { video: number; rating: number; comment: string }) {
  return request.post<Review>('/reviews/', data).then((r) => r.data)
}
