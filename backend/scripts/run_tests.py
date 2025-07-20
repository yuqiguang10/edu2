#!/usr/bin/env python3
"""
运行所有测试的脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def run_backend_tests():
    """运行后端测试"""
    print("🧪 运行后端测试...")
    
    # 进入后端目录
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # 运行测试
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--cov=app", 
        "--cov-report=html",
        "--cov-report=term"
    ], capture_output=False)
    
    return result.returncode == 0

def run_frontend_tests():
    """运行前端测试"""
    print("🧪 运行前端测试...")
    
    # 进入前端目录
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    # 运行测试
    result = subprocess.run([
        "npm", "run", "test", "--", "--coverage"
    ], capture_output=False)
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 开始运行测试套件...")
    
    backend_success = run_backend_tests()
    frontend_success = run_frontend_tests()
    
    print("\n📊 测试结果:")
    print(f"后端测试: {'✅ 通过' if backend_success else '❌ 失败'}")
    print(f"前端测试: {'✅ 通过' if frontend_success else '❌ 失败'}")
    
    if backend_success and frontend_success:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
        