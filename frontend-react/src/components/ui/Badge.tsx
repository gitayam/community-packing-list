import type { ReactNode } from 'react';

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
