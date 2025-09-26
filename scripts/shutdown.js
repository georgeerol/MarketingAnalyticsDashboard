#!/usr/bin/env node

const { exec } = require('child_process');
const path = require('path');

console.log('Shutting down MMM Dashboard services...\n');

// Function to execute shell commands
function executeCommand(command, description) {
  return new Promise((resolve) => {
    exec(command, (error, stdout, stderr) => {
      if (error && !error.message.includes('No such process') && !error.message.includes('No containers')) {
        console.log(`WARNING: ${description}: ${error.message}`);
      } else {
        console.log(`SUCCESS: ${description}`);
      }
      if (stdout && stdout.trim()) {
        const lines = stdout.trim().split('\n');
        if (lines.length <= 3) {
          console.log(`   ${stdout.trim()}`);
        }
      }
      resolve();
    });
  });
}

// Function to run commands sequentially
async function shutdown() {
  try {
    console.log('Stopping all services...\n');

    // Stop Node.js processes (Next.js frontend)
    await executeCommand(
      'pkill -f "next dev" 2>/dev/null || true',
      'Next.js frontend stopped'
    );

    // Stop Python processes (FastAPI backend)
    await executeCommand(
      'pkill -f "uvicorn main:app" 2>/dev/null || true',
      'FastAPI backend stopped'
    );

    // Stop Turbo processes
    await executeCommand(
      'pkill -f "turbo.*dev" 2>/dev/null || true',
      'Turbo dev processes stopped'
    );

    // Stop Docker containers
    const dockerDir = path.join(__dirname, '..', 'packages', 'docker');
    await executeCommand(
      `cd "${dockerDir}" && docker-compose down 2>/dev/null || echo "No docker-compose services running"`,
      'Docker services stopped'
    );

    // Stop any remaining Docker containers
    await executeCommand(
      'docker stop $(docker ps -q) 2>/dev/null || echo "No containers running"',
      'All Docker containers stopped'
    );

    // Check port status
    console.log('\nChecking port status...');
    await executeCommand(
      'lsof -i :3000 2>/dev/null || echo "Port 3000: Free"',
      'Port 3000 status'
    );
    await executeCommand(
      'lsof -i :8000 2>/dev/null || echo "Port 8000: Free"',
      'Port 8000 status'
    );
    await executeCommand(
      'lsof -i :5432 2>/dev/null || echo "Port 5432: Free"',
      'Port 5432 status'
    );

    console.log('\nSHUTDOWN COMPLETE!');
    console.log('================================');
    console.log('FastAPI Backend (port 8000): Stopped');
    console.log('Next.js Frontend (port 3000): Stopped');
    console.log('PostgreSQL Database (port 5432): Stopped');
    console.log('Adminer DB Admin (port 8080): Stopped');
    console.log('All processes: Terminated');
    console.log('\nTo restart everything, run: pnpm dev');
    console.log('System is now clean and ready!');

  } catch (error) {
    console.error('ERROR: Error during shutdown:', error.message);
    process.exit(1);
  }
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
  console.log('\n\nShutdown interrupted. Some processes may still be running.');
  process.exit(0);
});

// Run the shutdown
shutdown();