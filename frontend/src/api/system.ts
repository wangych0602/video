import request from './request'

export interface SiteConfig {
  site_name: string
  site_description: string
  default_language: string
  contact_email: string
  registration_enabled: boolean
  footer_text: string
  footer_copyright: string
  footer_icp: string
}

export function getSiteConfig() {
  return request.get<SiteConfig>('/site-config/').then((r) => r.data)
}