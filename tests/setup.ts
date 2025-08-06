/**
 * Jest setup file for TypeScript testing
 * This file runs before each test file is executed
 */

import 'jest';

// Mock DOM globals
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock console to reduce noise in tests unless explicitly needed
const mockConsole = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};

// Global test setup
beforeEach(() => {
  // Mock localStorage
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
    writable: true
  });

  // Mock console
  Object.defineProperty(global, 'console', {
    value: mockConsole,
    writable: true
  });

  // Mock fetch API
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      headers: new Headers(),
      redirected: false,
      statusText: 'OK',
      type: 'basic',
      url: '',
      clone: jest.fn(),
      body: null,
      bodyUsed: false
    } as Response)
  );

  // Mock IntersectionObserver
  global.IntersectionObserver = jest.fn(() => ({
    observe: jest.fn(),
    disconnect: jest.fn(),
    unobserve: jest.fn()
  }));

  // Mock ResizeObserver
  global.ResizeObserver = jest.fn(() => ({
    observe: jest.fn(),
    disconnect: jest.fn(),
    unobserve: jest.fn()
  }));

  // Clear all mocks before each test
  jest.clearAllMocks();
});

// Global test teardown
afterEach(() => {
  // Clean up DOM after each test
  document.body.innerHTML = '';
  document.head.innerHTML = '';
});

// Custom matchers
expect.extend({
  toBeInDocument(received) {
    if (received && received.parentNode && received.parentNode === document.body) {
      return {
        message: () => `Expected element not to be in document`,
        pass: true
      };
    } else {
      return {
        message: () => `Expected element to be in document`,
        pass: false
      };
    }
  }
});

// Types for custom matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInDocument(): R;
    }
  }
}