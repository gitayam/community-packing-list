import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Layout } from '@/components/layout/Layout';
import { HomePage } from '@/pages/HomePage';
import { CreateListPage } from '@/pages/CreateListPage';
import { UploadListPage } from '@/pages/UploadListPage';
import { ListDetailPage } from '@/pages/ListDetailPage';
import { StoreListPage } from '@/pages/StoreListPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

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
        element: <HomePage />,
      },
      {
        path: 'list/create',
        element: <CreateListPage />,
      },
      {
        path: 'list/upload',
        element: <UploadListPage />,
      },
      {
        path: 'list/:id',
        element: <ListDetailPage />,
      },
      {
        path: 'stores',
        element: <StoreListPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
