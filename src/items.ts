import { DOMUtils, FormUtils } from './common';
import { apiService } from './services/ApiService';
import { logger } from './services/Logger';
import { appState, StateUtils } from './services/StateManager';
import { cacheService, CacheConfigs } from './services/CacheService';

class ItemsPageManager {
  private unsubscribe?: () => void;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    logger.info('Initializing ItemsPageManager', 'items');
    
    this.setupStateManagement();
    this.setupEventListeners();
    this.setupViewToggle();
    this.preloadData();
  }

  private setupStateManagement(): void {
    // Subscribe to state changes
    this.unsubscribe = appState.subscribe((newState, previousState) => {
      this.handleStateChange(newState, previousState);
    });
  }

  private handleStateChange(newState: any, previousState: any): void {
    // Update UI based on state changes
    if (newState.ui.loading !== previousState.ui.loading) {
      this.updateLoadingState(newState.ui.loading);
    }
    
    if (newState.data.selectedItems !== previousState.data.selectedItems) {
      this.updateBulkActionsVisibility();
    }
  }

  private updateLoadingState(loading: boolean): void {
    const loadingIndicator = DOMUtils.getElement<HTMLElement>('#loading-indicator');
    if (loadingIndicator) {
      loadingIndicator.style.display = loading ? 'block' : 'none';
    }
  }

  private setupEventListeners(): void {
    // Price modal event delegation
    document.addEventListener('click', this.handlePriceModalClick.bind(this));
    
    // Item modal event delegation  
    document.addEventListener('click', this.handleItemModalClick.bind(this));
    
    // Price toggle event delegation
    document.addEventListener('click', this.handlePriceToggleClick.bind(this));
    
    // Selection change handling
    document.addEventListener('change', this.handleSelectionChange.bind(this));
    
    // Bulk actions
    document.addEventListener('click', this.handleBulkActions.bind(this));
    
    // Base filter change
    document.addEventListener('change', this.handleBaseChange.bind(this));
    
    // Modal close handlers
    this.setupModalCloseHandlers();
  }

  private setupModalCloseHandlers(): void {
    const closePriceModalBtn = DOMUtils.getElement<HTMLButtonElement>('#close-price-modal');
    if (closePriceModalBtn) {
      closePriceModalBtn.addEventListener('click', () => {
        UIUtils.hideModal('price-modal');
      });
    }

    const closeItemModalBtn = DOMUtils.getElement<HTMLButtonElement>('#close-item-modal');  
    if (closeItemModalBtn) {
      closeItemModalBtn.addEventListener('click', () => {
        UIUtils.hideModal('item-modal');
      });
    }

    // Close modal when clicking outside
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target.classList.contains('modal')) {
        StateUtils.toggleModal('priceModal', false);
        StateUtils.toggleModal('itemModal', false);
      }
    });
  }

  private async handlePriceModalClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    if (target.closest('.add-price-btn') || target.closest('.edit-price-btn')) {
      logger.logUserAction('price_modal_open', { target: target.className });
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.add-price-btn, .edit-price-btn') as HTMLElement;
      const itemId = btn.dataset.itemId;
      const priceId = btn.dataset.priceId;
      
      if (!itemId) return;
      
      logger.debug('Opening price modal', 'items', { itemId, priceId });
      
      this.showButtonLoading(btn as HTMLButtonElement);
      
      try {
        let url = `/item/${itemId}/add_price_modal/`;
        if (priceId) {
          url += `?price_id=${priceId}`;
        }
        
        const response = await apiService.get(url, { useCache: true, cacheTimeout: CacheConfigs.SHORT.ttl });
        
        if (response.html) {
          const modal = DOMUtils.getElement<HTMLElement>('#price-modal');
          const modalBody = DOMUtils.getElement<HTMLElement>('#price-modal-body');
          
          if (modal && modalBody) {
            modalBody.innerHTML = response.html;
            StateUtils.toggleModal('priceModal', true);
            
            // Set up form submission handler
            const form = modalBody.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupPriceFormSubmission(form);
            }
            
            // Focus first input
            setTimeout(() => {
              const firstInput = modal.querySelector('input, select, textarea') as HTMLElement;
              if (firstInput) {
                firstInput.focus();
              }
            }, 100);
          }
        }
      } catch (error) {
        logger.error('Error loading price modal', 'items', error);
        StateUtils.addNotification('Error loading price form. Please try again.', 'error');
      } finally {
        const buttonText = btn.classList.contains('add-price-btn') ? 'Add Price' : 'Edit';
        this.hideButtonLoading(btn as HTMLButtonElement, buttonText);
      }
    }
  }

  private async handleItemModalClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    if (target.closest('.edit-item-btn')) {
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.edit-item-btn') as HTMLElement;
      const itemId = btn.dataset.itemId;
      
      if (!itemId) return;
      
      this.showButtonLoading(btn as HTMLButtonElement);
      
      try {
        const url = `/item/${itemId}/edit_modal/`;
        const response = await apiService.get(url, { useCache: false });
        
        if (response.html) {
          const modal = DOMUtils.getElement<HTMLElement>('#item-modal');
          const modalBody = DOMUtils.getElement<HTMLElement>('#item-modal-body');
          
          if (modal && modalBody) {
            modalBody.innerHTML = response.html;
            modal.style.display = 'flex'; // Temporary fallback
            
            // Set up form submission handler
            const form = modalBody.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupItemFormSubmission(form);
            }
          }
        }
      } catch (error) {
        logger.error('Error loading item modal', 'items', error);
        StateUtils.addNotification('Error loading edit form. Please try again.', 'error');
      } finally {
        this.hideButtonLoading(btn as HTMLButtonElement, 'Edit');
      }
    }
  }

  private handlePriceToggleClick(event: Event): void {
    const target = event.target as HTMLElement;
    
    if (target.textContent?.includes('Show All') || target.textContent?.includes('Hide Prices')) {
      const button = target as HTMLButtonElement;
      const pricesDiv = button.nextElementSibling as HTMLElement;
      
      if (pricesDiv && pricesDiv.classList.contains('all-prices')) {
        if (pricesDiv.style.display === 'none' || !pricesDiv.style.display) {
          pricesDiv.style.display = 'block';
          button.textContent = 'Hide Prices';
        } else {
          pricesDiv.style.display = 'none';
          button.textContent = 'Show All Prices';
        }
      }
    }
  }

  private handleSelectionChange(event: Event): void {
    const target = event.target as HTMLElement;
    
    if (target.classList.contains('item-select')) {
      const checkbox = target as HTMLInputElement;
      const itemId = checkbox.value;
      
      if (checkbox.checked) {
        StateUtils.addSelectedItem(itemId);
        logger.logUserAction('item_selected', { itemId });
      } else {
        StateUtils.removeSelectedItem(itemId);
        logger.logUserAction('item_deselected', { itemId });
      }
    }
  }

  private handleBulkActions(event: Event): void {
    const target = event.target as HTMLElement;
    
    if (target.textContent?.includes('Clear Selection')) {
      this.clearSelection();
    } else if (target.textContent?.includes('Create Packing List')) {
      this.createPackingListFromSelected();
    }
  }

  private handleBaseChange(event: Event): void {
    const target = event.target as HTMLElement;
    
    if (target.id === 'base') {
      const baseSelect = target as HTMLSelectElement;
      const citySelect = DOMUtils.getElement<HTMLSelectElement>('#city');
      const stateSelect = DOMUtils.getElement<HTMLSelectElement>('#state');
      
      if (baseSelect.value) {
        if (citySelect) citySelect.disabled = true;
        if (stateSelect) stateSelect.disabled = true;
      } else {
        if (citySelect) citySelect.disabled = false;
        if (stateSelect) stateSelect.disabled = false;
      }
    }
  }

  private setupViewToggle(): void {
    const cardViewBtn = DOMUtils.getElement<HTMLButtonElement>('#cardViewBtn');
    const tableViewBtn = DOMUtils.getElement<HTMLButtonElement>('#tableViewBtn');
    
    if (cardViewBtn) {
      cardViewBtn.addEventListener('click', () => this.setItemsView('card'));
    }
    
    if (tableViewBtn) {
      tableViewBtn.addEventListener('click', () => this.setItemsView('table'));
    }
  }

  private setItemsView(view: 'card' | 'table'): void {
    const cardView = DOMUtils.getElement<HTMLElement>('#itemsCardView');
    const tableView = DOMUtils.getElement<HTMLElement>('#itemsTableView');
    const cardBtn = DOMUtils.getElement<HTMLButtonElement>('#cardViewBtn');
    const tableBtn = DOMUtils.getElement<HTMLButtonElement>('#tableViewBtn');
    
    if (view === 'card') {
      if (cardView) cardView.style.display = 'block';
      if (tableView) tableView.style.display = 'none';
      if (cardBtn) {
        cardBtn.classList.add('active');
        cardBtn.setAttribute('aria-pressed', 'true');
      }
      if (tableBtn) {
        tableBtn.classList.remove('active');
        tableBtn.setAttribute('aria-pressed', 'false');
      }
    } else {
      if (cardView) cardView.style.display = 'none';
      if (tableView) tableView.style.display = 'block';
      if (tableBtn) {
        tableBtn.classList.add('active');
        tableBtn.setAttribute('aria-pressed', 'true');
      }
      if (cardBtn) {
        cardBtn.classList.remove('active');
        cardBtn.setAttribute('aria-pressed', 'false');
      }
    }
    
    // Update state with preference
    StateUtils.updatePreferences({ viewMode: view });
    logger.logUserAction('view_changed', { view });
  }

  private updateBulkActionsVisibility(): void {
    const state = appState.getState();
    const selectedItems = state.data.selectedItems;
    const bulkActions = DOMUtils.getElement<HTMLElement>('#bulkActions');
    const selectedCount = DOMUtils.getElement<HTMLElement>('#selectedCount');
    
    if (selectedItems.size > 0) {
      if (bulkActions) bulkActions.style.display = 'block';
      if (selectedCount) {
        selectedCount.textContent = `${selectedItems.size} item${selectedItems.size > 1 ? 's' : ''} selected`;
      }
    } else {
      if (bulkActions) bulkActions.style.display = 'none';
    }
  }

  private clearSelection(): void {
    document.querySelectorAll('.item-select').forEach((cb) => {
      (cb as HTMLInputElement).checked = false;
    });
    StateUtils.clearSelectedItems();
    logger.logUserAction('selection_cleared');
  }

  private createPackingListFromSelected(): void {
    const state = appState.getState();
    const selectedItems = state.data.selectedItems;
    
    if (selectedItems.size === 0) {
      StateUtils.addNotification('Please select at least one item.', 'info');
      return;
    }
    
    logger.logUserAction('create_packing_list_from_selection', { itemCount: selectedItems.size });
    
    const params = new URLSearchParams();
    selectedItems.forEach(itemId => {
      params.append('selected_items', itemId);
    });
    
    window.location.href = '/create_packing_list_from_items/?' + params.toString();
  }

  private setupPriceFormSubmission(form: HTMLFormElement): void {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        this.showButtonLoading(submitBtn);
      }
      
      StateUtils.setLoading(true);

      try {
        const formData = FormUtils.getFormData(form);
        const response = await apiService.post(form.action, formData);

        if (response.success) {
          StateUtils.toggleModal('priceModal', false);
          StateUtils.addNotification('Price updated successfully!', 'success');
          
          // Clear related cache entries
          cacheService.invalidateByPattern(/\/item\//i);
          
          logger.logUserAction('price_updated', { success: true });
          location.reload();
        } else if (response.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#price-modal-body');
          if (modalBody) {
            modalBody.innerHTML = response.html;
            this.setupPriceFormSubmission(modalBody.querySelector('form') as HTMLFormElement);
          }
        } else {
          StateUtils.addNotification(response.message || 'Error updating price.', 'error');
        }
      } catch (error) {
        logger.error('Error updating price', 'items', error);
        StateUtils.addNotification('Error updating price. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          this.hideButtonLoading(submitBtn, 'Save Price');
        }
        StateUtils.setLoading(false);
      }
    });
  }

  private setupItemFormSubmission(form: HTMLFormElement): void {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        this.showButtonLoading(submitBtn);
      }
      
      StateUtils.setLoading(true);

      try {
        const formData = FormUtils.getFormData(form);
        const response = await apiService.post(form.action, formData);

        if (response.success) {
          StateUtils.toggleModal('itemModal', false);
          StateUtils.addNotification('Item updated successfully!', 'success');
          
          // Clear related cache entries
          cacheService.invalidateByPattern(/\/item\//i);
          
          logger.logUserAction('item_updated', { success: true });
          location.reload();
        } else if (response.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#item-modal-body');
          if (modalBody) {
            modalBody.innerHTML = response.html;
            this.setupItemFormSubmission(modalBody.querySelector('form') as HTMLFormElement);
          }
        } else {
          StateUtils.addNotification(response.message || 'Error updating item.', 'error');
        }
      } catch (error) {
        logger.error('Error updating item', 'items', error);
        StateUtils.addNotification('Error updating item. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          this.hideButtonLoading(submitBtn, 'Save Changes');
        }
        StateUtils.setLoading(false);
      }
    });
  }

  private showButtonLoading(button: HTMLButtonElement): void {
    button.classList.add('loading');
    button.disabled = true;
    button.dataset.originalText = button.textContent || '';
    button.textContent = 'Loading...';
  }

  private hideButtonLoading(button: HTMLButtonElement, originalText: string): void {
    button.classList.remove('loading');
    button.disabled = false;
    button.textContent = originalText;
  }

  private async preloadData(): Promise<void> {
    try {
      // Preload commonly accessed endpoints
      const preloadUrls = [
        '/api/user-preferences/',
        '/api/recent-items/'
      ];
      
      await apiService.preload(preloadUrls);
      logger.debug('Data preloading completed', 'items');
    } catch (error) {
      logger.warn('Failed to preload some data', 'items', error);
    }
  }

  // Cleanup method
  public destroy(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    logger.info('ItemsPageManager destroyed', 'items');
  }
}

// Initialize when DOM is loaded
function initializeItemsPage() {
  const manager = new ItemsPageManager();
  
  // Store reference for global access
  (window as any).itemsManager = manager;
  
  // Restore view preference from state
  const state = appState.getState();
  const savedView = state.user?.preferences?.viewMode;
  if (savedView) {
    (manager as any).setItemsView(savedView);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeItemsPage);
} else {
  initializeItemsPage();
}

export default ItemsPageManager;