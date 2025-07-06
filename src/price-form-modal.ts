import { DOMUtils } from './common';

class PriceFormModalManager {
  private addStoreDiv: HTMLElement | null = null;
  private storeSelect: HTMLSelectElement | null = null;
  private storeNameInput: HTMLInputElement | null = null;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.setupEventListeners();
    this.toggleAddStoreSection(); // Initial state
  }

  private setupElements(): void {
    this.addStoreDiv = DOMUtils.getElement<HTMLElement>('#inline-add-store');
    this.storeSelect = DOMUtils.getElement<HTMLSelectElement>('#id_store');
    this.storeNameInput = DOMUtils.getElement<HTMLInputElement>('#id_store_name');
  }

  private setupEventListeners(): void {
    if (this.storeSelect && this.addStoreDiv) {
      this.storeSelect.addEventListener('change', this.toggleAddStoreSection.bind(this));
    }
  }

  private toggleAddStoreSection(): void {
    if (!this.storeSelect || !this.addStoreDiv) return;

    if (this.storeSelect.value === '__add_new__') {
      this.addStoreDiv.style.display = 'block';
      if (this.storeNameInput) {
        this.storeNameInput.required = true;
      }
    } else {
      this.addStoreDiv.style.display = 'none';
      if (this.storeNameInput) {
        this.storeNameInput.required = false;
        this.storeNameInput.value = '';
      }
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PriceFormModalManager();
}); 