/**
 * Advanced caching service with multiple storage backends and cache strategies
 * Provides intelligent caching with TTL, size limits, and cache warming
 */

import { logger } from './Logger';

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  maxSize?: number; // Maximum cache size
  priority?: number; // Cache priority (higher = more important)
  tags?: string[]; // Tags for cache invalidation
}

export interface CacheEntry<T = any> {
  value: T;
  timestamp: number;
  ttl: number;
  accessCount: number;
  lastAccess: number;
  priority: number;
  size: number;
  tags: string[];
}

export interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitCount: number;
  missCount: number;
  hitRate: number;
  oldestEntry?: number;
  newestEntry?: number;
}

export abstract class CacheBackend {
  abstract get<T>(key: string): CacheEntry<T> | null;
  abstract set<T>(key: string, entry: CacheEntry<T>): void;
  abstract delete(key: string): boolean;
  abstract clear(): void;
  abstract keys(): string[];
  abstract size(): number;
}

/**
 * Memory cache backend
 */
export class MemoryCacheBackend extends CacheBackend {
  private cache = new Map<string, CacheEntry>();

  get<T>(key: string): CacheEntry<T> | null {
    return this.cache.get(key) as CacheEntry<T> || null;
  }

  set<T>(key: string, entry: CacheEntry<T>): void {
    this.cache.set(key, entry);
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  keys(): string[] {
    return Array.from(this.cache.keys());
  }

  size(): number {
    return this.cache.size;
  }
}

/**
 * LocalStorage cache backend
 */
export class LocalStorageCacheBackend extends CacheBackend {
  private prefix = 'cache_';

  get<T>(key: string): CacheEntry<T> | null {
    try {
      const item = localStorage.getItem(this.prefix + key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  }

  set<T>(key: string, entry: CacheEntry<T>): void {
    try {
      localStorage.setItem(this.prefix + key, JSON.stringify(entry));
    } catch (error) {
      logger.warn('Failed to save to localStorage cache', 'cache', error);
    }
  }

  delete(key: string): boolean {
    try {
      localStorage.removeItem(this.prefix + key);
      return true;
    } catch {
      return false;
    }
  }

  clear(): void {
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.prefix)) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  keys(): string[] {
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.prefix)) {
        keys.push(key.substring(this.prefix.length));
      }
    }
    return keys;
  }

  size(): number {
    return this.keys().length;
  }
}

/**
 * Cache eviction strategies
 */
export enum EvictionStrategy {
  LRU = 'lru', // Least Recently Used
  LFU = 'lfu', // Least Frequently Used
  FIFO = 'fifo', // First In First Out
  TTL = 'ttl' // Time To Live based
}

export class CacheService {
  private static instance: CacheService;
  private backends: Map<string, CacheBackend> = new Map();
  private defaultBackend = 'memory';
  private maxSize = 1000;
  private defaultTTL = 5 * 60 * 1000; // 5 minutes
  private stats = {
    hitCount: 0,
    missCount: 0
  };
  private evictionStrategy = EvictionStrategy.LRU;

  private constructor() {
    // Initialize default backends
    this.backends.set('memory', new MemoryCacheBackend());
    this.backends.set('localStorage', new LocalStorageCacheBackend());

    // Start cleanup interval
    this.startCleanupInterval();

    logger.info('CacheService initialized', 'cache', {
      backends: Array.from(this.backends.keys()),
      maxSize: this.maxSize,
      defaultTTL: this.defaultTTL
    });
  }

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  /**
   * Configure cache service
   */
  configure(options: {
    maxSize?: number;
    defaultTTL?: number;
    evictionStrategy?: EvictionStrategy;
  }): void {
    if (options.maxSize !== undefined) {
      this.maxSize = options.maxSize;
    }
    if (options.defaultTTL !== undefined) {
      this.defaultTTL = options.defaultTTL;
    }
    if (options.evictionStrategy !== undefined) {
      this.evictionStrategy = options.evictionStrategy;
    }

    logger.info('Cache configuration updated', 'cache', options);
  }

  /**
   * Get value from cache
   */
  get<T>(key: string, backend = this.defaultBackend): T | null {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      logger.warn(`Cache backend not found: ${backend}`, 'cache');
      return null;
    }

    const entry = cacheBackend.get<T>(key);
    if (!entry) {
      this.stats.missCount++;
      logger.debug(`Cache miss: ${key}`, 'cache');
      return null;
    }

    const now = Date.now();

    // Check if expired
    if (now > entry.timestamp + entry.ttl) {
      cacheBackend.delete(key);
      this.stats.missCount++;
      logger.debug(`Cache expired: ${key}`, 'cache');
      return null;
    }

    // Update access stats
    entry.accessCount++;
    entry.lastAccess = now;
    cacheBackend.set(key, entry);

    this.stats.hitCount++;
    logger.debug(`Cache hit: ${key}`, 'cache');
    
    return entry.value;
  }

  /**
   * Set value in cache
   */
  set<T>(
    key: string, 
    value: T, 
    options: CacheOptions = {},
    backend = this.defaultBackend
  ): void {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      logger.warn(`Cache backend not found: ${backend}`, 'cache');
      return;
    }

    const now = Date.now();
    const ttl = options.ttl ?? this.defaultTTL;
    const priority = options.priority ?? 1;
    const tags = options.tags ?? [];

    const entry: CacheEntry<T> = {
      value,
      timestamp: now,
      ttl,
      accessCount: 1,
      lastAccess: now,
      priority,
      size: this.calculateSize(value),
      tags
    };

    // Check if we need to make space
    if (cacheBackend.size() >= this.maxSize) {
      this.evict(backend, 1);
    }

    cacheBackend.set(key, entry);
    
    logger.debug(`Cache set: ${key}`, 'cache', {
      ttl,
      priority,
      tags,
      size: entry.size
    });
  }

  /**
   * Delete from cache
   */
  delete(key: string, backend = this.defaultBackend): boolean {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return false;
    }

    const deleted = cacheBackend.delete(key);
    if (deleted) {
      logger.debug(`Cache delete: ${key}`, 'cache');
    }
    
    return deleted;
  }

  /**
   * Check if key exists in cache (without updating access stats)
   */
  has(key: string, backend = this.defaultBackend): boolean {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return false;
    }

    const entry = cacheBackend.get(key);
    if (!entry) {
      return false;
    }

    // Check if expired
    const now = Date.now();
    if (now > entry.timestamp + entry.ttl) {
      cacheBackend.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Get or set pattern - get from cache or execute function and cache result
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T> | T,
    options: CacheOptions = {},
    backend = this.defaultBackend
  ): Promise<T> {
    // Try to get from cache first
    const cached = this.get<T>(key, backend);
    if (cached !== null) {
      return cached;
    }

    // Execute factory function
    const timer = logger.createTimer(`cache_factory_${key}`);
    try {
      const value = await factory();
      timer.end({ cache_miss: true });
      
      // Cache the result
      this.set(key, value, options, backend);
      
      return value;
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * Invalidate cache entries by tags
   */
  invalidateByTags(tags: string[], backend = this.defaultBackend): number {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return 0;
    }

    const keys = cacheBackend.keys();
    let invalidatedCount = 0;

    keys.forEach(key => {
      const entry = cacheBackend.get(key);
      if (entry && entry.tags.some(tag => tags.includes(tag))) {
        cacheBackend.delete(key);
        invalidatedCount++;
      }
    });

    if (invalidatedCount > 0) {
      logger.info(`Invalidated ${invalidatedCount} cache entries by tags`, 'cache', { tags });
    }

    return invalidatedCount;
  }

  /**
   * Invalidate cache entries by key pattern
   */
  invalidateByPattern(pattern: RegExp, backend = this.defaultBackend): number {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return 0;
    }

    const keys = cacheBackend.keys();
    let invalidatedCount = 0;

    keys.forEach(key => {
      if (pattern.test(key)) {
        cacheBackend.delete(key);
        invalidatedCount++;
      }
    });

    if (invalidatedCount > 0) {
      logger.info(`Invalidated ${invalidatedCount} cache entries by pattern`, 'cache', { pattern: pattern.source });
    }

    return invalidatedCount;
  }

  /**
   * Warm cache with data
   */
  async warm<T>(entries: Array<{ key: string; factory: () => Promise<T> | T; options?: CacheOptions }>, backend = this.defaultBackend): Promise<void> {
    logger.info(`Warming cache with ${entries.length} entries`, 'cache');
    
    const timer = logger.createTimer('cache_warm');

    const promises = entries.map(async ({ key, factory, options }) => {
      try {
        // Only warm if not already cached
        if (!this.has(key, backend)) {
          const value = await factory();
          this.set(key, value, options, backend);
        }
      } catch (error) {
        logger.warn(`Failed to warm cache for key: ${key}`, 'cache', error);
      }
    });

    await Promise.allSettled(promises);
    timer.end({ entryCount: entries.length });
  }

  /**
   * Clear all cache entries
   */
  clear(backend = this.defaultBackend): void {
    const cacheBackend = this.backends.get(backend);
    if (cacheBackend) {
      cacheBackend.clear();
      logger.info(`Cache cleared for backend: ${backend}`, 'cache');
    }
  }

  /**
   * Clear all backends
   */
  clearAll(): void {
    this.backends.forEach((backend, name) => {
      backend.clear();
      logger.info(`Cache cleared for backend: ${name}`, 'cache');
    });
  }

  /**
   * Get cache statistics
   */
  getStats(backend = this.defaultBackend): CacheStats {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return {
        totalEntries: 0,
        totalSize: 0,
        hitCount: this.stats.hitCount,
        missCount: this.stats.missCount,
        hitRate: 0
      };
    }

    const keys = cacheBackend.keys();
    let totalSize = 0;
    let oldestEntry: number | undefined;
    let newestEntry: number | undefined;

    keys.forEach(key => {
      const entry = cacheBackend.get(key);
      if (entry) {
        totalSize += entry.size;
        
        if (!oldestEntry || entry.timestamp < oldestEntry) {
          oldestEntry = entry.timestamp;
        }
        if (!newestEntry || entry.timestamp > newestEntry) {
          newestEntry = entry.timestamp;
        }
      }
    });

    const totalRequests = this.stats.hitCount + this.stats.missCount;
    const hitRate = totalRequests > 0 ? this.stats.hitCount / totalRequests : 0;

    return {
      totalEntries: keys.length,
      totalSize,
      hitCount: this.stats.hitCount,
      missCount: this.stats.missCount,
      hitRate,
      oldestEntry,
      newestEntry
    };
  }

  /**
   * Evict cache entries based on strategy
   */
  private evict(backend: string, count: number): void {
    const cacheBackend = this.backends.get(backend);
    if (!cacheBackend) {
      return;
    }

    const keys = cacheBackend.keys();
    const entries = keys.map(key => ({
      key,
      entry: cacheBackend.get(key)!
    })).filter(({ entry }) => entry);

    let toEvict: string[] = [];

    switch (this.evictionStrategy) {
      case EvictionStrategy.LRU:
        entries.sort((a, b) => a.entry.lastAccess - b.entry.lastAccess);
        toEvict = entries.slice(0, count).map(({ key }) => key);
        break;

      case EvictionStrategy.LFU:
        entries.sort((a, b) => a.entry.accessCount - b.entry.accessCount);
        toEvict = entries.slice(0, count).map(({ key }) => key);
        break;

      case EvictionStrategy.FIFO:
        entries.sort((a, b) => a.entry.timestamp - b.entry.timestamp);
        toEvict = entries.slice(0, count).map(({ key }) => key);
        break;

      case EvictionStrategy.TTL:
        const now = Date.now();
        entries.sort((a, b) => {
          const aExpiry = a.entry.timestamp + a.entry.ttl;
          const bExpiry = b.entry.timestamp + b.entry.ttl;
          return aExpiry - bExpiry;
        });
        toEvict = entries.slice(0, count).map(({ key }) => key);
        break;
    }

    // Also consider priority (lower priority gets evicted first)
    toEvict.sort((a, b) => {
      const entryA = cacheBackend.get(a)!;
      const entryB = cacheBackend.get(b)!;
      return entryA.priority - entryB.priority;
    });

    // Evict entries
    toEvict.slice(0, count).forEach(key => {
      cacheBackend.delete(key);
    });

    if (toEvict.length > 0) {
      logger.info(`Evicted ${toEvict.length} cache entries`, 'cache', {
        strategy: this.evictionStrategy,
        backend
      });
    }
  }

  /**
   * Calculate approximate size of value
   */
  private calculateSize(value: any): number {
    if (value === null || value === undefined) {
      return 0;
    }

    const jsonString = JSON.stringify(value);
    return jsonString.length * 2; // Approximate bytes (UTF-16)
  }

  /**
   * Start cleanup interval for expired entries
   */
  private startCleanupInterval(): void {
    setInterval(() => {
      this.cleanup();
    }, 60000); // Run every minute
  }

  /**
   * Cleanup expired entries
   */
  private cleanup(): void {
    const now = Date.now();
    let cleanedCount = 0;

    this.backends.forEach((backend, backendName) => {
      const keys = backend.keys();
      
      keys.forEach(key => {
        const entry = backend.get(key);
        if (entry && now > entry.timestamp + entry.ttl) {
          backend.delete(key);
          cleanedCount++;
        }
      });
    });

    if (cleanedCount > 0) {
      logger.debug(`Cleaned up ${cleanedCount} expired cache entries`, 'cache');
    }
  }
}

// Export singleton instance
export const cacheService = CacheService.getInstance();

// Common cache configurations
export const CacheConfigs = {
  SHORT: { ttl: 30 * 1000, priority: 1 }, // 30 seconds
  MEDIUM: { ttl: 5 * 60 * 1000, priority: 2 }, // 5 minutes
  LONG: { ttl: 30 * 60 * 1000, priority: 3 }, // 30 minutes
  USER_DATA: { ttl: 10 * 60 * 1000, priority: 5, tags: ['user'] }, // 10 minutes, high priority
  API_DATA: { ttl: 5 * 60 * 1000, priority: 3, tags: ['api'] }, // 5 minutes
  STATIC_DATA: { ttl: 60 * 60 * 1000, priority: 4, tags: ['static'] } // 1 hour
};