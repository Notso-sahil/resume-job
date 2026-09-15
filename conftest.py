# Root conftest.py — ensures the workspace root is on sys.path so that
# `from finder.xxx import ...` works in all test files without any
# package-relative import gymnastics.
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
