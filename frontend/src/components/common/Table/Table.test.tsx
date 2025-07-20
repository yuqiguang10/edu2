import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Table from './Table';

const mockData = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'student' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'teacher' },
];

const mockColumns = [
  { key: 'name', title: '姓名', dataIndex: 'name' },
  { key: 'email', title: '邮箱', dataIndex: 'email' },
  { key: 'role', title: '角色', dataIndex: 'role' },
];

describe('Table', () => {
  it('renders table with data and columns', () => {
    render(<Table data={mockData} columns={mockColumns} />);
    
    expect(screen.getByText('姓名')).toBeInTheDocument();
    expect(screen.getByText('邮箱')).toBeInTheDocument();
    expect(screen.getByText('角色')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
  });

  it('renders empty state when no data', () => {
    render(<Table data={[]} columns={mockColumns} />);
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
  });

  it('renders custom empty state', () => {
    render(
      <Table 
        data={[]} 
        columns={mockColumns} 
        emptyText="没有找到相关数据"
      />
    );
    expect(screen.getByText('没有找到相关数据')).toBeInTheDocument();
  });

  it('calls onRowClick when row is clicked', () => {
    const handleRowClick = vi.fn();
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        onRowClick={handleRowClick}
      />
    );
    
    const firstRow = screen.getByText('John Doe').closest('tr');
    fireEvent.click(firstRow!);
    
    expect(handleRowClick).toHaveBeenCalledWith(mockData[0], 0);
  });

  it('renders with custom row key', () => {
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        rowKey="email"
      />
    );
    
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        className="custom-table"
      />
    );
    
    const table = screen.getByRole('table');
    expect(table).toHaveClass('custom-table');
  });

  it('renders with loading state', () => {
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        loading={true}
      />
    );
    
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders with pagination', () => {
    const pagination = {
      current: 1,
      pageSize: 10,
      total: 100,
      onChange: vi.fn(),
    };
    
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        pagination={pagination}
      />
    );
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('renders with selection', () => {
    const selectedRowKeys = [1];
    const onSelectionChange = vi.fn();
    
    render(
      <Table 
        data={mockData} 
        columns={mockColumns} 
        rowSelection={{
          selectedRowKeys,
          onChange: onSelectionChange,
        }}
      />
    );
    
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(3); // header + 2 rows
  });

  it('renders with custom cell renderer', () => {
    const customColumns = [
      ...mockColumns,
      {
        key: 'actions',
        title: '操作',
        render: (value: any, record: any) => (
          <button onClick={() => console.log(record.id)}>
            编辑
          </button>
        ),
      },
    ];
    
    render(<Table data={mockData} columns={customColumns} />);
    
    const editButtons = screen.getAllByText('编辑');
    expect(editButtons).toHaveLength(2);
  });

  it('renders with fixed columns', () => {
    const fixedColumns = [
      { ...mockColumns[0], fixed: 'left' as const },
      ...mockColumns.slice(1),
    ];
    
    render(<Table data={mockData} columns={fixedColumns} />);
    
    const table = screen.getByRole('table');
    expect(table).toHaveClass('table-fixed');
  });

  it('handles sorting', () => {
    const sortableColumns = [
      { ...mockColumns[0], sorter: true },
      ...mockColumns.slice(1),
    ];
    
    render(<Table data={mockData} columns={sortableColumns} />);
    
    const nameHeader = screen.getByText('姓名');
    expect(nameHeader).toHaveClass('cursor-pointer');
  });
}); 