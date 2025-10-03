import { CheckCircle2, Package, AlertTriangle } from 'lucide-react';
import { Progress } from '@/components/ui/Progress';
import { Card } from '@/components/ui/Card';

interface ProgressStatsProps {
  totalItems: number;
  packedItems: number;
  requiredItems: number;
  packedRequired: number;
}

export function ProgressStats({
  totalItems,
  packedItems,
  requiredItems,
  packedRequired,
}: ProgressStatsProps) {
  const overallProgress = totalItems > 0 ? Math.round((packedItems / totalItems) * 100) : 0;
  const requiredProgress = requiredItems > 0 ? Math.round((packedRequired / requiredItems) * 100) : 0;

  // Determine variant based on progress
  const getVariant = (progress: number): 'danger' | 'warning' | 'success' => {
    if (progress < 25) return 'danger';
    if (progress < 75) return 'warning';
    return 'success';
  };

  const getMissionStatus = (progress: number): string => {
    if (progress === 100) return 'Mission Ready';
    if (progress >= 75) return 'Almost Ready';
    if (progress >= 50) return 'In Progress';
    if (progress >= 25) return 'Just Started';
    return 'Not Started';
  };

  return (
    <Card className="bg-gradient-to-br from-military-navy to-military-olive text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">Mission Status</h3>
        <div className="flex items-center gap-2">
          {overallProgress === 100 ? (
            <CheckCircle2 className="text-status-complete" size={24} />
          ) : overallProgress >= 50 ? (
            <Package className="text-yellow-300" size={24} />
          ) : (
            <AlertTriangle className="text-status-required" size={24} />
          )}
          <span className="text-2xl font-bold">{overallProgress}%</span>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-military-sand/90">Overall Progress</span>
          <span className="text-sm text-military-sand/90">
            {packedItems} / {totalItems} items
          </span>
        </div>
        <Progress
          value={overallProgress}
          max={100}
          variant={getVariant(overallProgress)}
          size="lg"
          className="bg-white/20"
        />
        <p className="text-xs text-military-sand/80 mt-1">{getMissionStatus(overallProgress)}</p>
      </div>

      {requiredItems > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-military-sand/90">Required Items</span>
            <span className="text-sm text-military-sand/90">
              {packedRequired} / {requiredItems} items
            </span>
          </div>
          <Progress
            value={requiredProgress}
            max={100}
            variant={getVariant(requiredProgress)}
            size="md"
            className="bg-white/20"
          />
          <p className="text-xs text-military-sand/80 mt-1">
            {requiredProgress === 100
              ? 'All required items packed!'
              : `${requiredItems - packedRequired} required items remaining`
            }
          </p>
        </div>
      )}
    </Card>
  );
}
