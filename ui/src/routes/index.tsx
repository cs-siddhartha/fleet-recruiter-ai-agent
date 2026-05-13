import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

import { fetchJobs, type JobSummary } from '~/utils/api'

export const Route = createFileRoute('/')({
  component: JobListPage,
})

function JobListPage() {
  const [jobs, setJobs] = useState<Array<JobSummary>>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchJobs()
      .then(setJobs)
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : 'Could not load jobs')
      })
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <div className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Open roles</p>
        <h1>Pick a job, then submit a candidate resume.</h1>
      </section>

      {isLoading ? <p className="muted">Loading jobs...</p> : null}
      {error ? <p className="error-text">{error}</p> : null}

      <section className="job-grid">
        {jobs.map((job) => (
          <a className="job-card" href={`/jobs/${job.id}`} key={job.id}>
            <span>{job.company}</span>
            <h2>{job.title}</h2>
            <p>{job.summary}</p>
            <small>{job.location}</small>
          </a>
        ))}
      </section>
    </div>
  )
}
