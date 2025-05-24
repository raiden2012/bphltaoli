#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner script for the funding arbitrage bot

This script runs all tests and provides a summary of test coverage.
"""

import os
import sys
import subprocess

def main():
    """Run all tests"""
    print("Running tests for funding arbitrage bot...")
    print("=" * 60)
    
    # Change to project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], check=True)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        return e.returncode
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())