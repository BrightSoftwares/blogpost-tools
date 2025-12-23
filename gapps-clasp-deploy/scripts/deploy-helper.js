#!/usr/bin/env node

/**
 * Deployment Helper for Notiwise
 * Handles environment-specific deployments and URL updates
 *
 * Usage:
 *   node scripts/deploy-helper.js dev              # Deploy to dev
 *   node scripts/deploy-helper.js production       # Deploy to production
 *   node scripts/deploy-helper.js get-deployment-id <env>  # Get deployment ID for env
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG_FILE = path.join(__dirname, '..', 'deployment-config.json');

/**
 * Load deployment configuration
 * @returns {object} Configuration object
 */
function loadConfig() {
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    return config;
  } catch (error) {
    console.error('Error loading deployment config:', error);
    process.exit(1);
  }
}

/**
 * Execute command and handle errors
 * @param {string} command - Command to execute
 * @param {boolean} silent - Suppress output
 * @returns {string} Command output
 */
function execCommand(command, silent = false) {
  try {
    const options = silent ? { stdio: 'pipe', encoding: 'utf8' } : { stdio: 'inherit', encoding: 'utf8' };
    return execSync(command, options);
  } catch (error) {
    console.error(`Error executing command: ${command}`);
    if (error.stdout) console.error(error.stdout);
    if (error.stderr) console.error(error.stderr);
    throw error;
  }
}

/**
 * Get deployment info from clasp
 * @param {string} deploymentId - Deployment ID to check
 * @returns {object|null} Deployment info or null
 */
function getDeploymentInfo(deploymentId) {
  try {
    const output = execCommand('npx clasp deployments', true);
    const lines = output.split('\n');

    for (const line of lines) {
      if (line.includes(deploymentId)) {
        return {
          id: deploymentId,
          exists: true,
          line: line.trim()
        };
      }
    }
    return null;
  } catch (error) {
    console.error('Error getting deployment info:', error);
    return null;
  }
}

/**
 * Create new deployment
 * @param {string} description - Deployment description
 * @returns {string} New deployment ID
 */
function createDeployment(description) {
  try {
    console.log(`Creating new deployment: ${description}`);
    const output = execCommand(`npx clasp deploy -d "${description}"`, true);
    console.log('Clasp deploy output:', output);

    // Try multiple regex patterns to extract deployment ID
    // Pattern 1: "- AKfyc..." format (older clasp versions)
    let match = output.match(/- (AKfyc[a-zA-Z0-9_-]+)/);

    // Pattern 2: "Deployment ID: AKfyc..." or similar
    if (!match) {
      match = output.match(/(?:Deployment ID|deploymentId|id)[:\s]+(AKfyc[a-zA-Z0-9_-]+)/i);
    }

    // Pattern 3: Just find any AKfyc ID in the output
    if (!match) {
      match = output.match(/(AKfyc[a-zA-Z0-9_-]+)/);
    }

    // Pattern 4: Look for @deploymentId format
    if (!match) {
      match = output.match(/@(AKfyc[a-zA-Z0-9_-]+)/);
    }

    if (match) {
      const deploymentId = match[1];
      console.log(`✅ New deployment created: ${deploymentId}`);
      return deploymentId;
    }

    // If we still can't find it, show what we got and throw
    console.error('Could not find deployment ID in clasp output.');
    console.error('Full output was:', output);
    throw new Error('Could not extract deployment ID from clasp output');
  } catch (error) {
    console.error('Error creating deployment:', error);
    throw error;
  }
}

/**
 * Deploy to specific deployment ID
 * @param {string} deploymentId - Deployment ID
 * @param {string} description - Deployment description
 */
function deployToId(deploymentId, description) {
  try {
    console.log(`Deploying to ${deploymentId}`);
    console.log(`Description: ${description}`);
    execCommand(`npx clasp deploy -i "${deploymentId}" -d "${description}"`);
    console.log('✅ Deployment successful');
  } catch (error) {
    console.error('Error deploying:', error);
    throw error;
  }
}

/**
 * Deploy to environment
 * @param {string} environment - Environment name (dev, production)
 * @param {string} customDescription - Optional custom description
 */
function deployToEnvironment(environment, customDescription = null) {
  const config = loadConfig();
  const env = config.environments[environment];

  if (!env) {
    console.error(`Unknown environment: ${environment}`);
    console.error(`Available environments: ${Object.keys(config.environments).join(', ')}`);
    process.exit(1);
  }

  console.log(`\n🚀 Deploying to ${env.name} environment\n`);

  // Debug: Show environment config
  console.log('Environment config:', JSON.stringify(env, null, 2));

  // Get version info
  const versionManager = path.join(__dirname, 'version-manager.js');
  const version = execSync(`node "${versionManager}" get-current`, { encoding: 'utf8' }).trim();
  const description = customDescription || execSync(`node "${versionManager}" description "${version}"`, { encoding: 'utf8' }).trim();

  try {
    // Push code first
    console.log('📦 Pushing code to Google Apps Script...');
    execCommand('npx clasp push --force');
    console.log('✅ Code pushed successfully\n');

    if (env.versionStrategy === 'HEAD') {
      // Deploy to @HEAD for dev
      if (env.deploymentId) {
        // Update existing dev deployment
        deployToId(env.deploymentId, description);
      } else {
        // Create new dev deployment
        const newId = createDeployment(description);
        // Update config file with new deployment ID
        config.environments[environment].deploymentId = newId;
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
        console.log(`Updated config with new ${environment} deployment ID`);
      }
    } else {
      // Production: Update existing deployment with new version (don't create new deployment)
      // Note: description from version-manager.js already includes version, so don't duplicate it
      const versionedDesc = description;

      if (env.deploymentId) {
        // Update existing production deployment with new version
        // This creates a new version and attaches it to the existing deployment ID
        console.log(`Updating production deployment ${env.deploymentId} with new version...`);
        deployToId(env.deploymentId, versionedDesc);

        // Store deployment info in history for potential rollback
        const deploymentHistory = loadDeploymentHistory();
        deploymentHistory.push({
          version: version,
          deploymentId: env.deploymentId,
          timestamp: new Date().toISOString(),
          description: description,
          environment: environment
        });
        saveDeploymentHistory(deploymentHistory);
        console.log(`✅ Saved deployment to history for potential rollback`);
      } else {
        // No existing deployment ID - create new deployment
        console.log('No existing production deployment ID found, creating new deployment...');
        const newId = createDeployment(versionedDesc);

        // Update config with the new deployment ID
        config.environments[environment].deploymentId = newId;
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
        console.log(`Updated config with new ${environment} deployment ID: ${newId}`);

        // Store in history
        const deploymentHistory = loadDeploymentHistory();
        deploymentHistory.push({
          version: version,
          deploymentId: newId,
          timestamp: new Date().toISOString(),
          description: description,
          environment: environment
        });
        saveDeploymentHistory(deploymentHistory);
      }
    }

    console.log(`\n✅ Successfully deployed to ${env.name}`);
    console.log(`Version: ${version}`);
    console.log(`Description: ${description}\n`);

    return {
      success: true,
      version: version,
      environment: environment,
      deploymentId: env.deploymentId
    };

  } catch (error) {
    console.error(`\n❌ Deployment to ${env.name} failed`);
    throw error;
  }
}

/**
 * Load deployment history
 * @returns {array} Deployment history
 */
function loadDeploymentHistory() {
  const historyFile = path.join(__dirname, '..', '.deployment-history.json');
  try {
    if (fs.existsSync(historyFile)) {
      return JSON.parse(fs.readFileSync(historyFile, 'utf8'));
    }
  } catch (error) {
    console.warn('Could not load deployment history:', error);
  }
  return [];
}

/**
 * Save deployment history
 * @param {array} history - Deployment history
 */
function saveDeploymentHistory(history) {
  const historyFile = path.join(__dirname, '..', '.deployment-history.json');
  try {
    // Keep only last 50 deployments
    const recentHistory = history.slice(-50);
    fs.writeFileSync(historyFile, JSON.stringify(recentHistory, null, 2));
  } catch (error) {
    console.error('Error saving deployment history:', error);
  }
}

/**
 * Get last successful deployment
 * @param {string} environment - Environment name
 * @returns {object|null} Last deployment info
 */
function getLastDeployment(environment) {
  const history = loadDeploymentHistory();
  const envDeployments = history.filter(d => d.environment === environment);
  return envDeployments.length > 0 ? envDeployments[envDeployments.length - 1] : null;
}

/**
 * Rollback to previous deployment
 * @param {string} environment - Environment name
 */
function rollback(environment) {
  const history = loadDeploymentHistory();
  const envDeployments = history.filter(d => d.environment === environment);

  if (envDeployments.length < 2) {
    console.error('No previous deployment found for rollback');
    process.exit(1);
  }

  // Get second-to-last deployment (previous one)
  const previousDeployment = envDeployments[envDeployments.length - 2];

  console.log(`\n🔄 Rolling back ${environment} to previous deployment`);
  console.log(`Version: ${previousDeployment.version}`);
  console.log(`Deployment ID: ${previousDeployment.deploymentId}`);
  console.log(`Original timestamp: ${previousDeployment.timestamp}\n`);

  try {
    const config = loadConfig();
    const env = config.environments[environment];

    if (!env) {
      throw new Error(`Unknown environment: ${environment}`);
    }

    // Deploy the previous version
    const rollbackDesc = `ROLLBACK to v${previousDeployment.version} - ${previousDeployment.description}`;

    if (env.deploymentId) {
      deployToId(env.deploymentId, rollbackDesc);
    }

    console.log('\n✅ Rollback successful');
    return previousDeployment;

  } catch (error) {
    console.error('\n❌ Rollback failed');
    throw error;
  }
}

// CLI Interface
const command = process.argv[2];
const arg = process.argv[3];
const arg2 = process.argv[4];

switch (command) {
  case 'dev':
  case 'development':
    deployToEnvironment('dev', arg);
    break;

  case 'prod':
  case 'production':
    deployToEnvironment('production', arg);
    break;

  case 'get-deployment-id': {
    const config = loadConfig();
    const env = config.environments[arg];
    if (env && env.deploymentId) {
      console.log(env.deploymentId);
    } else {
      console.log('');
    }
    break;
  }

  case 'rollback':
    rollback(arg || 'production');
    break;

  case 'history': {
    const history = loadDeploymentHistory();
    const env = arg || 'production';
    const envHistory = history.filter(d => d.environment === env);
    console.log(`\nDeployment history for ${env}:\n`);
    envHistory.slice(-10).forEach((d, i) => {
      console.log(`${i + 1}. v${d.version} - ${d.timestamp}`);
      console.log(`   ${d.description}`);
      console.log(`   ID: ${d.deploymentId}\n`);
    });
    break;
  }

  default:
    console.log('Notiwise Deployment Helper\n');
    console.log('Usage:');
    console.log('  node scripts/deploy-helper.js dev [description]        # Deploy to dev');
    console.log('  node scripts/deploy-helper.js production [description] # Deploy to production');
    console.log('  node scripts/deploy-helper.js get-deployment-id <env>  # Get deployment ID');
    console.log('  node scripts/deploy-helper.js rollback [env]           # Rollback to previous');
    console.log('  node scripts/deploy-helper.js history [env]            # Show deployment history');
    process.exit(command ? 1 : 0);
}
