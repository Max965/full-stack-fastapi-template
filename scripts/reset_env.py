import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command: list[str], cwd: str | None = None) -> None:
    """Run a command and print its output in real-time"""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
            
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

def reset_environment() -> None:
    """Delete and recreate the virtual environment"""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "fastapi"
    
    print("🗑️  Cleaning up old environment...")
    # Delete existing environment
    if venv_path.exists():
        shutil.rmtree(venv_path)
    
    print("🧹 Cleaning UV cache...")
    run_command(["uv", "cache", "clean"])
    
    print("🏗️  Creating new virtual environment...")
    # Create new environment using Python 3.11
    run_command(["py", "-3.11", "-m", "venv", "fastapi"])
    
    # Determine the pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "python.exe"
        uv_command = [str(pip_path), "-m", "pip", "install", "uv"]
    else:
        pip_path = venv_path / "bin" / "python"
        uv_command = [str(pip_path), "-m", "pip", "install", "uv"]
    
    print("📦 Installing UV...")
    run_command(uv_command)
    
    print("📥 Installing project dependencies...")
    run_command(["uv", "pip", "install", "-e", "."], cwd=str(project_root / "backend"))
    
    print("✨ Environment setup complete!")
    print("\nTo activate the environment:")
    if sys.platform == "win32":
        print("    .\\fastapi\\Scripts\\activate")
    else:
        print("    source fastapi/bin/activate")

if __name__ == "__main__":
    reset_environment() 