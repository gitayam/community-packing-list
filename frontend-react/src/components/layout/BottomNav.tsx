import { Link, useLocation } from 'react-router-dom';
import { Home, Package, Plus, Store } from 'lucide-react';

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
                    {/* Outer pulse ring */}
                    <div className="absolute inset-0 w-14 h-14 rounded-full border border-accent-cyan/20 animate-pulse" style={{ margin: '-2px' }} />
                    {/* Main button */}
                    <div className="relative flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-accent-cyan to-accent-cyan-dim glow-cyan tap-active transition-all duration-200 hover:scale-105">
                      <Plus size={26} className="text-tactical-bg" strokeWidth={2.5} />
                    </div>
                    {/* Label */}
                    <span className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[9px] font-tactical text-accent-cyan uppercase tracking-wider whitespace-nowrap">
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
                  <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                </div>
                <span className={`text-[9px] mt-0.5 font-tactical uppercase tracking-wider ${isActive ? 'text-accent-cyan' : ''}`}>
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
