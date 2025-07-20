#!/bin/bash

# 测试设置脚本
echo "🚀 设置测试环境..."

# 检查是否安装了依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 检查测试覆盖率目录
if [ ! -d "coverage" ]; then
    mkdir coverage
fi

# 运行类型检查
echo "🔍 运行类型检查..."
npm run type-check

# 运行代码检查
echo "🔍 运行代码检查..."
npm run lint

# 运行测试
echo "🧪 运行测试..."
npm run test

# 生成测试覆盖率报告
echo "📊 生成测试覆盖率报告..."
npm run test:coverage

echo "✅ 测试设置完成！" 