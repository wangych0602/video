import request from './request'

export interface AITask {
  id: number
  video: any
  task_type: string
  status: string
  progress: number
  current_step: string
  teacher: any
  school: any
  created_time: string
  started_time: string
  finished_time: string
  error_message: string
}

export interface TeachingEvaluation {
  id: number
  task: number
  overall_score: number
  grade: string
  knowledge_score: number
  interaction_score: number
  expression_score: number
  classroom_management_score: number
  teaching_structure_score: number
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  evaluation_method: string
  created_time: string
}

export interface AIReport {
  id: number
  task: number
  title: string
  summary: any
  teacher_report: any
  school_report: any
  html_content: string
  pdf_url: string
  download_count: number
  created_time: string
}

export interface Transcript {
  transcript: string
  speech_segments: any[]
  speaking_rate: any
  keywords: any[]
  knowledge_points: any[]
}

// 获取任务列表
export function getAITasks(params?: any) {
  return request.get('/ai/tasks/', { params })
}

// 获取任务详情
export function getAITask(id: number) {
  return request.get('/ai/tasks/' + id + '/')
}

// 创建分析任务
export function createAITask(data: any) {
  return request.post('/ai/tasks/', data)
}

// 获取教学评价
export function getEvaluation(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/evaluation/')
}

// 获取评分数据
export function getScore(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/score/')
}

// 获取分析报告
export function getReport(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/report/')
}

// 下载PDF报告
export function downloadReportPdf(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/report/pdf/', {
    responseType: 'blob'
  })
}

// 获取文字稿
export function getTranscript(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/transcript/')
}

// 获取关键词
export function getKeywords(taskId: number) {
  return request.get('/ai/tasks/' + taskId + '/keywords/')
}