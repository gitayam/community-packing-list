/**
 * Infrastructure tests to verify Jest and TypeScript setup is working
 */

describe('Test Infrastructure', () => {
  test('Jest is working', () => {
    expect(true).toBe(true);
  });

  test('TypeScript compilation works', () => {
    const testObject: { name: string; count: number } = {
      name: 'test',
      count: 42
    };
    
    expect(testObject.name).toBe('test');
    expect(testObject.count).toBe(42);
  });

  test('ES6 features work', () => {
    const arr = [1, 2, 3, 4, 5];
    const doubled = arr.map(x => x * 2);
    const evens = arr.filter(x => x % 2 === 0);
    
    expect(doubled).toEqual([2, 4, 6, 8, 10]);
    expect(evens).toEqual([2, 4]);
  });

  test('Async/await works', async () => {
    const asyncFunction = async (): Promise<string> => {
      return Promise.resolve('async result');
    };
    
    const result = await asyncFunction();
    expect(result).toBe('async result');
  });

  test('Promises work', () => {
    return Promise.resolve('promise result').then(result => {
      expect(result).toBe('promise result');
    });
  });
});

describe('DOM Environment', () => {
  test('document is available', () => {
    expect(document).toBeDefined();
  });

  test('window is available', () => {
    expect(window).toBeDefined();
  });

  test('can create elements', () => {
    const div = document.createElement('div');
    div.textContent = 'test content';
    
    expect(div.tagName).toBe('DIV');
    expect(div.textContent).toBe('test content');
  });

  test('can query elements', () => {
    document.body.innerHTML = '<div id="test">Test</div>';
    
    const element = document.getElementById('test');
    expect(element).toBeTruthy();
    expect(element?.textContent).toBe('Test');
    
    // Clean up
    document.body.innerHTML = '';
  });
});

describe('Mock Functions', () => {
  test('localStorage mock works', () => {
    expect(localStorage.setItem).toBeDefined();
    expect(jest.isMockFunction(localStorage.setItem)).toBe(true);
    
    localStorage.setItem('test-key', 'test-value');
    expect(localStorage.setItem).toHaveBeenCalledWith('test-key', 'test-value');
  });

  test('console mock works', () => {
    expect(jest.isMockFunction(console.log)).toBe(true);
    
    console.log('test message');
    expect(console.log).toHaveBeenCalledWith('test message');
  });

  test('fetch mock works', () => {
    expect(global.fetch).toBeDefined();
    expect(jest.isMockFunction(global.fetch)).toBe(true);
  });
});

describe('Error Handling', () => {
  test('can catch errors', () => {
    const errorFunction = () => {
      throw new Error('Test error');
    };
    
    expect(errorFunction).toThrow('Test error');
  });

  test('can handle async errors', async () => {
    const asyncErrorFunction = async () => {
      throw new Error('Async error');
    };
    
    await expect(asyncErrorFunction()).rejects.toThrow('Async error');
  });
});

describe('Jest Matchers', () => {
  test('basic matchers work', () => {
    expect(42).toBe(42);
    expect('hello').toBe('hello');
    expect(true).toBe(true);
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect('hello world').toContain('world');
  });

  test('object matchers work', () => {
    const obj = { a: 1, b: 2 };
    expect(obj).toEqual({ a: 1, b: 2 });
    expect(obj).toHaveProperty('a');
    expect(obj).toHaveProperty('a', 1);
  });

  test('array matchers work', () => {
    const arr = ['a', 'b', 'c'];
    expect(arr).toHaveLength(3);
    expect(arr).toContain('b');
    expect(arr).toEqual(expect.arrayContaining(['a', 'c']));
  });
});