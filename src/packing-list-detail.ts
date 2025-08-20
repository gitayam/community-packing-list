import { DOMUtils, FormUtils } from './common';
import { apiService } from './services/ApiService';
import { logger } from './services/Logger';
import { appState, StateUtils } from './services/StateManager';
import { cacheService, CacheConfigs } from './services/CacheService';
import type { TableSortState, FilterState, PriceDetailsData, TableRowData } from './types';
import { Modal } from './components/Modal';

class PackingListDetailManager {
  private filterInput: HTMLInputElement | null = null;
  private table: HTMLTableElement | null = null;
  private toggleBtn: HTMLButtonElement | null = null;
  private tableWrapper: HTMLElement | null = null;
  private rows: HTMLTableRowElement[] = [];
  private sortableHeaders: HTMLTableCellElement[] = [];
  private currentSortState: TableSortState = { column: '', direction: 'asc' };
  private unsubscribe?: () => void;

  constructor() {
    this.initialize();
    // Inject SVG icons into action buttons (DOM is already ready)
    this.injectActionButtonIcons();
  }

  private initialize(): void {
    logger.info('Initializing PackingListDetailManager', 'packing_list');
    
    this.setupStateManagement();
    this.setupElements();
    this.setupEventListeners();
    this.setupTableFunctionality();
    this.setupModalFunctionality();
    this.setupVoteFunctionality();
    this.setupFilterFunctionality();
    this.preloadData();
  }

  private setupStateManagement(): void {
    // Subscribe to state changes
    this.unsubscribe = appState.subscribe((newState, previousState) => {
      this.handleStateChange(newState, previousState);
    });
  }

  private handleStateChange(newState: any, previousState: any): void {
    if (newState.ui.loading !== previousState.ui.loading) {
      this.updateLoadingState(newState.ui.loading);
    }
  }

  private updateLoadingState(loading: boolean): void {
    const loadingIndicator = DOMUtils.getElement<HTMLElement>('#loading-indicator');
    if (loadingIndicator) {
      loadingIndicator.style.display = loading ? 'block' : 'none';
    }
  }

  private setupElements(): void {
    this.filterInput = DOMUtils.getElement<HTMLInputElement>('#item-table-filter');
    this.table = DOMUtils.getElement<HTMLTableElement>('.modern-table');
    this.toggleBtn = DOMUtils.getElement<HTMLButtonElement>('#toggle-columns');
    this.tableWrapper = DOMUtils.getElement<HTMLElement>('.modern-table-wrapper');

    if (!this.table || !this.filterInput || !this.toggleBtn || !this.tableWrapper) {
      logger.warn('Table elements not found, skipping table functionality', 'packing_list');
      return;
    }

    this.rows = DOMUtils.getElements<HTMLTableRowElement>('tbody tr.item-row');
    this.sortableHeaders = DOMUtils.getElements<HTMLTableCellElement>('.modern-table th.sortable');
  }

  private setupEventListeners(): void {
    if (!this.filterInput) return;

    // Table filtering
    this.filterInput.addEventListener('input', this.handleFilterInput.bind(this));

    // Clear filters
    const clearFiltersBtn = DOMUtils.getElement<HTMLButtonElement>('#clear-filters');
    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener('click', this.handleClearFilters.bind(this));
    }

    // Column toggle
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', this.handleColumnToggle.bind(this));
    }

    // Table sorting
    this.sortableHeaders.forEach(header => {
      header.addEventListener('click', this.handleSortClick.bind(this));
    });

    // Global event listeners
    document.addEventListener('click', this.handleGlobalClick.bind(this));
    document.addEventListener('keydown', this.handleKeyDown.bind(this));
  }

  private setupTableFunctionality(): void {
    // Table sorting functionality is already set up in setupEventListeners
  }

  private setupModalFunctionality(): void {
    // Price modal functionality
    document.addEventListener('click', this.handlePriceModalClick.bind(this));

    // Edit item modal functionality
    document.addEventListener('click', this.handleEditItemModalClick.bind(this));

    // Anonymous indicator functionality
    document.addEventListener('click', this.handleAnonymousIndicatorClick.bind(this));

    // Close modal functionality
    const closePriceModalBtn = DOMUtils.getElement<HTMLButtonElement>('#close-price-modal');
    if (closePriceModalBtn) {
      closePriceModalBtn.addEventListener('click', () => {
        this.hideModal('price-modal');
      });
    }

    const closeEditItemModalBtn = DOMUtils.getElement<HTMLButtonElement>('#close-edit-item-modal');
    if (closeEditItemModalBtn) {
      closeEditItemModalBtn.addEventListener('click', () => {
        this.hideModal('edit-item-modal');
      });
    }
  }

  private setupVoteFunctionality(): void {
    document.addEventListener('click', this.handleVoteClick.bind(this));
  }

  private setupFilterFunctionality(): void {
    const baseFilterForm = DOMUtils.getElement<HTMLFormElement>('#base-filter-form');
    const clearBaseFilterBtn = DOMUtils.getElement<HTMLButtonElement>('#clear-base-filter');

    if (clearBaseFilterBtn) {
      clearBaseFilterBtn.addEventListener('click', this.handleClearBaseFilter.bind(this));
    }

    if (baseFilterForm) {
      const baseSelect = DOMUtils.getElement<HTMLSelectElement>('#base-select');
      const radiusSelect = DOMUtils.getElement<HTMLSelectElement>('#radius-select');

      if (baseSelect) {
        baseSelect.addEventListener('change', this.handleBaseSelectChange.bind(this));
      }

      if (radiusSelect) {
        radiusSelect.addEventListener('change', this.handleRadiusSelectChange.bind(this));
      }
    }
  }

  private handleFilterInput(event: Event): void {
    const target = event.target as HTMLElement;
    const searchTerm = (target as HTMLInputElement).value.toLowerCase();

    this.rows.forEach(row => {
      const itemName = (row as HTMLElement).dataset.itemName || '';
      const visible = itemName.includes(searchTerm);
      row.style.display = visible ? '' : 'none';
    });
  }

  private handleClearFilters(): void {
    if (this.filterInput) {
      this.filterInput.value = '';
      this.rows.forEach(row => row.style.display = '');
    }
  }

  private handleColumnToggle(): void {
    if (!this.toggleBtn || !this.tableWrapper) return;

    const columnsVisible = this.tableWrapper.classList.contains('show-hidden-columns');
    
    if (!columnsVisible) {
      this.tableWrapper.classList.add('show-hidden-columns');
      this.toggleBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye-off"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
        Hide Details
      `;
    } else {
      this.tableWrapper.classList.remove('show-hidden-columns');
      this.toggleBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-columns"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="9" y2="15"></line><line x1="15" y1="9" x2="15" y2="15"></line></svg>
        Show Details
      `;
    }
  }

  private handleSortClick(event: Event): void {
    const header = event.target as HTMLElement;
    const sortType = (header as HTMLElement).dataset.sort || '';
    const currentSort = header.classList.contains('sort-asc') ? 'asc' : 
                       header.classList.contains('sort-desc') ? 'desc' : 'none';

    // Remove sort classes from all headers
    this.sortableHeaders.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));

    // Add appropriate sort class
    if (currentSort === 'none' || currentSort === 'desc') {
      header.classList.add('sort-asc');
      this.sortTable(sortType, 'asc');
    } else {
      header.classList.add('sort-desc');
      this.sortTable(sortType, 'desc');
    }
  }

  private sortTable(sortType: string, direction: 'asc' | 'desc'): void {
    if (!this.table) return;

    const tbody = this.table.querySelector('tbody');
    if (!tbody) return;

    const allRows = Array.from(tbody.querySelectorAll('tr'));

    // Separate rows
    const sectionHeaders = allRows.filter(row => row.classList.contains('section-header-row'));
    const itemRows = allRows.filter(row => row.classList.contains('item-row'));

    const getCellValue = (row: HTMLTableRowElement, selector: string, fallback = ''): string => {
      const cell = row.querySelector(selector);
      return cell ? cell.textContent?.trim().toLowerCase() || fallback : fallback;
    };

    // Sort items
    itemRows.sort((a, b) => {
      let aVal: string | number, bVal: string | number;
      
      switch (sortType) {
        case 'name':
          aVal = getCellValue(a, '.item-name-cell');
          bVal = getCellValue(b, '.item-name-cell');
          break;
        case 'quantity':
          aVal = parseInt(getCellValue(a, '.quantity-cell'), 10) || 0;
          bVal = parseInt(getCellValue(b, '.quantity-cell'), 10) || 0;
          break;
        case 'required':
          aVal = getCellValue(a, '.required-cell');
          bVal = getCellValue(b, '.required-cell');
          break;
        case 'store':
          aVal = getCellValue(a, '.store-cell');
          bVal = getCellValue(b, '.store-cell');
          break;
        case 'price':
          aVal = parseFloat(getCellValue(a, '.price-cell').replace(/[^\d.]/g, '')) || 0;
          bVal = parseFloat(getCellValue(b, '.price-cell').replace(/[^\d.]/g, '')) || 0;
          break;
        default:
          aVal = '';
          bVal = '';
      }

      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    // Re-insert sorted rows
    itemRows.forEach(row => tbody.appendChild(row));
  }

  private handleGlobalClick(event: Event): void {
    const target = event.target as HTMLElement;
    
    // Price details toggle
    if (target.closest('.price-details-btn')) {
      this.handlePriceDetailsClick(target.closest('.price-details-btn') as HTMLElement);
    }
    
    // Close price details when clicking outside
    if (!target.closest('.price-details') && 
        !target.closest('.price-details-btn') && 
        !target.closest('.price-details-backdrop')) {
      this.hidePriceDetails();
    }
  }

  private handlePriceDetailsClick(btn: HTMLElement): void {
    const itemId = btn.dataset.itemId;
    if (!itemId) return;

    const detailsDiv = DOMUtils.getElement<HTMLElement>(`#price-details-${itemId}`);
    if (!detailsDiv) return;

    // Hide all other price details and remove any existing backdrop
    document.querySelectorAll('.price-details').forEach(div => {
      if (div !== detailsDiv) {
        (div as HTMLElement).style.display = 'none';
      }
    });
    
    const existingBackdrop = document.querySelector('.price-details-backdrop');
    if (existingBackdrop) {
      existingBackdrop.remove();
    }

    // Toggle current details
    if (detailsDiv.style.display === 'none' || !detailsDiv.style.display) {
      // Create backdrop
      const backdrop = DOMUtils.createElement('div', { class: 'price-details-backdrop' });
      backdrop.onclick = () => this.hidePriceDetails();
      document.body.appendChild(backdrop);

      detailsDiv.style.display = 'block';

      // Smart positioning to keep popup in viewport
      const rect = btn.getBoundingClientRect();
      const viewport = {
        width: window.innerWidth,
        height: window.innerHeight
      };

      let top: number, left: number;

      // Check if we're on mobile (small screen)
      if (viewport.width <= 768) {
        // Center on mobile - will be handled by CSS media query
        detailsDiv.style.top = '';
        detailsDiv.style.left = '';
      } else {
        // Desktop positioning
        const popupWidth = 350;
        const popupHeight = 250; // Estimated height with new header

        // Try to position below the button
        top = rect.bottom + 8;

        // If popup would go off bottom of screen, position above
        if (top + popupHeight > viewport.height - 20) {
          top = rect.top - popupHeight - 8;
        }

        // Ensure top doesn't go negative
        top = Math.max(20, top);

        // Center horizontally relative to button, but keep in viewport
        left = rect.left - (popupWidth / 2) + (rect.width / 2);
        left = Math.max(10, Math.min(left, viewport.width - popupWidth - 10));

        detailsDiv.style.top = top + 'px';
        detailsDiv.style.left = left + 'px';
      }
    } else {
      this.hidePriceDetails();
    }
  }

  private hidePriceDetails(): void {
    document.querySelectorAll('.price-details').forEach(div => {
      (div as HTMLElement).style.display = 'none';
    });
    
    const backdrop = document.querySelector('.price-details-backdrop');
    if (backdrop) {
      backdrop.remove();
    }
  }

  private handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      this.hidePriceDetails();
      this.hideAnonymousPopup();
    }
  }

  private async handleAnonymousIndicatorClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    if (target.closest('.anonymous-indicator')) {
      const indicator = target.closest('.anonymous-indicator') as HTMLElement;
      const priceId = indicator.dataset.priceId;
      
      if (!priceId) return;
      
      try {
        const response = await apiService.get(`/api/price/${priceId}/anonymous-info/`);
        
        if (response.success && response.data) {
          this.showAnonymousPopup(indicator, response.data);
        }
      } catch (error) {
        console.error('Error loading anonymous info:', error);
      }
    }
  }

  private showAnonymousPopup(triggerElement: HTMLElement, data: any): void {
    const popup = DOMUtils.getElement<HTMLElement>('#anonymous-popup');
    if (!popup) return;

    // Update popup content
    const trustFill = popup.querySelector('#trust-fill') as HTMLElement;
    const trustPercentage = popup.querySelector('#trust-percentage') as HTMLElement;
    const trustLevel = popup.querySelector('#trust-level') as HTMLElement;
    const confidenceLevel = popup.querySelector('#confidence-level') as HTMLElement;
    const submitterId = popup.querySelector('#submitter-id') as HTMLElement;
    const verificationBadges = popup.querySelector('#verification-badges') as HTMLElement;
    const warningBadges = popup.querySelector('#warning-badges') as HTMLElement;

    if (trustFill) {
      trustFill.style.width = `${data.trust_score * 100}%`;
      trustFill.className = `trust-fill ${data.trust_color}`;
    }
    
    if (trustPercentage) {
      trustPercentage.textContent = `${Math.round(data.trust_score * 100)}%`;
    }
    
    if (trustLevel) {
      trustLevel.textContent = data.trust_level;
    }
    
    if (confidenceLevel) {
      confidenceLevel.textContent = data.confidence_adjusted.charAt(0).toUpperCase() + data.confidence_adjusted.slice(1);
    }
    
    if (submitterId) {
      submitterId.textContent = `...${data.ip_hash}`;
    }

    // Clear previous badges
    if (verificationBadges) {
      verificationBadges.innerHTML = '';
      if (data.is_verified) {
        verificationBadges.innerHTML = '<span class="verified-badge">✓ Verified</span>';
      }
    }

    if (warningBadges) {
      warningBadges.innerHTML = '';
      if (data.flagged_count > 0) {
        warningBadges.innerHTML = `<span class="flagged-warning">⚠ ${data.flagged_count} flags</span>`;
      }
    }

    // Position popup
    const rect = triggerElement.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight
    };

    // Check if we're on mobile
    if (viewport.width <= 768) {
      // Center on mobile
      popup.style.position = 'fixed';
      popup.style.top = '50%';
      popup.style.left = '50%';
      popup.style.transform = 'translate(-50%, -50%)';
    } else {
      // Desktop positioning
      popup.style.position = 'absolute';
      popup.style.transform = 'none';
      
      let top = rect.bottom + 8;
      let left = rect.left - 125; // Approximate center of popup width

      // Keep popup in viewport
      if (top + 200 > viewport.height) {
        top = rect.top - 200 - 8;
      }
      if (left < 10) {
        left = 10;
      }
      if (left + 250 > viewport.width - 10) {
        left = viewport.width - 260;
      }

      popup.style.top = top + 'px';
      popup.style.left = left + 'px';
    }

    // Show popup
    popup.classList.add('show');
  }

  private hideAnonymousPopup(): void {
    const popup = DOMUtils.getElement<HTMLElement>('#anonymous-popup');
    if (popup) {
      popup.classList.remove('show');
    }
  }

  private async handlePriceModalClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    // Add Price: open add price modal
    if (target.closest('.add-price-btn')) {
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.add-price-btn') as HTMLElement;
      const itemId = btn.dataset.itemId;
      const listId = btn.dataset.listId;
      
      if (!itemId || !listId) return;
      
      this.showButtonLoading(btn as HTMLButtonElement);
      
      try {
        const url = `/item/${itemId}/add_price_modal/to_list/${listId}/`;
        const response = await apiService.get(url, { useCache: false });
        
        if (response.html) {
          // Create content element first so we can query it
          const contentElement = document.createElement('div');
          contentElement.innerHTML = response.html;
          
          // Create and open modal using Modal component
          const modal = new Modal({
            title: 'Add Price',
            content: contentElement,
            size: 'md',
          });
          
          // Set up form submission handler
          modal.on('open', () => {
            const form = contentElement.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupPriceFormSubmission(form, itemId, listId);
            }
            
            // Focus first input
            setTimeout(() => {
              const firstInput = contentElement.querySelector('input, select, textarea') as HTMLElement;
              if (firstInput) {
                firstInput.focus();
              }
            }, 100);
          });
          
          await modal.open();
        }
      } catch (error) {
        logger.error('Error loading add price modal', 'packing_list', error);
        StateUtils.addNotification('Error loading price form. Please try again.', 'error');
      } finally {
        this.hideButtonLoading(btn as HTMLButtonElement, 'Add Price');
      }
    }
    
    // Edit Price: open edit price modal
    else if (target.closest('.edit-price-btn')) {
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.edit-price-btn') as HTMLElement;
      const priceId = btn.dataset.priceId;
      const listId = btn.dataset.listId;
      
      if (!priceId || !listId) return;
      
      this.showButtonLoading(btn as HTMLButtonElement);
      
      try {
        const url = `/list/${listId}/price/${priceId}/edit_modal/`;
        const response = await apiService.get(url, { useCache: false });
        
        if (response.html) {
          // Create content element first so we can query it
          const contentElement = document.createElement('div');
          contentElement.innerHTML = response.html;
          
          // Create and open modal using Modal component
          const modal = new Modal({
            title: 'Edit Price',
            content: contentElement,
            size: 'md',
          });
          
          // Set up form submission handler
          modal.on('open', () => {
            const form = contentElement.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupPriceFormSubmission(form, '', listId);
            }
            
            // Focus first input
            setTimeout(() => {
              const firstInput = contentElement.querySelector('input, select, textarea') as HTMLElement;
              if (firstInput) {
                firstInput.focus();
              }
            }, 100);
          });
          
          await modal.open();
        }
      } catch (error) {
        logger.error('Error loading edit price modal', 'packing_list', error);
        StateUtils.addNotification('Error loading price form. Please try again.', 'error');
      } finally {
        this.hideButtonLoading(btn as HTMLButtonElement, 'Edit');
      }
    }
    
    // Expand Price: open price details
    else if (target.closest('.expand-price-btn')) {
      const btn = target.closest('.expand-price-btn') as HTMLElement;
      const itemId = btn.dataset.itemId;
      if (!itemId) return Promise.resolve();
      this.handlePriceDetailsClick(btn);
    }
    return Promise.resolve();
  }

  private setDefaultFormValues(form: HTMLFormElement): void {
    // Set default quantity to 1 if empty
    const quantityInput = form.querySelector('#id_quantity') as HTMLInputElement;
    if (quantityInput) {
      if (!quantityInput.value) {
        quantityInput.value = '1';
      }
      quantityInput.required = true;
    }
    
    // Set default price requirement
    const priceInput = form.querySelector('#id_price') as HTMLInputElement;
    if (priceInput) {
      priceInput.required = true;
      priceInput.placeholder = 'Enter price (e.g. 9.99)';
    }
    
    // Ensure a store is selected (select first available store if none selected)
    const storeSelect = form.querySelector('#id_store') as HTMLSelectElement;
    if (storeSelect) {
      if (!storeSelect.value) {
        // Find first non-empty option
        const options = storeSelect.querySelectorAll('option') as NodeListOf<HTMLOptionElement>;
        
        for (let i = 1; i < options.length; i++) { // Skip first empty option
          if (options[i].value && options[i].value !== '__add_new__') {
            storeSelect.value = options[i].value;
            break;
          }
        }
      }
    }
    
    // Set default date to today if empty
    const dateInput = form.querySelector('#id_date_purchased') as HTMLInputElement;
    if (dateInput && !dateInput.value) {
      const today = new Date().toISOString().split('T')[0];
      dateInput.value = today;
    }
  }

  private setupStoreSelection(form: HTMLFormElement): void {
    const storeSelect = form.querySelector('#id_store') as HTMLSelectElement;
    const addStoreDiv = form.querySelector('#inline-add-store') as HTMLElement;
    const storeNameInput = form.querySelector('#id_store_name') as HTMLInputElement;

    console.log('Setting up store selection:', { storeSelect, addStoreDiv, storeNameInput });

    if (!storeSelect || !addStoreDiv) {
      console.log('Missing store selection elements');
      return;
    }

    // Log all available options
    const options = Array.from(storeSelect.options);
    console.log('Store dropdown options:', options.map(opt => ({ value: opt.value, text: opt.text })));

    storeSelect.addEventListener('change', () => {
      console.log('Store selection changed to:', storeSelect.value);
      if (storeSelect.value === '__add_new__') {
        console.log('Showing add store section');
        addStoreDiv.style.display = 'block';
        if (storeNameInput) {
          storeNameInput.required = true;
          storeNameInput.focus();
        }
      } else {
        console.log('Hiding add store section');
        addStoreDiv.style.display = 'none';
        if (storeNameInput) {
          storeNameInput.required = false;
          storeNameInput.value = '';
        }
      }
    });

    // Initialize the correct state
    if (storeSelect.value === '__add_new__') {
      console.log('Initializing add store section as visible');
      addStoreDiv.style.display = 'block';
      if (storeNameInput) {
        storeNameInput.required = true;
      }
    }
  }

  public setupPriceFormSubmission(form: HTMLFormElement, itemId: string, listId: string): void {
    
    // Set default values
    this.setDefaultFormValues(form);
    
    // Set up store selection change handler
    this.setupStoreSelection(form);
    
    // Set up quick price buttons
    const quickPriceBtns = form.querySelectorAll('.quick-price-btn');
    quickPriceBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const price = (e.target as HTMLElement).dataset.price;
        const priceInput = form.querySelector('#id_price') as HTMLInputElement;
        if (price && priceInput) {
          priceInput.value = price;
          priceInput.focus();
          // Trigger input event to update any validation or calculations
          priceInput.dispatchEvent(new Event('input'));
        }
      });
    });
    
    // Set up quantity buttons
    const quantityBtns = form.querySelectorAll('.set-quantity-btn');
    quantityBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const quantity = (e.target as HTMLElement).dataset.quantity;
        const quantityInput = form.querySelector('#id_quantity') as HTMLInputElement;
        if (quantity && quantityInput) {
          quantityInput.value = quantity;
          quantityInput.dispatchEvent(new Event('input'));
        }
      });
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Check form validity first
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      // Show loading state on submit button
      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        UIUtils.showLoading(submitBtn);
      }

      try {
        const formData = FormUtils.getFormData(form);
        
        // Validate required fields manually
        const price = formData.get('price');
        const quantity = formData.get('quantity');
        const store = formData.get('store');
        const storeName = formData.get('store_name');
        
        if (!price) {
          StateUtils.addNotification('Price is required', 'error');
          return;
        }
        if (!quantity) {
          StateUtils.addNotification('Quantity is required', 'error');
          return;
        }
        if (!store && !storeName) {
          StateUtils.addNotification('Please select a store or enter a new store name', 'error');
          return;
        }
        
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement)?.value || '',
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
          Modal.alert('Price added successfully!', 'Success');
          location.reload(); // Refresh to show new price
        } else if (data.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#price-modal-body');
          if (modalBody) {
            modalBody.innerHTML = data.html;
            const newForm = modalBody.querySelector('form') as HTMLFormElement;
            if (newForm) {
              this.setupPriceFormSubmission(newForm, itemId, listId);
            }
          }
        } else if (data.message) {
          StateUtils.addNotification(data.message, 'error');
        } else {
          StateUtils.addNotification('Unknown error occurred', 'error');
        }
      } catch (error) {
        StateUtils.addNotification('Error adding price. Please try again.', 'error');
      } finally {
        // Remove loading state
        if (submitBtn) {
          this.hideButtonLoading(submitBtn, 'Save Price');
        }
      }
    });
  }

  private async handleEditItemModalClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    
    if (target.closest('.edit-item-btn')) {
      event.preventDefault();
      event.stopPropagation();
      
      const btn = target.closest('.edit-item-btn') as HTMLElement;
      const pliId = btn.dataset.pliId;
      const listId = btn.dataset.listId;
      
      if (!pliId || !listId) return;
      
      this.showButtonLoading(btn as HTMLButtonElement);
      
      try {
        const response = await apiService.get(`/list/${listId}/item/${pliId}/edit_modal/`);
        
        if (response.html) {
          // Create content element first so we can query it
          const contentElement = document.createElement('div');
          contentElement.innerHTML = response.html;
          
          // Create and open modal using Modal component
          const modal = new Modal({
            title: 'Edit Item',
            content: contentElement,
            size: 'md',
          });
          
          // Set up form submission handler
          modal.on('open', () => {
            const form = contentElement.querySelector('form') as HTMLFormElement;
            if (form) {
              this.setupEditItemFormSubmission(form, pliId, listId);
            }
            
            // Focus first input
            setTimeout(() => {
              const firstInput = contentElement.querySelector('input, select, textarea') as HTMLElement;
              if (firstInput) {
                firstInput.focus();
              }
            }, 100);
          });
          
          await modal.open();
        }
      } catch (error) {
        logger.error('Error loading edit item modal', 'packing_list', error);
        StateUtils.addNotification('Error loading edit form. Please try again.', 'error');
      } finally {
        this.hideButtonLoading(btn as HTMLButtonElement, 'Edit');
      }
      return Promise.resolve();
    }
  }

  private setupEditItemFormSubmission(form: HTMLFormElement, listId: string, pliId: string): void {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Show loading state on submit button
      const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (submitBtn) {
        UIUtils.showLoading(submitBtn);
      }

      try {
        const formData = FormUtils.getFormData(form);
        const response = await apiService.post(form.action, formData);

        if (response.success) {
          Modal.alert('Item updated successfully!', 'Success');
          location.reload(); // Refresh to show changes
        } else if (response.html) {
          const modalBody = DOMUtils.getElement<HTMLElement>('#edit-item-modal-body');
          if (modalBody) {
            modalBody.innerHTML = response.html;
            const newForm = modalBody.querySelector('form') as HTMLFormElement;
            if (newForm) {
              this.setupEditItemFormSubmission(newForm, listId, pliId);
            }
          }
        }
      } catch (error) {
        StateUtils.addNotification('Error updating item. Please try again.', 'error');
      } finally {
        // Remove loading state
        if (submitBtn) {
          this.hideButtonLoading(submitBtn, 'Save Changes');
        }
      }
    });
  }

  private async handleVoteClick(event: Event): Promise<void> {
    const target = event.target as HTMLElement;
    if (target.classList.contains('vote-btn')) {
      const priceId = (target as HTMLElement).dataset.priceId;
      if (!priceId) return;
      const isUpvote = target.classList.contains('upvote');
      
      // Disable button to prevent double-clicking
      (target as HTMLButtonElement).disabled = true;

      try {
        const response = await apiService.vote(parseInt(priceId), isUpvote ? 'up' : 'down');
        
        if (response.success) {
          // Update vote counts
          const priceEntry = target.closest('.price-entry');
          if (priceEntry) {
            const upvoteBtn = priceEntry.querySelector('.vote-btn.upvote') as HTMLElement;
            const downvoteBtn = priceEntry.querySelector('.vote-btn.downvote') as HTMLElement;
            
            if (upvoteBtn) {
              upvoteBtn.innerHTML = upvoteBtn.innerHTML.replace(/\d+/, response.upvotes.toString());
            }
            if (downvoteBtn) {
              downvoteBtn.innerHTML = downvoteBtn.innerHTML.replace(/\d+/, response.downvotes.toString());
            }
          }
          
          // Show success message briefly
          const originalText = target.textContent || '';
          target.textContent = isUpvote ? '✓' : '✗';
          setTimeout(() => {
            target.textContent = originalText;
          }, 1000);
        } else {
          StateUtils.addNotification(response.message || 'Error voting. Please try again.', 'error');
        }
      } catch (error) {
        StateUtils.addNotification('Error voting. Please try again.', 'error');
      } finally {
        // Re-enable button
        (target as HTMLButtonElement).disabled = false;
      }
    }
  }

  private handleClearBaseFilter(): void {
    const baseSelect = DOMUtils.getElement<HTMLSelectElement>('#base-select');
    const radiusSelect = DOMUtils.getElement<HTMLSelectElement>('#radius-select');
    if (baseSelect) (baseSelect as HTMLSelectElement).disabled = false;
    if (radiusSelect) (radiusSelect as HTMLSelectElement).disabled = false;
    // Clear the form and redirect without filter parameters
    const url = new URL(window.location.href);
    url.searchParams.delete('base_filter');
    url.searchParams.delete('radius');
    window.location.href = url.toString();
  }

  private handleBaseSelectChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target.value) {
      const form = target.closest('form') as HTMLFormElement;
      if (form) {
        form.submit();
      }
    }
  }

  private handleRadiusSelectChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const baseSelect = DOMUtils.getElement<HTMLSelectElement>('#base-select');
    const baseValue = baseSelect?.value || '';
    
    if (baseValue) {
      const form = target.closest('form') as HTMLFormElement;
      if (form) {
        form.submit();
      }
    }
  }

  private injectActionButtonIcons(): void {
    console.log('Injecting SVG icons into action buttons...');
    
    // Define SVG icons
    const icons = {
      addPrice: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-dollar-sign"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`,
      expandPrice: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-bar-chart"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>`,
      editItem: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>`,
      review: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon></svg>`
    };

    // Inject icons with retry mechanism
    const injectIcons = (attempt = 1) => {
      const maxAttempts = 3;
      
      // Add price buttons
      const addPriceBtns = document.querySelectorAll('.add-price-btn .btn-icon');
      console.log(`Attempt ${attempt}: Found ${addPriceBtns.length} add-price button icons`);
      addPriceBtns.forEach((icon: Element) => {
        if (icon.textContent?.trim() === '$' || icon.innerHTML.trim() === '') {
          icon.innerHTML = icons.addPrice;
          console.log('Injected add-price icon');
        }
      });

      // Expand price buttons  
      const expandPriceBtns = document.querySelectorAll('.expand-price-btn .btn-icon');
      console.log(`Attempt ${attempt}: Found ${expandPriceBtns.length} expand-price button icons`);
      expandPriceBtns.forEach((icon: Element) => {
        if (icon.textContent?.includes('📊') || icon.innerHTML.trim() === '') {
          icon.innerHTML = icons.expandPrice;
          console.log('Injected expand-price icon');
        }
      });

      // Edit item buttons
      const editItemBtns = document.querySelectorAll('.edit-item-btn .btn-icon');
      console.log(`Attempt ${attempt}: Found ${editItemBtns.length} edit-item button icons`);
      editItemBtns.forEach((icon: Element) => {
        if (icon.textContent?.trim() === '✏' || icon.innerHTML.trim() === '') {
          icon.innerHTML = icons.editItem;
          console.log('Injected edit-item icon');
        }
      });

      // Review buttons
      const reviewBtns = document.querySelectorAll('.review-btn .btn-icon');
      console.log(`Attempt ${attempt}: Found ${reviewBtns.length} review button icons`);
      reviewBtns.forEach((icon: Element) => {
        if (icon.textContent?.trim() === '★' || icon.innerHTML.trim() === '') {
          icon.innerHTML = icons.review;
          console.log('Injected review icon');
        }
      });

      // Check if we successfully injected icons, if not retry
      const totalButtons = addPriceBtns.length + expandPriceBtns.length + editItemBtns.length + reviewBtns.length;
      const iconsInjected = document.querySelectorAll('.action-btn svg').length;
      
      console.log(`Total buttons: ${totalButtons}, Icons injected: ${iconsInjected}`);
      
      if (iconsInjected === 0 && attempt < maxAttempts && totalButtons > 0) {
        console.log(`No icons injected on attempt ${attempt}, retrying in 100ms...`);
        setTimeout(() => injectIcons(attempt + 1), 100);
      } else {
        console.log(`Icon injection complete. Attempt ${attempt}, ${iconsInjected} icons injected.`);
      }
    };

    // Start injection
    injectIcons();
  }

  private hideModal(modalId: string): void {
    const modal = DOMUtils.getElement<HTMLElement>(`#${modalId}`);
    if (modal) {
      modal.style.display = 'none';
    }
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
        '/api/recent-prices/',
        '/api/user-location/'
      ];
      
      await apiService.preload(preloadUrls);
      logger.debug('Data preloading completed', 'packing_list');
    } catch (error) {
      logger.warn('Failed to preload some data', 'packing_list', error);
    }
  }

  // Cleanup method
  public destroy(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    logger.info('PackingListDetailManager destroyed', 'packing_list');
  }
}

// Initialize when DOM is loaded or immediately if already loaded
function initializePackingListDetail() {
  const manager = new PackingListDetailManager();
  
  // Store manager reference for global access
  (window as any).packingListManager = manager;

  // Patch: Attach price form handler for static modal
  const form = document.querySelector('#price-form') as HTMLFormElement;
  if (form) {
    // Try to get itemId and listId from data attributes or fallback to empty string
    const itemId = form.dataset.itemId || '';
    const listId = form.dataset.listId || '';
    // Use the same handler as dynamic modal
    manager.setupPriceFormSubmission(form, itemId, listId);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializePackingListDetail);
} else {
  // DOM is already loaded
  initializePackingListDetail();
}

// Export for global access (if needed)
(window as any).hidePriceDetails = function(): void {
  const manager = (window as any).packingListManager;
  if (manager) {
    manager.hidePriceDetails();
  }
};

(window as any).hideAnonymousPopup = function(): void {
  const manager = (window as any).packingListManager;
  if (manager) {
    manager.hideAnonymousPopup();
  }
};

export default PackingListDetailManager; 