import { Link } from 'react-router-dom';
import { Package, Store, Menu, X } from 'lucide-react';
import { useState } from 'react';

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="bg-military-navy text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-xl font-bold hover:text-military-khaki transition-colors">
            <Package size={28} />
            <span className="hidden sm:inline">Community Packing List</span>
            <span className="sm:hidden">CPL</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <Link
              to="/"
              className="flex items-center gap-2 hover:text-military-khaki transition-colors"
            >
              <Package size={20} />
              <span>Lists</span>
            </Link>
            <Link
              to="/stores"
              className="flex items-center gap-2 hover:text-military-khaki transition-colors"
            >
              <Store size={20} />
              <span>Stores</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 hover:bg-military-navy/80 rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </nav>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 animate-slideDown">
            <div className="flex flex-col gap-3">
              <Link
                to="/"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-3 px-4 py-3 hover:bg-military-navy/80 rounded-lg transition-colors"
              >
                <Package size={20} />
                <span>Packing Lists</span>
              </Link>
              <Link
                to="/stores"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-3 px-4 py-3 hover:bg-military-navy/80 rounded-lg transition-colors"
              >
                <Store size={20} />
                <span>Stores</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
