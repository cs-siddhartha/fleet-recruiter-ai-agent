import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

import { Badge } from '~/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card'
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
    <div className="mx-auto grid max-w-6xl gap-8 px-6 py-10">
      <section className="grid gap-3">
        <Badge variant="outline">Open roles</Badge>
        <h1 className="font-heading max-w-3xl text-4xl leading-tight md:text-5xl">
          Select any job below
        </h1>
        <p className="text-muted-foreground max-w-2xl text-base leading-7">
          Review job descriptions and run a structured AI scorecard for each candidate.
        </p>
      </section>

      {isLoading ? <p className="text-muted-foreground">Loading jobs...</p> : null}
      {error ? <p className="text-destructive">{error}</p> : null}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <a className="group block" href={`/jobs/${job.id}`} key={job.id}>
            <Card className="h-full transition-colors group-hover:border-primary">
              <CardHeader>
                <Badge>{job.company}</Badge>
                <CardTitle>{job.title}</CardTitle>
                <CardDescription>{job.location}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-6">{job.summary}</p>
              </CardContent>
            </Card>
          </a>
        ))}
      </section>
    </div>
  )
}
