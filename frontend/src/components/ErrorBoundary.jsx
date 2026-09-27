import { Component } from 'react';
import { AlertTriangle } from 'lucide-react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('VeriX render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] p-6 text-center font-sans">
          <AlertTriangle size={48} className="text-saffron-500 mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-sm text-gray-500 max-w-md mb-4">
            This page encountered an unexpected error. Please go back and try again.
          </p>
          {import.meta.env.DEV && this.state.error && (
            <pre className="text-xs text-left bg-gray-100 p-3 rounded-lg max-w-lg overflow-auto mb-4 text-red-700">
              {this.state.error.message}
            </pre>
          )}
          <button
            onClick={() => window.location.assign('/projects')}
            className="btn-primary"
          >
            Back to Projects
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
