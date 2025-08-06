import { DOMUtils, UIUtils, apiClient, FormUtils } from './common';

class ItemsPageManager {
  private selectedItems: Set<string> = new Set();

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupEventListeners();
    this.setupViewToggle();
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
        UIUtils.hideModal('price-modal');
        UIUtils.hideModal('item-modal');
      }
    });
  }

  private async handlePriceModalClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    if (target.closest('.add-price-btn') || target.closest('.edit-price-btn')) {
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.add-price-btn, .edit-price-btn') as HTMLElement;
      const itemId = btn.dataset.itemId;
      const priceId = btn.dataset.priceId;
      
      if (!itemId) return;
      
      console.log('Opening price modal for item:', itemId, 'price:', priceId);
      
      UIUtils.showLoading(btn as HTMLButtonElement);
      
      try {
        let url = `/item/${itemId}/add_price_modal/`;
        if (priceId) {
          url += `?price_id=${priceId}`;
        }
        
        const response = await apiClient.get(url);
        
        if (response.html) {
          const modal = DOMUtils.getElement<HTMLElement>('#price-modal');
          const modalBody = DOMUtils.getElement<HTMLElement>('#price-modal-body');
          
          if (modal && modalBody) {
            modalBody.innerHTML = response.html;
            UIUtils.showModal('price-modal');
            
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
        console.error('Error loading price modal:', error);
        UIUtils.showNotification('Error loading price form. Please try again.', 'error');
      } finally {
        const buttonText = btn.classList.contains('add-price-btn') ? 'Add Price' : 'Edit';
        UIUtils.hideLoading(btn as HTMLButtonElement, buttonText);
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
      
      UIUtils.showLoading(btn as HTMLButtonElement);
      
      try {
        const url = `/item/${itemId}/edit_modal/`;
        const response = await apiClient.get(url);
        
        if (response.html) {
          const modal = DOMUtils.getElement<HTMLElement>('#item-modal');
          const modalBody = DOMUtils.getElement<HTMLElement>('#item-modal-body');
          
          if (modal && modalBody) {
            modalBody.innerHTML = response.html;
            UIUtils.showModal('item-modal');
            
            // Set up form submission handler
            const form = modalBody.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupItemFormSubmission(form);
            }
          }
        }
      } catch (error) {
        console.error('Error loading item modal:', error);
        UIUtils.showNotification('Error loading edit form. Please try again.', 'error');
      } finally {
        UIUtils.hideLoading(btn as HTMLButtonElement, 'Edit');
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
        this.selectedItems.add(itemId);
      } else {
        this.selectedItems.delete(itemId);
      }
      
      this.updateBulkActionsVisibility();
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
    
    // Store preference in localStorage
    localStorage.setItem('itemsViewPreference', view);
  }

  private updateBulkActionsVisibility(): void {
    const bulkActions = DOMUtils.getElement<HTMLElement>('#bulkActions');
    const selectedCount = DOMUtils.getElement<HTMLElement>('#selectedCount');
    
    if (this.selectedItems.size > 0) {
      if (bulkActions) bulkActions.style.display = 'block';
      if (selectedCount) {
        selectedCount.textContent = `${this.selectedItems.size} item${this.selectedItems.size > 1 ? 's' : ''} selected`;
      }
    } else {
      if (bulkActions) bulkActions.style.display = 'none';
    }
  }

  private clearSelection(): void {
    document.querySelectorAll('.item-select').forEach((cb) => {
      (cb as HTMLInputElement).checked = false;
    });
    this.selectedItems.clear();
    this.updateBulkActionsVisibility();
  }

  private createPackingListFromSelected(): void {
    if (this.selectedItems.size === 0) {
      UIUtils.showNotification('Please select at least one item.', 'warning');
      return;
    }
    
    const params = new URLSearchParams();
    this.selectedItems.forEach(itemId => {
      params.append('selected_items', itemId);
    });
    
    window.location.href = '/create_packing_list_from_items/?' + params.toString();
  }

  private setupPriceFormSubmission(form: HTMLFormElement): void {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        UIUtils.showLoading(submitBtn);
      }

      try {
        const formData = FormUtils.getFormData(form);
        const response = await apiClient.post(form.action, formData);

        if (response.success) {
          UIUtils.hideModal('price-modal');
          UIUtils.showNotification('Price updated successfully!', 'success');
          location.reload();
        } else if (response.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#price-modal-body');
          if (modalBody) {
            modalBody.innerHTML = response.html;
            this.setupPriceFormSubmission(modalBody.querySelector('form') as HTMLFormElement);
          }
        } else {
          UIUtils.showNotification(response.message || 'Error updating price.', 'error');
        }
      } catch (error) {
        UIUtils.showNotification('Error updating price. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          UIUtils.hideLoading(submitBtn, 'Save Price');
        }
      }
    });
  }

  private setupItemFormSubmission(form: HTMLFormElement): void {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        UIUtils.showLoading(submitBtn);
      }

      try {
        const formData = FormUtils.getFormData(form);
        const response = await apiClient.post(form.action, formData);

        if (response.success) {
          UIUtils.hideModal('item-modal');
          UIUtils.showNotification('Item updated successfully!', 'success');
          location.reload();
        } else if (response.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#item-modal-body');
          if (modalBody) {
            modalBody.innerHTML = response.html;
            this.setupItemFormSubmission(modalBody.querySelector('form') as HTMLFormElement);
          }
        } else {
          UIUtils.showNotification(response.message || 'Error updating item.', 'error');
        }
      } catch (error) {
        UIUtils.showNotification('Error updating item. Please try again.', 'error');
      } finally {
        if (submitBtn) {
          UIUtils.hideLoading(submitBtn, 'Save Changes');
        }
      }
    });
  }
}

// Initialize when DOM is loaded
function initializeItemsPage() {
  const manager = new ItemsPageManager();
  
  // Store reference for global access
  (window as any).itemsManager = manager;
  
  // Restore view preference
  const savedView = localStorage.getItem('itemsViewPreference') as 'card' | 'table';
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