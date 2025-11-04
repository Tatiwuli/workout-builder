export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  session_id?: string
}

export interface ProgressResponse {
  progress: number
  message: string
  status?: string
  final_plan?: any
}
