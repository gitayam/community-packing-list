import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { AlertCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Card className="m-4">
          <div className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="text-status-required mb-4" size={48} />
            <h2 className="text-xl font-semibold text-military-dark mb-2">Something went wrong</h2>
            <p className="text-gray-600 mb-4 text-center max-w-md">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <Button
              variant="primary"
              onClick={() => {
                this.setState({ hasError: false, error: undefined });
                window.location.href = '/';
              }}
            >
              Return to Home
            </Button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}
