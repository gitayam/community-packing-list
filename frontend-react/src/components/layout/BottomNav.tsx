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
