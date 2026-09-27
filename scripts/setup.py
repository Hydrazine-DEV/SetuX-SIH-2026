import subprocess
import sys
import os

def run():
    print("[SetuX Setup] Installing backend requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
    
    print("[SetuX Setup] Seeding database...")
    subprocess.run([sys.executable, "scripts/seed_database.py"], check=True)
    
    print("[SetuX Setup] Setup complete!")

if __name__ == "__main__":
    run()
