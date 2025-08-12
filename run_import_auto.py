#!/usr/bin/env python3
"""
Wrapper to run import script with automatic responses
"""
import subprocess
import os
import sys

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Prepare inputs
inputs = "\n1\n2\n"  # Empty line for file, 1 for skip duplicates, 2 for automatic mode

# Run the import script
process = subprocess.Popen(
    [sys.executable, 'scripts_cli/importar_movimientos_bbva.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Send all inputs at once
stdout, _ = process.communicate(input=inputs)

# Print output
print(stdout)