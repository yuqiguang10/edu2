import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AIChat from './AIChat';

// Mock the AI API
vi.mock('@/api/modules/ai', () => ({
  aiAPI: {
    chat: vi.fn(),
  },
}));

// Mock the auth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

describe('AIChat', () => {
  const mockAiAPI = {
    chat: vi.fn(),
  };
  
  const mockUseAuth = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mocks
    mockUseAuth.mockReturnValue({
      user: { id: 1, username: 'testuser', roles: ['student'] },
      isAuthenticated: true,
    });
    
    vi.doMock('@/api/modules/ai', () => ({
      aiAPI: mockAiAPI,
    }));
    
    vi.doMock('@/hooks/useAuth', () => ({
      useAuth: mockUseAuth,
    }));
  });

  it('renders chat interface', () => {
    render(<AIChat />);
    expect(screen.getByPlaceholderText('输入您的问题...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /发送/i })).toBeInTheDocument();
  });

  it('displays welcome message', () => {
    render(<AIChat />);
    expect(screen.getByText(/欢迎使用AI助手/i)).toBeInTheDocument();
  });

  it('allows user to type message', () => {
    render(<AIChat />);
    const input = screen.getByPlaceholderText('输入您的问题...');
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    expect(input).toHaveValue('Hello AI');
  });

  it('sends message when send button is clicked', async () => {
    mockAiAPI.chat.mockResolvedValue({
      data: {
        message: 'Hello! How can I help you?',
        suggestions: ['Tell me more', 'Ask another question'],
      },
    });

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(mockAiAPI.chat).toHaveBeenCalledWith({
        message: 'Hello AI',
        context: { role: 'student' },
        history: [],
      });
    });
  });

  it('sends message when Enter key is pressed', async () => {
    mockAiAPI.chat.mockResolvedValue({
      data: {
        message: 'Hello! How can I help you?',
        suggestions: ['Tell me more', 'Ask another question'],
      },
    });

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(mockAiAPI.chat).toHaveBeenCalled();
    });
  });

  it('displays loading state while sending message', async () => {
    mockAiAPI.chat.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    expect(screen.getByText('发送中...')).toBeInTheDocument();
  });

  it('displays AI response', async () => {
    const mockResponse = {
      data: {
        message: 'Hello! How can I help you?',
        suggestions: ['Tell me more', 'Ask another question'],
      },
    };
    
    mockAiAPI.chat.mockResolvedValue(mockResponse);

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
    });
  });

  it('displays suggestions', async () => {
    const mockResponse = {
      data: {
        message: 'Hello! How can I help you?',
        suggestions: ['Tell me more', 'Ask another question'],
      },
    };
    
    mockAiAPI.chat.mockResolvedValue(mockResponse);

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Tell me more')).toBeInTheDocument();
      expect(screen.getByText('Ask another question')).toBeInTheDocument();
    });
  });

  it('handles suggestion clicks', async () => {
    const mockResponse = {
      data: {
        message: 'Hello! How can I help you?',
        suggestions: ['Tell me more', 'Ask another question'],
      },
    };
    
    mockAiAPI.chat.mockResolvedValue(mockResponse);

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      const suggestion = screen.getByText('Tell me more');
      fireEvent.click(suggestion);
    });
    
    await waitFor(() => {
      expect(mockAiAPI.chat).toHaveBeenCalledWith({
        message: 'Tell me more',
        context: { role: 'student' },
        history: expect.any(Array),
      });
    });
  });

  it('handles error responses', async () => {
    mockAiAPI.chat.mockRejectedValue(new Error('API Error'));

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/抱歉，出现了错误/i)).toBeInTheDocument();
    });
  });

  it('clears input after sending message', async () => {
    mockAiAPI.chat.mockResolvedValue({
      data: {
        message: 'Hello! How can I help you?',
        suggestions: [],
      },
    });

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('prevents sending empty messages', () => {
    render(<AIChat />);
    
    const sendButton = screen.getByRole('button', { name: /发送/i });
    fireEvent.click(sendButton);
    
    expect(mockAiAPI.chat).not.toHaveBeenCalled();
  });

  it('displays user role in context', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, username: 'teacher', roles: ['teacher'] },
      isAuthenticated: true,
    });

    mockAiAPI.chat.mockResolvedValue({
      data: {
        message: 'Hello teacher!',
        suggestions: [],
      },
    });

    render(<AIChat />);
    
    const input = screen.getByPlaceholderText('输入您的问题...');
    const sendButton = screen.getByRole('button', { name: /发送/i });
    
    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(mockAiAPI.chat).toHaveBeenCalledWith({
        message: 'Hello AI',
        context: { role: 'teacher' },
        history: [],
      });
    });
  });
}); 