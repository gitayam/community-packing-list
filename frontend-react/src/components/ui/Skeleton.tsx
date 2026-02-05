interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`bg-tactical-elevated rounded animate-shimmer ${className}`}
      style={{
        backgroundImage: 'linear-gradient(90deg, #1A1F29 0%, #2A3441 50%, #1A1F29 100%)',
        backgroundSize: '200% 100%',
      }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg bg-tactical-elevated border border-tactical-border p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <div className="flex gap-1.5">
            <Skeleton className="h-4 w-14" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
        <Skeleton className="h-10 w-10 rounded" />
      </div>
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

export function ListSkeleton({ items = 3 }: { items?: number }) {
  return (
    <div className="space-y-4">
      {/* Stats skeleton */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-lg bg-tactical-elevated border border-tactical-border p-4">
            <Skeleton className="h-3 w-20 mb-2" />
            <Skeleton className="h-7 w-12 mb-2" />
            <Skeleton className="h-4 w-14" />
          </div>
        ))}
      </div>

      {/* Header skeleton */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Skeleton className="w-1 h-6" />
          <Skeleton className="h-6 w-40" />
        </div>
        <Skeleton className="h-5 w-16" />
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: items }).map((_, i) => (
          <div key={i} className="opacity-0 animate-fadeInUp" style={{ animationDelay: `${i * 0.08}s`, animationFillMode: 'forwards' }}>
            <CardSkeleton />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ItemSkeleton() {
  return (
    <div className="rounded-lg bg-tactical-elevated border border-tactical-border p-4">
      <div className="flex items-start gap-3">
        <Skeleton className="h-10 w-10 rounded flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <div className="flex gap-1.5">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-14" />
          </div>
        </div>
      </div>
    </div>
  );
}
