import { forwardRef } from 'react';
import type { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 tap-active disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
      primary: 'bg-accent-blue hover:bg-accent-glow text-white hover:glow-blue-sm',
      secondary: 'bg-dark-elevated hover:bg-dark-border text-text-primary border border-dark-border hover:border-accent-blue/50',
      danger: 'bg-status-danger hover:bg-red-600 text-white hover:glow-danger',
      success: 'bg-status-success hover:bg-emerald-600 text-white hover:glow-success',
    };

    const sizes = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-5 py-3 text-base',
      lg: 'px-8 py-4 text-lg',
    };

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
