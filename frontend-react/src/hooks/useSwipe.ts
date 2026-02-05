import { useState, useRef, type TouchEvent } from 'react';

interface SwipeState {
  offsetX: number;
  isSwiping: boolean;
  direction: 'left' | 'right' | null;
}

interface UseSwipeOptions {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  threshold?: number;
  commitThreshold?: number;
}

export function useSwipe({
  onSwipeLeft,
  onSwipeRight,
  threshold = 80,
  commitThreshold = 150,
}: UseSwipeOptions) {
  const [state, setState] = useState<SwipeState>({
    offsetX: 0,
    isSwiping: false,
    direction: null,
  });

  const startX = useRef(0);
  const currentX = useRef(0);

  const handleTouchStart = (e: TouchEvent) => {
    startX.current = e.touches[0].clientX;
    setState(s => ({ ...s, isSwiping: true }));
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!state.isSwiping) return;

    currentX.current = e.touches[0].clientX;
    const diff = currentX.current - startX.current;

    // Add resistance at edges
    const resistance = 0.5;
    const resistedDiff = diff > 0
      ? Math.min(diff, commitThreshold + (diff - commitThreshold) * resistance)
      : Math.max(diff, -commitThreshold + (diff + commitThreshold) * resistance);

    setState({
      offsetX: resistedDiff,
      isSwiping: true,
      direction: diff > 0 ? 'right' : diff < 0 ? 'left' : null,
    });
  };

  const handleTouchEnd = () => {
    const { offsetX } = state;

    if (offsetX >= commitThreshold && onSwipeRight) {
      onSwipeRight();
    } else if (offsetX <= -commitThreshold && onSwipeLeft) {
      onSwipeLeft();
    }

    setState({ offsetX: 0, isSwiping: false, direction: null });
  };

  return {
    ...state,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
    },
    isRevealed: Math.abs(state.offsetX) >= threshold,
    isCommitting: Math.abs(state.offsetX) >= commitThreshold,
  };
}
