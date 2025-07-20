import { describe, it, expect } from 'vitest';
import { cn, formatDate, formatDateTime, formatDuration, truncateText, debounce, throttle } from './helpers';

describe('helpers', () => {
  describe('cn', () => {
    it('combines class names correctly', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2');
    });

    it('handles conditional classes', () => {
      expect(cn('base', { conditional: true, hidden: false })).toBe('base conditional');
    });

    it('filters out falsy values', () => {
      expect(cn('base', null, undefined, false, 0, 'valid')).toBe('base valid');
    });

    it('handles arrays', () => {
      expect(cn('base', ['class1', 'class2'])).toBe('base class1 class2');
    });

    it('handles nested arrays', () => {
      expect(cn('base', [['class1'], 'class2'])).toBe('base class1 class2');
    });
  });

  describe('formatDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2023-12-25T10:30:00');
      expect(formatDate(date)).toBe('2023-12-25');
    });

    it('handles string date', () => {
      expect(formatDate('2023-12-25T10:30:00')).toBe('2023-12-25');
    });

    it('handles timestamp', () => {
      const timestamp = new Date('2023-12-25T10:30:00').getTime();
      expect(formatDate(timestamp)).toBe('2023-12-25');
    });

    it('returns empty string for invalid date', () => {
      expect(formatDate('invalid-date')).toBe('');
    });
  });

  describe('formatDateTime', () => {
    it('formats date and time correctly', () => {
      const date = new Date('2023-12-25T10:30:00');
      expect(formatDateTime(date)).toBe('2023-12-25 10:30');
    });

    it('handles string date', () => {
      expect(formatDateTime('2023-12-25T10:30:00')).toBe('2023-12-25 10:30');
    });

    it('returns empty string for invalid date', () => {
      expect(formatDateTime('invalid-date')).toBe('');
    });
  });

  describe('formatDuration', () => {
    it('formats seconds correctly', () => {
      expect(formatDuration(65)).toBe('1分5秒');
    });

    it('formats minutes correctly', () => {
      expect(formatDuration(3661)).toBe('1小时1分1秒');
    });

    it('formats hours correctly', () => {
      expect(formatDuration(7325)).toBe('2小时2分5秒');
    });

    it('handles zero duration', () => {
      expect(formatDuration(0)).toBe('0秒');
    });

    it('handles negative duration', () => {
      expect(formatDuration(-30)).toBe('0秒');
    });
  });

  describe('truncateText', () => {
    it('truncates long text', () => {
      const longText = 'This is a very long text that should be truncated';
      expect(truncateText(longText, 20)).toBe('This is a very long...');
    });

    it('does not truncate short text', () => {
      const shortText = 'Short text';
      expect(truncateText(shortText, 20)).toBe('Short text');
    });

    it('handles empty string', () => {
      expect(truncateText('', 10)).toBe('');
    });

    it('handles null and undefined', () => {
      expect(truncateText(null as any, 10)).toBe('');
      expect(truncateText(undefined as any, 10)).toBe('');
    });

    it('uses custom suffix', () => {
      const longText = 'This is a very long text';
      expect(truncateText(longText, 10, '***')).toBe('This is a***');
    });
  });

  describe('debounce', () => {
    it('debounces function calls', async () => {
      const mockFn = vi.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      expect(mockFn).not.toHaveBeenCalled();

      await new Promise(resolve => setTimeout(resolve, 150));
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('passes arguments correctly', async () => {
      const mockFn = vi.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn('arg1', 'arg2');

      await new Promise(resolve => setTimeout(resolve, 150));
      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
    });
  });

  describe('throttle', () => {
    it('throttles function calls', async () => {
      const mockFn = vi.fn();
      const throttledFn = throttle(mockFn, 100);

      throttledFn();
      throttledFn();
      throttledFn();

      expect(mockFn).toHaveBeenCalledTimes(1);

      await new Promise(resolve => setTimeout(resolve, 150));
      throttledFn();
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('passes arguments correctly', async () => {
      const mockFn = vi.fn();
      const throttledFn = throttle(mockFn, 100);

      throttledFn('arg1', 'arg2');

      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
    });
  });
}); 