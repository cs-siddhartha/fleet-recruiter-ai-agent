import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { IconFileUpload } from '@tabler/icons-react'
import { useEffect, useState } from 'react'

import { Badge } from '~/components/ui/badge'
import { Button } from '~/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '~/components/ui/card'
import { Input } from '~/components/ui/input'
import { Label } from '~/components/ui/label'
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
      await navigate({
        to: '/evaluations/$evaluationId',
        params: { evaluationId: evaluation.evaluation_id },
      })
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not submit resume')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!job) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-10">
        <p className={error ? 'text-destructive' : 'text-muted-foreground'}>
          {error ?? 'Loading job...'}
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-8 px-6 py-10 lg:grid-cols-[minmax(0,1fr)_360px]">
      <section className="grid max-w-3xl gap-8">
        <div className="grid gap-3">
          <div className="flex flex-wrap gap-2">
            <Badge>{job.company}</Badge>
            <Badge variant="outline">{job.location}</Badge>
          </div>
          <h1 className="font-heading text-4xl leading-tight md:text-5xl">{job.title}</h1>
          <p className="text-muted-foreground text-lg leading-8">{job.summary}</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Job description</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-line text-sm leading-7">{job.job_description}</div>
          </CardContent>
        </Card>
      </section>

      <Card className="h-fit lg:sticky lg:top-24">
        <CardHeader>
          <CardTitle>Submit candidate resume</CardTitle>
          <CardDescription>Upload a PDF to generate an evaluation scorecard.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <div className="grid gap-2">
              <Label htmlFor="resume">PDF resume</Label>
              <Input
                accept="application/pdf,.pdf"
                id="resume"
                type="file"
                onChange={(event) => setResume(event.target.files?.[0] ?? null)}
              />
            </div>
            {resume ? <p className="text-muted-foreground text-sm">{resume.name}</p> : null}
            {error ? <p className="text-destructive text-sm">{error}</p> : null}
            <Button disabled={isSubmitting} type="submit">
              <IconFileUpload data-icon="inline-start" />
              {isSubmitting ? 'Submitting...' : 'Run evaluation'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
