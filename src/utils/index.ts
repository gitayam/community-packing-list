// Advanced TypeScript utilities for the packing list application

/**
 * Type-safe event emitter for component communication
 */
export class TypedEventEmitter<T extends Record<string, any[]>> {
  private listeners = new Map<keyof T, Set<(...args: any[]) => void>>();

  on<K extends keyof T>(event: K, listener: (...args: T[K]) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);

    // Return unsubscribe function
    return () => this.off(event, listener);
  }

  off<K extends keyof T>(event: K, listener: (...args: T[K]) => void): void {
    this.listeners.get(event)?.delete(listener);
  }

  emit<K extends keyof T>(event: K, ...args: T[K]): void {
    this.listeners.get(event)?.forEach(listener => listener(...args));
  }

  clear(): void {
    this.listeners.clear();
  }
}

/**
 * Performance-optimized debounce with TypeScript generics
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): (...args: Parameters<T>) => void {
  let timeout: number | undefined;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = undefined;
      if (!immediate) func(...args);
    };

    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = window.setTimeout(later, wait);

    if (callNow) func(...args);
  };
}

/**
 * Throttle function with TypeScript support
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Type-safe local storage wrapper
 */
export class TypedStorage<T extends Record<string, any>> {
  constructor(private prefix = 'app') {}

  set<K extends keyof T>(key: K, value: T[K]): void {
    try {
      localStorage.setItem(`${this.prefix}:${String(key)}`, JSON.stringify(value));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  }

  get<K extends keyof T>(key: K): T[K] | null {
    try {
      const item = localStorage.getItem(`${this.prefix}:${String(key)}`);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.warn('Failed to read from localStorage:', error);
      return null;
    }
  }

  remove<K extends keyof T>(key: K): void {
    localStorage.removeItem(`${this.prefix}:${String(key)}`);
  }

  clear(): void {
    const keys = Object.keys(localStorage).filter(key => key.startsWith(`${this.prefix}:`));
    keys.forEach(key => localStorage.removeItem(key));
  }
}

/**
 * Intersection Observer wrapper for lazy loading and animations
 */
export class IntersectionObserverManager {
  private observer: IntersectionObserver;
  private callbacks = new Map<Element, (entry: IntersectionObserverEntry) => void>();

  constructor(options: IntersectionObserverInit = {}) {
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const callback = this.callbacks.get(entry.target);
        if (callback) {
          callback(entry);
        }
      });
    }, options);
  }

  observe(element: Element, callback: (entry: IntersectionObserverEntry) => void): void {
    this.callbacks.set(element, callback);
    this.observer.observe(element);
  }

  unobserve(element: Element): void {
    this.callbacks.delete(element);
    this.observer.unobserve(element);
  }

  disconnect(): void {
    this.observer.disconnect();
    this.callbacks.clear();
  }
}

/**
 * Async retry utility with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  baseDelay = 1000
): Promise<T> {
  let attempt = 1;

  while (attempt <= maxAttempts) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error;
      }

      const delay = baseDelay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, delay));
      attempt++;
    }
  }

  throw new Error('Max attempts reached');
}

/**
 * Type-safe CSS class utility
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Format currency with internationalization support
 */
export function formatCurrency(
  amount: number,
  currency = 'USD',
  locale = 'en-US'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
}

/**
 * Format relative time
 */
export function formatRelativeTime(date: Date, locale = 'en-US'): string {
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  const now = new Date();
  const diffInSeconds = (date.getTime() - now.getTime()) / 1000;

  if (Math.abs(diffInSeconds) < 60) {
    return rtf.format(Math.round(diffInSeconds), 'second');
  } else if (Math.abs(diffInSeconds) < 3600) {
    return rtf.format(Math.round(diffInSeconds / 60), 'minute');
  } else if (Math.abs(diffInSeconds) < 86400) {
    return rtf.format(Math.round(diffInSeconds / 3600), 'hour');
  } else {
    return rtf.format(Math.round(diffInSeconds / 86400), 'day');
  }
}

/**
 * Deep clone utility
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }

  if (typeof obj === 'object') {
    const cloned = {} as T;
    Object.keys(obj).forEach(key => {
      (cloned as any)[key] = deepClone((obj as any)[key]);
    });
    return cloned;
  }

  return obj;
}

/**
 * Type guard utilities
 */
export function isString(value: unknown): value is string {
  return typeof value === 'string';
}

export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value);
}

export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function isArray<T>(value: unknown): value is T[] {
  return Array.isArray(value);
}

/**
 * URL utilities
 */
export function buildURL(base: string, params: Record<string, string | number | boolean>): string {
  const url = new URL(base, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    url.searchParams.set(key, String(value));
  });
  return url.toString();
}

export function getURLParam(name: string): string | null {
  return new URLSearchParams(window.location.search).get(name);
}

/**
 * Device detection utilities
 */
export function isMobile(): boolean {
  return window.innerWidth < 768;
}

export function isTablet(): boolean {
  return window.innerWidth >= 768 && window.innerWidth < 1024;
}

export function isDesktop(): boolean {
  return window.innerWidth >= 1024;
}

export function isTouchDevice(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

/**
 * Animation utilities
 */
export function animate(
  element: HTMLElement,
  keyframes: Keyframe[],
  options: KeyframeAnimationOptions
): Promise<void> {
  return new Promise(resolve => {
    const animation = element.animate(keyframes, options);
    animation.addEventListener('finish', () => resolve());
  });
}

export function fadeIn(element: HTMLElement, duration = 300): Promise<void> {
  return animate(
    element,
    [{ opacity: 0 }, { opacity: 1 }],
    { duration, easing: 'ease-out' }
  );
}

export function fadeOut(element: HTMLElement, duration = 300): Promise<void> {
  return animate(
    element,
    [{ opacity: 1 }, { opacity: 0 }],
    { duration, easing: 'ease-in' }
  );
}

export function slideDown(element: HTMLElement, duration = 300): Promise<void> {
  const height = element.scrollHeight;
  return animate(
    element,
    [
      { height: '0px', overflow: 'hidden' },
      { height: `${height}px`, overflow: 'hidden' },
    ],
    { duration, easing: 'ease-out' }
  );
}

export function slideUp(element: HTMLElement, duration = 300): Promise<void> {
  const height = element.scrollHeight;
  return animate(
    element,
    [
      { height: `${height}px`, overflow: 'hidden' },
      { height: '0px', overflow: 'hidden' },
    ],
    { duration, easing: 'ease-in' }
  );
} 