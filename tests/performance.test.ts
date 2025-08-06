/**
 * Performance testing suite for client-side operations
 * Tests DOM manipulation, memory usage, and rendering performance
 */

describe('Performance - DOM Operations', () => {
  beforeEach(() => {
    // Create a large DOM structure for testing
    const container = document.createElement('div');
    container.id = 'performance-test-container';
    
    for (let i = 0; i < 1000; i++) {
      const item = document.createElement('div');
      item.className = 'test-item';
      item.id = `item-${i}`;
      item.innerHTML = `
        <h3>Item ${i}</h3>
        <p>Description for item ${i}</p>
        <button class="action-btn" data-id="${i}">Action</button>
      `;
      container.appendChild(item);
    }
    
    document.body.appendChild(container);
  });

  afterEach(() => {
    const container = document.getElementById('performance-test-container');
    if (container) {
      container.remove();
    }
  });

  test('should efficiently query large DOM structures', () => {
    const startTime = performance.now();
    
    // Test various query methods
    const byId = document.getElementById('item-500');
    const byClass = document.getElementsByClassName('test-item');
    const byQuerySelector = document.querySelectorAll('.test-item');
    const bySpecificQuery = document.querySelectorAll('[data-id="250"]');
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    // Performance assertions
    expect(duration).toBeLessThan(50); // Should complete in under 50ms
    expect(byId).toBeTruthy();
    expect(byClass.length).toBe(1000);
    expect(byQuerySelector.length).toBe(1000);
    expect(bySpecificQuery.length).toBe(1);
  });

  test('should efficiently manipulate multiple DOM elements', () => {
    const startTime = performance.now();
    
    // Batch DOM modifications using DocumentFragment for efficiency
    const items = document.querySelectorAll('.test-item');
    const fragment = document.createDocumentFragment();
    
    // Move elements to fragment (more efficient than individual operations)
    items.forEach((item, index) => {
      if (index % 2 === 0) { // Every other item
        const clone = item.cloneNode(true) as HTMLElement;
        clone.style.backgroundColor = 'lightblue';
        fragment.appendChild(clone);
      }
    });
    
    // Single DOM insertion
    const newContainer = document.createElement('div');
    newContainer.appendChild(fragment);
    document.body.appendChild(newContainer);
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(100); // Should complete in under 100ms
    expect(newContainer.children.length).toBe(500); // Half the items
    
    // Cleanup
    newContainer.remove();
  });

  test('should handle event delegation efficiently', () => {
    const clickCounts: { [key: string]: number } = {};
    
    // Use event delegation instead of individual handlers
    const container = document.getElementById('performance-test-container');
    
    const startTime = performance.now();
    
    const delegatedHandler = (event: Event) => {
      const target = event.target as HTMLElement;
      if (target.classList.contains('action-btn')) {
        const id = target.dataset.id || 'unknown';
        clickCounts[id] = (clickCounts[id] || 0) + 1;
      }
    };
    
    container!.addEventListener('click', delegatedHandler);
    
    // Simulate clicks on multiple buttons
    const buttons = container!.querySelectorAll('.action-btn');
    for (let i = 0; i < 100; i++) {
      buttons[i].click();
    }
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(20); // Should be very fast with delegation
    expect(Object.keys(clickCounts).length).toBe(100);
    
    container!.removeEventListener('click', delegatedHandler);
  });
});

describe('Performance - Memory Usage', () => {
  test('should not create excessive object references', () => {
    const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
    const objects: any[] = [];
    
    // Create and cleanup objects to test for leaks
    for (let i = 0; i < 1000; i++) {
      const obj = {
        id: i,
        data: new Array(100).fill(i),
        element: document.createElement('div'),
        cleanup: function() {
          this.element.remove();
          this.data = null;
        }
      };
      objects.push(obj);
    }
    
    // Cleanup objects properly
    objects.forEach(obj => obj.cleanup());
    objects.length = 0;
    
    // Force garbage collection if available (Chrome DevTools)
    if ((window as any).gc) {
      (window as any).gc();
    }
    
    const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
    
    // Memory shouldn't grow excessively (allowing for some variance)
    if (initialMemory > 0 && finalMemory > 0) {
      const memoryIncrease = finalMemory - initialMemory;
      expect(memoryIncrease).toBeLessThan(1024 * 1024); // Less than 1MB increase
    }
    
    // This test mainly ensures we're thinking about memory cleanup
    expect(objects.length).toBe(0);
  });

  test('should properly cleanup event listeners', () => {
    const elements: HTMLElement[] = [];
    const listeners: Array<() => void> = [];
    
    // Create elements with event listeners
    for (let i = 0; i < 100; i++) {
      const element = document.createElement('button');
      const listener = () => console.log(`Button ${i} clicked`);
      
      element.addEventListener('click', listener);
      document.body.appendChild(element);
      
      elements.push(element);
      listeners.push(listener);
    }
    
    // Proper cleanup
    elements.forEach((element, index) => {
      element.removeEventListener('click', listeners[index]);
      element.remove();
    });
    
    elements.length = 0;
    listeners.length = 0;
    
    // Verify cleanup
    expect(elements.length).toBe(0);
    expect(document.querySelectorAll('button').length).toBeLessThan(100);
  });
});

describe('Performance - Rendering', () => {
  test('should render large lists efficiently', async () => {
    const startTime = performance.now();
    
    // Simulate rendering a large list with virtual scrolling concept
    const container = document.createElement('div');
    container.style.height = '400px';
    container.style.overflow = 'auto';
    
    // Only render visible items (virtual scrolling simulation)
    const totalItems = 10000;
    const visibleItems = 20;
    const itemHeight = 50;
    
    const virtualList = {
      scrollTop: 0,
      renderVisibleItems() {
        const startIndex = Math.floor(this.scrollTop / itemHeight);
        const endIndex = Math.min(startIndex + visibleItems, totalItems);
        
        container.innerHTML = '';
        
        // Create spacer for items above visible area
        const topSpacer = document.createElement('div');
        topSpacer.style.height = `${startIndex * itemHeight}px`;
        container.appendChild(topSpacer);
        
        // Render visible items
        for (let i = startIndex; i < endIndex; i++) {
          const item = document.createElement('div');
          item.style.height = `${itemHeight}px`;
          item.textContent = `Item ${i}`;
          container.appendChild(item);
        }
        
        // Create spacer for items below visible area
        const bottomSpacer = document.createElement('div');
        bottomSpacer.style.height = `${(totalItems - endIndex) * itemHeight}px`;
        container.appendChild(bottomSpacer);
      }
    };
    
    virtualList.renderVisibleItems();
    document.body.appendChild(container);
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    // Should render quickly even with large dataset
    expect(duration).toBeLessThan(20);
    expect(container.children.length).toBeLessThanOrEqual(22); // Visible items + spacers
    
    container.remove();
  });

  test('should batch style changes to avoid layout thrashing', () => {
    const elements: HTMLElement[] = [];
    
    // Create test elements
    for (let i = 0; i < 100; i++) {
      const element = document.createElement('div');
      element.textContent = `Element ${i}`;
      document.body.appendChild(element);
      elements.push(element);
    }
    
    const startTime = performance.now();
    
    // Batch style changes using requestAnimationFrame
    return new Promise<void>((resolve) => {
      requestAnimationFrame(() => {
        // Apply all style changes in a single frame
        elements.forEach((element, index) => {
          element.style.transform = `translateX(${index * 2}px)`;
          element.style.backgroundColor = `hsl(${index * 3.6}, 50%, 70%)`;
          element.style.opacity = '0.8';
        });
        
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        expect(duration).toBeLessThan(50);
        
        // Cleanup
        elements.forEach(el => el.remove());
        resolve();
      });
    });
  });
});

describe('Performance - Async Operations', () => {
  test('should handle concurrent API requests efficiently', async () => {
    const mockApiCall = (id: number): Promise<{ id: number; data: string }> => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({ id, data: `Data for ${id}` });
        }, Math.random() * 10); // 0-10ms delay
      });
    };
    
    const startTime = performance.now();
    
    // Concurrent requests instead of sequential
    const requests = Array.from({ length: 20 }, (_, i) => mockApiCall(i));
    const results = await Promise.all(requests);
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    // Should complete faster than sequential requests
    expect(duration).toBeLessThan(100); // Much faster than 20 * 10ms sequential
    expect(results.length).toBe(20);
    expect(results[0]).toHaveProperty('id');
    expect(results[0]).toHaveProperty('data');
  });

  test('should implement efficient debouncing', async () => {
    let callCount = 0;
    
    const createDebouncedFunction = (delay: number) => {
      let timeoutId: NodeJS.Timeout;
      return () => {
        clearTimeout(timeoutId);
        return new Promise<void>(resolve => {
          timeoutId = setTimeout(() => {
            callCount++;
            resolve();
          }, delay);
        });
      };
    };
    
    const debouncedFunction = createDebouncedFunction(10); // Shorter delay for testing
    const startTime = performance.now();
    
    // Rapid calls should be debounced - only the last one should execute
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(debouncedFunction());
    }
    
    // Wait for the last debounced call to complete
    await promises[promises.length - 1];
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    // Should only call the function once despite 5 attempts
    expect(callCount).toBe(1);
    expect(duration).toBeGreaterThan(10); // At least one debounce delay
  });
});

describe('Performance - Resource Loading', () => {
  test('should efficiently preload resources', () => {
    const startTime = performance.now();
    
    // Simulate resource preloading
    const preloadResource = (url: string, type: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        link.as = type;
        
        link.onload = () => resolve();
        link.onerror = () => reject(new Error(`Failed to preload ${url}`));
        
        document.head.appendChild(link);
        
        // Simulate immediate resolution for testing
        setTimeout(() => {
          document.head.removeChild(link);
          resolve();
        }, 1);
      });
    };
    
    const resources = [
      { url: '/css/main.css', type: 'style' },
      { url: '/js/app.js', type: 'script' },
      { url: '/images/hero.jpg', type: 'image' }
    ];
    
    const preloadPromises = resources.map(resource => 
      preloadResource(resource.url, resource.type)
    );
    
    return Promise.all(preloadPromises).then(() => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      expect(duration).toBeLessThan(20);
    });
  });

  test('should implement lazy loading for non-critical resources', () => {
    const lazyImages: HTMLImageElement[] = [];
    
    // Create lazy-loaded images
    for (let i = 0; i < 10; i++) {
      const img = document.createElement('img');
      img.dataset.src = `/images/lazy-${i}.jpg`;
      img.alt = `Lazy image ${i}`;
      img.style.height = '200px';
      img.style.backgroundColor = '#f0f0f0';
      
      lazyImages.push(img);
      document.body.appendChild(img);
    }
    
    const startTime = performance.now();
    
    // Simulate intersection observer for lazy loading
    const loadImage = (img: HTMLImageElement) => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
        delete img.dataset.src;
      }
    };
    
    // Load only "visible" images (first 3 for testing)
    lazyImages.slice(0, 3).forEach(loadImage);
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(10);
    
    // Verify only first 3 images have src attribute
    const loadedImages = lazyImages.filter(img => img.src !== '');
    expect(loadedImages.length).toBe(3);
    
    // Cleanup
    lazyImages.forEach(img => img.remove());
  });
});

describe('Performance - Benchmarking', () => {
  test('should measure and compare algorithm performance', () => {
    const testData = Array.from({ length: 1000 }, (_, i) => Math.random() * 1000);
    
    // Algorithm 1: Traditional for loop
    const bubbleSortTime = (() => {
      const data = [...testData];
      const startTime = performance.now();
      
      for (let i = 0; i < data.length - 1; i++) {
        for (let j = 0; j < data.length - i - 1; j++) {
          if (data[j] > data[j + 1]) {
            [data[j], data[j + 1]] = [data[j + 1], data[j]];
          }
        }
      }
      
      return performance.now() - startTime;
    })();
    
    // Algorithm 2: Built-in sort
    const nativeSortTime = (() => {
      const data = [...testData];
      const startTime = performance.now();
      
      data.sort((a, b) => a - b);
      
      return performance.now() - startTime;
    })();
    
    // Native sort should be much faster
    expect(nativeSortTime).toBeLessThan(bubbleSortTime);
    expect(nativeSortTime).toBeLessThan(50); // Should be very fast
    
    console.log(`Bubble sort: ${bubbleSortTime.toFixed(2)}ms, Native sort: ${nativeSortTime.toFixed(2)}ms`);
  });
});