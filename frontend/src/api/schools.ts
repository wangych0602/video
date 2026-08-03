import request from './request'
import type { Building, Paginated, School } from './types'

export function getSchools() {
  return request.get<Paginated<School>>('/schools/').then((response) => response.data)
}

export interface CreateSchoolPayload {
  name: string
  building?: number | null
}

export function createSchool(data: CreateSchoolPayload) {
  return request.post<School>('/schools/', data).then((response) => response.data)
}

export function getBuildings() {
  return request.get<Paginated<Building>>('/buildings/').then((response) => response.data)
}

export interface CreateBuildingPayload {
  name: string
  description?: string
}

export function createBuilding(data: CreateBuildingPayload) {
  return request.post<Building>('/buildings/', data).then((response) => response.data)
}

export function deleteBuilding(id: number) {
  return request.delete(`/buildings/${id}/`)
}
