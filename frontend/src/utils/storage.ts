// src/utils/storage.ts
class Storage {
  private prefix = 'edu_platform_';

  private getKey(key: string): string {
    return this.prefix + key;
  }

  set(key: string, value: any): void {
    try {
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(this.getKey(key), serializedValue);
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(this.getKey(key));
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue || null;
    }
  }

  remove(key: string): void {
    localStorage.removeItem(this.getKey(key));
  }

  clear(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }

  // Session storage methods
  setSession(key: string, value: any): void {
    try {
      const serializedValue = JSON.stringify(value);
      sessionStorage.setItem(this.getKey(key), serializedValue);
    } catch (error) {
      console.error('Error saving to sessionStorage:', error);
    }
  }

  getSession<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = sessionStorage.getItem(this.getKey(key));
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('Error reading from sessionStorage:', error);
      return defaultValue || null;
    }
  }

  removeSession(key: string): void {
    sessionStorage.removeItem(this.getKey(key));
  }
}

export const storage = new Storage();
