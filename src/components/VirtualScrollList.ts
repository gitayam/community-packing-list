/**
 * Virtual scrolling component for efficient rendering of large item lists.
 * Only renders visible items to maintain performance with thousands of items.
 */

interface VirtualScrollItem {
  id: string | number;
  height?: number;
  data: any;
}

interface VirtualScrollOptions {
  itemHeight: number;
  containerHeight: number;
  visibleItems?: number;
  buffer?: number;
  scrollThreshold?: number;
}

export class VirtualScrollList {
  private container: HTMLElement;
  private scrollContainer: HTMLElement;
  private contentContainer: HTMLElement;
  private options: VirtualScrollOptions;
  private items: VirtualScrollItem[] = [];
  private visibleStartIndex = 0;
  private visibleEndIndex = 0;
  private renderCallback?: (item: VirtualScrollItem, index: number) => HTMLElement;
  private scrollTimeout?: number;
  private observer?: IntersectionObserver;

  constructor(
    containerId: string,
    options: VirtualScrollOptions,
    renderCallback: (item: VirtualScrollItem, index: number) => HTMLElement
  ) {
    const container = document.getElementById(containerId);
    if (!container) {
      throw new Error(`Container with id '${containerId}' not found`);
    }

    this.container = container;
    this.options = {
      visibleItems: Math.ceil(options.containerHeight / options.itemHeight) + 2,
      buffer: 5,
      scrollThreshold: 100,
      ...options,
    };
    this.renderCallback = renderCallback;

    this.initializeDOM();
    this.setupEventListeners();
    this.setupIntersectionObserver();
  }

  private initializeDOM(): void {
    this.container.innerHTML = `
      <div class="virtual-scroll-container" style="height: ${this.options.containerHeight}px; overflow-y: auto; position: relative;">
        <div class="virtual-scroll-spacer" style="height: 0px;"></div>
        <div class="virtual-scroll-content" style="transform: translateY(0px);"></div>
      </div>
    `;

    this.scrollContainer = this.container.querySelector('.virtual-scroll-container') as HTMLElement;
    this.contentContainer = this.container.querySelector('.virtual-scroll-content') as HTMLElement;
  }

  private setupEventListeners(): void {
    this.scrollContainer.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
    
    // Handle window resize
    window.addEventListener('resize', this.handleResize.bind(this));
  }

  private setupIntersectionObserver(): void {
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const element = entry.target as HTMLElement;
          if (entry.isIntersecting) {
            element.style.opacity = '1';
          } else {
            element.style.opacity = '0.1';
          }
        });
      },
      {
        root: this.scrollContainer,
        rootMargin: '50px',
        threshold: 0.1,
      }
    );
  }

  private handleScroll(): void {
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }

    this.scrollTimeout = window.setTimeout(() => {
      this.updateVisibleItems();
    }, 16); // 60fps
  }

  private handleResize(): void {
    this.updateVisibleItems();
  }

  private updateVisibleItems(): void {
    const scrollTop = this.scrollContainer.scrollTop;
    const containerHeight = this.options.containerHeight;
    
    // Calculate visible range with buffer
    const startIndex = Math.max(0, Math.floor(scrollTop / this.options.itemHeight) - (this.options.buffer || 0));
    const endIndex = Math.min(
      this.items.length - 1,
      Math.floor((scrollTop + containerHeight) / this.options.itemHeight) + (this.options.buffer || 0)
    );

    // Only re-render if the visible range changed significantly
    if (Math.abs(startIndex - this.visibleStartIndex) > 2 || Math.abs(endIndex - this.visibleEndIndex) > 2) {
      this.visibleStartIndex = startIndex;
      this.visibleEndIndex = endIndex;
      this.renderVisibleItems();
    }
  }

  private renderVisibleItems(): void {
    if (!this.renderCallback) return;

    // Clear existing content
    this.contentContainer.innerHTML = '';
    
    // Update spacer height to maintain scroll position
    const spacer = this.container.querySelector('.virtual-scroll-spacer') as HTMLElement;
    const totalHeight = this.items.length * this.options.itemHeight;
    const offsetY = this.visibleStartIndex * this.options.itemHeight;
    
    spacer.style.height = `${totalHeight}px`;
    this.contentContainer.style.transform = `translateY(${offsetY}px)`;

    // Render visible items
    const fragment = document.createDocumentFragment();
    for (let i = this.visibleStartIndex; i <= this.visibleEndIndex && i < this.items.length; i++) {
      const itemElement = this.renderCallback(this.items[i], i);
      itemElement.style.height = `${this.options.itemHeight}px`;
      itemElement.style.minHeight = `${this.options.itemHeight}px`;
      itemElement.dataset.virtualIndex = i.toString();
      
      // Add to intersection observer
      if (this.observer) {
        this.observer.observe(itemElement);
      }
      
      fragment.appendChild(itemElement);
    }
    
    this.contentContainer.appendChild(fragment);

    // Dispatch custom event for analytics
    this.container.dispatchEvent(new CustomEvent('virtualScrollRender', {
      detail: {
        startIndex: this.visibleStartIndex,
        endIndex: this.visibleEndIndex,
        totalItems: this.items.length,
        renderedItems: this.visibleEndIndex - this.visibleStartIndex + 1,
      }
    }));
  }

  public setItems(items: VirtualScrollItem[]): void {
    this.items = items;
    this.visibleStartIndex = 0;
    this.visibleEndIndex = Math.min(this.options.visibleItems || 10, items.length - 1);
    this.renderVisibleItems();
  }

  public addItems(newItems: VirtualScrollItem[]): void {
    this.items.push(...newItems);
    
    // Re-render if new items are in visible range
    if (this.visibleEndIndex >= this.items.length - newItems.length) {
      this.updateVisibleItems();
    }
  }

  public removeItem(itemId: string | number): void {
    const index = this.items.findIndex(item => item.id === itemId);
    if (index !== -1) {
      this.items.splice(index, 1);
      this.updateVisibleItems();
    }
  }

  public updateItem(itemId: string | number, newData: any): void {
    const item = this.items.find(item => item.id === itemId);
    if (item) {
      item.data = { ...item.data, ...newData };
      
      // Re-render if item is currently visible
      const index = this.items.indexOf(item);
      if (index >= this.visibleStartIndex && index <= this.visibleEndIndex) {
        this.renderVisibleItems();
      }
    }
  }

  public scrollToItem(itemId: string | number, behavior: ScrollBehavior = 'smooth'): void {
    const index = this.items.findIndex(item => item.id === itemId);
    if (index !== -1) {
      const scrollTop = index * this.options.itemHeight;
      this.scrollContainer.scrollTo({
        top: scrollTop,
        behavior,
      });
    }
  }

  public scrollToTop(behavior: ScrollBehavior = 'smooth'): void {
    this.scrollContainer.scrollTo({
      top: 0,
      behavior,
    });
  }

  public getVisibleItems(): VirtualScrollItem[] {
    return this.items.slice(this.visibleStartIndex, this.visibleEndIndex + 1);
  }

  public getTotalHeight(): number {
    return this.items.length * this.options.itemHeight;
  }

  public getScrollProgress(): number {
    const maxScroll = this.getTotalHeight() - this.options.containerHeight;
    return maxScroll > 0 ? this.scrollContainer.scrollTop / maxScroll : 0;
  }

  public destroy(): void {
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }

    if (this.observer) {
      this.observer.disconnect();
    }

    this.scrollContainer.removeEventListener('scroll', this.handleScroll.bind(this));
    window.removeEventListener('resize', this.handleResize.bind(this));
  }
}

// Performance monitoring utilities
export class VirtualScrollPerformanceMonitor {
  private renderTimes: number[] = [];
  private scrollEvents = 0;
  private startTime = Date.now();

  public recordRenderTime(renderTime: number): void {
    this.renderTimes.push(renderTime);
    
    // Keep only last 100 measurements
    if (this.renderTimes.length > 100) {
      this.renderTimes.shift();
    }
  }

  public incrementScrollEvents(): void {
    this.scrollEvents++;
  }

  public getAverageRenderTime(): number {
    if (this.renderTimes.length === 0) return 0;
    return this.renderTimes.reduce((sum, time) => sum + time, 0) / this.renderTimes.length;
  }

  public getScrollEventsPerSecond(): number {
    const elapsedSeconds = (Date.now() - this.startTime) / 1000;
    return this.scrollEvents / elapsedSeconds;
  }

  public getPerformanceReport(): {
    avgRenderTime: number;
    scrollEventsPerSecond: number;
    totalScrollEvents: number;
    renderTimeP95: number;
  } {
    const sortedRenderTimes = [...this.renderTimes].sort((a, b) => a - b);
    const p95Index = Math.floor(sortedRenderTimes.length * 0.95);
    
    return {
      avgRenderTime: this.getAverageRenderTime(),
      scrollEventsPerSecond: this.getScrollEventsPerSecond(),
      totalScrollEvents: this.scrollEvents,
      renderTimeP95: sortedRenderTimes[p95Index] || 0,
    };
  }

  public reset(): void {
    this.renderTimes = [];
    this.scrollEvents = 0;
    this.startTime = Date.now();
  }
}