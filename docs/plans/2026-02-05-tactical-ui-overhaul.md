# Tactical UI Overhaul - "Mission Control" Design System

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform Community Packing List into a visually stunning, memorable tactical mission control interface that looks like something from a military ops center or sci-fi command deck.

**Architecture:** Complete design system replacement with distinctive typography, atmospheric backgrounds, high-contrast data visualization, and purposeful motion design.

**Tech Stack:** React 19, Tailwind CSS 4, Google Fonts (Orbitron + JetBrains Mono), CSS custom properties, staggered animations

---

## Design Philosophy

**Aesthetic Direction:** TACTICAL COMMAND CENTER meets CYBERPUNK HUD

Think: Iron Man's JARVIS interface, military drone control systems, Tom Clancy game UIs, spacecraft mission control. High-information-density displays with purposeful visual hierarchy.

**What Makes This UNFORGETTABLE:**
- Scanline textures and radar/grid overlays on backgrounds
- Amber/cyan/red status indicators like real military systems
- Monospace typography for data, display font for headers
- Animated corner brackets and tactical frames on cards
- Progress bars that look like loading/scanning indicators
- Data presented like military intel briefings

**Color Palette:**
```
Background:       #0A0E14 (near-black with blue undertone)
Surface:          #12161D (slightly lighter)
Elevated:         #1A1F29 (card backgrounds)
Border:           #2A3441 (subtle contrast)
Accent Primary:   #00F0FF (cyan - active/info)
Accent Secondary: #FFB800 (amber - warnings/highlights)
Danger:           #FF3B3B (red - alerts/required)
Success:          #00FF87 (bright green - complete)
Text Primary:     #E8EDF5 (high contrast white)
Text Secondary:   #6B7A90 (muted)
Text Tactical:    #00F0FF (cyan for tactical data)
```

**Typography:**
- Headers: Orbitron (geometric, futuristic)
- Data/Code: JetBrains Mono (excellent monospace)
- Body: Inter (readable, clean)

---

### Task 1: Foundation - New Design System & Typography

**Files:**
- Modify: `frontend-react/tailwind.config.js`
- Modify: `frontend-react/src/index.css`
- Modify: `frontend-react/index.html`

**Step 1: Update index.html with Google Fonts**

Add to the `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

**Step 2: Replace tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Orbitron', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        tactical: {
          bg: '#0A0E14',
          surface: '#12161D',
          elevated: '#1A1F29',
          border: '#2A3441',
          'border-light': '#3A4555',
        },
        accent: {
          cyan: '#00F0FF',
          'cyan-dim': '#00A5B0',
          'cyan-glow': '#00F0FF40',
          amber: '#FFB800',
          'amber-dim': '#B08000',
          'amber-glow': '#FFB80040',
        },
        status: {
          danger: '#FF3B3B',
          'danger-dim': '#CC2E2E',
          'danger-glow': '#FF3B3B40',
          success: '#00FF87',
          'success-dim': '#00CC6B',
          'success-glow': '#00FF8740',
          warning: '#FFB800',
        },
        text: {
          primary: '#E8EDF5',
          secondary: '#6B7A90',
          muted: '#4A5568',
          tactical: '#00F0FF',
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 20px #00F0FF40, 0 0 40px #00F0FF20',
        'glow-amber': '0 0 20px #FFB80040, 0 0 40px #FFB80020',
        'glow-success': '0 0 20px #00FF8740, 0 0 40px #00FF8720',
        'glow-danger': '0 0 20px #FF3B3B40, 0 0 40px #FF3B3B20',
        'inner-glow': 'inset 0 1px 0 #ffffff10',
      },
      backgroundImage: {
        'grid-pattern': `
          linear-gradient(#00F0FF08 1px, transparent 1px),
          linear-gradient(90deg, #00F0FF08 1px, transparent 1px)
        `,
        'scanlines': 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00000010 2px, #00000010 4px)',
        'radial-vignette': 'radial-gradient(ellipse at center, transparent 0%, #0A0E14 100%)',
      },
      keyframes: {
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px #00F0FF40' },
          '50%': { opacity: '0.7', boxShadow: '0 0 30px #00F0FF60' },
        },
        'border-trace': {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '200% 200%' },
        },
        'fadeInUp': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slideInRight': {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'scaleIn': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'typewriter': {
          '0%': { width: '0' },
          '100%': { width: '100%' },
        },
      },
      animation: {
        'scan': 'scan 3s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'border-trace': 'border-trace 4s linear infinite',
        'fadeInUp': 'fadeInUp 0.5s ease-out forwards',
        'slideInRight': 'slideInRight 0.4s ease-out forwards',
        'scaleIn': 'scaleIn 0.3s ease-out forwards',
        'shimmer': 'shimmer 2s linear infinite',
      },
    },
  },
  plugins: [],
}
```

**Step 3: Replace index.css with tactical design system**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Tactical Command Design System */

:root {
  --tactical-bg: #0A0E14;
  --tactical-surface: #12161D;
  --tactical-elevated: #1A1F29;
  --tactical-border: #2A3441;
  --accent-cyan: #00F0FF;
  --accent-amber: #FFB800;
  --status-danger: #FF3B3B;
  --status-success: #00FF87;
  --text-primary: #E8EDF5;
  --text-secondary: #6B7A90;
}

/* Base Styles */
html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--tactical-bg);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Atmospheric Background */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, #00F0FF08 0%, transparent 50%),
    radial-gradient(ellipse at 0% 100%, #FFB80005 0%, transparent 40%),
    radial-gradient(ellipse at 100% 100%, #00FF8705 0%, transparent 40%);
  pointer-events: none;
  z-index: -1;
}

/* Grid overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background:
    linear-gradient(#00F0FF05 1px, transparent 1px),
    linear-gradient(90deg, #00F0FF05 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: -1;
}

/* Typography Utilities */
@layer utilities {
  .font-display {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.05em;
  }

  .font-tactical {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
  }

  /* Tactical Frame - The signature card style */
  .tactical-frame {
    position: relative;
    background: linear-gradient(135deg, var(--tactical-elevated) 0%, var(--tactical-surface) 100%);
    border: 1px solid var(--tactical-border);
    overflow: hidden;
  }

  .tactical-frame::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #00F0FF10 0%, transparent 50%);
    pointer-events: none;
  }

  /* Corner brackets decoration */
  .tactical-frame::after {
    content: '';
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    border: 1px solid #00F0FF20;
    border-radius: 2px;
    pointer-events: none;
  }

  /* Tactical Header Bar */
  .tactical-header {
    background: linear-gradient(90deg, #00F0FF15 0%, transparent 100%);
    border-left: 3px solid var(--accent-cyan);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
  }

  /* Status Indicator Pill */
  .status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 2px;
  }

  .status-indicator::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: pulse-glow 2s ease-in-out infinite;
  }

  .status-active::before { background: var(--status-success); }
  .status-warning::before { background: var(--accent-amber); }
  .status-danger::before { background: var(--status-danger); }

  /* Glow Effects */
  .glow-cyan { box-shadow: 0 0 20px #00F0FF40, 0 0 40px #00F0FF20; }
  .glow-amber { box-shadow: 0 0 20px #FFB80040, 0 0 40px #FFB80020; }
  .glow-success { box-shadow: 0 0 20px #00FF8740, 0 0 40px #00FF8720; }
  .glow-danger { box-shadow: 0 0 20px #FF3B3B40, 0 0 40px #FF3B3B20; }

  /* Text Glow */
  .text-glow-cyan { text-shadow: 0 0 10px #00F0FF80, 0 0 20px #00F0FF40; }
  .text-glow-amber { text-shadow: 0 0 10px #FFB80080, 0 0 20px #FFB80040; }

  /* Progress Bar - Tactical Style */
  .tactical-progress {
    position: relative;
    height: 8px;
    background: var(--tactical-surface);
    border: 1px solid var(--tactical-border);
    overflow: hidden;
  }

  .tactical-progress::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      90deg,
      transparent,
      transparent 4px,
      #00F0FF10 4px,
      #00F0FF10 8px
    );
  }

  .tactical-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-cyan), var(--status-success));
    transition: width 0.5s ease-out;
    position: relative;
  }

  .tactical-progress-bar::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 20px;
    background: linear-gradient(90deg, transparent, #ffffff40);
    animation: shimmer 1.5s ease-in-out infinite;
  }

  /* Data Display */
  .data-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.625rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-secondary);
  }

  .data-value {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    color: var(--text-primary);
  }

  /* Safe area padding for notched phones */
  .pb-safe {
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }

  /* Touch targets */
  .tap-target {
    min-height: 44px;
    min-width: 44px;
  }

  .tap-active:active {
    transform: scale(0.97);
    transition: transform 0.1s ease-out;
  }
}

/* Scrollbar - Tactical Style */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--tactical-surface);
}

::-webkit-scrollbar-thumb {
  background: var(--tactical-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--accent-cyan);
}

/* Selection */
::selection {
  background: #00F0FF30;
  color: var(--text-primary);
}

/* Focus styles */
:focus-visible {
  outline: 2px solid var(--accent-cyan);
  outline-offset: 2px;
}

/* Stagger animation helper classes */
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }
.stagger-5 { animation-delay: 0.5s; }
```

**Step 4: Verify build**

Run: `cd /Users/sac/Git/community-packing-list/frontend-react && npm run build`

**Step 5: Commit**

```bash
git add frontend-react/tailwind.config.js frontend-react/src/index.css frontend-react/index.html
git commit -m "feat: Add tactical command center design system

- Orbitron display font for headers
- JetBrains Mono for tactical data
- Cyan/amber/green status colors
- Grid overlay and atmospheric backgrounds
- Tactical frame card component
- Scanline and glow effects
- Custom progress bar styling

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Layout Components - Header & Bottom Nav

**Files:**
- Modify: `frontend-react/src/components/layout/Header.tsx`
- Modify: `frontend-react/src/components/layout/BottomNav.tsx`
- Modify: `frontend-react/src/components/layout/Layout.tsx`
- Modify: `frontend-react/src/components/layout/Footer.tsx`

**Step 1: Rewrite Header.tsx with tactical styling**

```tsx
import { Link, useLocation } from 'react-router-dom';
import { Package, Store, Search, Menu, X, Shield } from 'lucide-react';
import { useState } from 'react';

export function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'MISSION HQ', icon: Package },
    { path: '/stores', label: 'SUPPLY POINTS', icon: Store },
  ];

  return (
    <header className="sticky top-0 z-40 bg-tactical-surface/95 backdrop-blur-md border-b border-tactical-border">
      {/* Scan line effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-b from-accent-cyan/5 to-transparent h-1" />
      </div>

      <div className="container mx-auto px-4 relative">
        {/* Mobile Header */}
        <div className="flex md:hidden items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center glow-cyan">
                <Shield size={20} className="text-accent-cyan" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-status-success rounded-full animate-pulse" />
            </div>
            <div>
              <span className="font-display text-sm font-bold text-text-primary tracking-wider">CPL</span>
              <div className="text-[10px] font-tactical text-accent-cyan uppercase tracking-widest">ONLINE</div>
            </div>
          </Link>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="p-2.5 rounded bg-tactical-elevated border border-tactical-border text-text-secondary hover:text-accent-cyan hover:border-accent-cyan/50 transition-all tap-active"
            >
              <Search size={20} />
            </button>
          </div>
        </div>

        {/* Desktop Header */}
        <nav className="hidden md:flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-4 group">
            <div className="relative">
              <div className="w-12 h-12 rounded bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center group-hover:glow-cyan transition-all duration-300">
                <Shield size={24} className="text-accent-cyan" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-status-success rounded-full animate-pulse" />
            </div>
            <div>
              <span className="font-display text-lg font-bold text-text-primary tracking-wider group-hover:text-glow-cyan transition-all">
                COMMUNITY PACKING LIST
              </span>
              <div className="text-xs font-tactical text-accent-cyan uppercase tracking-[0.2em]">
                TACTICAL MISSION CONTROL
              </div>
            </div>
          </Link>

          <div className="flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              const Icon = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`
                    relative flex items-center gap-2 px-4 py-2 rounded font-tactical text-sm uppercase tracking-wider
                    transition-all duration-200
                    ${isActive
                      ? 'bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30'
                      : 'text-text-secondary hover:text-text-primary hover:bg-tactical-elevated border border-transparent'
                    }
                  `}
                >
                  <Icon size={16} />
                  <span>{link.label}</span>
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-0.5 bg-accent-cyan" />
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Mobile Search Drawer */}
        {isSearchOpen && (
          <div className="md:hidden pb-4 animate-fadeInUp">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary" size={18} />
              <input
                type="search"
                placeholder="SEARCH MISSION DATABASE..."
                className="w-full pl-12 pr-4 py-3 rounded bg-tactical-elevated border border-tactical-border text-text-primary placeholder-text-muted font-tactical text-sm uppercase tracking-wider focus:outline-none focus:border-accent-cyan focus:glow-cyan transition-all"
                autoFocus
              />
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
```

**Step 2: Rewrite BottomNav.tsx with tactical styling**

```tsx
import { Link, useLocation } from 'react-router-dom';
import { Home, Package, Plus, Store, Crosshair } from 'lucide-react';

const navItems = [
  { path: '/', icon: Home, label: 'HQ' },
  { path: '/lists', icon: Package, label: 'LISTS' },
  { path: '/list/create', icon: Plus, label: 'NEW', isAction: true },
  { path: '/stores', icon: Store, label: 'SUPPLY' },
];

export function BottomNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      {/* Top glow line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent-cyan/50 to-transparent" />

      <div className="bg-tactical-surface/95 backdrop-blur-md border-t border-tactical-border pb-safe">
        <div className="flex items-center justify-around h-16 px-2">
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
                  <div className="relative">
                    {/* Outer ring */}
                    <div className="absolute inset-0 w-16 h-16 rounded-full border-2 border-accent-cyan/30 animate-pulse" />
                    {/* Main button */}
                    <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-accent-cyan to-accent-cyan-dim glow-cyan tap-active transition-all duration-200 hover:scale-105">
                      <Crosshair size={28} className="text-tactical-bg" strokeWidth={2.5} />
                    </div>
                    {/* Label */}
                    <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[10px] font-tactical text-accent-cyan uppercase tracking-wider whitespace-nowrap">
                      {item.label}
                    </span>
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
                  transition-all duration-200 relative
                  ${isActive ? 'text-accent-cyan' : 'text-text-secondary'}
                `}
              >
                {isActive && (
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-accent-cyan" />
                )}
                <div className={`
                  relative p-2 rounded transition-all duration-200
                  ${isActive ? 'bg-accent-cyan/10' : ''}
                `}>
                  <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
                </div>
                <span className={`text-[10px] mt-1 font-tactical uppercase tracking-wider ${isActive ? 'text-accent-cyan' : ''}`}>
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

**Step 3: Update Layout.tsx**

```tsx
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';
import { BottomNav } from './BottomNav';

export function Layout() {
  return (
    <div className="flex flex-col min-h-screen bg-tactical-bg">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6 pb-28 md:pb-6">
        <Outlet />
      </main>
      <Footer />
      <BottomNav />
    </div>
  );
}
```

**Step 4: Update Footer.tsx**

```tsx
import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="hidden md:block border-t border-tactical-border py-6 mt-auto bg-tactical-surface/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center gap-3 text-text-muted">
          <Shield size={16} className="text-accent-cyan/50" />
          <span className="font-tactical text-xs uppercase tracking-[0.2em]">
            Community Packing List • Tactical Mission Control
          </span>
          <span className="text-accent-cyan/50">•</span>
          <span className="font-tactical text-xs uppercase tracking-[0.2em]">
            {new Date().getFullYear()}
          </span>
        </div>
      </div>
    </footer>
  );
}
```

**Step 5: Commit layout changes**

```bash
git add frontend-react/src/components/layout/
git commit -m "feat: Update layout components with tactical styling

- Header with mission control branding
- Tactical bottom nav with crosshair FAB
- Cyan accent colors and glow effects
- JetBrains Mono typography
- Status indicators and scan effects

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Core UI Components - Button, Badge, Card

**Files:**
- Modify: `frontend-react/src/components/ui/Button.tsx`
- Modify: `frontend-react/src/components/ui/Badge.tsx`
- Modify: `frontend-react/src/components/ui/Card.tsx`

**Step 1: Rewrite Button.tsx**

```tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', children, disabled, ...props }, ref) => {
    const baseStyles = `
      relative inline-flex items-center justify-center font-tactical uppercase tracking-wider
      rounded transition-all duration-200 tap-active overflow-hidden
      disabled:opacity-50 disabled:cursor-not-allowed
      focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-cyan focus-visible:ring-offset-2 focus-visible:ring-offset-tactical-bg
    `;

    const variants = {
      primary: `
        bg-gradient-to-r from-accent-cyan to-accent-cyan-dim text-tactical-bg font-semibold
        hover:glow-cyan hover:brightness-110
        before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent
        before:translate-x-[-200%] hover:before:translate-x-[200%] before:transition-transform before:duration-500
      `,
      secondary: `
        bg-tactical-elevated text-text-primary border border-tactical-border
        hover:border-accent-cyan/50 hover:text-accent-cyan
      `,
      danger: `
        bg-gradient-to-r from-status-danger to-status-danger-dim text-white font-semibold
        hover:glow-danger hover:brightness-110
      `,
      success: `
        bg-gradient-to-r from-status-success to-status-success-dim text-tactical-bg font-semibold
        hover:glow-success hover:brightness-110
      `,
      ghost: `
        bg-transparent text-text-secondary border border-transparent
        hover:bg-tactical-elevated hover:text-text-primary hover:border-tactical-border
      `,
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-xs',
      md: 'px-5 py-2.5 text-sm',
      lg: 'px-8 py-3.5 text-base',
    };

    return (
      <button
        ref={ref}
        disabled={disabled}
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

**Step 2: Rewrite Badge.tsx**

```tsx
import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'info' | 'success' | 'danger' | 'warning' | 'tactical';
  size?: 'sm' | 'md';
  className?: string;
  pulse?: boolean;
}

export function Badge({
  children,
  variant = 'default',
  size = 'sm',
  className = '',
  pulse = false
}: BadgeProps) {
  const baseStyles = `
    inline-flex items-center gap-1.5 font-tactical uppercase tracking-wider
    rounded border
  `;

  const variants = {
    default: 'bg-tactical-elevated/80 text-text-secondary border-tactical-border',
    info: 'bg-accent-cyan/10 text-accent-cyan border-accent-cyan/30',
    success: 'bg-status-success/10 text-status-success border-status-success/30',
    danger: 'bg-status-danger/10 text-status-danger border-status-danger/30',
    warning: 'bg-accent-amber/10 text-accent-amber border-accent-amber/30',
    tactical: 'bg-tactical-surface text-accent-cyan border-accent-cyan/50 glow-cyan',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-3 py-1 text-xs',
  };

  return (
    <span className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}>
      {pulse && (
        <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${
          variant === 'success' ? 'bg-status-success' :
          variant === 'danger' ? 'bg-status-danger' :
          variant === 'warning' ? 'bg-accent-amber' :
          'bg-accent-cyan'
        }`} />
      )}
      {children}
    </span>
  );
}
```

**Step 3: Rewrite Card.tsx**

```tsx
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'tactical';
  header?: ReactNode;
  headerLabel?: string;
}

export function Card({
  children,
  className = '',
  variant = 'default',
  header,
  headerLabel
}: CardProps) {
  const variants = {
    default: 'bg-tactical-elevated/80 border-tactical-border',
    elevated: 'bg-tactical-elevated border-tactical-border-light shadow-lg',
    tactical: 'tactical-frame',
  };

  return (
    <div className={`relative rounded-lg border overflow-hidden ${variants[variant]} ${className}`}>
      {/* Corner decorations */}
      <div className="absolute top-0 left-0 w-4 h-4 border-l-2 border-t-2 border-accent-cyan/30 rounded-tl" />
      <div className="absolute top-0 right-0 w-4 h-4 border-r-2 border-t-2 border-accent-cyan/30 rounded-tr" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-l-2 border-b-2 border-accent-cyan/30 rounded-bl" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-r-2 border-b-2 border-accent-cyan/30 rounded-br" />

      {/* Header bar */}
      {(header || headerLabel) && (
        <div className="tactical-header">
          {headerLabel && (
            <span className="data-label">{headerLabel}</span>
          )}
          {header}
        </div>
      )}

      {/* Content */}
      <div className="p-5 relative">
        {children}
      </div>
    </div>
  );
}
```

**Step 4: Commit core UI components**

```bash
git add frontend-react/src/components/ui/Button.tsx frontend-react/src/components/ui/Badge.tsx frontend-react/src/components/ui/Card.tsx
git commit -m "feat: Update Button, Badge, Card with tactical styling

- Gradient buttons with shine animation
- Status badges with pulse indicators
- Cards with corner bracket decorations
- Tactical header bars
- Cyan/amber/red status colors

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 4: HomePage - Complete Tactical Redesign

**Files:**
- Modify: `frontend-react/src/pages/HomePage.tsx`

**Step 1: Rewrite HomePage.tsx with tactical mission control interface**

```tsx
import { Suspense } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus, Upload, Eye, AlertCircle, Package, CheckCircle2,
  TrendingUp, Store, GraduationCap, MapPin, Shield, Activity,
  Target, Crosshair, Radio, Radar
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

          <h3 className="font-display text-2xl font-bold text-text-primary mb-3 tracking-wider">
            CONNECTION FAILED
          </h3>
          <p className="font-tactical text-sm text-text-secondary mb-8 max-w-md mx-auto uppercase tracking-wide">
            Unable to establish link with backend systems. Verify API deployment status.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
            <Link to="/list/create">
              <Button variant="primary">
                <Plus size={18} className="mr-2" />
                Initialize New List
              </Button>
            </Link>
            <Button variant="secondary" onClick={() => window.location.reload()}>
              <Radio size={18} className="mr-2" />
              Retry Connection
            </Button>
          </div>

          <div className="p-4 rounded bg-tactical-surface border border-accent-amber/30">
            <p className="font-tactical text-xs text-accent-amber uppercase tracking-wider">
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 mb-8">
        {/* Total Lists */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-cyan/50 transition-all">
          <div className="absolute top-0 right-0 w-20 h-20 bg-accent-cyan/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">TOTAL LISTS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-3xl md:text-4xl font-bold text-text-primary">{totalLists}</span>
              <Package className="text-accent-cyan opacity-50 group-hover:opacity-100 transition-opacity" size={24} />
            </div>
            <Badge variant="info" size="sm" pulse className="mt-2">ACTIVE</Badge>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-status-success/50 transition-all">
          <div className="absolute top-0 right-0 w-20 h-20 bg-status-success/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">RECENT OPS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-3xl md:text-4xl font-bold text-text-primary">3</span>
              <Activity className="text-status-success opacity-50 group-hover:opacity-100 transition-opacity" size={24} />
            </div>
            <Badge variant="success" size="sm" pulse className="mt-2">UPDATED</Badge>
          </div>
        </div>

        {/* Supply Points */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-amber/50 transition-all">
          <div className="absolute top-0 right-0 w-20 h-20 bg-accent-amber/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">SUPPLY POINTS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-3xl md:text-4xl font-bold text-text-primary">12</span>
              <Store className="text-accent-amber opacity-50 group-hover:opacity-100 transition-opacity" size={24} />
            </div>
            <Badge variant="warning" size="sm" className="mt-2">NEARBY</Badge>
          </div>
        </div>

        {/* Readiness */}
        <div className="col-span-1 rounded-lg bg-tactical-elevated border border-tactical-border p-4 relative overflow-hidden group hover:border-accent-cyan/50 transition-all">
          <div className="absolute top-0 right-0 w-20 h-20 bg-accent-cyan/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="relative">
            <div className="data-label mb-2">READINESS</div>
            <div className="flex items-end justify-between">
              <span className="font-display text-3xl md:text-4xl font-bold text-status-success">98%</span>
              <Target className="text-accent-cyan opacity-50 group-hover:opacity-100 transition-opacity" size={24} />
            </div>
            <Badge variant="tactical" size="sm" className="mt-2">OPTIMAL</Badge>
          </div>
        </div>
      </div>

      {/* Section Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-1 h-8 bg-accent-cyan rounded-full" />
          <h2 className="font-display text-xl md:text-2xl font-bold text-text-primary tracking-wider">
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
              className="group animate-fadeInUp"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="h-full rounded-lg bg-tactical-elevated border border-tactical-border hover:border-accent-cyan/50 transition-all duration-300 cursor-pointer overflow-hidden relative">
                {/* Hover glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-accent-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                {/* Corner brackets */}
                <div className="absolute top-2 left-2 w-3 h-3 border-l-2 border-t-2 border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute top-2 right-2 w-3 h-3 border-r-2 border-t-2 border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute bottom-2 left-2 w-3 h-3 border-l-2 border-b-2 border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />
                <div className="absolute bottom-2 right-2 w-3 h-3 border-r-2 border-b-2 border-accent-cyan/30 group-hover:border-accent-cyan transition-colors" />

                <div className="flex flex-col h-full p-5 relative">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1 min-w-0 pr-4">
                      <h3 className="font-display text-base font-bold text-text-primary group-hover:text-accent-cyan transition-colors mb-3 truncate tracking-wide">
                        {plist.name.toUpperCase()}
                      </h3>
                      <div className="flex flex-wrap gap-1.5">
                        {plist.type && (
                          <Badge variant="info" size="sm">{plist.type}</Badge>
                        )}
                        {plist.school && (
                          <Badge variant="default" size="sm">
                            <GraduationCap size={10} className="mr-1" />
                            {plist.school.name}
                          </Badge>
                        )}
                        {plist.base && (
                          <Badge variant="success" size="sm">
                            <MapPin size={10} className="mr-1" />
                            {plist.base.name}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 w-12 h-12 rounded bg-accent-cyan/10 border border-accent-cyan/30 flex items-center justify-center group-hover:glow-cyan transition-all">
                      <Package className="text-accent-cyan" size={20} />
                    </div>
                  </div>

                  {/* Description */}
                  {plist.description && (
                    <p className="text-text-secondary text-sm mb-4 line-clamp-2 flex-1 leading-relaxed">
                      {plist.description}
                    </p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-tactical-border">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
                      <span className="font-tactical text-xs text-status-success uppercase tracking-wider">READY</span>
                    </div>
                    <div className="flex items-center gap-2 text-accent-cyan font-tactical text-xs uppercase tracking-wider group-hover:gap-3 transition-all">
                      <span>ACCESS</span>
                      <Eye size={14} />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <Card variant="tactical" className="text-center py-16">
          <div className="max-w-md mx-auto">
            <div className="relative inline-flex items-center justify-center w-24 h-24 mb-6">
              <div className="absolute inset-0 rounded-full border-2 border-dashed border-accent-cyan/30 animate-spin" style={{ animationDuration: '20s' }} />
              <div className="relative w-16 h-16 rounded-full bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center">
                <Radar className="text-accent-cyan" size={32} />
              </div>
            </div>
            <h3 className="font-display text-2xl font-bold text-text-primary mb-3 tracking-wider">
              NO ACTIVE MISSIONS
            </h3>
            <p className="text-text-secondary mb-8 leading-relaxed">
              Initialize your first packing list to begin mission planning. Upload existing lists or create new from scratch.
            </p>
            <Link to="/list/create">
              <Button variant="primary" size="lg">
                <Crosshair size={20} className="mr-2" />
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
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-accent-cyan/10 via-transparent to-transparent" />

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `
              linear-gradient(#00F0FF10 1px, transparent 1px),
              linear-gradient(90deg, #00F0FF10 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px'
          }}
        />

        {/* Animated scan line */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-accent-cyan to-transparent animate-scan" />
        </div>

        {/* Corner decorations */}
        <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-accent-cyan/50" />
        <div className="absolute top-4 right-4 w-8 h-8 border-r-2 border-t-2 border-accent-cyan/50" />
        <div className="absolute bottom-4 left-4 w-8 h-8 border-l-2 border-b-2 border-accent-cyan/50" />
        <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-accent-cyan/50" />

        <div className="relative px-6 py-12 md:py-16">
          <div className="max-w-3xl mx-auto text-center">
            {/* Status badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded bg-tactical-elevated/80 border border-status-success/30 mb-6">
              <div className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
              <span className="font-tactical text-xs text-status-success uppercase tracking-[0.2em]">
                All Systems Operational
              </span>
            </div>

            {/* Heading */}
            <h1 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black text-text-primary mb-4 tracking-wider leading-tight">
              MISSION
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan via-status-success to-accent-cyan text-glow-cyan">
                READY
              </span>
            </h1>

            {/* Subtitle */}
            <p className="font-tactical text-sm md:text-base text-text-secondary mb-10 max-w-xl mx-auto tracking-wide uppercase">
              Community-driven packing lists for military schools, training courses, and deployments
            </p>

            {/* CTA Buttons - Desktop */}
            <div className="hidden md:flex flex-wrap items-center justify-center gap-4">
              <Link to="/list/create">
                <Button variant="primary" size="lg">
                  <Crosshair size={20} className="mr-2" />
                  New Mission
                </Button>
              </Link>
              <Link to="/list/upload">
                <Button variant="secondary" size="lg">
                  <Upload size={20} className="mr-2" />
                  Import List
                </Button>
              </Link>
              <Link to="/stores">
                <Button variant="secondary" size="lg">
                  <Store size={20} className="mr-2" />
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
```

**Step 2: Commit HomePage**

```bash
git add frontend-react/src/pages/HomePage.tsx
git commit -m "feat: Complete tactical redesign of HomePage

- Mission control hero section with scan effects
- Status dashboard with animated indicators
- Tactical card design with corner brackets
- Orbitron display typography
- JetBrains Mono data labels
- Cyan/amber/green status system

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Update Remaining Components

**Files:**
- Modify: `frontend-react/src/components/ui/Skeleton.tsx`
- Modify: `frontend-react/src/components/ui/Input.tsx`
- Modify: `frontend-react/src/components/ui/Select.tsx`
- Modify: `frontend-react/src/components/ui/Progress.tsx`
- Modify: `frontend-react/src/components/packing-lists/ProgressStats.tsx`
- Modify: `frontend-react/src/components/packing-lists/FilterBar.tsx`
- Modify: `frontend-react/src/components/packing-lists/ItemCard.tsx`
- Modify: `frontend-react/src/components/packing-lists/PackingListDetail.tsx`
- Modify: `frontend-react/src/pages/ListDetailPage.tsx`
- Modify: `frontend-react/src/pages/CreateListPage.tsx`
- Modify: `frontend-react/src/pages/UploadListPage.tsx`
- Modify: `frontend-react/src/pages/StoreListPage.tsx`
- Modify: `frontend-react/src/pages/NotFoundPage.tsx`

This task involves updating all remaining components with the tactical styling. Each component should use:
- `font-display` for headers
- `font-tactical` for data labels and status text
- Tactical color palette (cyan/amber/red indicators)
- Corner bracket decorations on cards
- Glow effects on interactive elements
- Uppercase tracking for tactical text

**NOTE:** Due to the extensive nature of this task, implement these updates component by component, committing after each logical group.

---

### Task 6: Final Build and Deploy

**Step 1: Run full build**

```bash
cd /Users/sac/Git/community-packing-list/frontend-react && npm run build
```

**Step 2: Test locally**

```bash
npm run preview
```

**Step 3: Deploy to Cloudflare Pages**

```bash
npx wrangler pages deploy dist --project-name=community-packing-list
```

**Step 4: Verify and commit**

```bash
git add -A
git commit -m "feat: Complete tactical UI overhaul - Mission Control design

- Orbitron + JetBrains Mono typography system
- Cyan/amber/red tactical color scheme
- Grid overlays and scan effects
- Corner bracket card decorations
- Status indicators with pulse animations
- All components updated with tactical styling

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin main
```

---

## Design Summary

This plan transforms the Community Packing List into a **TACTICAL MISSION CONTROL** interface that's:

1. **UNFORGETTABLE** - Military ops center aesthetic that stands out
2. **FUNCTIONAL** - High information density, clear visual hierarchy
3. **COHESIVE** - Consistent design language across all components
4. **MOBILE-FIRST** - Touch-friendly targets, bottom nav, pull-to-refresh

Key visual elements:
- Grid pattern overlays
- Scan line animations
- Corner bracket decorations
- Pulse indicators for status
- Gradient buttons with shine effects
- Monospace typography for data
- Cyan/amber/red status system

Total: 6 major tasks covering foundation, layout, components, and pages
