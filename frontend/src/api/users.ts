import request from './request'
import type { Paginated, UserRecord } from './types'

export interface CreateUserPayload {
  username: string
  email: string
  password: string
  role: string
  school?: number | null
}

export function getUsers(params: { page?: number } = {}) {
  return request.get<Paginated<UserRecord>>('/users/', { params }).then((response) => response.data)
}

export function createUser(data: CreateUserPayload) {
  return request.post<UserRecord>('/users/', data).then((response) => response.data)
}
