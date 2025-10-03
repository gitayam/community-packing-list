import { Suspense } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { CardSkeleton, TableSkeleton } from '@/components/ui/Skeleton';
import { usePackingList } from '@/hooks/usePackingList';
import { PackingListDetail } from '@/components/packing-lists/PackingListDetail';

function DetailContent({ id }: { id: number }) {
  const { data, error } = usePackingList(id);

  if (error) {
    return (
      <Card>
        <div className="flex items-center gap-3 text-status-required">
          <AlertCircle size={20} />
          <span>Error loading packing list. Please try again.</span>
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <div className="text-gray-600">Packing list not found.</div>
      </Card>
    );
  }

  return <PackingListDetail data={data} />;
}

export function ListDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div>
      <Button variant="secondary" onClick={() => navigate('/')} className="mb-4">
        <ArrowLeft className="inline mr-2" size={16} />
        Back to Lists
      </Button>

      <Suspense
        fallback={
          <div className="space-y-6">
            <CardSkeleton />
            <TableSkeleton rows={8} />
          </div>
        }
      >
        <DetailContent id={Number(id)} />
      </Suspense>
    </div>
  );
}
