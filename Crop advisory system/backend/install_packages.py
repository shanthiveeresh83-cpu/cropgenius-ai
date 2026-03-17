import subprocess
import sys
import os

venv_python = r"c:\Users\saik4\Downloads\Crop advisory system\backend\.venv\Scripts\python.exe"

result = subprocess.run(
    [venv_python, '-m', 'pip', 'install', 'pandas', 'scikit-learn'],
    capture_output=True,
    text=True
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)