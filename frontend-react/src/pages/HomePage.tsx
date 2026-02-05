import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, Activity,
  Store, GraduationCap, MapPin, Target, Radio, Radar
} from 'lucide-react';
import { usePackingLists } from '@/hooks/usePackingLists';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
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
      <Card variant="tactical" className="max-w-2xl mx-auto">
        <div className="text-center py-12 px-6">
          {/* Alert icon with glow */}
          <div className="relative inline-flex items-center justify-center w-20 h-20 mb-6">
            <div className="absolute inset-0 rounded-full bg-status-danger/20 animate-pulse" />
            <div className="relative w-16 h-16 rounded-full bg-tactical-elevated border-2 border-status-danger flex items-center justify-center glow-danger">
              <AlertCircle size={32} className="text-status-danger" />
            </div>
          </div>

          <h3 className="font-display text-xl font-bold text-text-primary mb-3 tracking-wider">
            CONNECTION FAILED
          </h3>
          <p className="font-tactical text-xs text-text-secondary mb-8 max-w-md mx-auto uppercase tracking-wide leading-relaxed">
            Unable to establish link with backend systems. Verify API deployment status.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
            <Link to="/list/create">
              <Button variant="primary" size="md">
                <Plus size={16} className="mr-2" />
                Initialize New List
              </Button>
            </Link>
            <Button variant="secondary" size="md" onClick={() => window.location.reload()}>
              <Radio size={16} className="mr-2" />
              Retry Connection
            </Button>
          </div>

          <div className="p-4 rounded bg-tactical-surface border border-accent-amber/30">
            <p className="font-tactical text-[10px] text-accent-amber uppercase tracking-wider">
              <strong>// SYSTEM NOTE:</strong> Deploy backend API via BACKEND_DEPLOYMENT.md
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const totalLists = packingLists?.length || 0;

  return (
    <PullToRefresh onRefresh={handleRefresh}>
      {/* Mission Status Dashboard */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {/* Total Lists */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-cyan/50 transition-all">
          <div className="absolute top-0 right-0 w-16 h-16 bg-accent-cyan/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">TOTAL LISTS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-2xl md:text-3xl font-bold text-text-primary">{totalLists}</span>
              <Package className="text-accent-cyan opacity-50 group-hover:opacity-100 transition-opacity" size={20} />
            </div>
            <Badge variant="info" size="sm" pulse className="mt-2">ACTIVE</Badge>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-status-success/50 transition-all">
          <div className="absolute top-0 right-0 w-16 h-16 bg-status-success/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">RECENT OPS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-2xl md:text-3xl font-bold text-text-primary">3</span>
              <Activity className="text-status-success opacity-50 group-hover:opacity-100 transition-opacity" size={20} />
            </div>
            <Badge variant="success" size="sm" pulse className="mt-2">UPDATED</Badge>
          </div>
        </div>

        {/* Supply Points */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-amber/50 transition-all">
          <div className="absolute top-0 right-0 w-16 h-16 bg-accent-amber/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">SUPPLY POINTS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-2xl md:text-3xl font-bold text-text-primary">12</span>
              <Store className="text-accent-amber opacity-50 group-hover:opacity-100 transition-opacity" size={20} />
            </div>
            <Badge variant="warning" size="sm" className="mt-2">NEARBY</Badge>
          </div>
        </div>

        {/* Readiness */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-cyan/50 transition-all">
          <div className="absolute top-0 right-0 w-16 h-16 bg-accent-cyan/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">READINESS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-2xl md:text-3xl font-bold text-status-success">98%</span>
              <Target className="text-accent-cyan opacity-50 group-hover:opacity-100 transition-opacity" size={20} />
            </div>
            <Badge variant="tactical" size="sm" className="mt-2">OPTIMAL</Badge>
          </div>
        </div>
      </div>

      {/* Section Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-1 h-6 bg-accent-cyan rounded-full" />
          <h2 className="font-display text-lg md:text-xl font-bold text-text-primary tracking-wider">
            MISSION INVENTORY
          </h2>
        </div>
        {totalLists > 0 && (
          <Badge variant="default" size="md">
            {totalLists} {totalLists === 1 ? 'LIST' : 'LISTS'}
          </Badge>
        )}
      </div>

      {packingLists && packingLists.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {packingLists.map((plist, index) => (
            <Link
              key={plist.id}
              to={`/list/${plist.id}`}
              className="group opacity-0 animate-fadeInUp"
              style={{ animationDelay: `${index * 0.08}s`, animationFillMode: 'forwards' }}
            >
              <div className="h-full rounded-lg bg-tactical-elevated border border-tactical-border hover:border-accent-cyan/50 transition-all duration-300 cursor-pointer overflow-hidden relative">
                {/* Hover glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-accent-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                {/* Corner brackets */}
                <div className="absolute top-2 left-2 w-2.5 h-2.5 border-l border-t border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute top-2 right-2 w-2.5 h-2.5 border-r border-t border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute bottom-2 left-2 w-2.5 h-2.5 border-l border-b border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-r border-b border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />

                <div className="flex flex-col h-full p-4 relative">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0 pr-3">
                      <h3 className="font-display text-sm font-bold text-text-primary group-hover:text-accent-cyan transition-colors mb-2 truncate tracking-wide">
                        {plist.name.toUpperCase()}
                      </h3>
                      <div className="flex flex-wrap gap-1">
                        {plist.type && (
                          <Badge variant="info" size="sm">{plist.type}</Badge>
                        )}
                        {plist.school && (
                          <Badge variant="default" size="sm">
                            <GraduationCap size={9} className="mr-1" />
                            {plist.school.name}
                          </Badge>
                        )}
                        {plist.base && (
                          <Badge variant="success" size="sm">
                            <MapPin size={9} className="mr-1" />
                            {plist.base.name}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 w-10 h-10 rounded bg-accent-cyan/10 border border-accent-cyan/30 flex items-center justify-center group-hover:glow-cyan transition-all">
                      <Package className="text-accent-cyan" size={18} />
                    </div>
                  </div>

                  {/* Description */}
                  {plist.description && (
                    <p className="text-text-secondary text-xs mb-3 line-clamp-2 flex-1 leading-relaxed">
                      {plist.description}
                    </p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-3 border-t border-tactical-border">
                    <div className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse" />
                      <span className="font-tactical text-[9px] text-status-success uppercase tracking-wider">READY</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-accent-cyan font-tactical text-[9px] uppercase tracking-wider group-hover:gap-2.5 transition-all">
                      <span>ACCESS</span>
                      <Eye size={12} />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <Card variant="tactical" className="text-center py-12">
          <div className="max-w-md mx-auto">
            <div className="relative inline-flex items-center justify-center w-20 h-20 mb-6">
              <div className="absolute inset-0 rounded-full border border-dashed border-accent-cyan/30 animate-spin-slow" />
              <div className="relative w-14 h-14 rounded-full bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center">
                <Radar className="text-accent-cyan" size={28} />
              </div>
            </div>
            <h3 className="font-display text-xl font-bold text-text-primary mb-3 tracking-wider">
              NO ACTIVE MISSIONS
            </h3>
            <p className="text-text-secondary text-sm mb-8 leading-relaxed">
              Initialize your first packing list to begin mission planning. Upload existing lists or create new from scratch.
            </p>
            <Link to="/list/create">
              <Button variant="primary" size="lg">
                <Plus size={18} className="mr-2" />
                Initialize First List
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </PullToRefresh>
  );
}

export function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-lg mb-8 border border-tactical-border">
        {/* Background layers */}
        <div className="absolute inset-0 bg-gradient-to-br from-tactical-surface via-tactical-elevated to-tactical-surface" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-accent-cyan/8 via-transparent to-transparent" />

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `
              linear-gradient(#00F0FF08 1px, transparent 1px),
              linear-gradient(90deg, #00F0FF08 1px, transparent 1px)
            `,
            backgroundSize: '30px 30px'
          }}
        />

        {/* Animated scan line */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-accent-cyan/60 to-transparent animate-scan" />
        </div>

        {/* Corner decorations */}
        <div className="absolute top-3 left-3 w-6 h-6 border-l-2 border-t-2 border-accent-cyan/40" />
        <div className="absolute top-3 right-3 w-6 h-6 border-r-2 border-t-2 border-accent-cyan/40" />
        <div className="absolute bottom-3 left-3 w-6 h-6 border-l-2 border-b-2 border-accent-cyan/40" />
        <div className="absolute bottom-3 right-3 w-6 h-6 border-r-2 border-b-2 border-accent-cyan/40" />

        <div className="relative px-5 py-10 md:py-14">
          <div className="max-w-2xl mx-auto text-center">
            {/* Status badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded bg-tactical-elevated/80 border border-status-success/30 mb-5">
              <div className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse" />
              <span className="font-tactical text-[9px] text-status-success uppercase tracking-[0.2em]">
                All Systems Operational
              </span>
            </div>

            {/* Heading */}
            <h1 className="font-display text-3xl sm:text-4xl md:text-5xl font-black text-text-primary mb-3 tracking-wider leading-tight">
              MISSION
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan via-status-success to-accent-cyan text-glow-cyan">
                READY
              </span>
            </h1>

            {/* Subtitle */}
            <p className="font-tactical text-[10px] md:text-xs text-text-secondary mb-8 max-w-lg mx-auto tracking-wide uppercase leading-relaxed">
              Community-driven packing lists for military schools, training courses, and deployments
            </p>

            {/* CTA Buttons - Desktop */}
            <div className="hidden md:flex flex-wrap items-center justify-center gap-3">
              <Link to="/list/create">
                <Button variant="primary" size="lg">
                  <Plus size={18} className="mr-2" />
                  New Mission
                </Button>
              </Link>
              <Link to="/list/upload">
                <Button variant="secondary" size="lg">
                  <Upload size={18} className="mr-2" />
                  Import List
                </Button>
              </Link>
              <Link to="/stores">
                <Button variant="secondary" size="lg">
                  <Store size={18} className="mr-2" />
                  Supply Points
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
