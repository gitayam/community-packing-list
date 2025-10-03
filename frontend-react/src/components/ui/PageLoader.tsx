import { Loader2 } from 'lucide-react';

/**
 * Full-page loading spinner for lazy-loaded routes
 * Displays during code splitting and async route loading
 */
export function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-military-navy animate-spin mx-auto mb-4" />
        <p className="text-gray-600 font-medium">Loading...</p>
      </div>
    </div>
  );
}
