import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Chart from './Chart';

// Mock Recharts components
vi.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: ({ dataKey }: any) => <div data-testid="line" data-key={dataKey} />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: ({ dataKey }: any) => <div data-testid="bar" data-key={dataKey} />,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: ({ dataKey }: any) => <div data-testid="pie" data-key={dataKey} />,
  XAxis: ({ dataKey }: any) => <div data-testid="x-axis" data-key={dataKey} />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
}));

const mockData = [
  { name: 'Jan', value: 100 },
  { name: 'Feb', value: 200 },
  { name: 'Mar', value: 150 },
];

describe('Chart', () => {
  it('renders line chart by default', () => {
    render(<Chart data={mockData} />);
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('renders line chart when type is line', () => {
    render(<Chart data={mockData} type="line" />);
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('renders bar chart when type is bar', () => {
    render(<Chart data={mockData} type="bar" />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders pie chart when type is pie', () => {
    render(<Chart data={mockData} type="pie" />);
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  it('renders with title', () => {
    render(<Chart data={mockData} title="Test Chart" />);
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
  });

  it('renders with custom height', () => {
    render(<Chart data={mockData} height={400} />);
    const container = screen.getByTestId('responsive-container');
    expect(container).toHaveStyle({ height: '400px' });
  });

  it('renders with custom width', () => {
    render(<Chart data={mockData} width={600} />);
    const container = screen.getByTestId('responsive-container');
    expect(container).toHaveStyle({ width: '600px' });
  });

  it('renders with data keys', () => {
    render(<Chart data={mockData} dataKeys={['value']} />);
    expect(screen.getByTestId('line')).toHaveAttribute('data-key', 'value');
  });

  it('renders with multiple data keys', () => {
    const multiData = [
      { name: 'Jan', value1: 100, value2: 150 },
      { name: 'Feb', value1: 200, value2: 250 },
    ];
    
    render(<Chart data={multiData} dataKeys={['value1', 'value2']} />);
    const lines = screen.getAllByTestId('line');
    expect(lines).toHaveLength(2);
  });

  it('renders with x axis data key', () => {
    render(<Chart data={mockData} xAxisDataKey="name" />);
    expect(screen.getByTestId('x-axis')).toHaveAttribute('data-key', 'name');
  });

  it('renders with tooltip', () => {
    render(<Chart data={mockData} showTooltip />);
    expect(screen.getByTestId('tooltip')).toBeInTheDocument();
  });

  it('renders with legend', () => {
    render(<Chart data={mockData} showLegend />);
    expect(screen.getByTestId('legend')).toBeInTheDocument();
  });

  it('renders with grid', () => {
    render(<Chart data={mockData} showGrid />);
    expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Chart data={mockData} className="custom-chart" />);
    const chart = screen.getByTestId('line-chart');
    expect(chart).toHaveClass('custom-chart');
  });

  it('renders loading state', () => {
    render(<Chart data={mockData} loading />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    render(<Chart data={mockData} error="数据加载失败" />);
    expect(screen.getByText('数据加载失败')).toBeInTheDocument();
  });

  it('renders empty state when no data', () => {
    render(<Chart data={[]} />);
    expect(screen.getByText('暂无数据')).toBeInTheDocument();
  });

  it('renders custom empty state', () => {
    render(<Chart data={[]} emptyText="没有图表数据" />);
    expect(screen.getByText('没有图表数据')).toBeInTheDocument();
  });
}); 