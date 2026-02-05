import type { ReactNode } from 'react';

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
    tactical: 'bg-tactical-surface text-accent-cyan border-accent-cyan/50',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[9px]',
    md: 'px-3 py-1 text-[10px]',
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
