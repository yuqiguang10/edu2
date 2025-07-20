import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Input from './Input';

describe('Input', () => {
  it('renders input with placeholder', () => {
    render(<Input placeholder="Enter your name" />);
    expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument();
  });

  it('renders input with label', () => {
    render(<Input label="Username" />);
    expect(screen.getByText('Username')).toBeInTheDocument();
  });

  it('calls onChange when value changes', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'test' } });
    
    expect(handleChange).toHaveBeenCalledWith('test');
  });

  it('displays error message', () => {
    render(<Input error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('applies error styles when error is present', () => {
    render(<Input error="Error message" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-error-500');
  });

  it('renders with icon', () => {
    const icon = <span data-testid="icon">🔍</span>;
    render(<Input icon={icon} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('renders with right icon', () => {
    const icon = <span data-testid="icon">✓</span>;
    render(<Input rightIcon={icon} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('applies different sizes', () => {
    const { rerender } = render(<Input size="sm" />);
    let input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-3');

    rerender(<Input size="md" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-4');

    rerender(<Input size="lg" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-6');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('applies custom className', () => {
    render(<Input className="custom-input" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('custom-input');
  });

  it('forwards ref correctly', () => {
    const ref = vi.fn();
    render(<Input ref={ref} />);
    expect(ref).toHaveBeenCalled();
  });

  it('renders with help text', () => {
    render(<Input helpText="This is help text" />);
    expect(screen.getByText('This is help text')).toBeInTheDocument();
  });

  it('renders with required indicator', () => {
    render(<Input label="Username" required />);
    const label = screen.getByText('Username');
    expect(label).toHaveTextContent('*');
  });

  it('handles different input types', () => {
    const { rerender } = render(<Input type="email" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'password');

    rerender(<Input type="number" />);
    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
  });
}); 