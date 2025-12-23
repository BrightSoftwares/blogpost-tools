#!/usr/bin/env node

/**
 * Semantic Version Manager for Notiwise
 * Manages version increments based on conventional commits
 *
 * Usage:
 *   node scripts/version-manager.js get-current       # Get current version
 *   node scripts/version-manager.js get-next          # Get next version based on commits
 *   node scripts/version-manager.js set <version>     # Set specific version
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VERSION_FILE = path.join(__dirname, '..', '.version');

/**
 * Get current version from file
 * @returns {string} Current version (e.g., "1.0.0")
 */
function getCurrentVersion() {
  try {
    if (fs.existsSync(VERSION_FILE)) {
      return fs.readFileSync(VERSION_FILE, 'utf8').trim();
    }
    // Default starting version
    return '0.1.0';
  } catch (error) {
    console.error('Error reading version file:', error);
    return '0.1.0';
  }
}

/**
 * Parse version string into components
 * @param {string} version - Version string (e.g., "1.2.3")
 * @returns {object} Version components
 */
function parseVersion(version) {
  const [major, minor, patch] = version.split('.').map(Number);
  return { major, minor, patch };
}

/**
 * Format version components into string
 * @param {object} version - Version components
 * @returns {string} Version string
 */
function formatVersion({ major, minor, patch }) {
  return `${major}.${minor}.${patch}`;
}

/**
 * Get commit messages since last tag or all commits
 * Excludes merge commits to get the actual work commits for version bumping
 * @returns {string[]} Array of commit messages
 */
function getCommitMessages() {
  try {
    // Try to get commits since last tag, excluding merge commits
    // --no-merges: excludes merge commits so we analyze the actual work commits
    // --first-parent: follows only the first parent (main branch history)
    let commits;
    try {
      const lastTag = execSync('git describe --tags --abbrev=0 2>/dev/null', { encoding: 'utf8' }).trim();
      // Use --no-merges to skip merge commits and get actual work commits
      commits = execSync(`git log ${lastTag}..HEAD --no-merges --pretty=format:"%s"`, { encoding: 'utf8' });

      // If no commits found (only merge commits), try getting commits from the merge
      if (!commits.trim()) {
        // Get the merge commit's parents and analyze those commits
        try {
          commits = execSync(`git log ${lastTag}..HEAD --pretty=format:"%s" --first-parent`, { encoding: 'utf8' });
        } catch {
          commits = '';
        }
      }
    } catch {
      // No tags found, get recent commits excluding merges
      commits = execSync('git log -10 --no-merges --pretty=format:"%s"', { encoding: 'utf8' });
    }

    const commitList = commits.split('\n').filter(msg => msg.trim());

    // Debug: log what commits we're analyzing
    console.log(`Found ${commitList.length} commits for version analysis`);
    if (commitList.length > 0 && commitList.length <= 5) {
      console.log('Commits:', commitList);
    }

    return commitList;
  } catch (error) {
    console.error('Error getting commit messages:', error);
    return [];
  }
}

/**
 * Determine version bump type from commit messages
 * @param {string[]} commits - Array of commit messages
 * @returns {string} Bump type: 'major', 'minor', 'patch'
 */
function determineBumpType(commits) {
  let hasMajor = false;
  let hasMinor = false;
  let hasPatch = false;

  for (const commit of commits) {
    const lowerCommit = commit.toLowerCase();

    // Check for breaking changes (major version)
    if (lowerCommit.includes('breaking change') ||
        lowerCommit.includes('breaking:') ||
        lowerCommit.match(/^[a-z]+!:/)) {
      hasMajor = true;
      break;
    }

    // Check for features (minor version)
    if (lowerCommit.startsWith('feat:') ||
        lowerCommit.startsWith('feat(') ||
        lowerCommit.startsWith('feature:')) {
      hasMinor = true;
    }

    // Check for fixes (patch version)
    if (lowerCommit.startsWith('fix:') ||
        lowerCommit.startsWith('fix(') ||
        lowerCommit.startsWith('bugfix:')) {
      hasPatch = true;
    }
  }

  if (hasMajor) return 'major';
  if (hasMinor) return 'minor';
  if (hasPatch) return 'patch';

  // Default to patch if no conventional commit format found
  return 'patch';
}

/**
 * Increment version based on bump type
 * @param {string} currentVersion - Current version
 * @param {string} bumpType - Type of bump: 'major', 'minor', 'patch'
 * @returns {string} New version
 */
function incrementVersion(currentVersion, bumpType) {
  const version = parseVersion(currentVersion);

  switch (bumpType) {
    case 'major':
      version.major += 1;
      version.minor = 0;
      version.patch = 0;
      break;
    case 'minor':
      version.minor += 1;
      version.patch = 0;
      break;
    case 'patch':
    default:
      version.patch += 1;
      break;
  }

  return formatVersion(version);
}

/**
 * Get next version based on commit messages
 * @returns {object} Next version info
 */
function getNextVersion() {
  const currentVersion = getCurrentVersion();
  const commits = getCommitMessages();
  const bumpType = determineBumpType(commits);
  const nextVersion = incrementVersion(currentVersion, bumpType);

  return {
    current: currentVersion,
    next: nextVersion,
    bumpType: bumpType,
    commits: commits.slice(0, 5) // First 5 commits
  };
}

/**
 * Set version to file
 * @param {string} version - Version to set
 */
function setVersion(version) {
  try {
    // Validate version format
    if (!/^\d+\.\d+\.\d+$/.test(version)) {
      throw new Error('Invalid version format. Use semantic versioning (e.g., 1.0.0)');
    }

    fs.writeFileSync(VERSION_FILE, version, 'utf8');
    console.log(`Version set to: ${version}`);
    return version;
  } catch (error) {
    console.error('Error setting version:', error);
    process.exit(1);
  }
}

/**
 * Create deployment description
 * @param {string} version - Version number
 * @returns {string} Deployment description
 */
function createDeploymentDescription(version) {
  try {
    const commitSha = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim();
    const commitMsg = execSync('git log -1 --pretty=format:"%s"', { encoding: 'utf8' }).trim();
    const timestamp = new Date().toISOString().replace('T', ' ').split('.')[0] + ' UTC';

    return `v${version} - ${commitMsg} (${commitSha}) - ${timestamp}`;
  } catch (error) {
    console.error('Error creating deployment description:', error);
    return `v${version}`;
  }
}

// CLI Interface
const command = process.argv[2];
const arg = process.argv[3];

switch (command) {
  case 'get-current':
    console.log(getCurrentVersion());
    break;

  case 'get-next': {
    const info = getNextVersion();
    if (process.argv.includes('--json')) {
      console.log(JSON.stringify(info, null, 2));
    } else {
      console.log(info.next);
    }
    break;
  }

  case 'set':
    if (!arg) {
      console.error('Error: Version argument required');
      console.log('Usage: node version-manager.js set <version>');
      process.exit(1);
    }
    setVersion(arg);
    break;

  case 'bump': {
    const info = getNextVersion();
    setVersion(info.next);
    console.log(`Bumped from ${info.current} to ${info.next} (${info.bumpType})`);
    break;
  }

  case 'description': {
    const version = arg || getCurrentVersion();
    console.log(createDeploymentDescription(version));
    break;
  }

  case 'info': {
    const info = getNextVersion();
    console.log('Current version:', info.current);
    console.log('Next version:', info.next);
    console.log('Bump type:', info.bumpType);
    console.log('\nRecent commits:');
    info.commits.forEach((commit, i) => {
      console.log(`  ${i + 1}. ${commit}`);
    });
    break;
  }

  default:
    console.log('Notiwise Version Manager\n');
    console.log('Usage:');
    console.log('  node scripts/version-manager.js get-current       # Get current version');
    console.log('  node scripts/version-manager.js get-next          # Get next version');
    console.log('  node scripts/version-manager.js get-next --json   # Get version info as JSON');
    console.log('  node scripts/version-manager.js set <version>     # Set specific version');
    console.log('  node scripts/version-manager.js bump              # Bump version and save');
    console.log('  node scripts/version-manager.js description [ver] # Get deployment description');
    console.log('  node scripts/version-manager.js info              # Show version info');
    process.exit(command ? 1 : 0);
}
