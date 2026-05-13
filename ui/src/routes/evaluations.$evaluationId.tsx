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
import { fetchEvaluation, type EvaluationRecord } from '~/utils/api'

export const Route = createFileRoute('/evaluations/$evaluationId')({
  component: EvaluationPage,
})

function EvaluationPage() {
  const { evaluationId } = Route.useParams()
  const [evaluation, setEvaluation] = useState<EvaluationRecord | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isActive = true
    let timeoutId: number | undefined

    async function pollEvaluation() {
      try {
        const nextEvaluation = await fetchEvaluation(evaluationId)
        if (!isActive) return
        setEvaluation(nextEvaluation)
        if (nextEvaluation.status === 'pending' || nextEvaluation.status === 'running') {
          timeoutId = window.setTimeout(pollEvaluation, 1500)
        }
      } catch (reason) {
        if (isActive) {
          setError(reason instanceof Error ? reason.message : 'Could not load evaluation')
        }
      }
    }

    pollEvaluation()
    return () => {
      isActive = false
      if (timeoutId) window.clearTimeout(timeoutId)
    }
  }, [evaluationId])

  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-10">
        <p className="text-destructive">{error}</p>
      </div>
    )
  }

  if (!evaluation) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-10">
        <p className="text-muted-foreground">Loading evaluation...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-8 px-6 py-10">
      <section className="grid gap-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">Evaluation</Badge>
          <Badge variant={evaluation.status === 'error' ? 'destructive' : 'secondary'}>
            {evaluation.status}
          </Badge>
        </div>
        <h1 className="font-heading max-w-3xl text-4xl leading-tight md:text-5xl">{evaluation.file_name}</h1>
        <p className="text-muted-foreground">Stage: {evaluation.stage}</p>
      </section>

      {evaluation.error ? <p className="text-destructive">{evaluation.error}</p> : null}
      {evaluation.result ? (
        <ScorecardView evaluation={evaluation} />
      ) : (
        <Card>
          <CardContent>
            <p className="text-muted-foreground">The agent is working through the resume and JD.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function ScorecardView({ evaluation }: { evaluation: EvaluationRecord }) {
  const result = evaluation.result
  if (!result) return null

  return (
    <section className="grid gap-6">
      <Card>
        <CardContent className="grid gap-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
          <div className="grid gap-2">
            <Badge variant="outline">Candidate</Badge>
            <h2 className="font-heading text-3xl leading-tight">{result.candidate_name}</h2>
            <p className="text-muted-foreground leading-7">{result.summary}</p>
          </div>
          <div className="text-left md:text-right">
            <p className="font-heading text-5xl">{Math.round(result.overall_score * 100)}%</p>
            <p className="text-muted-foreground text-sm">Overall match</p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {result.categories.map((category) => {
          const score = Math.round(category.score * 100)

          return (
            <Card key={category.name}>
              <CardHeader className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto]">
                <div>
                  <CardTitle>{category.name}</CardTitle>
                  <CardDescription>{category.comment}</CardDescription>
                </div>
                <p className="self-start text-sm font-semibold sm:text-right">{score}%</p>
              </CardHeader>
              <CardContent>
                <div className="bg-muted h-2 overflow-hidden">
                  <div className="bg-primary h-full" style={{ width: `${score}%` }} />
                </div>
                {category.evidence.length > 0 ? (
                  <ul className="grid gap-2 pl-5 text-sm leading-6 list-disc">
                    {category.evidence.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                ) : null}
              </CardContent>
            </Card>
          )
        })}
      </div>

      <section className="grid gap-4 lg:grid-cols-3">
        <TextList title="Missing information" items={result.missing_information} />
        <TextList title="Risks or concerns" items={result.risks_or_concerns} />
        <TextList title="Interview questions" items={result.interview_questions} ordered />
      </section>
    </section>
  )
}

function TextList({ title, items, ordered = false }: { title: string; items: Array<string>; ordered?: boolean }) {
  const ListTag = ordered ? 'ol' : 'ul'

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length > 0 ? (
          <ListTag
            className={`grid gap-2 pl-5 text-sm leading-6 ${
              ordered ? 'list-decimal' : 'list-disc'
            }`}
          >
            {items.map((item) => <li key={item}>{item}</li>)}
          </ListTag>
        ) : (
          <p className="text-muted-foreground text-sm">None reported.</p>
        )}
      </CardContent>
    </Card>
  )
}
