#!/usr/bin/env python
"""
Test Runner for KryptoMF Bot

Runs all tests with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with pytest."""
    print("=" * 70)
    print("Running KryptoMF Bot Tests")
    print("=" * 70)
    print()
    
    # Run pytest with coverage
    cmd = [
        sys.executable,
        '-m',
        'pytest',
        'tests/',
        '-v',                    # Verbose output
        '--cov=src',             # Coverage for src directory
        '--cov-report=term-missing',  # Show missing lines
        '--cov-report=html',     # Generate HTML report
        '--tb=short',            # Short traceback format
    ]
    
    result = subprocess.run(cmd)
    
    print()
    print("=" * 70)
    
    if result.returncode == 0:
        print("✓ All tests passed!")
        print()
        print("Coverage report generated in htmlcov/index.html")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
    
    print("=" * 70)


if __name__ == '__main__':
    run_tests()

