import { Link } from 'react-router-dom';
import { Plus, Upload, Eye } from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export function HomePage() {
  const { data: packingLists, isLoading, error } = usePackingLists();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-lg text-military-dark">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="text-status-required">Error loading packing lists. Please try again.</div>
      </Card>
    );
  }

  return (
    <div>
      <Card className="mb-8">
        <h2 className="text-3xl font-bold text-military-dark mb-4">Mission-Ready Packing, Simplified.</h2>
        <p className="text-lg text-gray-600 mb-6">
          Find, create, or upload packing lists for your next military school,
          assessment, or deployment.
        </p>
        <div className="flex flex-wrap gap-4">
          <Link to="/list/create">
            <Button variant="success">
              <Plus className="inline mr-2" size={18} />
              Create New List
            </Button>
          </Link>
          <Link to="/list/upload">
            <Button variant="secondary">
              <Upload className="inline mr-2" size={18} />
              Upload List
            </Button>
          </Link>
        </div>
      </Card>

      <h2 className="text-2xl font-semibold text-military-dark mb-4">Existing Packing Lists</h2>

      {packingLists && packingLists.length > 0 ? (
        <div className="space-y-4">
          {packingLists.map((plist) => (
            <Card key={plist.id}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">
                      <Link
                        to={`/list/${plist.id}`}
                        className="text-military-navy hover:text-military-olive transition-colors"
                      >
                        {plist.name}
                      </Link>
                    </h3>
                    {plist.school && (
                      <span className="school-tag">
                        {plist.school.name}
                      </span>
                    )}
                  </div>
                  {plist.description && (
                    <p className="text-gray-600">{plist.description}</p>
                  )}
                </div>
                <Link to={`/list/${plist.id}`}>
                  <Button size="sm">
                    <Eye className="inline mr-1" size={16} />
                    View
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-gray-600 text-center py-8">
            No packing lists found. Create or upload your first list to get started!
          </p>
        </Card>
      )}
    </div>
  );
}
