import { ThemeToggle } from '../components/ThemeToggle';

export function PartnerSubmission() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background/95 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto flex max-w-3xl items-center justify-end px-6 py-4">
          <ThemeToggle />
        </div>
      </header>
      <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl font-semibold">Partner Submission</h1>
      <p className="mt-3 text-sm text-muted-foreground">
        This page is available for partner event submissions. The backend endpoint is ready at
        <code className="mx-1 rounded bg-muted px-1 py-0.5">/api/partner-submissions</code>.
      </p>
      </main>
    </div>
  );
}
