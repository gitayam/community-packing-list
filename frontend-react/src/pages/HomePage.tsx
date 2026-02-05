import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, CheckCircle2,
  TrendingUp, Store, GraduationCap, MapPin
} from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { PullToRefresh } from '@/components/ui/PullToRefresh';
import { useQueryClient } from '@tanstack/react-query';

function PackingListsContent() {
  const { data: packingLists, error, refetch } = usePackingLists();
  const queryClient = useQueryClient();

  const handleRefresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['packingLists'] });
    await refetch();
  };

  if (error) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="glass rounded-2xl overflow-hidden border border-status-danger/30">
          <div className="text-center py-12 px-6">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6 bg-status-danger/20">
              <AlertCircle size={40} className="text-status-danger" />
            </div>

            <h3 className="text-2xl font-bold text-text-primary mb-3">
              Unable to Load Packing Lists
            </h3>

            <p className="text-lg text-text-secondary mb-8 max-w-md mx-auto">
              The backend API is not available. This is expected if the Django backend hasn't been deployed yet.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
              <Link to="/list/create">
                <Button className="bg-accent-blue hover:bg-accent-glow glow-blue text-white">
                  <Plus size={20} className="mr-2" />
                  Create Your First List
                </Button>
              </Link>
              <Button
                variant="secondary"
                onClick={() => window.location.reload()}
                className="glass"
              >
                Try Again
              </Button>
            </div>

            <div className="glass p-4 rounded-xl max-w-lg mx-auto">
              <p className="text-sm text-accent-glow">
                <strong>Note:</strong> To connect to a live backend, deploy the Django API using the instructions in{' '}
                <code className="px-2 py-1 rounded bg-dark-elevated font-mono text-sm">
                  BACKEND_DEPLOYMENT.md
                </code>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalLists = packingLists?.length || 0;

  return (
    <PullToRefresh onRefresh={handleRefresh}>
      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="glass rounded-xl p-5 border border-dark-border hover:border-accent-blue/50 transition-all group">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 rounded-xl bg-accent-blue/20 flex items-center justify-center group-hover:glow-blue-sm transition-all">
              <Package className="text-accent-blue" size={24} />
            </div>
            <Badge className="bg-accent-muted text-accent-glow border-accent-blue/30">Active</Badge>
          </div>
          <div className="text-3xl font-black text-text-primary mb-1">{totalLists}</div>
          <div className="text-sm font-medium text-text-secondary">Total Lists</div>
        </div>

        <div className="glass rounded-xl p-5 border border-dark-border hover:border-status-success/50 transition-all group">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 rounded-xl bg-status-success/20 flex items-center justify-center group-hover:glow-success transition-all">
              <TrendingUp className="text-status-success" size={24} />
            </div>
            <Badge className="bg-status-success/20 text-status-success border-status-success/30">Updated</Badge>
          </div>
          <div className="text-3xl font-black text-text-primary mb-1">3</div>
          <div className="text-sm font-medium text-text-secondary">Recent Lists</div>
        </div>

        <div className="glass rounded-xl p-5 border border-dark-border hover:border-purple-500/50 transition-all group">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <Store className="text-purple-400" size={24} />
            </div>
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">Nearby</Badge>
          </div>
          <div className="text-3xl font-black text-text-primary mb-1">12</div>
          <div className="text-sm font-medium text-text-secondary">Stores Found</div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-text-primary">Your Packing Lists</h2>
        {totalLists > 0 && (
          <Badge className="bg-dark-elevated text-text-secondary border-dark-border px-3 py-1.5">
            {totalLists} {totalLists === 1 ? 'List' : 'Lists'}
          </Badge>
        )}
      </div>

      {packingLists && packingLists.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {packingLists.map((plist, index) => (
            <Link
              key={plist.id}
              to={`/list/${plist.id}`}
              className="group animate-fadeIn"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="h-full glass rounded-xl border border-dark-border hover:border-accent-blue/50 hover:glow-blue-sm transition-all duration-300 cursor-pointer overflow-hidden">
                <div className="flex flex-col h-full p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-text-primary group-hover:text-accent-glow transition-colors mb-3 truncate">
                        {plist.name}
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {plist.type && (
                          <Badge className="bg-accent-muted text-accent-glow border-accent-blue/30 text-xs">
                            {plist.type}
                          </Badge>
                        )}
                        {plist.school && (
                          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                            <GraduationCap size={12} className="mr-1" />
                            {plist.school.name}
                          </Badge>
                        )}
                        {plist.base && (
                          <Badge className="bg-status-success/20 text-status-success border-status-success/30 text-xs">
                            <MapPin size={12} className="mr-1" />
                            {plist.base.name}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 ml-4 w-12 h-12 rounded-xl bg-accent-blue/20 flex items-center justify-center group-hover:glow-blue-sm transition-all">
                      <Package className="text-accent-blue" size={22} />
                    </div>
                  </div>

                  {plist.description && (
                    <p className="text-text-secondary mb-4 line-clamp-2 flex-1 text-sm leading-relaxed">
                      {plist.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between pt-4 border-t border-dark-border">
                    <div className="flex items-center gap-2 text-sm text-text-muted font-medium">
                      <CheckCircle2 size={16} className="text-status-success" />
                      <span>Ready</span>
                    </div>
                    <div className="flex items-center gap-1 text-accent-blue font-semibold text-sm group-hover:gap-2 transition-all">
                      <span>View</span>
                      <Eye size={16} />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="glass rounded-xl p-12 border border-dark-border text-center">
          <div className="max-w-md mx-auto">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-accent-blue/20 mb-6">
              <Package className="text-accent-blue" size={40} />
            </div>
            <h3 className="text-2xl font-bold text-text-primary mb-3">No Packing Lists Yet</h3>
            <p className="text-text-secondary mb-8 leading-relaxed">
              Get started by creating your first packing list or uploading an existing one.
            </p>
            <Link to="/list/create">
              <Button className="bg-accent-blue hover:bg-accent-glow glow-blue text-white px-8 py-3 rounded-xl font-semibold">
                <Plus size={20} className="mr-2" />
                Create Your First List
              </Button>
            </Link>
          </div>
        </div>
      )}
    </PullToRefresh>
  );
}

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl mb-8 border border-dark-border">
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #0F172A 100%)'
          }}
        />
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(59, 130, 246, 0.5) 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}
        />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent-blue/20 rounded-full blur-3xl" />

        <div className="relative px-6 py-16 md:py-20">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-6 glass border border-status-success/30">
              <CheckCircle2 size={16} className="text-status-success" />
              <span className="text-status-success">Mission-Ready Preparation</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-text-primary mb-4 leading-tight">
              Pack Smart,
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-blue to-status-success text-glow">
                Deploy Ready
              </span>
            </h1>

            <p className="text-lg text-text-secondary mb-10 max-w-xl mx-auto leading-relaxed">
              Community-driven packing lists for military schools, training courses, and deployments.
            </p>

            <div className="hidden md:flex flex-wrap items-center justify-center gap-4">
              <Link to="/list/create">
                <Button className="bg-accent-blue hover:bg-accent-glow glow-blue text-white px-8 py-4 text-base font-semibold rounded-xl">
                  <Plus size={20} className="mr-2" />
                  Create New List
                </Button>
              </Link>
              <Link to="/list/upload">
                <Button variant="secondary" className="glass px-8 py-4 text-base font-semibold rounded-xl">
                  <Upload size={20} className="mr-2" />
                  Upload List
                </Button>
              </Link>
              <Link to="/stores">
                <Button variant="secondary" className="glass px-8 py-4 text-base font-semibold rounded-xl">
                  <Store size={20} className="mr-2" />
                  Find Stores
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <Suspense fallback={<ListSkeleton items={5} />}>
        <PackingListsContent />
      </Suspense>
    </div>
  );
}
