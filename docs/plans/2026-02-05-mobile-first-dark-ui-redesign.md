# Mobile-First Dark UI Redesign

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Community Packing List into a modern dark-themed mobile-first app with bottom navigation, swipe gestures, pull-to-refresh, and glassmorphism effects.

**Architecture:** Update Tailwind config with dark theme colors, create new BottomNav and SwipeableCard components, add touch gesture handling with CSS transforms, implement pull-to-refresh with intersection observer.

**Tech Stack:** React 19, Tailwind CSS 4, CSS transforms for gestures (no external libraries), Lucide icons

---

## Design Tokens

```
Background:     #0F172A (slate-900)
Surface:        #1E293B (slate-800)
Surface Elevated: #334155 (slate-700)
Border:         #475569 (slate-600)
Primary:        #3B82F6 (blue-500)
Primary Glow:   #60A5FA (blue-400)
Text Primary:   #F8FAFC (slate-50)
Text Secondary: #94A3B8 (slate-400)
Success:        #10B981
Danger:         #EF4444
Warning:        #F59E0B
```

---

### Task 1: Update Tailwind Config with Dark Theme

**Files:**
- Modify: `frontend-react/tailwind.config.js`
- Modify: `frontend-react/src/index.css`

**Step 1: Update tailwind.config.js with dark theme colors**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0F172A',
          surface: '#1E293B',
          elevated: '#334155',
          border: '#475569',
        },
        accent: {
          blue: '#3B82F6',
          glow: '#60A5FA',
          muted: '#1E3A5F',
        },
        status: {
          success: '#10B981',
          danger: '#EF4444',
          warning: '#F59E0B',
        },
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        checkmark: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '50%': { transform: 'scale(1.2)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)' },
          '50%': { boxShadow: '0 0 30px rgba(59, 130, 246, 0.6)' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s linear infinite',
        fadeIn: 'fadeIn 0.3s ease-out forwards',
        slideDown: 'slideDown 0.2s ease-out',
        slideUp: 'slideUp 0.2s ease-out',
        scaleIn: 'scaleIn 0.2s ease-out',
        checkmark: 'checkmark 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        pulse: 'pulse 2s ease-in-out infinite',
        glow: 'glow 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
```

**Step 2: Update index.css with dark theme base styles**

Replace the entire file with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Dark Theme Design System */

:root {
  --dark-bg: #0F172A;
  --dark-surface: #1E293B;
  --dark-elevated: #334155;
  --dark-border: #475569;
  --accent-blue: #3B82F6;
  --accent-glow: #60A5FA;
  --accent-muted: #1E3A5F;
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --status-success: #10B981;
  --status-danger: #EF4444;
  --status-warning: #F59E0B;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
  background: var(--dark-bg);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Glassmorphism Utilities */
@layer utilities {
  .glass {
    background: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(71, 85, 105, 0.5);
  }

  .glass-strong {
    background: rgba(30, 41, 59, 0.9);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(71, 85, 105, 0.6);
  }

  .glow-blue {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4),
                0 0 40px rgba(59, 130, 246, 0.2);
  }

  .glow-blue-sm {
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
  }

  .glow-success {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
  }

  .glow-danger {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
  }

  .text-glow {
    text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
  }

  /* Safe area padding for notched phones */
  .pb-safe {
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }

  .mb-safe {
    margin-bottom: env(safe-area-inset-bottom, 0px);
  }

  /* Touch-friendly tap targets */
  .tap-target {
    min-height: 44px;
    min-width: 44px;
  }

  /* Active state for touch */
  .tap-active:active {
    transform: scale(0.97);
    transition: transform 0.1s ease-out;
  }
}

/* Scrollbar styling for dark theme */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--dark-surface);
}

::-webkit-scrollbar-thumb {
  background: var(--dark-border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--accent-blue);
}

/* Selection styling */
::selection {
  background: rgba(59, 130, 246, 0.3);
  color: var(--text-primary);
}
```

**Step 3: Verify changes compile**

Run: `cd /Users/sac/Git/community-packing-list/frontend-react && npm run build`

Expected: Build succeeds with no errors

**Step 4: Commit foundation changes**

```bash
git add frontend-react/tailwind.config.js frontend-react/src/index.css
git commit -m "feat: Add dark theme foundation with glassmorphism utilities

- Dark color palette (slate-900 base, blue-500 accent)
- Glass effect utilities
- Glow effects for interactive elements
- Safe area padding for notched phones
- Custom scrollbar styling

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Create Bottom Navigation Component

**Files:**
- Create: `frontend-react/src/components/layout/BottomNav.tsx`
- Modify: `frontend-react/src/components/layout/Layout.tsx`

**Step 1: Create BottomNav.tsx**

```tsx
import { Link, useLocation } from 'react-router-dom';
import { Home, Package, Plus, Store } from 'lucide-react';

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/lists', icon: Package, label: 'Lists' },
  { path: '/list/create', icon: Plus, label: 'Add', isAction: true },
  { path: '/stores', icon: Store, label: 'Stores' },
];

export function BottomNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div className="glass-strong border-t border-dark-border pb-safe">
        <div className="flex items-center justify-around h-16">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path ||
              (item.path === '/lists' && location.pathname.startsWith('/list/') && !location.pathname.includes('create'));
            const Icon = item.icon;

            if (item.isAction) {
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="relative -mt-6"
                >
                  <div className="flex items-center justify-center w-14 h-14 rounded-full bg-accent-blue glow-blue tap-active transition-all duration-200 hover:scale-105">
                    <Icon size={24} className="text-white" />
                  </div>
                </Link>
              );
            }

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex flex-col items-center justify-center flex-1 h-full tap-active
                  transition-all duration-200
                  ${isActive ? 'text-accent-blue' : 'text-text-secondary hover:text-text-primary'}
                `}
              >
                <div className={`
                  relative p-2 rounded-xl transition-all duration-200
                  ${isActive ? 'bg-accent-muted' : ''}
                `}>
                  <Icon size={22} />
                  {isActive && (
                    <div className="absolute inset-0 rounded-xl glow-blue-sm opacity-50" />
                  )}
                </div>
                <span className={`text-xs mt-1 font-medium ${isActive ? 'text-accent-blue' : ''}`}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
```

**Step 2: Update Layout.tsx to include BottomNav**

```tsx
import { Header } from './Header';
import { Footer } from './Footer';
import { BottomNav } from './BottomNav';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-dark-bg">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6 pb-24 md:pb-6">
        {children}
      </main>
      <Footer />
      <BottomNav />
    </div>
  );
}
```

**Step 3: Verify component renders**

Run: `cd /Users/sac/Git/community-packing-list/frontend-react && npm run dev`

Expected: Bottom nav visible on mobile viewport, hidden on desktop

**Step 4: Commit bottom nav**

```bash
git add frontend-react/src/components/layout/BottomNav.tsx frontend-react/src/components/layout/Layout.tsx
git commit -m "feat: Add bottom navigation bar for mobile

- Fixed bottom nav with glass effect
- Floating action button for Add
- Active state with blue glow
- Hidden on desktop (md:hidden)
- Safe area padding for notched phones

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Update Header for Dark Theme

**Files:**
- Modify: `frontend-react/src/components/layout/Header.tsx`

**Step 1: Rewrite Header.tsx with dark theme**

```tsx
import { Link } from 'react-router-dom';
import { Package, Store, Search } from 'lucide-react';
import { useState } from 'react';

export function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 glass-strong border-b border-dark-border">
      <div className="container mx-auto px-4">
        {/* Mobile Header */}
        <div className="flex md:hidden items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2 text-lg font-bold text-text-primary">
            <div className="w-8 h-8 rounded-lg bg-accent-blue flex items-center justify-center">
              <Package size={18} className="text-white" />
            </div>
            <span>CPL</span>
          </Link>
          <button
            onClick={() => setIsSearchOpen(!isSearchOpen)}
            className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-dark-elevated transition-colors tap-active"
          >
            <Search size={22} />
          </button>
        </div>

        {/* Desktop Header */}
        <nav className="hidden md:flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3 text-xl font-bold text-text-primary hover:text-accent-glow transition-colors">
            <div className="w-10 h-10 rounded-xl bg-accent-blue glow-blue-sm flex items-center justify-center">
              <Package size={22} className="text-white" />
            </div>
            <span>Community Packing List</span>
          </Link>

          <div className="flex items-center gap-1">
            <Link
              to="/"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-dark-elevated transition-all"
            >
              <Package size={18} />
              <span>Lists</span>
            </Link>
            <Link
              to="/stores"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-dark-elevated transition-all"
            >
              <Store size={18} />
              <span>Stores</span>
            </Link>
          </div>
        </nav>

        {/* Mobile Search Drawer */}
        {isSearchOpen && (
          <div className="md:hidden pb-3 animate-slideDown">
            <input
              type="search"
              placeholder="Search lists..."
              className="w-full px-4 py-3 rounded-xl bg-dark-elevated border border-dark-border text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-blue focus:glow-blue-sm transition-all"
              autoFocus
            />
          </div>
        )}
      </div>
    </header>
  );
}
```

**Step 2: Verify header renders correctly**

Run: `npm run dev` and check both mobile and desktop views

**Step 3: Commit header changes**

```bash
git add frontend-react/src/components/layout/Header.tsx
git commit -m "feat: Update header with dark theme and mobile search

- Glass effect background
- Compact mobile header (48px)
- Search drawer on mobile
- Blue glow on logo
- Desktop nav with hover states

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 4: Create SwipeableCard Component

**Files:**
- Create: `frontend-react/src/components/ui/SwipeableCard.tsx`
- Create: `frontend-react/src/hooks/useSwipe.ts`

**Step 1: Create useSwipe.ts hook**

```typescript
import { useState, useRef, TouchEvent } from 'react';

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
```

**Step 2: Create SwipeableCard.tsx**

```tsx
import { ReactNode } from 'react';
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
    isRevealed,
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
```

**Step 3: Verify swipe component works**

Run: `npm run dev` and test swipe gestures on mobile

**Step 4: Commit swipe components**

```bash
git add frontend-react/src/hooks/useSwipe.ts frontend-react/src/components/ui/SwipeableCard.tsx
git commit -m "feat: Add swipeable card component with touch gestures

- useSwipe hook for touch handling
- SwipeableCard wrapper component
- Swipe right to pack (green)
- Swipe left to delete (red)
- Spring physics with resistance
- Visual feedback at thresholds

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Create PullToRefresh Component

**Files:**
- Create: `frontend-react/src/components/ui/PullToRefresh.tsx`

**Step 1: Create PullToRefresh.tsx**

```tsx
import { useState, useRef, ReactNode, TouchEvent } from 'react';
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
            <ArrowDown size={20} className="transition-transform" style={{ transform: `rotate(${Math.min(pullDistance / PULL_THRESHOLD * 180, 180)}deg)` }} />
            <span className="text-sm">Pull to refresh</span>
          </div>
        );
      case 'ready':
        return (
          <div className="flex items-center gap-2 text-accent-blue">
            <ArrowDown size={20} className="rotate-180" />
            <span className="text-sm font-medium">Release to refresh</span>
          </div>
        );
      case 'refreshing':
        return (
          <div className="flex items-center gap-2 text-accent-blue">
            <Loader2 size={20} className="animate-spin" />
            <span className="text-sm">Refreshing...</span>
          </div>
        );
      case 'complete':
        return (
          <div className="flex items-center gap-2 text-status-success">
            <Check size={20} />
            <span className="text-sm font-medium">Updated!</span>
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
```

**Step 2: Verify pull-to-refresh works**

Run: `npm run dev` and test on mobile

**Step 3: Commit pull-to-refresh**

```bash
git add frontend-react/src/components/ui/PullToRefresh.tsx
git commit -m "feat: Add pull-to-refresh component

- Pull down gesture detection
- Visual states: pulling, ready, refreshing, complete
- Arrow rotation feedback
- Resistance on over-pull
- Async refresh support

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Update ItemCard with Dark Theme and Swipe

**Files:**
- Modify: `frontend-react/src/components/packing-lists/ItemCard.tsx`

**Step 1: Rewrite ItemCard.tsx with dark theme**

```tsx
import { Check, Edit, Trash2, DollarSign, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { SwipeableCard } from '@/components/ui/SwipeableCard';
import type { PackingListItem, Item, PriceWithVotes } from '@/types';

interface ItemCardProps {
  pli: PackingListItem;
  item: Item;
  prices: PriceWithVotes[];
  onTogglePacked: () => void;
  onDelete: () => void;
  onEdit?: () => void;
  onVote: (priceId: number, isUpvote: boolean) => void;
  isPending?: boolean;
}

export function ItemCard({
  pli,
  item,
  prices,
  onTogglePacked,
  onDelete,
  onEdit,
  onVote,
  isPending = false,
}: ItemCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const bestPrice = prices[0];
  const hasDetails = pli.notes || pli.instructions || pli.nsn_lin;

  return (
    <SwipeableCard
      onSwipeRight={onTogglePacked}
      onSwipeLeft={onDelete}
      rightLabel={pli.packed ? 'Unpack' : 'Pack'}
      disabled={isPending}
    >
      <div
        className={`
          relative rounded-xl border transition-all duration-200 p-5
          ${pli.packed
            ? 'bg-dark-elevated/50 border-dark-border'
            : 'bg-dark-surface border-dark-border hover:border-accent-blue/50'
          }
          ${pli.required && !pli.packed ? 'border-l-4 border-l-status-danger' : ''}
          ${!pli.required && !pli.packed ? 'border-l-4 border-l-accent-blue' : ''}
        `}
      >
        {/* Header Row */}
        <div className="flex items-start gap-4 mb-4">
          {/* Checkbox */}
          <button
            onClick={onTogglePacked}
            disabled={isPending}
            className={`
              flex-shrink-0 w-12 h-12 rounded-xl border-2 flex items-center justify-center
              transition-all duration-200 tap-active
              ${pli.packed
                ? 'bg-status-success border-status-success glow-success'
                : 'bg-dark-elevated border-dark-border hover:border-accent-blue'
              }
              ${isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {pli.packed && <Check size={24} strokeWidth={3} className="text-white animate-checkmark" />}
          </button>

          {/* Item Info */}
          <div className="flex-1 min-w-0">
            <h3
              className={`
                text-lg font-bold mb-2 transition-opacity
                ${pli.packed ? 'text-text-muted line-through' : 'text-text-primary'}
              `}
            >
              {item.name}
            </h3>

            {/* Badges */}
            <div className="flex flex-wrap gap-2">
              {pli.required ? (
                <Badge variant="danger" size="sm">REQUIRED</Badge>
              ) : (
                <Badge variant="info" size="sm">Optional</Badge>
              )}
              {pli.quantity > 1 && (
                <Badge variant="default" size="sm">Qty: {pli.quantity}</Badge>
              )}
              {pli.nsn_lin && (
                <Badge variant="default" size="sm" className="font-mono text-xs">
                  {pli.nsn_lin}
                </Badge>
              )}
            </div>
          </div>

          {/* Actions - Desktop only */}
          <div className="hidden md:flex flex-shrink-0 gap-2">
            {onEdit && (
              <Button
                size="sm"
                variant="secondary"
                onClick={onEdit}
                disabled={isPending}
                className="px-3"
              >
                <Edit size={16} />
              </Button>
            )}
            <Button
              size="sm"
              variant="danger"
              onClick={onDelete}
              disabled={isPending}
              className="px-3"
            >
              <Trash2 size={16} />
            </Button>
          </div>
        </div>

        {/* Quick Notes */}
        {pli.notes && pli.notes.length < 60 && (
          <p className="text-sm text-text-secondary mb-4">{pli.notes}</p>
        )}

        {/* Price Info */}
        {bestPrice ? (
          <div className="glass rounded-xl p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xl font-bold text-status-success">
                  ${parseFloat(bestPrice.price.price).toFixed(2)}
                </span>
                <span className="text-sm text-text-secondary ml-2">
                  @ {bestPrice.price.store.name}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => onVote(bestPrice.price.id, true)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-success hover:glow-success rounded-lg px-2 py-1 transition-all tap-active disabled:opacity-50"
                >
                  <ThumbsUp size={18} />
                  <span className="text-sm font-medium">{bestPrice.upvotes}</span>
                </button>
                <button
                  onClick={() => onVote(bestPrice.price.id, false)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-danger hover:glow-danger rounded-lg px-2 py-1 transition-all tap-active disabled:opacity-50"
                >
                  <ThumbsDown size={18} />
                  <span className="text-sm font-medium">{bestPrice.downvotes}</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <Button size="sm" variant="secondary" className="w-full mb-4 glass">
            <DollarSign size={16} className="mr-2" />
            Add Price
          </Button>
        )}

        {/* Expandable Details */}
        {hasDetails && (
          <>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 text-sm text-accent-blue hover:text-accent-glow transition-colors w-full tap-active"
            >
              {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              <span className="font-medium">
                {isExpanded ? 'Hide Details' : 'Show Details'}
              </span>
            </button>

            {isExpanded && (
              <div className="mt-4 pt-4 border-t border-dark-border space-y-3 animate-slideDown">
                {pli.notes && pli.notes.length >= 60 && (
                  <div>
                    <p className="text-xs font-semibold text-text-secondary mb-1">Notes:</p>
                    <p className="text-sm text-text-primary">{pli.notes}</p>
                  </div>
                )}
                {pli.instructions && (
                  <div>
                    <p className="text-xs font-semibold text-text-secondary mb-1">Instructions:</p>
                    <p className="text-sm text-text-primary italic">{pli.instructions}</p>
                  </div>
                )}

                {/* Mobile Actions */}
                <div className="flex gap-2 pt-2 md:hidden">
                  {onEdit && (
                    <Button size="sm" variant="secondary" onClick={onEdit} disabled={isPending} className="flex-1">
                      <Edit size={16} className="mr-2" />
                      Edit
                    </Button>
                  )}
                  <Button size="sm" variant="danger" onClick={onDelete} disabled={isPending} className="flex-1">
                    <Trash2 size={16} className="mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </SwipeableCard>
  );
}
```

**Step 2: Verify ItemCard renders**

Run: `npm run dev`

**Step 3: Commit ItemCard changes**

```bash
git add frontend-react/src/components/packing-lists/ItemCard.tsx
git commit -m "feat: Update ItemCard with dark theme and swipe gestures

- Dark theme styling with glassmorphism
- Integrated SwipeableCard wrapper
- Swipe right to pack, swipe left to delete
- Mobile actions in expanded details
- Glow effects on vote buttons
- Improved touch targets

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Update HomePage with Dark Theme

**Files:**
- Modify: `frontend-react/src/pages/HomePage.tsx`

**Step 1: Rewrite HomePage.tsx with dark theme**

```tsx
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
                  {/* Header */}
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

                  {/* Description */}
                  {plist.description && (
                    <p className="text-text-secondary mb-4 line-clamp-2 flex-1 text-sm leading-relaxed">
                      {plist.description}
                    </p>
                  )}

                  {/* Footer */}
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
              Get started by creating your first packing list or uploading an existing one. Build your mission-ready checklist in minutes.
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
        {/* Background gradient */}
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #0F172A 100%)'
          }}
        />

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(59, 130, 246, 0.5) 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}
        />

        {/* Glow effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent-blue/20 rounded-full blur-3xl" />

        <div className="relative px-6 py-16 md:py-20">
          <div className="max-w-3xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-6 glass border border-status-success/30">
              <CheckCircle2 size={16} className="text-status-success" />
              <span className="text-status-success">Mission-Ready Preparation</span>
            </div>

            {/* Heading */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-text-primary mb-4 leading-tight">
              Pack Smart,
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-blue to-status-success text-glow">
                Deploy Ready
              </span>
            </h1>

            {/* Description */}
            <p className="text-lg text-text-secondary mb-10 max-w-xl mx-auto leading-relaxed">
              Community-driven packing lists for military schools, training courses, and deployments.
            </p>

            {/* CTA Buttons - Desktop */}
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

      {/* Main Content */}
      <Suspense fallback={<ListSkeleton items={5} />}>
        <PackingListsContent />
      </Suspense>
    </div>
  );
}
```

**Step 2: Verify HomePage renders**

Run: `npm run dev`

**Step 3: Commit HomePage changes**

```bash
git add frontend-react/src/pages/HomePage.tsx
git commit -m "feat: Update HomePage with dark theme and pull-to-refresh

- Dark gradient hero section with glow effects
- Glass effect stat cards with hover states
- Pull-to-refresh integration
- Packing list cards with glassmorphism
- Blue accent highlights and glows
- Mobile-optimized layout

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 8: Update Button Component for Dark Theme

**Files:**
- Modify: `frontend-react/src/components/ui/Button.tsx`

**Step 1: Update Button.tsx**

```tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 tap-active disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
      primary: 'bg-accent-blue hover:bg-accent-glow text-white hover:glow-blue-sm',
      secondary: 'bg-dark-elevated hover:bg-dark-border text-text-primary border border-dark-border hover:border-accent-blue/50',
      danger: 'bg-status-danger hover:bg-red-600 text-white hover:glow-danger',
      success: 'bg-status-success hover:bg-emerald-600 text-white hover:glow-success',
    };

    const sizes = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-5 py-3 text-base',
      lg: 'px-8 py-4 text-lg',
    };

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

**Step 2: Commit Button changes**

```bash
git add frontend-react/src/components/ui/Button.tsx
git commit -m "feat: Update Button component with dark theme

- Dark theme color variants
- Glow effects on hover
- Tap-active animation class
- Consistent rounded-xl corners

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 9: Update Badge Component for Dark Theme

**Files:**
- Modify: `frontend-react/src/components/ui/Badge.tsx`

**Step 1: Update Badge.tsx**

```tsx
import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'info' | 'success' | 'danger' | 'warning';
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({ children, variant = 'default', size = 'sm', className = '' }: BadgeProps) {
  const baseStyles = 'inline-flex items-center font-semibold rounded-lg border';

  const variants = {
    default: 'bg-dark-elevated text-text-secondary border-dark-border',
    info: 'bg-accent-muted text-accent-glow border-accent-blue/30',
    success: 'bg-status-success/20 text-status-success border-status-success/30',
    danger: 'bg-status-danger/20 text-status-danger border-status-danger/30',
    warning: 'bg-status-warning/20 text-status-warning border-status-warning/30',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  return (
    <span className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}>
      {children}
    </span>
  );
}
```

**Step 2: Commit Badge changes**

```bash
git add frontend-react/src/components/ui/Badge.tsx
git commit -m "feat: Update Badge component with dark theme

- Dark background variants
- Subtle border styling
- Glow-compatible colors

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 10: Update Skeleton Component for Dark Theme

**Files:**
- Modify: `frontend-react/src/components/ui/Skeleton.tsx`

**Step 1: Update Skeleton.tsx**

```tsx
interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`bg-dark-elevated rounded-lg animate-shimmer ${className}`}
      style={{
        backgroundImage: 'linear-gradient(90deg, #1E293B 0%, #334155 50%, #1E293B 100%)',
        backgroundSize: '200% 100%',
      }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="glass rounded-xl border border-dark-border p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-3">
          <Skeleton className="h-6 w-3/4" />
          <div className="flex gap-2">
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-5 w-20" />
          </div>
        </div>
        <Skeleton className="h-12 w-12 rounded-xl" />
      </div>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  );
}

export function ListSkeleton({ items = 3 }: { items?: number }) {
  return (
    <div className="space-y-4">
      {/* Stats skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass rounded-xl border border-dark-border p-5">
            <div className="flex items-center justify-between mb-3">
              <Skeleton className="h-12 w-12 rounded-xl" />
              <Skeleton className="h-6 w-16 rounded-lg" />
            </div>
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>

      {/* Header skeleton */}
      <div className="flex items-center justify-between mb-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-6 w-20 rounded-lg" />
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: items }).map((_, i) => (
          <div key={i} className="animate-fadeIn" style={{ animationDelay: `${i * 100}ms` }}>
            <CardSkeleton />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ItemSkeleton() {
  return (
    <div className="glass rounded-xl border border-dark-border p-5">
      <div className="flex items-start gap-4">
        <Skeleton className="h-12 w-12 rounded-xl flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-6 w-3/4" />
          <div className="flex gap-2">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-5 w-16" />
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Commit Skeleton changes**

```bash
git add frontend-react/src/components/ui/Skeleton.tsx
git commit -m "feat: Update Skeleton components with dark theme

- Dark gradient shimmer effect
- Glass effect containers
- Staggered fade-in animations

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 11: Update Footer for Dark Theme

**Files:**
- Modify: `frontend-react/src/components/layout/Footer.tsx`

**Step 1: Update Footer.tsx**

```tsx
export function Footer() {
  return (
    <footer className="hidden md:block border-t border-dark-border py-6 mt-auto">
      <div className="container mx-auto px-4 text-center text-text-muted text-sm">
        <p>Community Packing List &copy; {new Date().getFullYear()}</p>
      </div>
    </footer>
  );
}
```

**Step 2: Commit Footer changes**

```bash
git add frontend-react/src/components/layout/Footer.tsx
git commit -m "feat: Update Footer with dark theme

- Dark border styling
- Hidden on mobile (bottom nav takes over)
- Muted text color

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 12: Final Build and Deploy

**Files:** None (build and deploy commands)

**Step 1: Run full build**

Run:
```bash
cd /Users/sac/Git/community-packing-list/frontend-react && npm run build
```

Expected: Build succeeds with no errors

**Step 2: Test locally**

Run:
```bash
npm run preview
```

Expected: App loads with dark theme, bottom nav works on mobile viewport

**Step 3: Deploy to Cloudflare Pages**

Run:
```bash
npx wrangler pages deploy dist --project-name=community-packing-list
```

Expected: Deployment succeeds

**Step 4: Verify production**

Run:
```bash
curl -sL "https://community-packing-list.pages.dev" | grep -o '<title>[^<]*</title>'
```

Expected: `<title>Community Packing List</title>`

**Step 5: Final commit with deployment update**

```bash
cd /Users/sac/Git/community-packing-list
git add -A
git commit -m "feat: Complete mobile-first dark UI redesign

- Dark theme with glassmorphism effects
- Bottom navigation for mobile
- Swipe gestures for pack/delete
- Pull-to-refresh on lists
- Electric blue accent with glow effects
- Updated all components for dark theme

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin main
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] Dark theme renders correctly (slate-900 background)
- [ ] Bottom nav appears on mobile, hidden on desktop
- [ ] Floating action button (+) has blue glow
- [ ] Swipe right on item card reveals green "Pack"
- [ ] Swipe left on item card reveals red "Delete"
- [ ] Pull-to-refresh works on home page
- [ ] Glass effects render with backdrop blur
- [ ] Blue glow appears on interactive elements
- [ ] All text is readable (proper contrast)
- [ ] Build passes with no errors
- [ ] Cloudflare deployment succeeds

---

## Summary

This plan transforms the Community Packing List from a light military theme to a modern dark theme with:

1. **Color System:** Dark slate backgrounds with electric blue accents
2. **Bottom Navigation:** Thumb-friendly nav with floating add button
3. **Swipe Gestures:** Swipe to pack/delete items
4. **Pull-to-Refresh:** Pull down to refresh lists
5. **Glassmorphism:** Blur effects on cards and modals
6. **Micro-interactions:** Glow effects, scale animations, spring physics

Total: 12 tasks, ~45 steps
