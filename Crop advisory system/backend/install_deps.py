import subprocess
import sys

packages = ['pandas', 'scikit-learn']
for package in packages:
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    print(f"{package} installed successfully!")

print("All packages installed!")