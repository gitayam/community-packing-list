import { DOMUtils } from './common';

interface PriceData {
  price: number;
  quantity: number;
  store: string;
  date: string;
}

interface QuickPriceSettings {
  lastStore: string;
  recentPrices: number[];
  autoFillConfidence: string;
}

class PriceFormModalManager {
  private modal: HTMLElement | null = null;
  private addStoreDiv: HTMLElement | null = null;
  private storeSelect: HTMLSelectElement | null = null;
  private storeNameInput: HTMLInputElement | null = null;
  private priceInput: HTMLInputElement | null = null;
  private quantityInput: HTMLInputElement | null = null;
  private confidenceSelect: HTMLSelectElement | null = null;
  private pricePerUnitDisplay: HTMLElement | null = null;
  private priceValidationMessage: HTMLElement | null = null;
  private submitButton: HTMLButtonElement | null = null;
  private historicalPrices: PriceData[] = [];
  private currentItemId: string | null = null;
  private currentListId: string | null = null;
  private settings!: QuickPriceSettings;

  constructor() {
    this.loadSettings();
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.setupEventListeners();
    this.setupPriceCalculator();
    this.setupKeyboardShortcuts();
    this.setupMobileOptimizations();
    this.createModal();
    this.toggleAddStoreSection(); // Initial state
  }

  private loadSettings(): void {
    const saved = localStorage.getItem('priceFormSettings');
    this.settings = saved ? JSON.parse(saved) : {
      lastStore: '',
      recentPrices: [],
      autoFillConfidence: 'medium'
    };
  }

  private saveSettings(): void {
    localStorage.setItem('priceFormSettings', JSON.stringify(this.settings));
  }

  private setupElements(): void {
    this.modal = document.getElementById('price-modal');
    this.addStoreDiv = document.getElementById('inline-add-store');
    this.storeSelect = document.getElementById('id_store') as HTMLSelectElement;
    this.storeNameInput = document.getElementById('id_store_name') as HTMLInputElement;
    this.priceInput = document.getElementById('id_price') as HTMLInputElement;
    this.quantityInput = document.getElementById('id_quantity') as HTMLInputElement;
    this.confidenceSelect = document.getElementById('id_confidence') as HTMLSelectElement;
    this.submitButton = document.querySelector('#price-form button[type="submit"]') as HTMLButtonElement;
    
    // Create price per unit display if it doesn't exist
    if (this.priceInput && !document.getElementById('price-per-unit-display')) {
      const priceContainer = this.priceInput.parentElement;
      if (priceContainer) {
        const pricePerUnitDiv = document.createElement('div');
        pricePerUnitDiv.id = 'price-per-unit-display';
        pricePerUnitDiv.className = 'price-calculator mt-2';
        pricePerUnitDiv.innerHTML = '<small class="text-muted">Price per unit: <span id="price-per-unit-value">--</span></small>';
        priceContainer.appendChild(pricePerUnitDiv);
        this.pricePerUnitDisplay = pricePerUnitDiv;
      }
    }
    
    // Create validation message container
    if (this.priceInput && !document.getElementById('price-validation-message')) {
      const priceContainer = this.priceInput.parentElement;
      if (priceContainer) {
        const validationDiv = document.createElement('div');
        validationDiv.id = 'price-validation-message';
        validationDiv.className = 'price-validation mt-1';
        priceContainer.appendChild(validationDiv);
        this.priceValidationMessage = validationDiv;
      }
    }
  }

  private createModal(): void {
    if (this.modal) return; // Modal already exists
    
    this.modal = document.createElement('div');
    this.modal.id = 'price-modal';
    this.modal.className = 'modal-overlay';
    this.modal.innerHTML = `
      <div class="modal-content mobile-optimized">
        <div class="modal-header">
          <h3 id="modal-title">Add Price</h3>
          <button type="button" class="modal-close" onclick="closePriceModal()">×</button>
        </div>
        <div class="modal-body" id="price-modal-body">
          <!-- Form will be loaded here via AJAX -->
        </div>
      </div>
    `;
    
    document.body.appendChild(this.modal);
    
    // Add mobile-optimized CSS
    if (!document.getElementById('price-modal-styles')) {
      const styles = document.createElement('style');
      styles.id = 'price-modal-styles';
      styles.textContent = `
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: none;
          z-index: 1000;
          align-items: flex-start;
          justify-content: center;
          padding: 20px;
          box-sizing: border-box;
          overflow-y: auto;
        }
        
        .modal-content {
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          width: 100%;
          max-width: 500px;
          max-height: 90vh;
          overflow-y: auto;
          margin-top: 5vh;
        }
        
        .mobile-optimized {
          position: relative;
        }
        
        .modal-header {
          padding: 16px 20px;
          border-bottom: 1px solid #eee;
          display: flex;
          justify-content: space-between;
          align-items: center;
          position: sticky;
          top: 0;
          background: white;
          z-index: 1;
        }
        
        .modal-header h3 {
          margin: 0;
          font-size: 18px;
        }
        
        .modal-close {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
        }
        
        .modal-close:hover {
          background: #f5f5f5;
        }
        
        .modal-body {
          padding: 20px;
        }
        
        .form-group {
          margin-bottom: 16px;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
          font-size: 14px;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
          width: 100%;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
          box-sizing: border-box;
        }
        
        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        
        .quick-actions {
          margin: 12px 0;
        }
        
        .btn-group {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .btn-group button {
          flex: 1;
          min-width: 60px;
          padding: 8px 12px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }
        
        .btn-group button:hover {
          background: #f8f9fa;
          border-color: #007bff;
        }
        
        .btn-group button:active {
          background: #e9ecef;
        }
        
        .form-actions {
          margin-top: 24px;
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          position: sticky;
          bottom: 0;
          background: white;
          padding: 16px 0 0;
          border-top: 1px solid #eee;
        }
        
        .button {
          padding: 12px 24px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 500;
          min-width: 80px;
          transition: all 0.2s;
        }
        
        .button.success {
          background: #28a745;
          color: white;
        }
        
        .button.success:hover {
          background: #218838;
        }
        
        .button.success:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }
        
        .button.secondary {
          background: #6c757d;
          color: white;
        }
        
        .button.secondary:hover {
          background: #5a6268;
        }
        
        .price-calculator {
          font-size: 14px;
          color: #28a745;
        }
        
        .price-validation {
          font-size: 14px;
        }
        
        .text-success { color: #28a745; }
        .text-warning { color: #ffc107; }
        .text-danger { color: #dc3545; }
        .text-muted { color: #6c757d; }
        
        .keyboard-hints {
          margin-top: 8px;
          text-align: center;
        }
        
        @media (max-width: 768px) {
          .modal-overlay {
            padding: 0;
            align-items: flex-end;
          }
          
          .modal-content {
            max-width: 100%;
            margin-top: 0;
            border-radius: 12px 12px 0 0;
            max-height: 85vh;
          }
          
          .modal-header {
            padding: 12px 16px;
          }
          
          .modal-body {
            padding: 16px;
          }
          
          .form-group input,
          .form-group select {
            font-size: 16px;
            padding: 14px 12px;
          }
          
          .btn-group {
            gap: 6px;
          }
          
          .btn-group button {
            padding: 10px 8px;
            font-size: 13px;
          }
          
          .form-actions {
            padding: 12px 0 0;
          }
          
          .button {
            padding: 14px 20px;
            font-size: 16px;
          }
        }
      `;
      document.head.appendChild(styles);
    }
  }

  private setupEventListeners(): void {
    if (this.storeSelect && this.addStoreDiv) {
      this.storeSelect.addEventListener('change', this.onStoreChange.bind(this));
    }
    
    if (this.priceInput) {
      this.priceInput.addEventListener('input', this.onPriceInput.bind(this));
      this.priceInput.addEventListener('blur', this.validatePrice.bind(this));
    }
    
    if (this.quantityInput) {
      this.quantityInput.addEventListener('input', this.calculatePricePerUnit.bind(this));
    }
    
    // Form submission with AJAX
    const form = document.getElementById('price-form') as HTMLFormElement;
    if (form) {
      form.addEventListener('submit', this.handleFormSubmit.bind(this));
    }
    
    // Modal close events
    if (this.modal) {
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) {
          this.closeModal();
        }
      });
    }
  }

  private setupMobileOptimizations(): void {
    // Prevent zoom on focus for iOS
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach((input) => {
      if (input instanceof HTMLInputElement || input instanceof HTMLSelectElement) {
        if (input.style.fontSize === '' || parseFloat(getComputedStyle(input).fontSize) < 16) {
          input.style.fontSize = '16px';
        }
      }
    });
    
    // Add touch-friendly interaction hints
    document.addEventListener('touchstart', () => {}, {passive: true});
  }

  private setupPriceCalculator(): void {
    // Expose global functions for backward compatibility
    (window as any).calculatePricePerUnit = this.calculatePricePerUnit.bind(this);
    (window as any).setQuickPrice = this.setQuickPrice.bind(this);
    (window as any).openPriceModal = this.openModal.bind(this);
    (window as any).closePriceModal = this.closeModal.bind(this);
  }

  private setupKeyboardShortcuts(): void {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Enter to submit form
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('price-form') as HTMLFormElement;
        if (form) {
          form.submit();
        }
      }
      
      // Escape to close modal
      if (e.key === 'Escape') {
        const modal = document.getElementById('price-modal') as HTMLElement;
        if (modal) {
          modal.style.display = 'none';
        }
      }
    });
  }

  private onPriceInput(): void {
    this.calculatePricePerUnit();
    this.clearValidationMessage();
  }

  private calculatePricePerUnit(): void {
    if (!this.priceInput || !this.quantityInput) return;
    
    const price = parseFloat(this.priceInput.value);
    const quantity = parseInt(this.quantityInput.value);
    const pricePerUnitSpan = document.getElementById('price-per-unit-value');
    
    if (pricePerUnitSpan) {
      if (price > 0 && quantity > 0) {
        const pricePerUnit = (price / quantity).toFixed(2);
        pricePerUnitSpan.textContent = `$${pricePerUnit}`;
        pricePerUnitSpan.className = 'text-success';
      } else {
        pricePerUnitSpan.textContent = '--';
        pricePerUnitSpan.className = 'text-muted';
      }
    }
  }

  private validatePrice(): void {
    if (!this.priceInput || !this.priceValidationMessage) return;
    
    const price = parseFloat(this.priceInput.value);
    
    if (isNaN(price) || price <= 0) {
      this.showValidationMessage('Please enter a valid price greater than zero.', 'error');
      return;
    }
    
    if (price > 10000) {
      this.showValidationMessage('This price seems unusually high. Please verify the amount.', 'warning');
      return;
    }
    
    if (price < 0.01) {
      this.showValidationMessage('Price must be at least $0.01.', 'error');
      return;
    }
    
    // Check against historical prices if available
    if (this.historicalPrices.length > 0) {
      const avgPrice = this.historicalPrices.reduce((sum, p) => sum + p.price, 0) / this.historicalPrices.length;
      
      if (price > avgPrice * 3) {
        this.showValidationMessage(`This price is significantly higher than the average ($${avgPrice.toFixed(2)}). Please verify.`, 'warning');
      } else if (price < avgPrice * 0.3) {
        this.showValidationMessage(`This price is significantly lower than the average ($${avgPrice.toFixed(2)}). Please verify.`, 'warning');
      } else {
        this.showValidationMessage('Price looks reasonable based on historical data.', 'success');
      }
    }
  }

  private showValidationMessage(message: string, type: 'success' | 'warning' | 'error'): void {
    if (!this.priceValidationMessage) return;
    
    this.priceValidationMessage.innerHTML = `
      <small class="text-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger'}">
        ${message}
      </small>
    `;
  }

  private clearValidationMessage(): void {
    if (this.priceValidationMessage) {
      this.priceValidationMessage.innerHTML = '';
    }
  }

  private toggleAddStoreSection(): void {
    if (!this.storeSelect || !this.addStoreDiv) return;

    if (this.storeSelect.value === '__add_new__') {
      this.addStoreDiv.style.display = 'block';
      if (this.storeNameInput) {
        this.storeNameInput.required = true;
        this.storeNameInput.focus();
      }
    } else {
      this.addStoreDiv.style.display = 'none';
      if (this.storeNameInput) {
        this.storeNameInput.required = false;
        this.storeNameInput.value = '';
      }
    }
  }

  // Public method to set historical prices for validation
  public setHistoricalPrices(prices: PriceData[]): void {
    this.historicalPrices = prices;
  }

  // Quick price setting method
  private setQuickPrice(price: number): void {
    if (this.priceInput) {
      this.priceInput.value = price.toFixed(2);
      this.priceInput.focus();
      this.calculatePricePerUnit();
      this.validatePrice();
    }
  }

  // Store selection with memory
  private onStoreChange(): void {
    this.toggleAddStoreSection();
    
    if (this.storeSelect && this.storeSelect.value && this.storeSelect.value !== '__add_new__') {
      // Remember the selected store
      this.settings.lastStore = this.storeSelect.value;
      this.saveSettings();
    }
  }

  // Modal management methods
  public async openModal(itemId: string, listId?: string, priceId?: string): Promise<void> {
    this.currentItemId = itemId;
    this.currentListId = listId || null;
    
    if (!this.modal) {
      this.createModal();
    }
    
    try {
      // Load form content via AJAX
      const url = listId 
        ? `/item/${itemId}/add_price_modal/to_list/${listId}/`
        : `/item/${itemId}/add_price_modal/`;
      
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load price form');
      }
      
      const html = await response.text();
      const modalBody = this.modal!.querySelector('#price-modal-body');
      if (modalBody) {
        modalBody.innerHTML = html;
      }
      
      // Re-setup elements after loading new content
      this.setupElements();
      this.setupEventListeners();
      
      // Pre-fill with remembered store
      if (this.settings.lastStore && this.storeSelect) {
        const option = this.storeSelect.querySelector(`option[value="${this.settings.lastStore}"]`);
        if (option) {
          this.storeSelect.value = this.settings.lastStore;
        }
      }
      
      // Pre-fill confidence
      if (this.confidenceSelect) {
        this.confidenceSelect.value = this.settings.autoFillConfidence;
      }
      
      // Show modal
      this.modal!.style.display = 'flex';
      
      // Focus on price input for quick entry
      setTimeout(() => {
        if (this.priceInput) {
          this.priceInput.focus();
        }
      }, 100);
      
    } catch (error) {
      console.error('Error opening price modal:', error);
      alert('Failed to load price form. Please try again.');
    }
  }

  public closeModal(): void {
    if (this.modal) {
      this.modal.style.display = 'none';
    }
  }

  // AJAX form submission
  private async handleFormSubmit(e: Event): Promise<void> {
    e.preventDefault();
    
    if (!this.submitButton) return;
    
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    
    // Disable submit button during submission
    this.submitButton.disabled = true;
    this.submitButton.textContent = 'Saving...';
    
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      if (response.ok) {
        // Success - remember settings and close modal
        if (this.storeSelect && this.storeSelect.value && this.storeSelect.value !== '__add_new__') {
          this.settings.lastStore = this.storeSelect.value;
        }
        
        if (this.confidenceSelect) {
          this.settings.autoFillConfidence = this.confidenceSelect.value;
        }
        
        // Add price to recent prices for suggestions
        if (this.priceInput && this.priceInput.value) {
          const price = parseFloat(this.priceInput.value);
          if (price > 0) {
            this.settings.recentPrices.unshift(price);
            this.settings.recentPrices = this.settings.recentPrices.slice(0, 5); // Keep only 5 recent
          }
        }
        
        this.saveSettings();
        this.closeModal();
        
        // Show success message
        this.showToast('Price added successfully!', 'success');
        
        // Refresh the page or update the price display
        window.location.reload();
        
      } else {
        // Handle form errors
        const html = await response.text();
        const modalBody = this.modal!.querySelector('#price-modal-body');
        if (modalBody) {
          modalBody.innerHTML = html;
          this.setupElements();
          this.setupEventListeners();
        }
      }
      
    } catch (error) {
      console.error('Error submitting form:', error);
      this.showToast('Failed to save price. Please try again.', 'error');
    } finally {
      // Re-enable submit button
      if (this.submitButton) {
        this.submitButton.disabled = false;
        this.submitButton.textContent = 'Save Price';
      }
    }
  }

  private showToast(message: string, type: 'success' | 'error'): void {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 24px;
      border-radius: 4px;
      color: white;
      font-weight: 500;
      z-index: 10000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      ${type === 'success' ? 'background: #28a745;' : 'background: #dc3545;'}
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
      toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  }
}

// Initialize when DOM is loaded or immediately if already loaded
function initializePriceFormModal() {
  new PriceFormModalManager();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializePriceFormModal);
} else {
  // DOM is already loaded
  initializePriceFormModal();
} 