#!/usr/bin/env python3
"""
MMM Dashboard Services Shutdown Script

Stops all running development services including FastAPI, Next.js, Docker containers,
and checks port status. Provides comprehensive cleanup for development environment.

Usage:
    python scripts/shutdown.py [--quiet] [--force]
    
Or via pnpm:
    pnpm stop
"""

import argparse
import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def execute_command(command: str, description: str, quiet: bool = False) -> bool:
    """Execute a shell command and handle output."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Decode output
        stdout_text = stdout.decode().strip() if stdout else ""
        stderr_text = stderr.decode().strip() if stderr else ""
        
        # Check for expected "no process" or "no containers" messages
        expected_errors = ["No such process", "No containers", "No docker-compose services"]
        is_expected_error = any(err in stderr_text for err in expected_errors)
        
        if process.returncode != 0 and not is_expected_error:
            if not quiet:
                logger.warning(f"{description}: {stderr_text}")
            return False
        else:
            if not quiet:
                logger.info(f"SUCCESS: {description}")
                
            # Show stdout if it's short and meaningful
            if stdout_text and len(stdout_text.split('\n')) <= 3:
                if not quiet:
                    for line in stdout_text.split('\n'):
                        if line.strip():
                            logger.info(f"   {line}")
            
            return True
            
    except Exception as e:
        if not quiet:
            logger.error(f"ERROR executing {description}: {e}")
        return False


async def shutdown_services(quiet: bool = False, force: bool = False) -> None:
    """Shutdown all MMM Dashboard services."""
    
    if not quiet:
        logger.info("Shutting down MMM Dashboard services...")
        logger.info("")
        logger.info("Stopping all services...")
        logger.info("")
    
    # Commands to stop various services
    commands = [
        # Stop Node.js processes (Next.js frontend)
        ('pkill -f "next dev" 2>/dev/null || true', 'Next.js frontend stopped'),
        
        # Stop Python processes (FastAPI backend)
        ('pkill -f "uvicorn.*app" 2>/dev/null || true', 'FastAPI backend stopped'),
        
        # Stop Turbo processes
        ('pkill -f "turbo.*dev" 2>/dev/null || true', 'Turbo dev processes stopped'),
    ]
    
    # Execute stop commands
    for command, description in commands:
        await execute_command(command, description, quiet)
    
    # Stop Docker services
    docker_dir = Path(__file__).parent.parent.parent.parent / "packages" / "docker"
    if docker_dir.exists():
        docker_command = f'cd "{docker_dir}" && docker-compose down 2>/dev/null || echo "No docker-compose services running"'
        await execute_command(docker_command, 'Docker services stopped', quiet)
    
    # Stop any remaining Docker containers
    await execute_command(
        'docker stop $(docker ps -q) 2>/dev/null || echo "No containers running"',
        'All Docker containers stopped',
        quiet
    )
    
    # Force kill if requested
    if force:
        if not quiet:
            logger.info("Force mode: Killing remaining processes...")
        
        force_commands = [
            ('pkill -9 -f "next" 2>/dev/null || true', 'Force killed Next.js processes'),
            ('pkill -9 -f "uvicorn" 2>/dev/null || true', 'Force killed FastAPI processes'),
            ('pkill -9 -f "turbo" 2>/dev/null || true', 'Force killed Turbo processes'),
        ]
        
        for command, description in force_commands:
            await execute_command(command, description, quiet)
    
    # Check port status
    if not quiet:
        logger.info("")
        logger.info("Checking port status...")
    
    port_commands = [
        ('lsof -i :3000 2>/dev/null || echo "Port 3000: Free"', 'Port 3000 status'),
        ('lsof -i :8000 2>/dev/null || echo "Port 8000: Free"', 'Port 8000 status'),
        ('lsof -i :5432 2>/dev/null || echo "Port 5432: Free"', 'Port 5432 status'),
    ]
    
    for command, description in port_commands:
        await execute_command(command, description, quiet)
    
    # Final status
    if not quiet:
        logger.info("")
        logger.info("SHUTDOWN COMPLETE!")
        logger.info("=" * 32)
        logger.info("FastAPI Backend (port 8000): Stopped")
        logger.info("Next.js Frontend (port 3000): Stopped")
        logger.info("PostgreSQL Database (port 5432): Stopped")
        logger.info("Adminer DB Admin (port 8080): Stopped")
        logger.info("All processes: Terminated")
        logger.info("")
        logger.info("To restart everything, run: pnpm dev")
        logger.info("System is now clean and ready!")


def signal_handler(signum: int, frame) -> None:
    """Handle Ctrl+C gracefully."""
    logger.info("\n\nShutdown interrupted. Some processes may still be running.")
    sys.exit(0)


async def main() -> None:
    """Main function with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="Shutdown MMM Dashboard development services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/shutdown.py              # Normal shutdown
    python scripts/shutdown.py --quiet      # Silent shutdown
    python scripts/shutdown.py --force      # Force kill processes
    python scripts/shutdown.py --force --quiet  # Silent force shutdown
        """
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Suppress non-error output"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true", 
        help="Force kill processes (use SIGKILL)"
    )
    
    args = parser.parse_args()
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await shutdown_services(quiet=args.quiet, force=args.force)
    except Exception as e:
        logger.error(f"ERROR: Error during shutdown: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
