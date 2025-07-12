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
  private settings: QuickPriceSettings;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.setupEventListeners();
    this.setupPriceCalculator();
    this.setupKeyboardShortcuts();
    this.toggleAddStoreSection(); // Initial state
  }

  private setupElements(): void {
    this.addStoreDiv = DOMUtils.getElement<HTMLElement>('#inline-add-store');
    this.storeSelect = DOMUtils.getElement<HTMLSelectElement>('#id_store');
    this.storeNameInput = DOMUtils.getElement<HTMLInputElement>('#id_store_name');
    this.priceInput = DOMUtils.getElement<HTMLInputElement>('#id_price');
    this.quantityInput = DOMUtils.getElement<HTMLInputElement>('#id_quantity');
    
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

  private setupEventListeners(): void {
    if (this.storeSelect && this.addStoreDiv) {
      this.storeSelect.addEventListener('change', this.toggleAddStoreSection.bind(this));
    }
    
    if (this.priceInput) {
      this.priceInput.addEventListener('input', this.onPriceInput.bind(this));
      this.priceInput.addEventListener('blur', this.validatePrice.bind(this));
    }
    
    if (this.quantityInput) {
      this.quantityInput.addEventListener('input', this.calculatePricePerUnit.bind(this));
    }
  }

  private setupPriceCalculator(): void {
    // Expose global functions for backward compatibility
    (window as any).calculatePricePerUnit = this.calculatePricePerUnit.bind(this);
    (window as any).setQuickPrice = this.setQuickPrice.bind(this);
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PriceFormModalManager();
}); 