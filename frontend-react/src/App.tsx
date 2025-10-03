import { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Layout } from '@/components/layout/Layout';
import { PageLoader } from '@/components/ui/PageLoader';

// Lazy load all pages for code splitting
const HomePage = lazy(() => import('@/pages/HomePage').then(m => ({ default: m.HomePage })));
const CreateListPage = lazy(() => import('@/pages/CreateListPage').then(m => ({ default: m.CreateListPage })));
const UploadListPage = lazy(() => import('@/pages/UploadListPage').then(m => ({ default: m.UploadListPage })));
const ListDetailPage = lazy(() => import('@/pages/ListDetailPage').then(m => ({ default: m.ListDetailPage })));
const StoreListPage = lazy(() => import('@/pages/StoreListPage').then(m => ({ default: m.StoreListPage })));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
    },
  },
});

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<PageLoader />}>
            <HomePage />
          </Suspense>
        ),
      },
      {
        path: 'list/create',
        element: (
          <Suspense fallback={<PageLoader />}>
            <CreateListPage />
          </Suspense>
        ),
      },
      {
        path: 'list/upload',
        element: (
          <Suspense fallback={<PageLoader />}>
            <UploadListPage />
          </Suspense>
        ),
      },
      {
        path: 'list/:id',
        element: (
          <Suspense fallback={<PageLoader />}>
            <ListDetailPage />
          </Suspense>
        ),
      },
      {
        path: 'stores',
        element: (
          <Suspense fallback={<PageLoader />}>
            <StoreListPage />
          </Suspense>
        ),
      },
      {
        path: '*',
        element: (
          <Suspense fallback={<PageLoader />}>
            <NotFoundPage />
          </Suspense>
        ),
      },
    ],
  },
]);

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#2C2C2C',
              border: '1px solid #E5E7EB',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            },
            success: {
              iconTheme: {
                primary: '#28A745',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#DC3545',
                secondary: '#fff',
              },
            },
          }}
        />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
