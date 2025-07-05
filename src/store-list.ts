import { DOMUtils, UIUtils, apiClient, FormUtils, GeolocationUtils } from './common';
import type { StoreFormData } from './types';

class StoreListManager {
  private findNearMeButton: HTMLButtonElement | null = null;
  private addStoreButton: HTMLButtonElement | null = null;
  private storeModal: HTMLElement | null = null;
  private storeModalBody: HTMLElement | null = null;
  private closeStoreModalButton: HTMLButtonElement | null = null;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.setupEventListeners();
  }

  private setupElements(): void {
    this.findNearMeButton = DOMUtils.getElement<HTMLButtonElement>('#find-near-me');
    this.addStoreButton = DOMUtils.getElement<HTMLButtonElement>('#add-store-btn');
    this.storeModal = DOMUtils.getElement<HTMLElement>('#store-modal');
    this.storeModalBody = DOMUtils.getElement<HTMLElement>('#store-modal-body');
    this.closeStoreModalButton = DOMUtils.getElement<HTMLButtonElement>('#close-store-modal');
  }

  private setupEventListeners(): void {
    // Find stores near me functionality
    if (this.findNearMeButton) {
      this.findNearMeButton.addEventListener('click', this.handleFindNearMe.bind(this));
    }

    // Add store modal functionality
    if (this.addStoreButton) {
      this.addStoreButton.addEventListener('click', this.handleAddStore.bind(this));
    }

    // Close modal functionality
    if (this.closeStoreModalButton) {
      this.closeStoreModalButton.addEventListener('click', this.handleCloseModal.bind(this));
    }

    // Close modal when clicking outside
    if (this.storeModal) {
      this.storeModal.addEventListener('click', this.handleModalOutsideClick.bind(this));
    }
  }

  private async handleFindNearMe(): Promise<void> {
    if (!this.findNearMeButton) return;

    try {
      const position = await GeolocationUtils.getCurrentPosition();
      
      const userLatInput = DOMUtils.getElement<HTMLInputElement>('#user_lat');
      const userLonInput = DOMUtils.getElement<HTMLInputElement>('#user_lon');
      const schoolIdSelect = DOMUtils.getElement<HTMLSelectElement>('#school_id');
      
      if (userLatInput && userLonInput) {
        userLatInput.value = position.coords.latitude.toString();
        userLonInput.value = position.coords.longitude.toString();
      }
      
      // Clear other location-based filters if user clicks "near me"
      if (schoolIdSelect) {
        schoolIdSelect.value = '';
      }
      
      // Submit the form
      const form = DOMUtils.getElement<HTMLFormElement>('.filter-form form');
      if (form) {
        form.submit();
      }
    } catch (error) {
      console.error('Geolocation error:', error);
      let userMessage = 'Error getting location: ';
      
      if (error instanceof GeolocationPositionError) {
        userMessage += GeolocationUtils.getErrorMessage(error);
      } else if (error instanceof Error) {
        userMessage += error.message;
      } else {
        userMessage += 'An unknown error occurred.';
      }
      
      UIUtils.showNotification(userMessage, 'error');
    }
  }

  private async handleAddStore(): Promise<void> {
    if (!this.storeModal || !this.storeModalBody) return;

    UIUtils.showModal('store-modal');
    this.storeModalBody.innerHTML = '<p>Loading...</p>';

    try {
      const response = await apiClient.get('/add_store_modal/');
      
      if (response.html) {
        this.storeModalBody.innerHTML = response.html;
        this.bindStoreFormAjax();
      }
    } catch (error) {
      console.error('Error loading store form:', error);
      UIUtils.showNotification('Error loading store form. Please try again.', 'error');
      this.storeModalBody.innerHTML = '<p>Error loading form. Please try again.</p>';
    }
  }

  private handleCloseModal(): void {
    if (this.storeModal) {
      UIUtils.hideModal('store-modal');
    }
  }

  private handleModalOutsideClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (target === this.storeModal) {
      this.handleCloseModal();
    }
  }

  private bindStoreFormAjax(): void {
    const storeForm = DOMUtils.getElement<HTMLFormElement>('#store-form');
    if (!storeForm) return;

    storeForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = storeForm.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        UIUtils.showLoading(submitBtn);
      }

      try {
        const formData = FormUtils.getFormData(storeForm);
        const response = await apiClient.post(storeForm.action || window.location.href, formData);

        if (response.success) {
          this.handleCloseModal();
          window.location.reload();
        } else if (response.html) {
          if (this.storeModalBody) {
            this.storeModalBody.innerHTML = response.html;
            this.bindStoreFormAjax();
          }
        } else if (response.errors) {
          FormUtils.showFormErrors(storeForm, response.errors);
        }
      } catch (error) {
        console.error('Error submitting store form:', error);
        UIUtils.showNotification('Error saving store. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          UIUtils.hideLoading(submitBtn, 'Save Store');
        }
      }
    });
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new StoreListManager();
}); 