import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, CheckCircle2,
  TrendingUp, Store, GraduationCap, MapPin
} from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatsCard } from '@/components/ui/StatsCard';
import { EmptyState } from '@/components/ui/EmptyState';
import { ListSkeleton } from '@/components/ui/Skeleton';

function PackingListsContent() {
  const { data: packingLists, error } = usePackingLists();

  if (error) {
    return (
      <Card>
        <div className="flex items-center gap-3 text-status-required">
          <AlertCircle size={20} />
          <span>Error loading packing lists. Please try again.</span>
        </div>
      </Card>
    );
  }

  const totalLists = packingLists?.length || 0;

  return (
    <>
      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatsCard
          title="Total Lists"
          value={totalLists}
          icon={Package}
          variant="military"
        />
        <StatsCard
          title="Quick Access"
          value="3 Recent"
          icon={TrendingUp}
          variant="default"
        />
        <StatsCard
          title="Nearby Stores"
          value="12 Found"
          icon={Store}
          variant="success"
        />
      </div>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-military-dark">Your Packing Lists</h2>
        {totalLists > 0 && (
          <Badge variant="military">
            {totalLists} {totalLists === 1 ? 'List' : 'Lists'}
          </Badge>
        )}
      </div>

      {packingLists && packingLists.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {packingLists.map((plist, index) => (
            <Link
              key={plist.id}
              to={`/list/${plist.id}`}
              className="group animate-fadeIn"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <Card className="h-full hover:shadow-lg transition-all duration-300 hover:border-military-olive/40 hover:-translate-y-1 cursor-pointer">
                <div className="flex flex-col h-full">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-military-navy group-hover:text-military-olive transition-colors mb-2">
                        {plist.name}
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {plist.type && (
                          <Badge variant="default" size="sm">
                            {plist.type}
                          </Badge>
                        )}
                        {plist.school && (
                          <Badge variant="military" size="sm">
                            <GraduationCap size={12} className="mr-1" />
                            {plist.school.name}
                          </Badge>
                        )}
                        {plist.base && (
                          <Badge variant="info" size="sm">
                            <MapPin size={12} className="mr-1" />
                            {plist.base.name}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="rounded-full bg-military-sand/40 p-3 group-hover:bg-military-olive/10 transition-colors">
                      <Package className="text-military-olive" size={24} />
                    </div>
                  </div>

                  {/* Description */}
                  {plist.description && (
                    <p className="text-gray-600 mb-4 line-clamp-2 flex-1">
                      {plist.description}
                    </p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <CheckCircle2 size={16} className="text-status-complete" />
                      <span>Ready to pack</span>
                    </div>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="group-hover:bg-military-navy group-hover:text-white transition-colors"
                    >
                      <Eye size={16} className="mr-1" />
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Package}
          title="No Packing Lists Yet"
          description="Get started by creating your first packing list or uploading an existing one. Build your mission-ready checklist in minutes."
          action={{
            label: 'Create Your First List',
            onClick: () => window.location.href = '/list/create',
            icon: Plus,
          }}
        />
      )}
    </>
  );
}

export function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-military-navy via-military-navy to-military-olive rounded-xl mb-8 shadow-xl">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="relative px-8 py-12 md:py-16">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-military-olive/20 text-military-sand px-3 py-1.5 rounded-full text-sm font-medium mb-6 border border-military-sand/20">
              <CheckCircle2 size={16} />
              <span>Mission-Ready Preparation</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
              Pack Smart,
              <br />
              Deploy Ready
            </h1>
            <p className="text-lg md:text-xl text-military-sand/90 mb-8 max-w-2xl">
              Community-driven packing lists for military schools, training courses, and deployments.
              Get the gear you need, when you need it.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/list/create">
                <Button
                  variant="success"
                  className="bg-status-complete hover:bg-status-complete/90 text-white border-0 shadow-lg hover:shadow-xl transition-all"
                >
                  <Plus className="mr-2" size={20} />
                  Create New List
                </Button>
              </Link>
              <Link to="/list/upload">
                <Button
                  variant="secondary"
                  className="bg-white/10 hover:bg-white/20 text-white border-white/30 backdrop-blur-sm"
                >
                  <Upload className="mr-2" size={20} />
                  Upload Existing List
                </Button>
              </Link>
              <Link to="/stores">
                <Button
                  variant="secondary"
                  className="bg-white/10 hover:bg-white/20 text-white border-white/30 backdrop-blur-sm"
                >
                  <Store className="mr-2" size={20} />
                  Find Stores
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Suspense fallback={<ListSkeleton items={5} />}>
        <PackingListsContent />
      </Suspense>
    </div>
  );
}
