export interface UserInfo {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  school: number | null
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

export interface LoginResponse {
  token: string
  user: UserInfo
}

export interface UserRecord {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  school: number | null
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

export interface VideoCategory {
  id: number
  name: string
  description: string
  created_at: string
}

export interface VideoAlbumMini {
  id: number
  name: string
  cover_image: string | null
}

export interface Video {
  albums: VideoAlbumMini[]
  id: number
  title: string
  description: string
  teacher: number | null
  school: number | null
  category: number | null
  file: string | null
  cover_image: string | null
  duration: string | null
  file_size: number
  resolution: string
  status: string
  view_count: number
  created_at: string
  updated_at: string
}

export interface Device {
  id: number
  device_name: string
  device_sn: string
  device_type: string
  manufacturer: string
  model: string
  firmware_version: string
  school: number | null
  school_name: string
  location: string
  ip_address: string
  mac_address: string
  status: string
  last_online_time: string | null
  created_at: string
  updated_at: string
}

export interface School {
  id: number
  name: string
  building: number | null
  building_name: string | null
  created_at: string
}

export interface Building {
  id: number
  name: string
  description: string
  created_at: string
}

export interface LiveRoom {
  id: number
  name: string
  school: number | null
  teacher: number | null
  status: string
  scheduled_at: string | null
  started_at: string | null
  ended_at: string | null
  created_at: string
  updated_at: string
}

export interface LiveSession {
  id: number
  device_name: string
  title: string
  school: number | null
  school_name: string | null
  hls_url: string | null
  status: string
  created_time: string
  start_time: string | null
  end_time: string | null
}

export interface VideoAlbum {
  id: number
  name: string
  teacher: number | null
  description: string
  cover_image: string | null
  view_count: number
  videos: VideoMini[]
  created_at: string
  updated_at: string
}

export interface VideoMini {
  id: number
  title: string
  cover_image: string | null
  duration: string | null
  status: string
  file_size: number
}

export interface TeacherRecord {
  id: number
  username: string
  first_name: string
  subject: string
  avatar: string | null
  school_name: string | null
  description: string | null
}

export interface SearchResult {
  videos: VideoMini[]
  albums: VideoAlbum[]
  teachers: TeacherRecord[]
}

export interface SiteSettings {
  banner_image: string | null
  id: number
  site_name: string
  footer_description: string
  footer_copyright: string
  updated_at: string
}

export interface Review {
  id: number
  user: number
  user_username: string
  user_first_name: string
  video: number
  rating: number
  comment: string
  is_approved: boolean
  created_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
