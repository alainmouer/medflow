import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PYTHONPATH"] = "."

# Seed dev data if DB doesn't exist or is empty
subprocess.run([sys.executable, "app/scripts/seed_dev.py"], check=False)

# Start uvicorn server
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
])
