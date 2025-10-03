import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { usePackingList } from '@/hooks/usePackingList';
import { PackingListDetail } from '@/components/packing-lists/PackingListDetail';

export function ListDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, isLoading, error } = usePackingList(Number(id));

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-lg text-military-dark">Loading packing list...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Button variant="secondary" onClick={() => navigate('/')} className="mb-4">
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <Card>
          <div className="text-status-required">
            Error loading packing list. Please try again.
          </div>
        </Card>
      </div>
    );
  }

  if (!data) {
    return (
      <div>
        <Button variant="secondary" onClick={() => navigate('/')} className="mb-4">
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <Card>
          <div className="text-gray-600">Packing list not found.</div>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <Button variant="secondary" onClick={() => navigate('/')} className="mb-4">
        <ArrowLeft className="inline mr-2" size={16} />
        Back to Lists
      </Button>
      <PackingListDetail data={data} />
    </div>
  );
}
