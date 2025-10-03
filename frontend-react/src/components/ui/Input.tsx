import { forwardRef } from 'react';
import type { InputHTMLAttributes } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="mb-4">
        {label && (
          <label className="block text-sm font-medium text-military-dark mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={clsx(
            'w-full px-3 py-2 border border-gray-300 rounded-md',
            'focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent',
            'transition-colors duration-200',
            error && 'border-status-required',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-status-required">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
