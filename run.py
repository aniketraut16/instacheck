import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running uvicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
