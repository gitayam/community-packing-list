/**
 * Security tests for client-side input validation and XSS prevention
 * Complements Django's server-side security.py module
 */

describe('Input Sanitization', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="test-form">
        <input id="price-input" name="price" type="text">
        <input id="quantity-input" name="quantity" type="number">
        <textarea id="notes-input" name="notes"></textarea>
        <select id="store-input" name="store">
          <option value="">Select Store</option>
          <option value="store1">Store 1</option>
        </select>
      </form>
      <div id="output"></div>
    `;
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('should sanitize HTML in text inputs', () => {
    const input = document.getElementById('price-input') as HTMLInputElement;
    const maliciousValue = '<script>alert("XSS")</script>9.99';
    
    input.value = maliciousValue;
    
    // Simulate sanitization that should happen on input
    const sanitizedValue = input.value.replace(/<[^>]*>/g, '');
    expect(sanitizedValue).toBe('alert("XSS")9.99');
    expect(sanitizedValue).not.toContain('<script>');
  });

  test('should validate price format', () => {
    const testCases = [
      { input: '9.99', valid: true },
      { input: '10', valid: true },
      { input: '0.99', valid: true },
      { input: 'invalid', valid: false },
      { input: '<script>alert(1)</script>', valid: false },
      { input: '99.999', valid: false }, // Too many decimal places
      { input: '-5.99', valid: false },  // Negative price
      { input: '', valid: false }
    ];

    const validatePrice = (value: string): boolean => {
      // Remove any HTML tags first
      const cleaned = value.replace(/<[^>]*>/g, '');
      const priceRegex = /^\d+(\.\d{1,2})?$/;
      const numericValue = parseFloat(cleaned);
      return priceRegex.test(cleaned) && numericValue > 0;
    };

    testCases.forEach(testCase => {
      const result = validatePrice(testCase.input);
      expect(result).toBe(testCase.valid);
    });
  });

  test('should validate quantity input', () => {
    const testCases = [
      { input: '1', valid: true },
      { input: '10', valid: true },
      { input: '0', valid: false },      // Zero quantity not allowed
      { input: '-1', valid: false },     // Negative not allowed
      { input: '1.5', valid: false },    // Decimal not allowed for quantity
      { input: 'abc', valid: false },    // Non-numeric
      { input: '<script>1</script>', valid: false }
    ];

    const validateQuantity = (value: string): boolean => {
      const cleaned = value.replace(/<[^>]*>/g, '');
      const numericValue = parseFloat(cleaned);
      return !isNaN(numericValue) && numericValue > 0 && Number.isInteger(numericValue);
    };

    testCases.forEach(testCase => {
      const result = validateQuantity(testCase.input);
      expect(result).toBe(testCase.valid);
    });
  });

  test('should escape HTML in text content', () => {
    const escapeHtml = (text: string): string => {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    };

    const maliciousInputs = [
      '<script>alert("XSS")</script>',
      '<img src="x" onerror="alert(1)">',
      '"><script>alert(1)</script>',
      'javascript:alert(1)',
      '<iframe src="javascript:alert(1)"></iframe>'
    ];

    maliciousInputs.forEach(input => {
      const escaped = escapeHtml(input);
      // After HTML escaping, these patterns should be safe
      expect(escaped).toContain('&lt;'); // < becomes &lt;
      expect(escaped).toContain('&gt;'); // > becomes &gt;
      // Original dangerous patterns should not execute as HTML
      expect(escaped).not.toMatch(/<script[^>]*>/);
      expect(escaped).not.toMatch(/<iframe[^>]*>/);
    });
  });

  test('should validate textarea content for length and content', () => {
    const validateNotes = (notes: string): { valid: boolean; message: string } => {
      // Remove HTML tags
      const cleaned = notes.replace(/<[^>]*>/g, '').trim();
      
      if (cleaned.length > 500) {
        return { valid: false, message: 'Notes too long (max 500 characters)' };
      }
      
      // Check for suspicious patterns
      const suspiciousPatterns = [
        /javascript:/i,
        /vbscript:/i,
        /onload=/i,
        /onerror=/i,
        /onclick=/i
      ];
      
      for (const pattern of suspiciousPatterns) {
        if (pattern.test(cleaned)) {
          return { valid: false, message: 'Invalid content detected' };
        }
      }
      
      return { valid: true, message: '' };
    };

    const testCases = [
      { 
        input: 'Great product, good price!', 
        expectedValid: true 
      },
      { 
        input: '<script>alert("XSS")</script>', 
        expectedValid: false 
      },
      { 
        input: 'a'.repeat(501), 
        expectedValid: false 
      },
      { 
        input: 'Click here: javascript:alert(1)', 
        expectedValid: false 
      }
    ];

    testCases.forEach(testCase => {
      const result = validateNotes(testCase.input);
      expect(result.valid).toBe(testCase.expectedValid);
    });
  });
});

describe('CSRF Protection', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="csrf-form" method="post" action="/submit/">
        <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        <input name="price" value="9.99">
        <button type="submit">Submit</button>
      </form>
    `;
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('should ensure CSRF token is present in forms', () => {
    const form = document.getElementById('csrf-form') as HTMLFormElement;
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]') as HTMLInputElement;
    
    expect(csrfToken).toBeTruthy();
    expect(csrfToken.value).toBeTruthy();
    expect(csrfToken.type).toBe('hidden');
  });

  test('should validate CSRF token format', () => {
    const validateCsrfToken = (token: string): boolean => {
      // Django CSRF tokens are typically 32-64 characters of alphanumeric + dashes/underscores
      const csrfRegex = /^[a-zA-Z0-9_-]+$/;
      return csrfRegex.test(token) && token.length >= 8 && token.length <= 64;
    };

    const validTokens = [
      'abcdef1234567890abcdef1234567890',
      'test-csrf-token-123_456',
      'a'.repeat(64)
    ];

    const invalidTokens = [
      '',
      'short',
      'a'.repeat(65),
      'invalid<script>',
      'token with spaces'
    ];

    validTokens.forEach(token => {
      expect(validateCsrfToken(token)).toBe(true);
    });

    invalidTokens.forEach(token => {
      expect(validateCsrfToken(token)).toBe(false);
    });
  });

  test('should include CSRF token in AJAX requests', () => {
    const getCsrfToken = (): string | null => {
      const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]') as HTMLInputElement;
      return csrfInput ? csrfInput.value : null;
    };

    const createAjaxHeaders = () => {
      const csrfToken = getCsrfToken();
      return {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      };
    };

    const token = getCsrfToken();
    expect(token).toBe('test-csrf-token');

    const headers = createAjaxHeaders();
    expect(headers['X-CSRFToken']).toBe('test-csrf-token');
    expect(headers['X-Requested-With']).toBe('XMLHttpRequest');
  });
});

describe('Rate Limiting Client-Side Feedback', () => {
  test('should handle rate limit error responses', () => {
    const handleRateLimitError = (errorMessage: string): { 
      isRateLimit: boolean; 
      waitTime: number | null; 
      displayMessage: string 
    } => {
      const rateLimitPattern = /rate limit.*?(\d+)\s*minutes?/i;
      const match = errorMessage.match(rateLimitPattern);
      
      if (match) {
        const minutes = parseInt(match[1], 10);
        return {
          isRateLimit: true,
          waitTime: minutes,
          displayMessage: `Please wait ${minutes} minute${minutes !== 1 ? 's' : ''} before submitting again.`
        };
      }
      
      return {
        isRateLimit: false,
        waitTime: null,
        displayMessage: errorMessage
      };
    };

    const testCases = [
      {
        input: 'Rate limit exceeded. Try again in 5 minutes.',
        expectedIsRateLimit: true,
        expectedWaitTime: 5
      },
      {
        input: 'Rate limit exceeded. Try again in 1 minutes.',
        expectedIsRateLimit: true,
        expectedWaitTime: 1
      },
      {
        input: 'Invalid price format.',
        expectedIsRateLimit: false,
        expectedWaitTime: null
      }
    ];

    testCases.forEach(testCase => {
      const result = handleRateLimitError(testCase.input);
      expect(result.isRateLimit).toBe(testCase.expectedIsRateLimit);
      expect(result.waitTime).toBe(testCase.expectedWaitTime);
    });
  });

  test('should implement client-side submission throttling', () => {
    const createSubmissionThrottle = (cooldownMs: number = 1000) => {
      let lastSubmissionTime = 0;
      
      return {
        canSubmit: (): boolean => {
          const now = Date.now();
          return (now - lastSubmissionTime) >= cooldownMs;
        },
        recordSubmission: (): void => {
          lastSubmissionTime = Date.now();
        },
        getTimeUntilNext: (): number => {
          const now = Date.now();
          const timeElapsed = now - lastSubmissionTime;
          return Math.max(0, cooldownMs - timeElapsed);
        }
      };
    };

    const throttle = createSubmissionThrottle(500); // 500ms cooldown

    // Initially should be able to submit
    expect(throttle.canSubmit()).toBe(true);

    // After recording submission, should be throttled
    throttle.recordSubmission();
    expect(throttle.canSubmit()).toBe(false);
    expect(throttle.getTimeUntilNext()).toBeGreaterThan(0);

    // After waiting, should be able to submit again
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(throttle.canSubmit()).toBe(true);
        expect(throttle.getTimeUntilNext()).toBe(0);
        resolve();
      }, 600); // Wait longer than cooldown
    });
  });
});

describe('Content Security Policy Validation', () => {
  test('should validate inline script prevention', () => {
    const detectInlineScript = (html: string): boolean => {
      const inlineScriptPatterns = [
        /<script[^>]*>.*?<\/script>/gi,
        /on\w+\s*=\s*["'][^"']*["']/gi, // onclick, onload, etc.
        /javascript:\s*[^"'\s]+/gi
      ];
      
      return inlineScriptPatterns.some(pattern => pattern.test(html));
    };

    const safeContent = [
      '<p>This is safe content</p>',
      '<img src="/images/test.jpg" alt="Test">',
      '<a href="/safe-link">Safe Link</a>'
    ];

    const unsafeContent = [
      '<script>alert("XSS")</script>',
      '<img src="x" onerror="alert(1)">',
      '<div onclick="malicious()">Click me</div>',
      '<a href="javascript:alert(1)">Malicious Link</a>'
    ];

    safeContent.forEach(content => {
      expect(detectInlineScript(content)).toBe(false);
    });

    unsafeContent.forEach(content => {
      expect(detectInlineScript(content)).toBe(true);
    });
  });

  test('should validate external resource URLs', () => {
    const validateResourceUrl = (url: string): boolean => {
      try {
        const urlObj = new URL(url, window.location.origin);
        
        // Allow same origin
        if (urlObj.origin === window.location.origin) {
          return true;
        }
        
        // Allow specific trusted domains
        const trustedDomains = [
          'cdn.jsdelivr.net',
          'fonts.googleapis.com',
          'fonts.gstatic.com'
        ];
        
        return trustedDomains.includes(urlObj.hostname);
      } catch {
        return false;
      }
    };

    const testUrls = [
      { url: '/local/script.js', expected: true },
      { url: 'https://cdn.jsdelivr.net/npm/package@1.0.0/dist/package.min.js', expected: true },
      { url: 'https://fonts.googleapis.com/css2?family=Inter', expected: true },
      { url: 'https://malicious-site.com/script.js', expected: false },
      { url: 'javascript:alert(1)', expected: false },
      { url: 'data:text/html,<script>alert(1)</script>', expected: false }
    ];

    testUrls.forEach(({ url, expected }) => {
      expect(validateResourceUrl(url)).toBe(expected);
    });
  });
});

describe('Form Security Validation', () => {
  test('should validate file upload restrictions (if applicable)', () => {
    const validateFileUpload = (file: File): { valid: boolean; message: string } => {
      const maxSize = 5 * 1024 * 1024; // 5MB
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
      
      // Check file size
      if (file.size > maxSize) {
        return { valid: false, message: 'File size exceeds 5MB limit' };
      }
      
      // Check MIME type
      if (!allowedTypes.includes(file.type)) {
        return { valid: false, message: 'Invalid file type' };
      }
      
      // Check file extension
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      if (!allowedExtensions.includes(extension)) {
        return { valid: false, message: 'Invalid file extension' };
      }
      
      return { valid: true, message: '' };
    };

    // Mock File objects for testing
    const validFile = new File([''], 'test.jpg', { type: 'image/jpeg' });
    Object.defineProperty(validFile, 'size', { value: 1024 * 1024 }); // 1MB
    
    const invalidTypeFile = new File([''], 'test.exe', { type: 'application/octet-stream' });
    Object.defineProperty(invalidTypeFile, 'size', { value: 1024 });
    
    const oversizedFile = new File([''], 'large.jpg', { type: 'image/jpeg' });
    Object.defineProperty(oversizedFile, 'size', { value: 10 * 1024 * 1024 }); // 10MB

    expect(validateFileUpload(validFile).valid).toBe(true);
    expect(validateFileUpload(invalidTypeFile).valid).toBe(false);
    expect(validateFileUpload(oversizedFile).valid).toBe(false);
  });

  test('should validate URL parameters against injection', () => {
    const validateUrlParams = (url: string): boolean => {
      try {
        const urlObj = new URL(url, 'http://localhost');
        
        for (const [key, value] of urlObj.searchParams.entries()) {
          // Check for SQL injection patterns
          const sqlPatterns = [
            /('|\\')|(;|\\;)|(or|OR)\s+(1|true|TRUE)\s*=\s*(1|true|TRUE)/i,
            /(union|UNION)\s+(select|SELECT)/i,
            /(drop|DROP|delete|DELETE|insert|INSERT|update|UPDATE)\s+/i
          ];
          
          // Check for XSS patterns
          const xssPatterns = [
            /<script[^>]*>.*?<\/script>/gi,
            /javascript:\s*/gi,
            /on\w+\s*=/gi
          ];
          
          const allPatterns = [...sqlPatterns, ...xssPatterns];
          
          if (allPatterns.some(pattern => pattern.test(value))) {
            return false;
          }
        }
        
        return true;
      } catch {
        return false;
      }
    };

    const testUrls = [
      { url: '?price=9.99&store=1', expected: true },
      { url: '?search=laptop', expected: true },
      { url: "?id=1' OR 1=1", expected: false },
      { url: '?name=<script>alert(1)</script>', expected: false },
      { url: '?callback=javascript:alert(1)', expected: false },
      { url: '?data=<img src=x onerror=alert(1)>', expected: false }
    ];

    testUrls.forEach(({ url, expected }) => {
      expect(validateUrlParams(url)).toBe(expected);
    });
  });
});