import { TypedEventEmitter, fadeIn, fadeOut } from '../utils';

interface ModalEvents extends Record<string, any[]> {
  open: [];
  close: [];
  confirm: [data?: any];
  cancel: [];
}

export interface ModalOptions {
  title?: string;
  content?: string | HTMLElement;
  showCloseButton?: boolean;
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  animation?: boolean;
  buttons?: ModalButton[];
}

export interface ModalButton {
  text: string;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  action?: 'confirm' | 'cancel' | 'custom';
  handler?: () => void | Promise<void>;
}

export class Modal extends TypedEventEmitter<ModalEvents> {
  private element!: HTMLElement;
  private backdrop!: HTMLElement;
  private content!: HTMLElement;
  private isOpen = false;
  private options: Required<ModalOptions>;

  constructor(options: ModalOptions = {}) {
    super();
    
    this.options = {
      title: '',
      content: '',
      showCloseButton: true,
      closeOnBackdrop: true,
      closeOnEscape: true,
      size: 'md',
      animation: true,
      buttons: [],
      ...options,
    };

    this.createElement();
    this.bindEvents();
  }

  private createElement(): void {
    // Create backdrop
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal';
    this.backdrop.setAttribute('role', 'dialog');
    this.backdrop.setAttribute('aria-modal', 'true');
    this.backdrop.setAttribute('aria-hidden', 'true');

    // Create modal content container
    this.content = document.createElement('div');
    this.content.className = `modal__content modal__content--${this.options.size}`;

    // Create header
    if (this.options.title || this.options.showCloseButton) {
      const header = this.createHeader();
      this.content.appendChild(header);
    }

    // Create body
    const body = this.createBody();
    this.content.appendChild(body);

    // Create footer if buttons are provided
    if (this.options.buttons.length > 0) {
      const footer = this.createFooter();
      this.content.appendChild(footer);
    }

    this.backdrop.appendChild(this.content);
    this.element = this.backdrop;
  }

  private createHeader(): HTMLElement {
    const header = document.createElement('div');
    header.className = 'modal__header';

    if (this.options.title) {
      const title = document.createElement('h3');
      title.className = 'modal__title';
      title.textContent = this.options.title;
      title.id = this.generateId('title');
      this.backdrop.setAttribute('aria-labelledby', title.id);
      header.appendChild(title);
    }

    if (this.options.showCloseButton) {
      const closeButton = document.createElement('button');
      closeButton.className = 'modal__close';
      closeButton.setAttribute('aria-label', 'Close modal');
      closeButton.innerHTML = '×';
      closeButton.addEventListener('click', () => this.close());
      header.appendChild(closeButton);
    }

    return header;
  }

  private createBody(): HTMLElement {
    const body = document.createElement('div');
    body.className = 'modal__body';
    body.id = this.generateId('body');
    this.backdrop.setAttribute('aria-describedby', body.id);

    if (typeof this.options.content === 'string') {
      body.innerHTML = this.options.content;
    } else if (this.options.content instanceof HTMLElement) {
      body.appendChild(this.options.content);
    }

    return body;
  }

  private createFooter(): HTMLElement {
    const footer = document.createElement('div');
    footer.className = 'modal__footer';

    this.options.buttons.forEach(buttonConfig => {
      const button = document.createElement('button');
      button.className = `btn btn--${buttonConfig.variant || 'secondary'}`;
      button.textContent = buttonConfig.text;

      button.addEventListener('click', async () => {
        if (buttonConfig.handler) {
          await buttonConfig.handler();
        }

        switch (buttonConfig.action) {
          case 'confirm':
            this.emit('confirm');
            this.close();
            break;
          case 'cancel':
            this.emit('cancel');
            this.close();
            break;
          default:
            // Custom action, don't auto-close
            break;
        }
      });

      footer.appendChild(button);
    });

    return footer;
  }

  private bindEvents(): void {
    // Close on backdrop click
    if (this.options.closeOnBackdrop) {
      this.backdrop.addEventListener('click', (e) => {
        if (e.target === this.backdrop) {
          this.close();
        }
      });
    }

    // Close on escape key
    if (this.options.closeOnEscape) {
      document.addEventListener('keydown', this.handleEscapeKey.bind(this));
    }
  }

  private handleEscapeKey(e: KeyboardEvent): void {
    if (e.key === 'Escape' && this.isOpen) {
      this.close();
    }
  }

  private generateId(suffix: string): string {
    return `modal-${Math.random().toString(36).substr(2, 9)}-${suffix}`;
  }

  async open(): Promise<void> {
    if (this.isOpen) return;

    document.body.appendChild(this.element);
    document.body.style.overflow = 'hidden';
    
    this.isOpen = true;
    this.backdrop.setAttribute('aria-hidden', 'false');

    if (this.options.animation) {
      this.backdrop.classList.add('modal--open');
      await fadeIn(this.backdrop);
    } else {
      this.backdrop.style.display = 'flex';
    }

    // Focus management
    const firstFocusable = this.content.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as HTMLElement;
    
    if (firstFocusable) {
      firstFocusable.focus();
    }

    this.emit('open');
  }

  async close(): Promise<void> {
    if (!this.isOpen) return;

    this.isOpen = false;
    this.backdrop.setAttribute('aria-hidden', 'true');

    if (this.options.animation) {
      await fadeOut(this.backdrop);
      this.backdrop.classList.remove('modal--open');
    }

    document.body.removeChild(this.element);
    document.body.style.overflow = '';

    this.emit('close');
  }

  setContent(content: string | HTMLElement): void {
    const body = this.content.querySelector('.modal__body');
    if (body) {
      if (typeof content === 'string') {
        body.innerHTML = content;
      } else {
        body.innerHTML = '';
        body.appendChild(content);
      }
    }
  }

  setTitle(title: string): void {
    const titleElement = this.content.querySelector('.modal__title');
    if (titleElement) {
      titleElement.textContent = title;
    }
  }

  destroy(): void {
    if (this.isOpen) {
      this.close();
    }
    
    document.removeEventListener('keydown', this.handleEscapeKey.bind(this));
    this.clear();
  }

  // Static factory methods
  static alert(message: string, title = 'Alert'): Promise<void> {
    return new Promise(resolve => {
      const modal = new Modal({
        title,
        content: message,
        buttons: [
          {
            text: 'OK',
            variant: 'primary',
            action: 'confirm',
          },
        ],
      });

      modal.on('confirm', () => {
        modal.destroy();
        resolve();
      });

      modal.open();
    });
  }

  static confirm(message: string, title = 'Confirm'): Promise<boolean> {
    return new Promise(resolve => {
      const modal = new Modal({
        title,
        content: message,
        buttons: [
          {
            text: 'Cancel',
            variant: 'secondary',
            action: 'cancel',
          },
          {
            text: 'Confirm',
            variant: 'primary',
            action: 'confirm',
          },
        ],
      });

      modal.on('confirm', () => {
        modal.destroy();
        resolve(true);
      });

      modal.on('cancel', () => {
        modal.destroy();
        resolve(false);
      });

      modal.open();
    });
  }
} 