#!/usr/bin/env node

/**
 * Sync version from pyproject.toml to package.json
 * Usage: node scripts/sync-version.js [version]
 */

const fs = require('fs');
const path = require('path');

function getPyprojectVersion() {
  const pyprojectPath = path.join(__dirname, '..', 'pyproject.toml');

  if (!fs.existsSync(pyprojectPath)) {
    console.error('pyproject.toml not found');
    process.exit(1);
  }

  const content = fs.readFileSync(pyprojectPath, 'utf8');
  const versionMatch = content.match(/^version = "(.+)"$/m);

  if (!versionMatch) {
    console.error('Version not found in pyproject.toml');
    process.exit(1);
  }

  return versionMatch[1];
}

function updatePackageJsonVersion(version) {
  const packagePath = path.join(__dirname, '..', 'package.json');

  if (!fs.existsSync(packagePath)) {
    console.error('package.json not found');
    process.exit(1);
  }

  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  packageJson.version = version;

  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2) + '\n');
  console.log(`✓ Updated package.json to version ${version}`);
}

function main() {
  const targetVersion = process.argv[2] || getPyprojectVersion();

  if (!targetVersion) {
    console.error('No version specified and could not read from pyproject.toml');
    process.exit(1);
  }

  console.log(`Syncing version to: ${targetVersion}`);
  updatePackageJsonVersion(targetVersion);
  console.log('✓ Version sync complete');
}

if (require.main === module) {
  main();
}

module.exports = { updatePackageJsonVersion, getPyprojectVersion };
