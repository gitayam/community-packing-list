import type { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

export interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'military';
  className?: string;
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
  variant = 'default',
  className,
}: StatsCardProps) {
  const variantStyles = {
    default: 'bg-white border-gray-200',
    success: 'bg-green-50 border-green-200',
    warning: 'bg-yellow-50 border-yellow-200',
    danger: 'bg-red-50 border-red-200',
    military: 'bg-military-sand/30 border-military-olive/20',
  };

  const iconVariants = {
    default: 'text-gray-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600',
    military: 'text-military-olive',
  };

  return (
    <div
      className={clsx(
        'rounded-lg border p-6 shadow-sm transition-all hover:shadow-md',
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">{title}</p>
          <p className="mt-2 text-3xl font-bold text-military-dark">{value}</p>
          {trend && (
            <p className="mt-2 flex items-center text-sm">
              <span
                className={clsx(
                  'font-medium',
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                )}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="ml-2 text-gray-500">vs last week</span>
            </p>
          )}
        </div>
        {Icon && (
          <div
            className={clsx(
              'rounded-full p-3 bg-white/50',
              iconVariants[variant]
            )}
          >
            <Icon size={24} />
          </div>
        )}
      </div>
    </div>
  );
}
