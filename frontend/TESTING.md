# 测试指南

本文档描述了K12智能教育平台前端的测试策略和实现。

## 📋 测试概述

### 测试类型
- **单元测试**: 测试独立的函数、组件和模块
- **集成测试**: 测试组件间的交互
- **端到端测试**: 测试完整的用户流程（计划中）

### 测试覆盖率目标
- 组件测试覆盖率: 80%+
- 工具函数测试覆盖率: 90%+
- API模块测试覆盖率: 85%+
- 整体测试覆盖率: 80%+

## 🛠️ 测试技术栈

- **测试框架**: Vitest
- **测试环境**: jsdom
- **测试工具**: @testing-library/react
- **断言库**: Vitest内置
- **覆盖率**: @vitest/coverage-v8

## 📁 测试文件结构

```
src/
├── test/
│   └── setup.ts                 # 测试环境配置
├── components/
│   ├── common/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.test.tsx  # 组件测试
│   │   │   └── index.ts
│   │   └── ...
│   └── business/
│       └── AIChat/
│           ├── AIChat.tsx
│           ├── AIChat.test.tsx  # 业务组件测试
│           └── index.ts
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts          # Hook测试
├── utils/
│   ├── helpers.ts
│   └── helpers.test.ts          # 工具函数测试
├── api/
│   └── modules/
│       ├── auth.ts
│       └── auth.test.ts         # API模块测试
└── store/
    └── slices/
        ├── authSlice.ts
        └── authSlice.test.ts    # Store测试
```

## 🧪 运行测试

### 基本命令
```bash
# 运行所有测试
npm run test

# 运行测试并监听文件变化
npm run test -- --watch

# 运行测试UI
npm run test:ui

# 生成覆盖率报告
npm run test:coverage

# 运行特定测试文件
npm run test Button.test.tsx

# 运行特定测试套件
npm run test -- --grep "Button"
```

### 测试脚本
```bash
# 运行完整的测试流程
./scripts/test-setup.sh
```

## 📝 测试编写指南

### 组件测试

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Button from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Hook测试

```typescript
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useAuth } from './useAuth';

describe('useAuth', () => {
  it('returns auth state', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });
});
```

### API测试

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authAPI } from './auth';

vi.mock('@/api/request', () => ({
  request: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authAPI', () => {
  it('calls login endpoint', async () => {
    const credentials = { username: 'test', password: 'pass' };
    const mockResponse = { data: { user: { id: 1 } } };
    
    mockRequest.post.mockResolvedValue(mockResponse);
    
    const result = await authAPI.login(credentials);
    expect(mockRequest.post).toHaveBeenCalledWith('/auth/login', credentials);
    expect(result).toEqual(mockResponse);
  });
});
```

### Store测试

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createAuthSlice } from './authSlice';

describe('authSlice', () => {
  let set: any;
  let get: any;

  beforeEach(() => {
    set = vi.fn();
    get = vi.fn();
  });

  it('has correct initial state', () => {
    const slice = createAuthSlice(set, get);
    
    expect(slice.user).toBe(null);
    expect(slice.isAuthenticated).toBe(false);
  });
});
```

## 🔧 测试配置

### Vitest配置 (vitest.config.ts)
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### 测试环境设置 (src/test/setup.ts)
```typescript
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  },
  writable: true,
});

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: 1,
}));
```

## 🎯 测试最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 遵循 "should" 或 "when" 模式
- 使用中文描述业务逻辑

### 2. 测试组织
- 按功能模块组织测试
- 使用 describe 块分组相关测试
- 保持测试文件结构清晰

### 3. Mock策略
- Mock外部依赖（API、localStorage等）
- 使用 vi.fn() 创建模拟函数
- 避免过度Mock，保持测试的真实性

### 4. 断言
- 使用具体的断言
- 测试用户可见的行为
- 避免测试实现细节

### 5. 测试数据
- 使用工厂函数创建测试数据
- 保持测试数据的真实性
- 避免硬编码的测试数据

## 📊 覆盖率报告

运行 `npm run test:coverage` 后，可以在以下位置查看覆盖率报告：

- **控制台输出**: 显示总体覆盖率
- **HTML报告**: `coverage/index.html`
- **JSON报告**: `coverage/coverage-final.json`

### 覆盖率指标
- **Statements**: 语句覆盖率
- **Branches**: 分支覆盖率
- **Functions**: 函数覆盖率
- **Lines**: 行覆盖率

## 🚀 持续集成

### GitHub Actions配置
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: npm run lint
      - run: npm run type-check
```

## 🔍 调试测试

### 调试失败的测试
```bash
# 运行特定测试并显示详细输出
npm run test -- --reporter=verbose

# 在浏览器中调试
npm run test:ui

# 运行单个测试文件
npm run test Button.test.tsx
```

### 常见问题
1. **Mock不生效**: 检查Mock的导入路径
2. **异步测试失败**: 使用 waitFor 等待异步操作
3. **组件渲染问题**: 检查测试环境配置
4. **类型错误**: 确保测试文件包含正确的类型导入

## 📚 参考资源

- [Vitest文档](https://vitest.dev/)
- [React Testing Library文档](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest DOM文档](https://github.com/testing-library/jest-dom)
- [测试最佳实践](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) 