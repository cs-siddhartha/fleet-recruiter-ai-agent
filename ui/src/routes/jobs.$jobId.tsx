import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

import { createEvaluation, fetchJob, type JobDetail } from '~/utils/api'

export const Route = createFileRoute('/jobs/$jobId')({
  component: JobDetailPage,
})

function JobDetailPage() {
  const { jobId } = Route.useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [resume, setResume] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchJob(jobId)
      .then(setJob)
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : 'Could not load job')
      })
  }, [jobId])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!resume) {
      setError('Choose a PDF resume first.')
      return
    }

    setIsSubmitting(true)
    setError(null)
    try {
      const evaluation = await createEvaluation(jobId, resume)
      await navigate({ to: '/evaluations/$evaluationId', params: { evaluationId: evaluation.evaluation_id } })
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not submit resume')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!job) {
    return (
      <div className="page-shell">
        <p className="muted">{error ?? 'Loading job...'}</p>
      </div>
    )
  }

  return (
    <div className="page-shell detail-layout">
      <section className="job-detail">
        <p className="eyebrow">{job.company} · {job.location}</p>
        <h1>{job.title}</h1>
        <p className="lede">{job.summary}</p>
        <h2>Job description</h2>
        <p>{job.job_description}</p>
      </section>

      <form className="upload-panel" onSubmit={handleSubmit}>
        <h2>Submit candidate resume</h2>
        <label>
          PDF resume
          <input
            accept="application/pdf,.pdf"
            type="file"
            onChange={(event) => setResume(event.target.files?.[0] ?? null)}
          />
        </label>
        {resume ? <p className="muted">{resume.name}</p> : null}
        {error ? <p className="error-text">{error}</p> : null}
        <button disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Submitting...' : 'Run evaluation'}
        </button>
      </form>
    </div>
  )
}
