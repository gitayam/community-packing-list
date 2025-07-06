import axios, { AxiosResponse } from 'axios';
import type { ApiResponse, VoteResponse } from './types';

// API base configuration
const API_BASE_URL = '';

// Configure axios defaults
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Get CSRF token from Django template
function getCSRFToken(): string {
  const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
  return tokenElement?.value || '';
}

// API helper functions
export class ApiClient {
  private static instance: ApiClient;
  
  private constructor() {}
  
  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  async get<T>(url: string): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error('API GET error:', error);
      throw error;
    }
  }

  async post<T>(url: string, data: FormData | object): Promise<ApiResponse<T>> {
    try {
      const headers: Record<string, string> = {
        'X-CSRFToken': getCSRFToken()
      };

      if (data instanceof FormData) {
        delete headers['Content-Type']; // Let browser set multipart boundary
      }

      const response: AxiosResponse<ApiResponse<T>> = await axios.post(url, data, { headers });
      return response.data;
    } catch (error) {
      console.error('API POST error:', error);
      throw error;
    }
  }

  async vote(priceId: number, voteType: 'up' | 'down'): Promise<VoteResponse> {
    const formData = new FormData();
    formData.append('price_id', priceId.toString());
    formData.append('vote_type', voteType);

    try {
      const response: AxiosResponse<VoteResponse> = await axios.post('/handle_vote/', formData, {
        headers: {
          'X-CSRFToken': getCSRFToken()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Vote error:', error);
      throw error;
    }
  }
}

// DOM utility functions
export class DOMUtils {
  static getElement<T extends HTMLElement>(selector: string): T | null {
    return document.querySelector(selector) as T | null;
  }

  static getElementOrThrow<T extends HTMLElement>(selector: string): T {
    const element = this.getElement<T>(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    return element;
  }

  static getElements<T extends HTMLElement>(selector: string): T[] {
    return Array.from(document.querySelectorAll(selector)) as T[];
  }

  static createElement<K extends keyof HTMLElementTagNameMap>(
    tagName: K,
    attributes: Record<string, string> = {},
    textContent?: string
  ): HTMLElementTagNameMap[K] {
    const element = document.createElement(tagName);
    
    Object.entries(attributes).forEach(([key, value]) => {
      element.setAttribute(key, value);
    });
    
    if (textContent) {
      element.textContent = textContent;
    }
    
    return element;
  }

  static addEventListeners(
    element: HTMLElement,
    events: Record<string, EventListener>
  ): void {
    Object.entries(events).forEach(([event, listener]) => {
      element.addEventListener(event, listener);
    });
  }

  static removeEventListeners(
    element: HTMLElement,
    events: Record<string, EventListener>
  ): void {
    Object.entries(events).forEach(([event, listener]) => {
      element.removeEventListener(event, listener);
    });
  }
}

// Form utility functions
export class FormUtils {
  static getFormData(form: HTMLFormElement): FormData {
    return new FormData(form);
  }

  static getFormDataAsObject(form: HTMLFormElement): Record<string, any> {
    const formData = new FormData(form);
    const data: Record<string, any> = {};
    
    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }
    
    return data;
  }

  static setFormData(form: HTMLFormElement, data: Record<string, any>): void {
    Object.entries(data).forEach(([key, value]) => {
      const field = form.querySelector(`[name="${key}"]`) as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
      if (field) {
        if (field.type === 'checkbox') {
          (field as HTMLInputElement).checked = Boolean(value);
        } else {
          field.value = String(value);
        }
      }
    });
  }

  static clearForm(form: HTMLFormElement): void {
    form.reset();
  }

  static validateForm(form: HTMLFormElement): boolean {
    return form.checkValidity();
  }

  static showFormErrors(form: HTMLFormElement, errors: Record<string, string[]>): void {
    // Clear existing error displays
    form.querySelectorAll('.form-field-errors').forEach(el => el.remove());
    
    Object.entries(errors).forEach(([fieldName, fieldErrors]) => {
      const field = form.querySelector(`[name="${fieldName}"]`) as HTMLElement;
      if (field) {
        const errorList = DOMUtils.createElement('ul', { class: 'form-field-errors' });
        fieldErrors.forEach(error => {
          const errorItem = DOMUtils.createElement('li', {}, error);
          errorList.appendChild(errorItem);
        });
        
        // Insert after the field
        field.parentNode?.insertBefore(errorList, field.nextSibling);
      }
    });
  }
}

// UI utility functions
export class UIUtils {
  static showLoading(button: HTMLButtonElement): void {
    button.classList.add('loading');
    button.disabled = true;
    button.textContent = 'Loading...';
  }

  static hideLoading(button: HTMLButtonElement, originalText: string): void {
    button.classList.remove('loading');
    button.disabled = false;
    button.textContent = originalText;
  }

  static showModal(modalId: string): void {
    const modal = DOMUtils.getElement<HTMLElement>(`#${modalId}`);
    if (modal) {
      modal.style.display = 'flex';
    }
  }

  static hideModal(modalId: string): void {
    const modal = DOMUtils.getElement<HTMLElement>(`#${modalId}`);
    if (modal) {
      modal.style.display = 'none';
    }
  }

  static showNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    const notification = DOMUtils.createElement('div', {
      class: `notification notification-${type}`,
      style: `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 4px;
        color: white;
        z-index: 10000;
        max-width: 300px;
        word-wrap: break-word;
      `
    }, message);

    // Set background color based on type
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      info: '#17a2b8'
    };
    notification.style.backgroundColor = colors[type];

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }

  static formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }

  static formatDistance(distance: number): string {
    return `${distance.toFixed(2)} km`;
  }

  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: number;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = window.setTimeout(() => func(...args), wait);
    };
  }

  static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

// Geolocation utility functions
export class GeolocationUtils {
  static async getCurrentPosition(): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      });
    });
  }

  static getErrorMessage(error: GeolocationPositionError): string {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return "User denied the request for Geolocation.";
      case error.POSITION_UNAVAILABLE:
        return "Location information is unavailable.";
      case error.TIMEOUT:
        return "The request to get user location timed out.";
      default:
        return "An unknown error occurred.";
    }
  }
}

// Export singleton instances
export const apiClient = ApiClient.getInstance(); 