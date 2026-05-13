import { Link } from '@tanstack/react-router'

import { Button, buttonVariants } from '~/components/ui/button'

export function NotFound({ children }: { children?: any }) {
  return (
    <div className="mx-auto grid min-h-[60vh] max-w-3xl place-items-center px-6 py-10 text-center">
      <div className="grid gap-4">
        <div className="text-muted-foreground">
          {children || <p>The page you are looking for does not exist.</p>}
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Button variant="outline" onClick={() => window.history.back()}>
            Go back
          </Button>
          <Link to="/" className={buttonVariants()}>
            Start Over
          </Link>
        </div>
      </div>
    </div>
  )
}
