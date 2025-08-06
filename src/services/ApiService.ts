/**
 * Enhanced API service with caching, retry logic, and error handling
 * Provides centralized API management with consistent error handling
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { logger, errorHandler } from './Logger';
import type { ApiResponse, VoteResponse } from '../types';

export interface RequestConfig extends AxiosRequestConfig {
  useCache?: boolean;
  cacheTimeout?: number;
  retryCount?: number;
  retryDelay?: number;
}

export interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
}

export class ApiService {
  private static instance: ApiService;
  private axiosInstance: AxiosInstance;
  private cache: Map<string, CacheEntry> = new Map();
  private defaultCacheTimeout = 5 * 60 * 1000; // 5 minutes
  private defaultRetryCount = 3;
  private defaultRetryDelay = 1000; // 1 second

  private constructor() {
    this.axiosInstance = axios.create({
      timeout: 10000,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Add CSRF token
        const csrfToken = this.getCSRFToken();
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken;
        }

        // Log API call start
        logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, 'api');

        return config;
      },
      (error) => {
        logger.error('Request interceptor error', 'api', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => {
        // Log successful API call
        logger.logApiCall(
          response.config.method?.toUpperCase() || 'UNKNOWN',
          response.config.url || 'unknown',
          performance.now(), // This would need to be calculated properly
          response.status
        );

        return response;
      },
      (error) => {
        // Log API error
        const method = error.config?.method?.toUpperCase() || 'UNKNOWN';
        const url = error.config?.url || 'unknown';
        const status = error.response?.status;

        logger.logApiCall(method, url, undefined, status);
        errorHandler.handleApiError(error, 'api_response');

        return Promise.reject(error);
      }
    );
  }

  /**
   * GET request with caching and retry logic
   */
  async get<T>(url: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const cacheKey = this.getCacheKey('GET', url, config.params);
    
    // Check cache first
    if (config.useCache !== false) {
      const cachedData = this.getFromCache(cacheKey);
      if (cachedData) {
        logger.debug(`Cache hit for ${url}`, 'api_cache');
        return cachedData;
      }
    }

    const timer = logger.createTimer(`GET ${url}`);

    try {
      const response = await this.executeWithRetry(() =>
        this.axiosInstance.get(url, config),
        config
      );

      timer.end({ status: response.status });

      // Cache successful responses
      if (config.useCache !== false && response.status === 200) {
        this.setCache(cacheKey, response.data, config.cacheTimeout);
      }

      return response.data;
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * POST request with retry logic
   */
  async post<T>(url: string, data: FormData | object, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const timer = logger.createTimer(`POST ${url}`);

    try {
      // Handle FormData properly
      const requestConfig = { ...config };
      if (data instanceof FormData) {
        delete requestConfig.headers?.['Content-Type'];
      }

      const response = await this.executeWithRetry(() =>
        this.axiosInstance.post(url, data, requestConfig),
        config
      );

      timer.end({ status: response.status });

      // Invalidate related cache entries
      if (response.status === 200 || response.status === 201) {
        this.invalidateCacheByPattern(url);
      }

      return response.data;
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data: any, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const timer = logger.createTimer(`PUT ${url}`);

    try {
      const response = await this.executeWithRetry(() =>
        this.axiosInstance.put(url, data, config),
        config
      );

      timer.end({ status: response.status });

      // Invalidate cache
      if (response.status === 200) {
        this.invalidateCacheByPattern(url);
      }

      return response.data;
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const timer = logger.createTimer(`DELETE ${url}`);

    try {
      const response = await this.executeWithRetry(() =>
        this.axiosInstance.delete(url, config),
        config
      );

      timer.end({ status: response.status });

      // Invalidate cache
      if (response.status === 200 || response.status === 204) {
        this.invalidateCacheByPattern(url);
      }

      return response.data;
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * Specialized vote method
   */
  async vote(priceId: number, voteType: 'up' | 'down'): Promise<VoteResponse> {
    const formData = new FormData();
    formData.append('price_id', priceId.toString());
    formData.append('vote_type', voteType);

    logger.logUserAction('vote', { priceId, voteType });

    return this.post('/handle_vote/', formData);
  }

  /**
   * Batch request method
   */
  async batch(requests: Array<{ method: string; url: string; data?: any }>): Promise<any[]> {
    logger.debug(`Executing batch request with ${requests.length} requests`, 'api_batch');
    
    const timer = logger.createTimer('batch_request');

    try {
      const promises = requests.map(({ method, url, data }) => {
        switch (method.toLowerCase()) {
          case 'get':
            return this.get(url);
          case 'post':
            return this.post(url, data);
          case 'put':
            return this.put(url, data);
          case 'delete':
            return this.delete(url);
          default:
            throw new Error(`Unsupported batch method: ${method}`);
        }
      });

      const results = await Promise.allSettled(promises);
      timer.end({ requestCount: requests.length });

      return results.map((result, index) => {
        if (result.status === 'rejected') {
          logger.error(`Batch request ${index} failed`, 'api_batch', result.reason);
          return { error: result.reason };
        }
        return result.value;
      });
    } catch (error) {
      timer.end({ error: true });
      throw error;
    }
  }

  /**
   * Execute request with retry logic
   */
  private async executeWithRetry(
    requestFn: () => Promise<AxiosResponse>,
    config: RequestConfig
  ): Promise<AxiosResponse> {
    const retryCount = config.retryCount ?? this.defaultRetryCount;
    const retryDelay = config.retryDelay ?? this.defaultRetryDelay;

    for (let attempt = 1; attempt <= retryCount; attempt++) {
      try {
        return await requestFn();
      } catch (error: any) {
        const isLastAttempt = attempt === retryCount;
        const shouldRetry = this.shouldRetry(error, attempt);

        if (isLastAttempt || !shouldRetry) {
          throw error;
        }

        logger.warn(`Request attempt ${attempt} failed, retrying in ${retryDelay}ms`, 'api_retry', {
          attempt,
          error: error.message
        });

        await this.delay(retryDelay * attempt); // Exponential backoff
      }
    }

    throw new Error('Max retry attempts exceeded');
  }

  /**
   * Determine if a request should be retried
   */
  private shouldRetry(error: any, attempt: number): boolean {
    // Don't retry client errors (4xx)
    if (error.response?.status >= 400 && error.response?.status < 500) {
      return false;
    }

    // Don't retry form submission errors
    if (error.config?.method?.toLowerCase() === 'post' && error.response?.status >= 400) {
      return false;
    }

    // Retry network errors and 5xx server errors
    return !error.response || error.response.status >= 500;
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get CSRF token from DOM
   */
  private getCSRFToken(): string {
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
    return tokenElement?.value || '';
  }

  /**
   * Generate cache key
   */
  private getCacheKey(method: string, url: string, params?: any): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${method}:${url}:${paramString}`;
  }

  /**
   * Get data from cache
   */
  private getFromCache(key: string): any {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now > entry.timestamp + entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * Set data in cache
   */
  private setCache(key: string, data: any, ttl?: number): void {
    const cacheTimeout = ttl ?? this.defaultCacheTimeout;
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: cacheTimeout
    });

    // Cleanup old entries periodically
    if (this.cache.size > 100) {
      this.cleanupCache();
    }
  }

  /**
   * Invalidate cache entries by URL pattern
   */
  private invalidateCacheByPattern(urlPattern: string): void {
    const keysToDelete = Array.from(this.cache.keys()).filter(key =>
      key.includes(urlPattern)
    );

    keysToDelete.forEach(key => this.cache.delete(key));
    
    if (keysToDelete.length > 0) {
      logger.debug(`Invalidated ${keysToDelete.length} cache entries for pattern: ${urlPattern}`, 'api_cache');
    }
  }

  /**
   * Clean up expired cache entries
   */
  private cleanupCache(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    this.cache.forEach((entry, key) => {
      if (now > entry.timestamp + entry.ttl) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.cache.delete(key));
    
    logger.debug(`Cleaned up ${keysToDelete.length} expired cache entries`, 'api_cache');
  }

  /**
   * Clear all cache
   */
  clearCache(): void {
    this.cache.clear();
    logger.info('API cache cleared', 'api_cache');
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }

  /**
   * Preload data for specified URLs
   */
  async preload(urls: string[]): Promise<void> {
    logger.info(`Preloading ${urls.length} URLs`, 'api_preload');
    
    const promises = urls.map(url => 
      this.get(url, { useCache: true }).catch(error => 
        logger.warn(`Failed to preload ${url}`, 'api_preload', error)
      )
    );

    await Promise.allSettled(promises);
  }
}

// Export singleton instance
export const apiService = ApiService.getInstance();