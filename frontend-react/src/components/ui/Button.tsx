import { forwardRef } from 'react';
import type { ButtonHTMLAttributes } from 'react';

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
      sm: 'px-3 py-1.5 text-[10px]',
      md: 'px-4 py-2.5 text-xs',
      lg: 'px-6 py-3 text-sm',
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
