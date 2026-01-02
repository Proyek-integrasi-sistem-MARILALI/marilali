#!/usr/bin/env python
"""
Test Runner Script
Runs all pytest tests and generates coverage report
"""
import subprocess
import sys


def run_tests():
    """Run pytest with coverage"""
    print("=" * 60)
    print("Starting Automated Test Suite")
    print("=" * 60)
    
    # Run pytest with coverage
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-m", "not slow"
    ]
    
    print(f"\nRunning command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd="backend")
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed!")
        print("Coverage report generated in: backend/htmlcov/index.html")
    else:
        print("❌ Some tests failed. Please review the output above.")
    print("=" * 60)
    
    return result.returncode


def run_specific_module(module: str):
    """Run tests for a specific module"""
    print(f"\n🔍 Running {module} tests...")
    
    cmd = [
        "pytest",
        f"tests/test_{module}.py",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, cwd="backend")
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific module
        module = sys.argv[1]
        exit_code = run_specific_module(module)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)
