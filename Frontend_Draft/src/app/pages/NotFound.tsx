import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Home, Search } from 'lucide-react';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
      <div className="text-center space-y-6 px-4">
        <div className="space-y-2">
          <h1 className="text-9xl font-bold text-blue-600">404</h1>
          <h2 className="text-3xl font-bold">Page Not Found</h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={() => navigate('/feed')} size="lg">
            <Home className="w-4 h-4 mr-2" />
            Go to Home
          </Button>
          <Button onClick={() => navigate(-1)} variant="outline" size="lg">
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
