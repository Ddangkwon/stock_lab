import os
import subprocess
import sys



if __name__ == "__main__":
    # os.system("pip install numpy")
    subprocess.check_call([sys.executable, "-m", "pip", "install", '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'pyinstaller'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'numpy'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'pandas==1.3.5'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'matplotlib==3.5.2'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'beautifulsoup4'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'finance-datareader'])
