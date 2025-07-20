import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Loading from './Loading';

describe('Loading', () => {
  it('renders with default props', () => {
    render(<Loading />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<Loading text="请稍候..." />);
    expect(screen.getByText('请稍候...')).toBeInTheDocument();
  });

  it('applies different sizes', () => {
    const { rerender } = render(<Loading size="sm" />);
    const loadingElement = screen.getByText('加载中...').parentElement;
    expect(loadingElement).toBeInTheDocument();

    rerender(<Loading size="md" />);
    expect(loadingElement).toBeInTheDocument();

    rerender(<Loading size="lg" />);
    expect(loadingElement).toBeInTheDocument();
  });

  it('renders fullscreen when fullScreen is true', () => {
    render(<Loading fullScreen />);
    const container = screen.getByText('加载中...').closest('div');
    expect(container).toHaveClass('fixed');
    expect(container).toHaveClass('inset-0');
  });

  it('applies custom className', () => {
    render(<Loading className="custom-loading" />);
    const container = screen.getByText('加载中...').parentElement;
    expect(container).toHaveClass('custom-loading');
  });

  it('renders without text when text is empty', () => {
    render(<Loading text="" />);
    expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
  });

  it('has correct structure', () => {
    render(<Loading />);
    const container = screen.getByText('加载中...').parentElement;
    expect(container).toHaveClass('flex');
    expect(container).toHaveClass('flex-col');
    expect(container).toHaveClass('items-center');
    expect(container).toHaveClass('justify-center');
  });
}); 