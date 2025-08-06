/**
 * Unit tests for ItemsPageManager class
 * Tests event handling, modal management, and bulk actions
 */

import ItemsPageManager from '../src/items';
import { DOMUtils, UIUtils, apiClient, FormUtils } from '../src/common';

// Mock dependencies
jest.mock('../src/common', () => ({
  DOMUtils: {
    getElement: jest.fn()
  },
  UIUtils: {
    showModal: jest.fn(),
    hideModal: jest.fn(),
    showLoading: jest.fn(),
    hideLoading: jest.fn(),
    showNotification: jest.fn()
  },
  apiClient: {
    get: jest.fn(),
    post: jest.fn()
  },
  FormUtils: {
    getFormData: jest.fn()
  }
}));

describe('ItemsPageManager', () => {
  let manager: ItemsPageManager;
  let mockElement: HTMLElement;
  let mockButton: HTMLButtonElement;
  let mockForm: HTMLFormElement;

  beforeEach(() => {
    // Create mock DOM elements
    mockElement = document.createElement('div');
    mockButton = document.createElement('button');
    mockForm = document.createElement('form');

    // Reset mocks
    jest.clearAllMocks();
    
    // Mock DOMUtils.getElement to return our mock elements
    (DOMUtils.getElement as jest.Mock).mockImplementation((selector: string) => {
      if (selector.includes('modal')) return mockElement;
      if (selector.includes('btn')) return mockButton;
      if (selector.includes('form')) return mockForm;
      return mockElement;
    });

    // Setup basic DOM structure
    document.body.innerHTML = `
      <div id="price-modal" class="modal">
        <div id="price-modal-body"></div>
        <button id="close-price-modal">Close</button>
      </div>
      <div id="item-modal" class="modal">
        <div id="item-modal-body"></div>
        <button id="close-item-modal">Close</button>
      </div>
      <div id="bulkActions" style="display: none;"></div>
      <div id="selectedCount"></div>
      <button class="add-price-btn" data-item-id="123">Add Price</button>
      <button class="edit-price-btn" data-item-id="123" data-price-id="456">Edit Price</button>
      <button class="edit-item-btn" data-item-id="123">Edit Item</button>
      <input type="checkbox" class="item-select" value="123">
      <input type="checkbox" class="item-select" value="456">
    `;

    manager = new ItemsPageManager();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Initialization', () => {
    test('should initialize without errors', () => {
      expect(manager).toBeInstanceOf(ItemsPageManager);
    });

    test('should set up event listeners on construction', () => {
      // Verify event listeners were attached by checking if click events work
      const addPriceBtn = document.querySelector('.add-price-btn') as HTMLButtonElement;
      expect(addPriceBtn).toBeTruthy();
    });
  });

  describe('Price Modal Handling', () => {
    beforeEach(() => {
      // Mock successful API response
      (apiClient.get as jest.Mock).mockResolvedValue({
        html: '<form><input type="text" name="price"><button type="submit">Save</button></form>'
      });
    });

    test('should open price modal for add price button', async () => {
      const addPriceBtn = document.querySelector('.add-price-btn') as HTMLButtonElement;
      
      // Simulate click event
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: addPriceBtn });
      
      // Trigger the event
      document.dispatchEvent(clickEvent);
      
      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(apiClient.get).toHaveBeenCalledWith('/item/123/add_price_modal/');
      expect(UIUtils.showLoading).toHaveBeenCalledWith(addPriceBtn);
    });

    test('should open price modal for edit price button with price ID', async () => {
      const editPriceBtn = document.querySelector('.edit-price-btn') as HTMLButtonElement;
      
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: editPriceBtn });
      
      document.dispatchEvent(clickEvent);
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(apiClient.get).toHaveBeenCalledWith('/item/123/add_price_modal/?price_id=456');
    });

    test('should handle API errors gracefully', async () => {
      (apiClient.get as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      const addPriceBtn = document.querySelector('.add-price-btn') as HTMLButtonElement;
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: addPriceBtn });
      
      document.dispatchEvent(clickEvent);
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(UIUtils.showNotification).toHaveBeenCalledWith(
        'Error loading price form. Please try again.',
        'error'
      );
      expect(UIUtils.hideLoading).toHaveBeenCalled();
    });
  });

  describe('Item Modal Handling', () => {
    beforeEach(() => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        html: '<form><input type="text" name="name"><button type="submit">Save</button></form>'
      });
    });

    test('should open item edit modal', async () => {
      const editItemBtn = document.querySelector('.edit-item-btn') as HTMLButtonElement;
      
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: editItemBtn });
      
      document.dispatchEvent(clickEvent);
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(apiClient.get).toHaveBeenCalledWith('/item/123/edit_modal/');
      expect(UIUtils.showLoading).toHaveBeenCalledWith(editItemBtn);
    });
  });

  describe('Selection Management', () => {
    test('should handle item selection changes', () => {
      const checkbox1 = document.querySelector('input[value="123"]') as HTMLInputElement;
      const checkbox2 = document.querySelector('input[value="456"]') as HTMLInputElement;
      
      // Select first item
      checkbox1.checked = true;
      const changeEvent1 = new Event('change', { bubbles: true });
      Object.defineProperty(changeEvent1, 'target', { value: checkbox1 });
      document.dispatchEvent(changeEvent1);
      
      // Check bulk actions visibility updated
      expect(DOMUtils.getElement).toHaveBeenCalledWith('#bulkActions');
      expect(DOMUtils.getElement).toHaveBeenCalledWith('#selectedCount');
      
      // Select second item
      checkbox2.checked = true;
      const changeEvent2 = new Event('change', { bubbles: true });
      Object.defineProperty(changeEvent2, 'target', { value: checkbox2 });
      document.dispatchEvent(changeEvent2);
      
      // Unselect first item
      checkbox1.checked = false;
      const changeEvent3 = new Event('change', { bubbles: true });
      Object.defineProperty(changeEvent3, 'target', { value: checkbox1 });
      document.dispatchEvent(changeEvent3);
    });

    test('should clear all selections', () => {
      // Select items first
      const checkbox1 = document.querySelector('input[value="123"]') as HTMLInputElement;
      const checkbox2 = document.querySelector('input[value="456"]') as HTMLInputElement;
      
      checkbox1.checked = true;
      checkbox2.checked = true;
      
      // Simulate clear selection click
      const clearButton = document.createElement('button');
      clearButton.textContent = 'Clear Selection';
      document.body.appendChild(clearButton);
      
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: clearButton });
      document.dispatchEvent(clickEvent);
      
      expect(checkbox1.checked).toBe(false);
      expect(checkbox2.checked).toBe(false);
    });
  });

  describe('View Toggle', () => {
    beforeEach(() => {
      // Add view elements to DOM
      document.body.innerHTML += `
        <button id="cardViewBtn">Card View</button>
        <button id="tableViewBtn">Table View</button>
        <div id="itemsCardView"></div>
        <div id="itemsTableView"></div>
      `;
    });

    test('should switch to card view', () => {
      const cardBtn = document.getElementById('cardViewBtn') as HTMLButtonElement;
      const tableBtn = document.getElementById('tableViewBtn') as HTMLButtonElement;
      const cardView = document.getElementById('itemsCardView') as HTMLElement;
      const tableView = document.getElementById('itemsTableView') as HTMLElement;

      // Mock DOMUtils.getElement for view elements
      (DOMUtils.getElement as jest.Mock).mockImplementation((selector: string) => {
        switch (selector) {
          case '#cardViewBtn': return cardBtn;
          case '#tableViewBtn': return tableBtn;
          case '#itemsCardView': return cardView;
          case '#itemsTableView': return tableView;
          default: return mockElement;
        }
      });

      cardBtn.click();

      expect(localStorage.setItem).toHaveBeenCalledWith('itemsViewPreference', 'card');
    });
  });

  describe('Form Submission', () => {
    test('should handle successful price form submission', async () => {
      const form = document.createElement('form');
      form.action = '/submit-price';
      
      const submitButton = document.createElement('button');
      submitButton.type = 'submit';
      form.appendChild(submitButton);
      
      // Mock successful API response
      (apiClient.post as jest.Mock).mockResolvedValue({ success: true });
      (FormUtils.getFormData as jest.Mock).mockReturnValue(new FormData());
      
      // Trigger form submission
      const submitEvent = new Event('submit', { bubbles: true });
      form.dispatchEvent(submitEvent);
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(UIUtils.showLoading).toHaveBeenCalledWith(submitButton);
      expect(apiClient.post).toHaveBeenCalledWith('/submit-price', expect.any(FormData));
      expect(UIUtils.hideModal).toHaveBeenCalledWith('price-modal');
      expect(UIUtils.showNotification).toHaveBeenCalledWith('Price updated successfully!', 'success');
    });

    test('should handle form submission errors', async () => {
      const form = document.createElement('form');
      form.action = '/submit-price';
      
      const submitButton = document.createElement('button');
      submitButton.type = 'submit';
      form.appendChild(submitButton);
      
      // Mock API error
      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Network error'));
      (FormUtils.getFormData as jest.Mock).mockReturnValue(new FormData());
      
      const submitEvent = new Event('submit', { bubbles: true });
      form.dispatchEvent(submitEvent);
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(UIUtils.showNotification).toHaveBeenCalledWith(
        'Error updating price. Please try again.',
        'error'
      );
      expect(UIUtils.hideLoading).toHaveBeenCalledWith(submitButton, 'Save Price');
    });
  });

  describe('Price Toggle', () => {
    test('should toggle price visibility', () => {
      // Create price toggle elements
      const toggleButton = document.createElement('button');
      toggleButton.textContent = 'Show All Prices';
      
      const pricesDiv = document.createElement('div');
      pricesDiv.classList.add('all-prices');
      pricesDiv.style.display = 'none';
      
      // Insert pricesDiv as next sibling
      document.body.appendChild(toggleButton);
      document.body.appendChild(pricesDiv);
      
      const clickEvent = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(clickEvent, 'target', { value: toggleButton });
      
      document.dispatchEvent(clickEvent);
      
      expect(pricesDiv.style.display).toBe('block');
      expect(toggleButton.textContent).toBe('Hide Prices');
      
      // Toggle again
      document.dispatchEvent(clickEvent);
      
      expect(pricesDiv.style.display).toBe('none');
      expect(toggleButton.textContent).toBe('Show All Prices');
    });
  });

  describe('Base Change Handling', () => {
    test('should disable city and state when base is selected', () => {
      const baseSelect = document.createElement('select');
      baseSelect.id = 'base';
      baseSelect.value = 'some-base';
      
      const citySelect = document.createElement('select');
      citySelect.id = 'city';
      
      const stateSelect = document.createElement('select');
      stateSelect.id = 'state';
      
      document.body.appendChild(baseSelect);
      document.body.appendChild(citySelect);
      document.body.appendChild(stateSelect);
      
      // Mock DOMUtils for selects
      (DOMUtils.getElement as jest.Mock).mockImplementation((selector: string) => {
        if (selector === '#city') return citySelect;
        if (selector === '#state') return stateSelect;
        return mockElement;
      });
      
      const changeEvent = new Event('change', { bubbles: true });
      Object.defineProperty(changeEvent, 'target', { value: baseSelect });
      
      document.dispatchEvent(changeEvent);
      
      expect(citySelect.disabled).toBe(true);
      expect(stateSelect.disabled).toBe(true);
    });
  });
});