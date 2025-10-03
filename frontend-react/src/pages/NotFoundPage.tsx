import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function NotFoundPage() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-military-navy mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-military-dark mb-2">Page Not Found</h2>
        <p className="text-gray-600 mb-6">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/">
          <Button variant="primary">
            <Home className="inline mr-2" size={18} />
            Back to Home
          </Button>
        </Link>
      </Card>
    </div>
  );
}
