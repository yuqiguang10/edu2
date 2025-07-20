// src/hooks/useApi.ts
import { useState, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  immediate?: boolean;
}

export const useApi = <T = any>(
  apiFunction: (...args: any[]) => Promise<any>,
  options: UseApiOptions = {}
) => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const { onSuccess, onError, immediate = false } = options;

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        
        const response = await apiFunction(...args);
        const data = response.data || response;
        
        setState({ data, loading: false, error: null });
        
        if (onSuccess) {
          onSuccess(data);
        }
        
        return data;
      } catch (error: any) {
        const errorMessage = error.message || '请求失败';
        setState(prev => ({ ...prev, loading: false, error: errorMessage }));
        
        if (onError) {
          onError(error);
        }
        
        throw error;
      }
    },
    [apiFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  // 立即执行
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return {
    ...state,
    execute,
    reset,
  };
};
