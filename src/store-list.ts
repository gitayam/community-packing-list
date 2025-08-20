import { DOMUtils, apiClient, FormUtils, GeolocationUtils } from './common';
import { StateUtils } from './services/StateManager';
import { Modal } from './components/Modal';
import type { StoreFormData } from './types';

class StoreListManager {
  private findNearMeButton: HTMLButtonElement | null = null;
  private addStoreButton: HTMLButtonElement | null = null;
  private storeModal: HTMLElement | null = null;
  private storeModalBody: HTMLElement | null = null;
  private closeStoreModalButton: HTMLButtonElement | null = null;
  private currentModal: Modal | null = null;

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
      this.addStoreButton.addEventListener('click', this.handleAddStoreClick.bind(this));
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
      
      StateUtils.addNotification(userMessage, 'error');
    }
  }

  private async handleAddStoreClick(event: Event): Promise<void> {
    event.preventDefault();
    
    // Show loading state
    const target = event.currentTarget as HTMLButtonElement;
    const originalText = target.textContent || 'Add Store';
    this.showButtonLoading(target);
    
    try {
      const response = await apiClient.get('/stores/add/modal/');
      
      if (response.html) {
        // Create content element first so we can query it
        const contentElement = document.createElement('div');
        contentElement.innerHTML = response.html;
        
        // Create and open modal using Modal component
        this.currentModal = new Modal({
          title: 'Add Store',
          content: contentElement,
          size: 'md',
        });
        
        // Set up form submission handler
        this.currentModal.on('open', () => {
          const form = contentElement.querySelector('form') as HTMLFormElement;
          if (form) {
            this.bindStoreFormAjax(form);
          }
          
          // Focus first input
          setTimeout(() => {
            const firstInput = contentElement.querySelector('input, select, textarea') as HTMLElement;
            if (firstInput) {
              firstInput.focus();
            }
          }, 100);
        });
        
        await this.currentModal.open();
      }
    } catch (error) {
      Modal.alert('Error loading form. Please try again.', 'Error');
    } finally {
      this.hideButtonLoading(target, originalText);
    }
  }

  private handleCloseModal(): void {
    if (this.currentModal) {
      this.currentModal.close();
    }
  }

  private handleModalOutsideClick(event: Event): void {
    const target = event.target as HTMLElement;
    if (target === this.storeModal) {
      this.handleCloseModal();
    }
  }

  private bindStoreFormAjax(form?: HTMLFormElement): void {
    const storeForm = form || DOMUtils.getElement<HTMLFormElement>('#store-form');
    if (!storeForm) return;

    storeForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = storeForm.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        this.showButtonLoading(submitBtn);
      }

      try {
        const formData = new FormData(storeForm);
        const response = await apiClient.post('/stores/add/', formData);
        
        const data = await response.json();
        
        if (data.success) {
          Modal.alert('Store added successfully!', 'Success');
          location.reload(); // Refresh to show new store
        } else if (data.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#store-modal-body');
          if (modalBody) {
            modalBody.innerHTML = data.html;
            this.bindStoreFormAjax(storeForm);
          }
        } else if (data.message) {
          StateUtils.addNotification(data.message, 'error');
        } else {
          StateUtils.addNotification('Unknown error occurred', 'error');
        }
      } catch (error) {
        StateUtils.addNotification('Error adding store. Please try again.', 'error');
      } finally {
        // Remove loading state
        if (submitBtn) {
          this.hideButtonLoading(submitBtn, 'Add Store');
        }
      }
    });
  }
}

// Initialize when DOM is loaded or immediately if already loaded
function initializeStoreList() {
  new StoreListManager();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeStoreList);
} else {
  // DOM is already loaded
  initializeStoreList();
} 