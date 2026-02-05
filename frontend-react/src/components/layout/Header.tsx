import { Link, useLocation } from 'react-router-dom';
import { Package, Store, Search, Shield } from 'lucide-react';
import { useState } from 'react';

export function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'MISSION HQ', icon: Package },
    { path: '/stores', label: 'SUPPLY', icon: Store },
  ];

  return (
    <header className="sticky top-0 z-40 bg-tactical-surface/95 backdrop-blur-md border-b border-tactical-border">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent-cyan/50 to-transparent" />

      <div className="container mx-auto px-4 relative">
        {/* Mobile Header */}
        <div className="flex md:hidden items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center">
                <Shield size={20} className="text-accent-cyan" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-status-success rounded-full animate-pulse" />
            </div>
            <div>
              <span className="font-display text-sm font-bold text-text-primary tracking-wider">CPL</span>
              <div className="text-[9px] font-tactical text-accent-cyan uppercase tracking-[0.15em]">ONLINE</div>
            </div>
          </Link>

          <button
            onClick={() => setIsSearchOpen(!isSearchOpen)}
            className="p-2.5 rounded bg-tactical-elevated border border-tactical-border text-text-secondary hover:text-accent-cyan hover:border-accent-cyan/50 transition-all tap-active"
          >
            <Search size={20} />
          </button>
        </div>

        {/* Desktop Header */}
        <nav className="hidden md:flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-4 group">
            <div className="relative">
              <div className="w-11 h-11 rounded bg-tactical-elevated border border-accent-cyan/50 flex items-center justify-center group-hover:glow-cyan transition-all duration-300">
                <Shield size={22} className="text-accent-cyan" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-status-success rounded-full animate-pulse" />
            </div>
            <div>
              <span className="font-display text-base font-bold text-text-primary tracking-wider group-hover:text-glow-cyan transition-all">
                COMMUNITY PACKING LIST
              </span>
              <div className="text-[10px] font-tactical text-accent-cyan uppercase tracking-[0.2em]">
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
                    relative flex items-center gap-2 px-4 py-2 rounded font-tactical text-xs uppercase tracking-wider
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
                className="w-full pl-12 pr-4 py-3 rounded bg-tactical-elevated border border-tactical-border text-text-primary placeholder-text-muted font-tactical text-xs uppercase tracking-wider focus:outline-none focus:border-accent-cyan transition-all"
                autoFocus
              />
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
