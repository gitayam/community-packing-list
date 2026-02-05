import type { ReactNode } from 'react';
import { Check, Trash2 } from 'lucide-react';
import { useSwipe } from '@/hooks/useSwipe';

interface SwipeableCardProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftLabel?: string;
  rightLabel?: string;
  disabled?: boolean;
}

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftLabel = 'Delete',
  rightLabel = 'Pack',
  disabled = false,
}: SwipeableCardProps) {
  const {
    offsetX,
    isSwiping,
    direction,
    handlers,
    isCommitting,
  } = useSwipe({
    onSwipeLeft,
    onSwipeRight,
    threshold: 80,
    commitThreshold: 150,
  });

  if (disabled) {
    return <div>{children}</div>;
  }

  return (
    <div className="relative overflow-hidden rounded-xl">
      {/* Left action (swipe right to reveal) */}
      <div
        className={`
          absolute inset-y-0 left-0 w-32 flex items-center justify-start pl-6
          transition-opacity duration-200
          ${direction === 'right' ? 'opacity-100' : 'opacity-0'}
          ${isCommitting && direction === 'right' ? 'bg-status-success' : 'bg-status-success/80'}
        `}
      >
        <div className={`flex items-center gap-2 text-white transition-transform ${isCommitting ? 'scale-110' : ''}`}>
          <Check size={24} />
          <span className="font-semibold">{rightLabel}</span>
        </div>
      </div>

      {/* Right action (swipe left to reveal) */}
      <div
        className={`
          absolute inset-y-0 right-0 w-32 flex items-center justify-end pr-6
          transition-opacity duration-200
          ${direction === 'left' ? 'opacity-100' : 'opacity-0'}
          ${isCommitting && direction === 'left' ? 'bg-status-danger' : 'bg-status-danger/80'}
        `}
      >
        <div className={`flex items-center gap-2 text-white transition-transform ${isCommitting ? 'scale-110' : ''}`}>
          <span className="font-semibold">{leftLabel}</span>
          <Trash2 size={24} />
        </div>
      </div>

      {/* Main card content */}
      <div
        {...handlers}
        className={`
          relative bg-dark-surface
          ${isSwiping ? '' : 'transition-transform duration-300 ease-out'}
        `}
        style={{
          transform: `translateX(${offsetX}px)`,
        }}
      >
        {children}
      </div>
    </div>
  );
}
