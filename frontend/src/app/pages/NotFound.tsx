import { useRouter } from 'next/router';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '../components/ui/button';
import { Home, Search } from 'lucide-react';

export function NotFound() {
  const router = useRouter();

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center text-foreground">
      <div className="absolute top-4 right-4 z-10">
        <ThemeToggle />
      </div>
      <div className="text-center space-y-6 px-4">
        <div className="space-y-2">
          <h1 className="text-9xl font-bold text-blue-600">404</h1>
          <h2 className="text-3xl font-bold">Page Not Found</h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={() => router.push('/feed')} size="lg">
            <Home className="w-4 h-4 mr-2" />
            Go to Home
          </Button>
          <Button onClick={() => router.back()} variant="outline" size="lg">
            Go Back
          </Button>
        </div>

        <div className="pt-8">
          <Search className="w-24 h-24 text-muted-foreground/20 mx-auto" />
        </div>
      </div>
    </div>
  );
}
