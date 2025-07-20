// src/components/common/Table/Table.tsx
import React, { ReactNode } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/helpers';
import Button from '../Button/Button';

export interface Column<T = any> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  render?: (value: any, record: T, index: number) => ReactNode;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

export interface TableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
  rowKey?: keyof T | ((record: T) => string);
  onRow?: (record: T, index: number) => {
    onClick?: () => void;
    onDoubleClick?: () => void;
  };
  className?: string;
  emptyText?: string;
}

const Table = <T extends Record<string, any>>({
  columns,
  data,
  loading = false,
  pagination,
  rowKey = 'id',
  onRow,
  className,
  emptyText = '暂无数��',
}: TableProps<T>) => {
  const getRowKey = (record: T, index: number): string => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return String(record[rowKey] || index);
  };

  const handlePageChange = (page: number) => {
    if (pagination) {
      pagination.onChange(page, pagination.pageSize);
    }
  };

  const renderPagination = () => {
    if (!pagination) return null;

    const { current, pageSize, total } = pagination;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (current - 1) * pageSize + 1;
    const endIndex = Math.min(current * pageSize, total);

    return (
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
        <div className="text-sm text-gray-700">
          显示 {startIndex} 到 {endIndex} 条，共 {total} 条
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            disabled={current <= 1}
            onClick={() => handlePageChange(current - 1)}
            icon={<ChevronLeft size={16} />}
          >
            上一页
          </Button>
          
          <span className="text-sm text-gray-700">
            第 {current} 页，共 {totalPages} 页
          </span>
          
          <Button
            variant="outline"
            size="sm"
            disabled={current >= totalPages}
            onClick={() => handlePageChange(current + 1)}
            iconPosition="right"
            icon={<ChevronRight size={16} />}
          >
            下一页
          </Button>
        </div>
      </div>
    );
  };

  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg overflow-hidden', className)}>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn(
                    'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider',
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right'
                  )}
                  style={{ width: column.width }}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-4 text-center">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                    <span className="ml-2 text-gray-500">加载中...</span>
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((record, index) => {
                const rowProps = onRow?.(record, index);
                return (
                  <tr
                    key={getRowKey(record, index)}
                    className={cn(
                      'hover:bg-gray-50 transition-colors',
                      rowProps?.onClick && 'cursor-pointer'
                    )}
                    onClick={rowProps?.onClick}
                    onDoubleClick={rowProps?.onDoubleClick}
                  >
                    {columns.map((column) => {
                      const value = column.dataIndex ? record[column.dataIndex] : undefined;
                      const cellContent = column.render
                        ? column.render(value, record, index)
                        : value;

                      return (
                        <td
                          key={column.key}
                          className={cn(
                            'px-6 py-4 text-sm text-gray-900',
                            column.align === 'center' && 'text-center',
                            column.align === 'right' && 'text-right'
                          )}
                        >
                          {cellContent}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      
      {renderPagination()}
    </div>
  );
};

export default Table;
