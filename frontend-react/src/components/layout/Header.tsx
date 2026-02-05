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
