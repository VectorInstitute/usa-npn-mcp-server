#!/usr/bin/env node

const { spawn } = require('cross-spawn');
const which = require('which');
const path = require('path');
const fs = require('fs');

// Parse command line arguments
const args = process.argv.slice(2);

// Check for help flag
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
USA-NPN MCP Server

Usage: npx usa-npn-mcp-server [OPTIONS] [ALLOWED_DIRS...]

Options:
  -v, --verbose    Increase verbosity (can be used multiple times)
  -h, --help       Show this help message

Arguments:
  ALLOWED_DIRS     Optional directory paths that are allowed for file export operations

Examples:
  npx usa-npn-mcp-server
  npx usa-npn-mcp-server -v /path/to/allowed/dir
  npx usa-npn-mcp-server -vv /dir1 /dir2

Requirements:
  - Python 3.12 or higher
  - uv (Python package manager)

To install uv:
  curl -LsSf https://astral.sh/uv/install.sh | sh
`);
  process.exit(0);
}

// Check for required tools
function checkRequirements() {
  const errors = [];

  // Check for uv
  try {
    which.sync('uv');
  } catch (e) {
    errors.push('uv is not installed');
  }

  // Check for Python
  try {
    const pythonCmd = which.sync('python3') || which.sync('python');
    const result = require('child_process').execSync(`${pythonCmd} --version`, {
      encoding: 'utf8'
    });

    const versionMatch = result.match(/Python (\d+)\.(\d+)/);
    if (versionMatch) {
      const major = parseInt(versionMatch[1]);
      const minor = parseInt(versionMatch[2]);
      if (major < 3 || (major === 3 && minor < 12)) {
        errors.push(`Python 3.12+ required, found ${major}.${minor}`);
      }
    }
  } catch (e) {
    errors.push('Python is not installed');
  }

  if (errors.length > 0) {
    console.error('Error: Missing requirements:\n');
    errors.forEach(err => console.error(`  - ${err}`));
    console.error('\nInstallation instructions:');
    console.error('  Python 3.12+: https://www.python.org/downloads/');
    console.error('  uv: curl -LsSf https://astral.sh/uv/install.sh | sh');
    process.exit(1);
  }
}

// Main execution
function main() {
  checkRequirements();

  // Determine the package root (where pyproject.toml is)
  const packageRoot = __dirname;
  const pyprojectPath = path.join(packageRoot, 'pyproject.toml');

  if (!fs.existsSync(pyprojectPath)) {
    console.error('Error: pyproject.toml not found in package directory');
    console.error('Package may be corrupted. Try reinstalling.');
    process.exit(1);
  }

  // Build the uv run command
  // Use --project to ensure uv uses our bundled pyproject.toml
  const uvArgs = [
    'run',
    '--project', packageRoot,
    'usa_npn_mcp_server',
    ...args
    // Pass command line args to python script
  ];

  console.error('Starting USA-NPN MCP Server...');
  console.error(`Working directory: ${packageRoot}`);

  // Spawn the Python process
  const child = spawn('uv', uvArgs, {
    stdio: 'inherit',
    cwd: packageRoot,
    env: {
      ...process.env,
      // Pass env vars and ensure Python uses unbuffered output
      PYTHONUNBUFFERED: '1'
    }
  });

  // Handle process termination
  child.on('error', (err) => {
    console.error('Failed to start server:', err.message);
    process.exit(1);
  });

  child.on('exit', (code, signal) => {
    if (signal) {
      console.error(`Server terminated by signal: ${signal}`);
      process.exit(1);
    } else if (code !== 0) {
      console.error(`Server exited with code: ${code}`);
      process.exit(code);
    }
  });

  // Forward termination signals to the child process
  ['SIGINT', 'SIGTERM'].forEach(signal => {
    process.on(signal, () => {
      child.kill(signal);
    });
  });
}

// Run if executed directly
if (require.main === module) {
  main();
}
