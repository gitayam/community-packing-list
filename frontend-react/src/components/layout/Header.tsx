import { Link } from 'react-router-dom';
import { Package, Store } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-military-navy text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <nav className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold hover:text-military-khaki transition-colors">
            <Package size={28} />
            <span>Community Packing List</span>
          </Link>

          <div className="flex items-center gap-6">
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
        </nav>
      </div>
    </header>
  );
}
