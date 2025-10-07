
"""
Script to start the FastAPI server and/or Streamlit app
"""

import subprocess
import sys
import os
import time
from threading import Thread


def run_fastapi():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])


def run_streamlit():
    """Run the Streamlit app"""
    print("🎨 Starting Streamlit app on http://localhost:8501")
    # Wait a moment for FastAPI to start
    time.sleep(2)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/Home.py",
        "--server.port", "8501"
    ])


def main():

    print("🏋️‍♂️ Starting Workout Builder servers...")

    if not os.path.exists("app.py"):
        print("❌ Error: Please run this script from the workout-builder directory")
        sys.exit(1)

    run_fastapi()
    # Start FastAPI in a separate thread
    # fastapi_thread = Thread(target=run_fastapi, daemon=True)
    # fastapi_thread.start()

    # Start Streamlit in main thread (easier to stop with Ctrl+C)
    # try:
    #     run_streamlit()
    # except KeyboardInterrupt:
    #     print("\n👋 Shutting down servers...")
    #     sys.exit(0)


if __name__ == "__main__":
    main()
