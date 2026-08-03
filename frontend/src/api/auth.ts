import request from './request'
import type { LoginResponse } from './types'

export function login(username: string, password: string) {
  return request.post<LoginResponse>('/auth/login/', { username, password }).then((response) => response.data)
}
