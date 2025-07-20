import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Modal from './Modal';

describe('Modal', () => {
  it('renders modal when open is true', () => {
    render(
      <Modal open={true} onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render modal when open is false', () => {
    render(
      <Modal open={false} onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(
      <Modal open={true} onClose={handleClose}>
        <div>Modal content</div>
      </Modal>
    );
    
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('renders with title', () => {
    render(
      <Modal open={true} onClose={vi.fn()} title="Test Modal">
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(
      <Modal open={true} onClose={vi.fn()} className="custom-modal">
        <div>Modal content</div>
      </Modal>
    );
    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('custom-modal');
  });
}); 