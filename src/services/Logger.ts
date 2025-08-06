/**
 * Enhanced logging service with different log levels and structured logging
 * Provides centralized logging for debugging, monitoring, and error tracking
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: Date;
  category?: string;
  data?: any;
  stack?: string;
  userAgent?: string;
  url?: string;
}

export class Logger {
  private static instance: Logger;
  private currentLevel: LogLevel = LogLevel.INFO;
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;
  private remoteLoggingEnabled: boolean = false;
  private remoteEndpoint?: string;

  private constructor() {
    // Set log level based on environment
    if (process.env.NODE_ENV === 'development') {
      this.currentLevel = LogLevel.DEBUG;
    } else if (process.env.NODE_ENV === 'production') {
      this.currentLevel = LogLevel.WARN;
    }
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * Configure logger settings
   */
  configure(options: {
    level?: LogLevel;
    maxLogs?: number;
    remoteEndpoint?: string;
  }): void {
    if (options.level !== undefined) {
      this.currentLevel = options.level;
    }
    if (options.maxLogs !== undefined) {
      this.maxLogs = options.maxLogs;
    }
    if (options.remoteEndpoint) {
      this.remoteEndpoint = options.remoteEndpoint;
      this.remoteLoggingEnabled = true;
    }
  }

  /**
   * Log a debug message
   */
  debug(message: string, category?: string, data?: any): void {
    this.log(LogLevel.DEBUG, message, category, data);
  }

  /**
   * Log an info message
   */
  info(message: string, category?: string, data?: any): void {
    this.log(LogLevel.INFO, message, category, data);
  }

  /**
   * Log a warning message
   */
  warn(message: string, category?: string, data?: any): void {
    this.log(LogLevel.WARN, message, category, data);
  }

  /**
   * Log an error message
   */
  error(message: string, category?: string, error?: Error | any): void {
    const stack = error instanceof Error ? error.stack : undefined;
    this.log(LogLevel.ERROR, message, category, error, stack);
  }

  /**
   * Log a user action for analytics
   */
  logUserAction(action: string, data?: any): void {
    this.info(`User Action: ${action}`, 'user_action', data);
  }

  /**
   * Log a performance metric
   */
  logPerformance(metric: string, duration: number, data?: any): void {
    this.info(`Performance: ${metric} took ${duration}ms`, 'performance', {
      metric,
      duration,
      ...data
    });
  }

  /**
   * Log an API call
   */
  logApiCall(method: string, url: string, duration?: number, status?: number): void {
    this.info(`API: ${method} ${url}`, 'api', {
      method,
      url,
      duration,
      status
    });
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, category?: string, data?: any, stack?: string): void {
    if (level < this.currentLevel) {
      return;
    }

    const logEntry: LogEntry = {
      level,
      message,
      timestamp: new Date(),
      category,
      data,
      stack,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Add to internal log store
    this.logs.push(logEntry);
    
    // Maintain max logs limit
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Console output
    this.outputToConsole(logEntry);

    // Remote logging (if enabled)
    if (this.remoteLoggingEnabled && level >= LogLevel.WARN) {
      this.sendToRemote(logEntry);
    }
  }

  /**
   * Output log entry to console with appropriate styling
   */
  private outputToConsole(entry: LogEntry): void {
    const timestamp = entry.timestamp.toISOString();
    const prefix = entry.category ? `[${entry.category}]` : '';
    const message = `${timestamp} ${prefix} ${entry.message}`;

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(`🐛 ${message}`, entry.data);
        break;
      case LogLevel.INFO:
        console.info(`ℹ️ ${message}`, entry.data);
        break;
      case LogLevel.WARN:
        console.warn(`⚠️ ${message}`, entry.data);
        break;
      case LogLevel.ERROR:
        console.error(`❌ ${message}`, entry.data, entry.stack);
        break;
    }
  }

  /**
   * Send log entry to remote logging service
   */
  private async sendToRemote(entry: LogEntry): void {
    if (!this.remoteEndpoint) return;

    try {
      await fetch(this.remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry)
      });
    } catch (error) {
      // Avoid infinite logging loop
      console.error('Failed to send log to remote service:', error);
    }
  }

  /**
   * Get recent logs
   */
  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logs.slice(-count);
  }

  /**
   * Get logs by category
   */
  getLogsByCategory(category: string): LogEntry[] {
    return this.logs.filter(log => log.category === category);
  }

  /**
   * Get logs by level
   */
  getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logs.filter(log => log.level >= level);
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = [];
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Create a performance timer
   */
  createTimer(name: string): PerformanceTimer {
    return new PerformanceTimer(name, this);
  }
}

/**
 * Performance timer utility
 */
export class PerformanceTimer {
  private startTime: number;
  private name: string;
  private logger: Logger;

  constructor(name: string, logger: Logger) {
    this.name = name;
    this.logger = logger;
    this.startTime = performance.now();
  }

  /**
   * End the timer and log the duration
   */
  end(data?: any): number {
    const duration = performance.now() - this.startTime;
    this.logger.logPerformance(this.name, duration, data);
    return duration;
  }
}

/**
 * Global error handler
 */
export class ErrorHandler {
  private logger: Logger;

  constructor(logger: Logger) {
    this.logger = logger;
    this.setupGlobalHandlers();
  }

  private setupGlobalHandlers(): void {
    // Handle uncaught JavaScript errors
    window.addEventListener('error', (event) => {
      this.logger.error('Uncaught Error', 'global_error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logger.error('Unhandled Promise Rejection', 'promise_rejection', {
        reason: event.reason
      });
    });
  }

  /**
   * Handle API errors consistently
   */
  handleApiError(error: any, context: string): void {
    let errorMessage = 'Unknown error occurred';
    let errorData: any = {};

    if (error.response) {
      // Server responded with error status
      errorMessage = `API Error: ${error.response.status}`;
      errorData = {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.config?.url,
        method: error.config?.method
      };
    } else if (error.request) {
      // Network error
      errorMessage = 'Network Error: No response received';
      errorData = {
        url: error.config?.url,
        method: error.config?.method
      };
    } else {
      // Request setup error
      errorMessage = `Request Error: ${error.message}`;
      errorData = {
        message: error.message,
        url: error.config?.url
      };
    }

    this.logger.error(errorMessage, context, errorData);
  }

  /**
   * Handle form validation errors
   */
  handleValidationError(errors: Record<string, string[]>, context: string): void {
    this.logger.warn('Form Validation Error', context, errors);
  }

  /**
   * Report error to external service
   */
  async reportError(error: Error, context: string, additionalData?: any): Promise<void> {
    this.logger.error(`Reported Error: ${error.message}`, context, {
      error: error.message,
      stack: error.stack,
      ...additionalData
    });

    // Could integrate with services like Sentry, Rollbar, etc.
  }
}

// Export singleton instances
export const logger = Logger.getInstance();
export const errorHandler = new ErrorHandler(logger);