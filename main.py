#!/usr/bin/env python3
"""
Backward compatibility wrapper for Mardblog CLI.

This file allows the old usage pattern (python main.py) to continue working
while the package is now installable via pip/uv.

For new usage, install the package and use the `mardblog` command directly.
"""

from src.mardblog.cli import main

if __name__ == "__main__":
    main()
