export type JobSummary = {
  id: string
  title: string
  company: string
  location: string
  summary: string
}

export type JobDetail = JobSummary & {
  job_description: string
}

export type ScorecardCategory = {
  name: string
  score: number
  comment: string
  evidence: Array<string>
}

export type CandidateScorecard = {
  candidate_name: string
  job_title: string
  overall_score: number
  summary: string
  categories: Array<ScorecardCategory>
  missing_information: Array<string>
  risks_or_concerns: Array<string>
  interview_questions: Array<string>
  confidence: number
}

export type EvaluationRecord = {
  evaluation_id: string
  job_id: string
  file_name: string
  status: 'pending' | 'running' | 'complete' | 'error'
  stage: string
  error: string | null
  resume_text: string | null
  result: CandidateScorecard | null
}

export async function fetchJobs(): Promise<Array<JobSummary>> {
  return request('/api/jobs')
}

export async function fetchJob(jobId: string): Promise<JobDetail> {
  return request(`/api/jobs/${jobId}`)
}

export async function createEvaluation(jobId: string, resume: File): Promise<EvaluationRecord> {
  const body = new FormData()
  body.append('resume', resume)
  return request(`/api/jobs/${jobId}/evaluations`, { method: 'POST', body })
}

export async function fetchEvaluation(evaluationId: string): Promise<EvaluationRecord> {
  return request(`/api/evaluations/${evaluationId}`)
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed with ${response.status}`)
  }
  return response.json() as Promise<T>
}
