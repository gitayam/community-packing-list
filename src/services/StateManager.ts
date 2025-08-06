/**
 * Simple state management service for application state
 * Provides reactive state management with persistence and validation
 */

import { logger } from './Logger';

export type StateListener<T> = (newState: T, previousState: T) => void;
export type StateValidator<T> = (state: T) => boolean | string;

export interface StateConfig<T> {
  initialState: T;
  validators?: StateValidator<T>[];
  persist?: boolean;
  persistKey?: string;
}

export class StateManager<T = any> {
  private state: T;
  private listeners: Set<StateListener<T>> = new Set();
  private validators: StateValidator<T>[] = [];
  private persist: boolean = false;
  private persistKey?: string;
  private history: T[] = [];
  private maxHistorySize: number = 10;

  constructor(config: StateConfig<T>) {
    this.validators = config.validators || [];
    this.persist = config.persist || false;
    this.persistKey = config.persistKey;

    // Load initial state
    this.state = this.loadInitialState(config.initialState);
    
    // Save initial state to history
    this.history.push(this.deepClone(this.state));

    logger.debug('StateManager initialized', 'state', {
      persist: this.persist,
      persistKey: this.persistKey,
      initialState: this.state
    });
  }

  /**
   * Get current state
   */
  getState(): T {
    return this.deepClone(this.state);
  }

  /**
   * Set new state
   */
  setState(newState: Partial<T> | T | ((currentState: T) => T)): void {
    const previousState = this.deepClone(this.state);
    
    let updatedState: T;
    
    if (typeof newState === 'function') {
      updatedState = (newState as (currentState: T) => T)(this.state);
    } else if (typeof newState === 'object' && newState !== null) {
      updatedState = { ...this.state, ...newState };
    } else {
      updatedState = newState as T;
    }

    // Validate state
    const validationError = this.validateState(updatedState);
    if (validationError) {
      logger.error(`State validation failed: ${validationError}`, 'state', {
        previousState,
        attemptedState: updatedState
      });
      throw new Error(`State validation failed: ${validationError}`);
    }

    // Update state
    this.state = updatedState;

    // Add to history
    this.addToHistory(this.deepClone(this.state));

    // Persist if enabled
    if (this.persist) {
      this.persistState();
    }

    // Notify listeners
    this.notifyListeners(this.state, previousState);

    logger.debug('State updated', 'state', {
      previousState,
      newState: this.state
    });
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener: StateListener<T>): () => void {
    this.listeners.add(listener);
    
    logger.debug('State listener added', 'state', {
      listenerCount: this.listeners.size
    });

    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
      logger.debug('State listener removed', 'state', {
        listenerCount: this.listeners.size
      });
    };
  }

  /**
   * Update specific property in state
   */
  updateProperty<K extends keyof T>(property: K, value: T[K]): void {
    this.setState({ [property]: value } as Partial<T>);
  }

  /**
   * Reset state to initial value
   */
  reset(): void {
    if (this.history.length > 0) {
      const initialState = this.history[0];
      this.setState(initialState);
      logger.info('State reset to initial value', 'state');
    }
  }

  /**
   * Undo last state change
   */
  undo(): boolean {
    if (this.history.length > 1) {
      // Remove current state
      this.history.pop();
      
      // Get previous state
      const previousState = this.history[this.history.length - 1];
      
      // Set state without adding to history
      const oldState = this.deepClone(this.state);
      this.state = this.deepClone(previousState);
      
      // Persist if enabled
      if (this.persist) {
        this.persistState();
      }

      // Notify listeners
      this.notifyListeners(this.state, oldState);

      logger.info('State undo performed', 'state');
      return true;
    }
    
    return false;
  }

  /**
   * Get state history
   */
  getHistory(): T[] {
    return this.history.map(state => this.deepClone(state));
  }

  /**
   * Clear state history
   */
  clearHistory(): void {
    this.history = [this.deepClone(this.state)];
    logger.info('State history cleared', 'state');
  }

  /**
   * Load initial state from persistence or use default
   */
  private loadInitialState(defaultState: T): T {
    if (this.persist && this.persistKey) {
      try {
        const persistedData = localStorage.getItem(this.persistKey);
        if (persistedData) {
          const parsed = JSON.parse(persistedData);
          logger.info('State loaded from persistence', 'state', { persistKey: this.persistKey });
          return parsed;
        }
      } catch (error) {
        logger.error('Failed to load persisted state', 'state', error);
      }
    }
    
    return defaultState;
  }

  /**
   * Persist current state
   */
  private persistState(): void {
    if (!this.persistKey) return;

    try {
      localStorage.setItem(this.persistKey, JSON.stringify(this.state));
      logger.debug('State persisted', 'state', { persistKey: this.persistKey });
    } catch (error) {
      logger.error('Failed to persist state', 'state', error);
    }
  }

  /**
   * Validate state against all validators
   */
  private validateState(state: T): string | null {
    for (const validator of this.validators) {
      const result = validator(state);
      if (result !== true) {
        return typeof result === 'string' ? result : 'Validation failed';
      }
    }
    return null;
  }

  /**
   * Add state to history
   */
  private addToHistory(state: T): void {
    this.history.push(state);
    
    // Maintain max history size
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    }
  }

  /**
   * Notify all listeners of state change
   */
  private notifyListeners(newState: T, previousState: T): void {
    this.listeners.forEach(listener => {
      try {
        listener(newState, previousState);
      } catch (error) {
        logger.error('State listener error', 'state', error);
      }
    });
  }

  /**
   * Deep clone object
   */
  private deepClone(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
  }
}

/**
 * Application state interface
 */
export interface AppState {
  user?: {
    preferences: {
      viewMode: 'card' | 'table';
      itemsPerPage: number;
      showPrices: boolean;
    };
    location?: {
      latitude: number;
      longitude: number;
    };
  };
  ui: {
    loading: boolean;
    notifications: Array<{
      id: string;
      message: string;
      type: 'success' | 'error' | 'info';
      timestamp: number;
    }>;
    modals: {
      priceModal: boolean;
      itemModal: boolean;
    };
  };
  data: {
    selectedItems: Set<string>;
    cachedPrices: Map<string, any>;
    lastApiCall?: number;
  };
}

/**
 * Create application state manager
 */
function createAppStateManager(): StateManager<AppState> {
  const initialState: AppState = {
    user: {
      preferences: {
        viewMode: 'table',
        itemsPerPage: 20,
        showPrices: true
      }
    },
    ui: {
      loading: false,
      notifications: [],
      modals: {
        priceModal: false,
        itemModal: false
      }
    },
    data: {
      selectedItems: new Set(),
      cachedPrices: new Map()
    }
  };

  const validators: StateValidator<AppState>[] = [
    (state) => {
      if (state.user?.preferences.itemsPerPage && state.user.preferences.itemsPerPage <= 0) {
        return 'Items per page must be greater than 0';
      }
      return true;
    },
    (state) => {
      if (state.ui.notifications.length > 50) {
        return 'Too many notifications';
      }
      return true;
    }
  ];

  return new StateManager({
    initialState,
    validators,
    persist: true,
    persistKey: 'packingListAppState'
  });
}

// Global app state manager
export const appState = createAppStateManager();

/**
 * Utility functions for common state operations
 */
export const StateUtils = {
  /**
   * Add notification to state
   */
  addNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    const currentState = appState.getState();
    const newNotification = {
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message,
      type,
      timestamp: Date.now()
    };

    appState.setState({
      ui: {
        ...currentState.ui,
        notifications: [...currentState.ui.notifications, newNotification]
      }
    });

    // Auto-remove after 5 seconds
    setTimeout(() => {
      StateUtils.removeNotification(newNotification.id);
    }, 5000);
  },

  /**
   * Remove notification from state
   */
  removeNotification(id: string): void {
    const currentState = appState.getState();
    appState.setState({
      ui: {
        ...currentState.ui,
        notifications: currentState.ui.notifications.filter(n => n.id !== id)
      }
    });
  },

  /**
   * Set loading state
   */
  setLoading(loading: boolean): void {
    const currentState = appState.getState();
    appState.setState({
      ui: {
        ...currentState.ui,
        loading
      }
    });
  },

  /**
   * Toggle modal state
   */
  toggleModal(modal: keyof AppState['ui']['modals'], open?: boolean): void {
    const currentState = appState.getState();
    const isOpen = open !== undefined ? open : !currentState.ui.modals[modal];
    
    appState.setState({
      ui: {
        ...currentState.ui,
        modals: {
          ...currentState.ui.modals,
          [modal]: isOpen
        }
      }
    });
  },

  /**
   * Update user preferences
   */
  updatePreferences(preferences: Partial<AppState['user']['preferences']>): void {
    const currentState = appState.getState();
    appState.setState({
      user: {
        ...currentState.user,
        preferences: {
          ...currentState.user?.preferences,
          ...preferences
        }
      }
    });
  },

  /**
   * Add selected item
   */
  addSelectedItem(itemId: string): void {
    const currentState = appState.getState();
    const newSelectedItems = new Set(currentState.data.selectedItems);
    newSelectedItems.add(itemId);
    
    appState.setState({
      data: {
        ...currentState.data,
        selectedItems: newSelectedItems
      }
    });
  },

  /**
   * Remove selected item
   */
  removeSelectedItem(itemId: string): void {
    const currentState = appState.getState();
    const newSelectedItems = new Set(currentState.data.selectedItems);
    newSelectedItems.delete(itemId);
    
    appState.setState({
      data: {
        ...currentState.data,
        selectedItems: newSelectedItems
      }
    });
  },

  /**
   * Clear selected items
   */
  clearSelectedItems(): void {
    const currentState = appState.getState();
    appState.setState({
      data: {
        ...currentState.data,
        selectedItems: new Set()
      }
    });
  }
};