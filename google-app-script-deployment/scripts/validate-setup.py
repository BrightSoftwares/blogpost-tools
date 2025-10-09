#!/usr/bin/env python3
"""
Validate Setup Script
Tests all prerequisites before running the deployment workflow
"""

import sys
import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

class SetupValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
    def check_files(self) -> bool:
        """Check required files exist"""
        print_header("Checking Required Files")
        
        required_files = {
            'marketplace-config.yaml': 'Marketplace configuration',
            'appsscript.json': 'Apps Script manifest',
            '.github/workflows/deploy-marketplace.yml': 'Deployment workflow',
            '.github/workflows/monitor-approval.yml': 'Approval monitor workflow'
        }
        
        all_exist = True
        for file_path, description in required_files.items():
            if os.path.exists(file_path):
                print_success(f"{description}: {file_path}")
                self.passed_checks.append(f"File exists: {file_path}")
            else:
                print_error(f"Missing {description}: {file_path}")
                self.errors.append(f"Required file missing: {file_path}")
                all_exist = False
        
        return all_exist
    
    def check_config(self) -> bool:
        """Validate marketplace configuration"""
        print_header("Validating Configuration")
        
        config_path = 'marketplace-config.yaml'
        
        if not os.path.exists(config_path):
            print_error("Configuration file not found")
            return False
        
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = [
                ('project.id', 'Project ID'),
                ('project.name', 'Project name'),
                ('project.script_id', 'Apps Script ID'),
                ('oauth_consent.support_email', 'Support email')
            ]
            
            all_valid = True
            for field_path, field_name in required_fields:
                value = self._get_nested(config, field_path)
                if value:
                    print_success(f"{field_name}: {value}")
                    self.passed_checks.append(f"Config field set: {field_name}")
                else:
                    print_error(f"Missing {field_name}: {field_path}")
                    self.errors.append(f"Required config field missing: {field_path}")
                    all_valid = False
            
            # Check OAuth consent for external apps
            if self._get_nested(config, 'oauth_consent.user_type') == 'external':
                privacy_url = self._get_nested(config, 'oauth_consent.privacy_policy_url')
                terms_url = self._get_nested(config, 'oauth_consent.terms_of_service_url')
                
                if not privacy_url or not privacy_url.startswith('https://'):
                    print_error("External apps require HTTPS privacy policy URL")
                    self.errors.append("Missing or invalid privacy_policy_url")
                    all_valid = False
                else:
                    print_success(f"Privacy policy URL: {privacy_url}")
                
                if not terms_url or not terms_url.startswith('https://'):
                    print_error("External apps require HTTPS terms of service URL")
                    self.errors.append("Missing or invalid terms_of_service_url")
                    all_valid = False
                else:
                    print_success(f"Terms of service URL: {terms_url}")
            
            # Validate asset paths
            asset_location = self._get_nested(config, 'marketplace.asset_location', 'external')
            icon_config = self._get_nested(config, 'marketplace.assets.icon', {})
            
            if asset_location == 'repo':
                icon_path = icon_config.get('repo_path', '')
                if icon_path and os.path.exists(icon_path):
                    print_success(f"Icon file found: {icon_path}")
                elif icon_path:
                    print_warning(f"Icon file not found: {icon_path}")
                    self.warnings.append(f"Icon file missing: {icon_path}")
            elif asset_location == 'external':
                icon_url = icon_config.get('external_url', '')
                if icon_url and icon_url.startswith('https://'):
                    print_success(f"Icon URL configured: {icon_url}")
                elif icon_url:
                    print_warning(f"Icon URL should use HTTPS: {icon_url}")
                    self.warnings.append("Icon URL should use HTTPS")
            
            return all_valid
            
        except yaml.YAMLError as e:
            print_error(f"Invalid YAML syntax: {e}")
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            print_error(f"Configuration validation failed: {e}")
            self.errors.append(f"Configuration error: {e}")
            return False
    
    def check_appsscript_manifest(self) -> bool:
        """Validate appsscript.json"""
        print_header("Validating Apps Script Manifest")
        
        manifest_path = 'appsscript.json'
        
        if not os.path.exists(manifest_path):
            print_error("appsscript.json not found")
            return False
        
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            # Check runtime version
            runtime = manifest.get('runtimeVersion', 'DEPRECATED_ES5')
            if runtime == 'V8':
                print_success(f"Runtime version: {runtime}")
            else:
                print_warning(f"Runtime version {runtime} - V8 recommended")
                self.warnings.append("Consider upgrading to V8 runtime")
            
            # Check OAuth scopes
            scopes = manifest.get('oauthScopes', [])
            if scopes:
                print_success(f"OAuth scopes defined: {len(scopes)} scope(s)")
                for scope in scopes:
                    print_info(f"  - {scope}")
                self.passed_checks.append(f"OAuth scopes: {len(scopes)} defined")
            else:
                print_warning("No OAuth scopes defined in manifest")
                self.warnings.append("No OAuth scopes found in appsscript.json")
            
            # Check time zone
            timezone = manifest.get('timeZone')
            if timezone:
                print_success(f"Time zone: {timezone}")
            else:
                print_warning("Time zone not specified")
                self.warnings.append("Consider setting timeZone in manifest")
            
            return True
            
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON syntax: {e}")
            self.errors.append(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            print_error(f"Manifest validation failed: {e}")
            self.errors.append(f"Manifest error: {e}")
            return False
    
    def check_github_secrets(self) -> bool:
        """Check if GitHub secrets are configured"""
        print_header("Checking GitHub Environment")
        
        # Check if running in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS'):
            print_success("Running in GitHub Actions environment")
            
            # Check for service account key
            if os.environ.get('GCP_SERVICE_ACCOUNT_KEY'):
                print_success("GCP_SERVICE_ACCOUNT_KEY is set")
                self.passed_checks.append("Service account key configured")
                
                # Validate it's valid JSON
                try:
                    sa_key = json.loads(os.environ['GCP_SERVICE_ACCOUNT_KEY'])
                    if sa_key.get('type') == 'service_account':
                        print_success("Service account key format is valid")
                    else:
                        print_error("Service account key has invalid format")
                        self.errors.append("Invalid service account key format")
                        return False
                except json.JSONDecodeError:
                    print_error("Service account key is not valid JSON")
                    self.errors.append("Service account key JSON parsing failed")
                    return False
            else:
                print_error("GCP_SERVICE_ACCOUNT_KEY secret not set")
                self.errors.append("Missing GCP_SERVICE_ACCOUNT_KEY secret")
                return False
        else:
            print_info("Not running in GitHub Actions")
            print_warning("Cannot validate GitHub secrets outside of Actions")
            print_info("Please ensure GCP_SERVICE_ACCOUNT_KEY secret is set in:")
            print_info("  Repository Settings > Secrets and variables > Actions")
            self.warnings.append("GitHub secrets validation skipped (not in Actions)")
        
        return True
    
    def check_git_setup(self) -> bool:
        """Check Git configuration"""
        print_header("Checking Git Configuration")
        
        try:
            # Check if Git is installed
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
            print_success(f"Git installed: {result.stdout.strip()}")
            
            # Check if in a Git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, text=True, check=True)
            print_success("In a Git repository")
            
            # Check remote
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                print_success("Git remote configured")
                self.passed_checks.append("Git repository properly configured")
            else:
                print_warning("No Git remote configured")
                self.warnings.append("Git remote not configured")
            
            # Check current branch
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            if current_branch:
                print_success(f"Current branch: {current_branch}")
            
            return True
            
        except subprocess.CalledProcessError:
            print_error("Git is not installed or not a Git repository")
            self.errors.append("Git not properly configured")
            return False
        except FileNotFoundError:
            print_error("Git is not installed")
            self.errors.append("Git not installed")
            return False
    
    def check_dependencies(self) -> bool:
        """Check required dependencies"""
        print_header("Checking Dependencies")
        
        # Check Python packages
        required_packages = [
            ('yaml', 'PyYAML'),
            ('google.auth', 'google-auth'),
            ('googleapiclient', 'google-api-python-client')
        ]
        
        all_installed = True
        for module, package_name in required_packages:
            try:
                __import__(module)
                print_success(f"Python package installed: {package_name}")
            except ImportError:
                print_error(f"Missing Python package: {package_name}")
                print_info(f"  Install with: pip install {package_name}")
                self.errors.append(f"Missing dependency: {package_name}")
                all_installed = False
        
        # Check for clasp (optional but recommended)
        try:
            result = subprocess.run(['clasp', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"clasp installed: {result.stdout.strip()}")
                self.passed_checks.append("clasp CLI installed")
            else:
                print_warning("clasp not found (optional but recommended)")
                print_info("  Install with: npm install -g @google/clasp")
                self.warnings.append("clasp not installed")
        except FileNotFoundError:
            print_warning("clasp not found (optional but recommended)")
            print_info("  Install with: npm install -g @google/clasp")
            self.warnings.append("clasp not installed")
        
        return all_installed
    
    def check_assets(self) -> bool:
        """Check marketplace assets"""
        print_header("Checking Marketplace Assets")
        
        # Load config to get asset location
        if not os.path.exists('marketplace-config.yaml'):
            print_warning("Config not found, skipping asset validation")
            return True
        
        with open('marketplace-config.yaml') as f:
            config = yaml.safe_load(f)
        
        asset_location = self._get_nested(config, 'marketplace.asset_location', 'external')
        
        if asset_location == 'repo':
            # Check if Pillow is installed for image validation
            try:
                from PIL import Image
                
                # Check icon
                icon_path = self._get_nested(config, 'marketplace.assets.icon.repo_path', '')
                if icon_path and os.path.exists(icon_path):
                    try:
                        img = Image.open(icon_path)
                        if img.size == (128, 128) and img.format == 'PNG':
                            print_success(f"Icon valid: {icon_path} (128x128 PNG)")
                            self.passed_checks.append("Icon dimensions correct")
                        else:
                            print_warning(f"Icon should be 128x128 PNG, found {img.size} {img.format}")
                            self.warnings.append(f"Icon format issue: {img.size} {img.format}")
                    except Exception as e:
                        print_error(f"Cannot open icon: {e}")
                        self.errors.append(f"Icon validation error: {e}")
                
                # Check screenshots
                screenshots = self._get_nested(config, 'marketplace.assets.screenshots', [])
                for idx, screenshot in enumerate(screenshots):
                    ss_path = screenshot.get('repo_path', '')
                    if ss_path and os.path.exists(ss_path):
                        try:
                            img = Image.open(ss_path)
                            if img.size == (1280, 800) and img.format == 'PNG':
                                print_success(f"Screenshot {idx+1} valid: {ss_path}")
                            else:
                                print_warning(f"Screenshot {idx+1} should be 1280x800 PNG, found {img.size} {img.format}")
                                self.warnings.append(f"Screenshot {idx+1} format issue")
                        except Exception as e:
                            print_error(f"Cannot open screenshot {idx+1}: {e}")
                            self.errors.append(f"Screenshot {idx+1} error: {e}")
                
            except ImportError:
                print_warning("Pillow not installed, cannot validate image dimensions")
                print_info("  Install with: pip install Pillow")
                self.warnings.append("Cannot validate images without Pillow")
        else:
            print_info("Assets use external URLs, validation skipped")
            print_info("Ensure external URLs are accessible and use HTTPS")
        
        return True
    
    def _get_nested(self, d: dict, path: str, default=None):
        """Get nested dictionary value using dot notation"""
        keys = path.split('.')
        value = d
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def print_summary(self):
        """Print validation summary"""
        print_header("Validation Summary")
        
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Passed: {len(self.passed_checks)}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠ Warnings: {len(self.warnings)}{Colors.END}")
        print(f"  {Colors.RED}✗ Errors: {len(self.errors)}{Colors.END}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠ {warning}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}✗ {error}{Colors.END}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.END}")
            print(f"{Colors.RED}Please fix the errors above before deploying.{Colors.END}")
            return False
        elif self.warnings:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ VALIDATION PASSED WITH WARNINGS{Colors.END}")
            print(f"{Colors.YELLOW}Consider addressing warnings for best results.{Colors.END}")
            return True
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ VALIDATION SUCCESSFUL{Colors.END}")
            print(f"{Colors.GREEN}Your setup is ready for deployment!{Colors.END}")
            return True
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "  Google Apps Script Marketplace Setup Validator".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "═" * 58 + "╝")
        print(Colors.END)
        
        checks = [
            self.check_files,
            self.check_config,
            self.check_appsscript_manifest,
            self.check_git_setup,
            self.check_dependencies,
            self.check_assets,
            self.check_github_secrets
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                print_error(f"Check failed with exception: {e}")
                self.errors.append(f"Check exception: {e}")
        
        return self.print_summary()

def main():
    """Main entry point"""
    validator = SetupValidator()
    success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()