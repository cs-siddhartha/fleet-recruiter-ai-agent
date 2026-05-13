import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'

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

    async function pollEvaluation() {
      try {
        const nextEvaluation = await fetchEvaluation(evaluationId)
        if (!isActive) return
        setEvaluation(nextEvaluation)
        if (nextEvaluation.status === 'pending' || nextEvaluation.status === 'running') {
          window.setTimeout(pollEvaluation, 1500)
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
    }
  }, [evaluationId])

  if (error) {
    return <div className="page-shell"><p className="error-text">{error}</p></div>
  }

  if (!evaluation) {
    return <div className="page-shell"><p className="muted">Loading evaluation...</p></div>
  }

  return (
    <div className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Evaluation</p>
        <h1>{evaluation.file_name}</h1>
        <p className="muted">Status: {evaluation.status} · Stage: {evaluation.stage}</p>
      </section>

      {evaluation.error ? <p className="error-text">{evaluation.error}</p> : null}
      {evaluation.result ? <ScorecardView evaluation={evaluation} /> : <p className="muted">The agent is working through the resume and JD.</p>}
    </div>
  )
}

function ScorecardView({ evaluation }: { evaluation: EvaluationRecord }) {
  const result = evaluation.result
  if (!result) return null

  return (
    <section className="scorecard">
      <div className="score-summary">
        <div>
          <p className="eyebrow">Candidate</p>
          <h2>{result.candidate_name}</h2>
          <p>{result.summary}</p>
        </div>
        <strong>{Math.round(result.overall_score * 100)}%</strong>
      </div>

      <div className="category-list">
        {result.categories.map((category) => (
          <article className="category-card" key={category.name}>
            <div>
              <h3>{category.name}</h3>
              <p>{category.comment}</p>
            </div>
            <span>{Math.round(category.score * 100)}%</span>
            {category.evidence.length > 0 ? (
              <ul>
                {category.evidence.map((item) => <li key={item}>{item}</li>)}
              </ul>
            ) : null}
          </article>
        ))}
      </div>

      <section className="notes-grid">
        <TextList title="Missing information" items={result.missing_information} />
        <TextList title="Risks or concerns" items={result.risks_or_concerns} />
        <TextList title="Interview questions" items={result.interview_questions} />
      </section>
    </section>
  )
}

function TextList({ title, items }: { title: string; items: Array<string> }) {
  return (
    <article className="note-card">
      <h3>{title}</h3>
      {items.length > 0 ? <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="muted">None reported.</p>}
    </article>
  )
}
