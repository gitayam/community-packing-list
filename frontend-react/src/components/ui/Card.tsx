import type { ReactNode } from 'react';

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
      <div className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2 border-accent-cyan/30 rounded-tl" />
      <div className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2 border-accent-cyan/30 rounded-tr" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-l-2 border-b-2 border-accent-cyan/30 rounded-bl" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-b-2 border-accent-cyan/30 rounded-br" />

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
