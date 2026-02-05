import { useState, useRef } from 'react';
import type { ReactNode, TouchEvent } from 'react';
import { ArrowDown, Check, Loader2 } from 'lucide-react';

interface PullToRefreshProps {
  children: ReactNode;
  onRefresh: () => Promise<void>;
  disabled?: boolean;
}

type RefreshState = 'idle' | 'pulling' | 'ready' | 'refreshing' | 'complete';

export function PullToRefresh({ children, onRefresh, disabled = false }: PullToRefreshProps) {
  const [state, setState] = useState<RefreshState>('idle');
  const [pullDistance, setPullDistance] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);

  const PULL_THRESHOLD = 80;
  const MAX_PULL = 120;

  const handleTouchStart = (e: TouchEvent) => {
    if (disabled || state === 'refreshing') return;
    if (containerRef.current && containerRef.current.scrollTop === 0) {
      startY.current = e.touches[0].clientY;
      setState('pulling');
    }
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (state !== 'pulling' && state !== 'ready') return;

    const currentY = e.touches[0].clientY;
    const diff = currentY - startY.current;

    if (diff > 0) {
      const resistance = 0.4;
      const distance = Math.min(diff * resistance, MAX_PULL);
      setPullDistance(distance);
      setState(distance >= PULL_THRESHOLD ? 'ready' : 'pulling');
    }
  };

  const handleTouchEnd = async () => {
    if (state === 'ready') {
      setState('refreshing');
      setPullDistance(60);

      try {
        await onRefresh();
        setState('complete');
        setTimeout(() => {
          setState('idle');
          setPullDistance(0);
        }, 500);
      } catch {
        setState('idle');
        setPullDistance(0);
      }
    } else {
      setState('idle');
      setPullDistance(0);
    }
  };

  const getIndicator = () => {
    switch (state) {
      case 'pulling':
        return (
          <div className="flex items-center gap-2 text-text-secondary">
            <ArrowDown size={18} className="transition-transform" style={{ transform: `rotate(${Math.min(pullDistance / PULL_THRESHOLD * 180, 180)}deg)` }} />
            <span className="font-tactical text-[10px] uppercase tracking-wider">Pull to refresh</span>
          </div>
        );
      case 'ready':
        return (
          <div className="flex items-center gap-2 text-accent-cyan">
            <ArrowDown size={18} className="rotate-180" />
            <span className="font-tactical text-[10px] uppercase tracking-wider font-medium">Release to sync</span>
          </div>
        );
      case 'refreshing':
        return (
          <div className="flex items-center gap-2 text-accent-cyan">
            <Loader2 size={18} className="animate-spin" />
            <span className="font-tactical text-[10px] uppercase tracking-wider">Syncing...</span>
          </div>
        );
      case 'complete':
        return (
          <div className="flex items-center gap-2 text-status-success">
            <Check size={18} />
            <span className="font-tactical text-[10px] uppercase tracking-wider font-medium">Synced!</span>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {/* Pull indicator */}
      <div
        className={`
          absolute left-0 right-0 flex items-center justify-center
          transition-all duration-200 overflow-hidden
          ${state === 'idle' ? 'opacity-0' : 'opacity-100'}
        `}
        style={{
          height: `${pullDistance}px`,
          top: 0,
        }}
      >
        {getIndicator()}
      </div>

      {/* Content */}
      <div
        className={`transition-transform ${state === 'idle' ? 'duration-300' : 'duration-0'}`}
        style={{
          transform: `translateY(${pullDistance}px)`,
        }}
      >
        {children}
      </div>
    </div>
  );
}
