import subprocess
import sys
from pathlib import Path
import logging
from sqlmodel import Session
from app.core.db import db  # Import the db instance directly
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command: list[str]) -> bool:
    """Run a command and return True if successful"""
    try:
        result = subprocess.run(
            command, 
            check=True,
            env={
                **os.environ,
                "PYTHONPATH": str(Path(__file__).parent.parent.parent)
            }
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        logger.error(f"Error: {e}")
        return False

def create_migration(message: str) -> bool:
    """Create a new migration"""
    logger.info(f"Creating migration: {message}")
    return run_command(["alembic", "revision", "--autogenerate", "-m", message])

def upgrade_db() -> bool:
    """Upgrade database to latest migration"""
    logger.info("Upgrading database to latest migration")
    return run_command(["alembic", "upgrade", "head"])

def run_seeds() -> bool:
    """Run database seeds"""
    logger.info("Running database seeds")
    try:
        # Use the existing db connection from core.db
        session = db.session
        from app.seeds.seeder import Seeder
        seeder = Seeder(session)
        seeder.seed_all()
        return True
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        return False

def main():
    """Main function to handle database operations"""
    if len(sys.argv) < 2:
        logger.error("Please provide a command: migrate, upgrade, seed, or all")
        sys.exit(1)

    command = sys.argv[1].lower()
    
    if command == "migrate":
        if len(sys.argv) < 3:
            logger.error("Please provide a migration message")
            sys.exit(1)
        message = sys.argv[2]
        success = create_migration(message)
    
    elif command == "upgrade":
        success = upgrade_db()
    
    elif command == "seed":
        success = run_seeds()
    
    elif command == "all":
        if len(sys.argv) < 3:
            logger.error("Please provide a migration message")
            sys.exit(1)
        message = sys.argv[2]
        success = (
            create_migration(message) 
            and upgrade_db() 
            and run_seeds()
        )
    
    else:
        logger.error("Unknown command. Use: migrate, upgrade, seed, or all")
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 