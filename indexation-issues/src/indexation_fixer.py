#!/usr/bin/env python3
"""
Indexation Fixer - Automated fixes for SEO indexation issues
Can work standalone or with analysis results from the analyzer
"""

import os
import json
import yaml
import re
import logging
import shutil
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
import hashlib
import requests
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FixResult:
    """Result of applying a fix"""
    success: bool
    fix_type: str
    file_path: str
    details: Dict
    error: Optional[str] = None

class IndexationFixer:
    """Automated fixer for indexation issues"""
    
    def __init__(self, site_url: str = "", site_type: str = "jekyll", dry_run: bool = False):
        self.site_url = site_url.rstrip('/') if site_url else ""
        self.site_type = site_type.lower()
        self.dry_run = dry_run
        self.changes_log = []
        self.backup_dir = None
        
        # Safety limits
        self.max_files_per_batch = 100
        self.max_redirects = 50
        self.max_robots_rules = 10
        
        # Content directories by site type
        self.content_dirs = {
            "jekyll": ["_posts", "_pages", "content", "_drafts"],
            "hugo": ["content/posts", "content/pages", "content", "content/blog"]
        }
        
        # File patterns to skip
        self.skip_patterns = [
            r'\.git/',
            r'node_modules/',
            r'_site/',
            r'public/',
            r'dist/',
            r'\.bundle/',
            r'vendor/'
        ]
    
    def create_backup(self) -> bool:
        """Create comprehensive backup before making changes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = f"indexation_backup_{timestamp}"
            
            if os.path.exists(self.backup_dir):
                shutil.rmtree(self.backup_dir)
            
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Backup content directories
            backed_up_dirs = []
            for content_dir in self._get_content_directories():
                if os.path.exists(content_dir):
                    dest_dir = os.path.join(self.backup_dir, content_dir)
                    shutil.copytree(content_dir, dest_dir)
                    backed_up_dirs.append(content_dir)
            
            # Backup important configuration files
            config_files = [
                "robots.txt", "_config.yml", "config.yaml", "config.toml",
                "_site/robots.txt", "public/robots.txt", "static/robots.txt"
            ]
            
            backed_up_files = []
            for config_file in config_files:
                if os.path.exists(config_file):
                    dest_path = os.path.join(self.backup_dir, os.path.basename(config_file))
                    shutil.copy2(config_file, dest_path)
                    backed_up_files.append(config_file)
            
            # Create backup manifest
            manifest = {
                "timestamp": timestamp,
                "site_url": self.site_url,
                "site_type": self.site_type,
                "backed_up_directories": backed_up_dirs,
                "backed_up_files": backed_up_files,
                "total_files": sum(len(list(Path(d).rglob("*"))) for d in backed_up_dirs if os.path.exists(d))
            }
            
            with open(os.path.join(self.backup_dir, "manifest.json"), 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Backup created: {self.backup_dir}")
            logger.info(f"Backed up {len(backed_up_dirs)} directories and {len(backed_up_files)} files")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup directory not found: {backup_path}")
                return False
            
            manifest_path = os.path.join(backup_path, "manifest.json")
            if not os.path.exists(manifest_path):
                logger.error("Backup manifest not found")
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            logger.info(f"Restoring backup from {manifest['timestamp']}")
            
            # Restore directories
            for dir_name in manifest["backed_up_directories"]:
                backup_dir_path = os.path.join(backup_path, dir_name)
                if os.path.exists(backup_dir_path):
                    if os.path.exists(dir_name):
                        shutil.rmtree(dir_name)
                    shutil.copytree(backup_dir_path, dir_name)
                    logger.info(f"Restored directory: {dir_name}")
            
            # Restore files
            for file_name in manifest["backed_up_files"]:
                backup_file_path = os.path.join(backup_path, os.path.basename(file_name))
                if os.path.exists(backup_file_path):
                    shutil.copy2(backup_file_path, file_name)
                    logger.info(f"Restored file: {file_name}")
            
            logger.info("Backup restoration completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def fix_noindex_issues(self, limit: Optional[int] = None) -> List[FixResult]:
        """Fix pages with noindex issues"""
        logger.info("Scanning for noindex issues...")
        results = []
        files_processed = 0
        
        try:
            for content_dir in self._get_content_directories():
                if not os.path.exists(content_dir):
                    continue
                
                for file_path in Path(content_dir).rglob("*.md"):
                    if limit and files_processed >= limit:
                        break
                    
                    if self._should_skip_file(str(file_path)):
                        continue
                    
                    try:
                        result = self._fix_single_noindex_issue(str(file_path))
                        if result:
                            results.append(result)
                            files_processed += 1
                    except Exception as e:
                        logger.warning(f"Error processing {file_path}: {e}")
                        continue
            
            logger.info(f"Fixed {len([r for r in results if r.success])} noindex issues")
            return results
            
        except Exception as e:
            logger.error(f"Error fixing noindex issues: {e}")
            return results
    
    def _fix_single_noindex_issue(self, file_path: str) -> Optional[FixResult]:
        """Fix noindex issue in a single file"""
        try:
            front_matter, content = self._parse_front_matter(file_path)
            
            changes_made = []
            issues_found = []
            
            # Check for various noindex conditions
            if front_matter.get('published') == False:
                if len(content.strip()) > 200:  # Only fix if there's substantial content
                    front_matter['published'] = True
                    changes_made.append("Set published: true")
                else:
                    issues_found.append("published: false (content too short)")
            
            if front_matter.get('noindex') == True:
                del front_matter['noindex']
                changes_made.append("Removed noindex: true")
            
            if front_matter.get('draft') == True:
                front_matter['draft'] = False
                changes_made.append("Set draft: false")
            
            if 'robots' in front_matter:
                robots_value = str(front_matter['robots']).lower()
                if 'noindex' in robots_value:
                    front_matter['robots'] = 'index, follow'
                    changes_made.append("Updated robots directive")
            
            if changes_made:
                if not self.dry_run:
                    success = self._save_front_matter(file_path, front_matter, content)
                else:
                    success = True  # Assume success in dry run
                
                self._log_change({
                    "type": "noindex_fixed",
                    "file": file_path,
                    "changes": changes_made
                })
                
                return FixResult(
                    success=success,
                    fix_type="noindex",
                    file_path=file_path,
                    details={"changes": changes_made, "issues_found": issues_found}
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="noindex",
                file_path=file_path,
                details={},
                error=str(e)
            )
    
    def fix_robots_txt_issues(self) -> List[FixResult]:
        """Fix robots.txt blocking issues"""
        logger.info("Scanning for robots.txt issues...")
        results = []
        
        try:
            # Find robots.txt file
            robots_paths = ["robots.txt", "_site/robots.txt", "public/robots.txt", "static/robots.txt"]
            robots_file = None
            
            for path in robots_paths:
                if os.path.exists(path):
                    robots_file = path
                    break
            
            if not robots_file:
                logger.info("No robots.txt file found")
                return results
            
            with open(robots_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyze disallow rules
            problematic_rules = self._find_problematic_robots_rules(content)
            
            if not problematic_rules:
                logger.info("No problematic robots.txt rules found")
                return results
            
            # Create backup of robots.txt
            backup_path = f"{robots_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if not self.dry_run:
                shutil.copy2(robots_file, backup_path)
            
            # Fix robots.txt
            new_content = self._fix_robots_content(content, problematic_rules)
            
            if not self.dry_run:
                with open(robots_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            self._log_change({
                "type": "robots_fixed",
                "file": robots_file,
                "backup": backup_path,
                "rules_removed": problematic_rules
            })
            
            results.append(FixResult(
                success=True,
                fix_type="robots_txt",
                file_path=robots_file,
                details={
                    "rules_removed": problematic_rules,
                    "backup_path": backup_path
                }
            ))
            
            logger.info(f"Fixed robots.txt: removed {len(problematic_rules)} problematic rules")
            return results
            
        except Exception as e:
            logger.error(f"Error fixing robots.txt: {e}")
            results.append(FixResult(
                success=False,
                fix_type="robots_txt",
                file_path=robots_file or "robots.txt",
                details={},
                error=str(e)
            ))
            return results
    
    def fix_broken_internal_links(self, create_redirects: bool = True) -> List[FixResult]:
        """Fix broken internal links"""
        logger.info("Scanning for broken internal links...")
        results = []
        
        try:
            # Extract all internal links
            link_map = self._extract_internal_links()
            broken_links = self._find_broken_links(link_map)
            
            logger.info(f"Found {len(broken_links)} broken internal links")
            
            if not broken_links:
                return results
            
            # Process each broken link
            for broken_url, link_info in broken_links.items():
                try:
                    # Try to find replacement
                    replacement_url = self._find_replacement_url(broken_url)
                    
                    if replacement_url:
                        # Update internal links
                        for referring_file in link_info["referring_files"]:
                            result = self._update_links_in_file(
                                referring_file, broken_url, replacement_url
                            )
                            if result:
                                results.append(result)
                        
                        # Create redirect if requested
                        if create_redirects:
                            redirect_result = self._create_redirect(broken_url, replacement_url)
                            if redirect_result:
                                results.append(redirect_result)
                    else:
                        # Remove broken links (manual review recommended)
                        for referring_file in link_info["referring_files"]:
                            results.append(FixResult(
                                success=False,
                                fix_type="broken_link_removal",
                                file_path=referring_file,
                                details={
                                    "broken_url": broken_url,
                                    "action": "manual_review_required"
                                },
                                error="No replacement found - manual review required"
                            ))
                
                except Exception as e:
                    logger.warning(f"Error processing broken link {broken_url}: {e}")
                    continue
            
            successful_fixes = len([r for r in results if r.success])
            logger.info(f"Fixed {successful_fixes} broken link issues")
            return results
            
        except Exception as e:
            logger.error(f"Error fixing broken links: {e}")
            return results
    
    def fix_canonical_issues(self) -> List[FixResult]:
        """Fix canonical tag issues"""
        logger.info("Scanning for canonical issues...")
        results = []
        
        try:
            # Find duplicate content
            content_hashes = {}
            duplicate_groups = []
            
            for content_dir in self._get_content_directories():
                if not os.path.exists(content_dir):
                    continue
                
                for file_path in Path(content_dir).rglob("*.md"):
                    if self._should_skip_file(str(file_path)):
                        continue
                    
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        # Generate content hash
                        content_clean = re.sub(r'\s+', ' ', content[:1000]).strip().lower()
                        content_hash = hashlib.md5(content_clean.encode()).hexdigest()
                        
                        url = self._get_url_from_file_path(str(file_path))
                        
                        page_info = {
                            "file_path": str(file_path),
                            "url": url,
                            "canonical_url": front_matter.get('canonical_url'),
                            "content_length": len(content),
                            "front_matter": front_matter
                        }
                        
                        if content_hash in content_hashes:
                            # Found duplicate
                            original = content_hashes[content_hash]
                            duplicate_groups.append({
                                "original": original,
                                "duplicate": page_info,
                                "content_hash": content_hash
                            })
                        else:
                            content_hashes[content_hash] = page_info
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing {file_path} for duplicates: {e}")
                        continue
            
            # Fix duplicate content issues
            for group in duplicate_groups:
                duplicate_page = group["duplicate"]
                original_page = group["original"]
                
                # Add canonical URL to duplicate
                if not duplicate_page["canonical_url"]:
                    result = self._add_canonical_url(
                        duplicate_page["file_path"], 
                        original_page["url"]
                    )
                    if result:
                        results.append(result)
            
            logger.info(f"Fixed {len([r for r in results if r.success])} canonical issues")
            return results
            
        except Exception as e:
            logger.error(f"Error fixing canonical issues: {e}")
            return results
    
    def improve_content_quality(self, limit: Optional[int] = None) -> List[FixResult]:
        """Improve content quality issues"""
        logger.info("Scanning for content quality issues...")
        results = []
        files_processed = 0
        
        try:
            for content_dir in self._get_content_directories():
                if not os.path.exists(content_dir):
                    continue
                
                for file_path in Path(content_dir).rglob("*.md"):
                    if limit and files_processed >= limit:
                        break
                    
                    if self._should_skip_file(str(file_path)):
                        continue
                    
                    try:
                        result = self._improve_single_content(str(file_path))
                        if result:
                            results.append(result)
                            files_processed += 1
                    except Exception as e:
                        logger.warning(f"Error improving {file_path}: {e}")
                        continue
            
            logger.info(f"Improved {len([r for r in results if r.success])} content quality issues")
            return results
            
        except Exception as e:
            logger.error(f"Error improving content quality: {e}")
            return results
    
    def _improve_single_content(self, file_path: str) -> Optional[FixResult]:
        """Improve content quality for a single file"""
        try:
            front_matter, content = self._parse_front_matter(file_path)
            
            improvements = []
            
            # Add missing title
            if not front_matter.get('title'):
                suggested_title = self._generate_title(file_path, content)
                if suggested_title:
                    front_matter['title'] = suggested_title
                    improvements.append(f"Added title: {suggested_title}")
            
            # Add missing description
            if not front_matter.get('description'):
                suggested_description = self._generate_description(content)
                if suggested_description:
                    front_matter['description'] = suggested_description
                    improvements.append("Added meta description")
            
            # Add missing date for posts
            if "_posts" in file_path and not front_matter.get('date'):
                date = self._extract_date_from_filename(file_path)
                if date:
                    front_matter['date'] = date
                    improvements.append(f"Added date: {date}")
            
            if improvements:
                if not self.dry_run:
                    success = self._save_front_matter(file_path, front_matter, content)
                else:
                    success = True
                
                self._log_change({
                    "type": "content_improved",
                    "file": file_path,
                    "improvements": improvements
                })
                
                return FixResult(
                    success=success,
                    fix_type="content_quality",
                    file_path=file_path,
                    details={"improvements": improvements}
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="content_quality",
                file_path=file_path,
                details={},
                error=str(e)
            )
    
    def run_comprehensive_fix(self, 
                            fix_noindex: bool = True,
                            fix_robots: bool = True,
                            fix_broken_links: bool = True,
                            fix_canonical: bool = True,
                            improve_content: bool = True,
                            create_redirects: bool = True,
                            limits: Optional[Dict[str, int]] = None) -> Dict:
        """Run comprehensive fix operation"""
        
        if not self.dry_run:
            logger.info("Creating backup before applying fixes...")
            if not self.create_backup():
                return {"error": "Failed to create backup - aborting"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "backup_dir": self.backup_dir,
            "fixes": {},
            "summary": {
                "total_fixes_attempted": 0,
                "total_fixes_successful": 0,
                "total_fixes_failed": 0
            }
        }
        
        limits = limits or {}
        
        try:
            # Fix noindex issues
            if fix_noindex:
                logger.info("Running noindex fixes...")
                noindex_results = self.fix_noindex_issues(limits.get('noindex'))
                results["fixes"]["noindex"] = [r.__dict__ for r in noindex_results]
                results["summary"]["total_fixes_attempted"] += len(noindex_results)
                results["summary"]["total_fixes_successful"] += len([r for r in noindex_results if r.success])
            
            # Fix robots.txt issues
            if fix_robots:
                logger.info("Running robots.txt fixes...")
                robots_results = self.fix_robots_txt_issues()
                results["fixes"]["robots_txt"] = [r.__dict__ for r in robots_results]
                results["summary"]["total_fixes_attempted"] += len(robots_results)
                results["summary"]["total_fixes_successful"] += len([r for r in robots_results if r.success])
            
            # Fix broken links
            if fix_broken_links:
                logger.info("Running broken link fixes...")
                link_results = self.fix_broken_internal_links(create_redirects)
                results["fixes"]["broken_links"] = [r.__dict__ for r in link_results]
                results["summary"]["total_fixes_attempted"] += len(link_results)
                results["summary"]["total_fixes_successful"] += len([r for r in link_results if r.success])
            
            # Fix canonical issues
            if fix_canonical:
                logger.info("Running canonical fixes...")
                canonical_results = self.fix_canonical_issues()
                results["fixes"]["canonical"] = [r.__dict__ for r in canonical_results]
                results["summary"]["total_fixes_attempted"] += len(canonical_results)
                results["summary"]["total_fixes_successful"] += len([r for r in canonical_results if r.success])
            
            # Improve content quality
            if improve_content:
                logger.info("Running content quality improvements...")
                content_results = self.improve_content_quality(limits.get('content_quality'))
                results["fixes"]["content_quality"] = [r.__dict__ for r in content_results]
                results["summary"]["total_fixes_attempted"] += len(content_results)
                results["summary"]["total_fixes_successful"] += len([r for r in content_results if r.success])
            
            results["summary"]["total_fixes_failed"] = (
                results["summary"]["total_fixes_attempted"] - 
                results["summary"]["total_fixes_successful"]
            )
            
            # Log summary
            summary = results["summary"]
            logger.info(f"Fix operation completed:")
            logger.info(f"  Total fixes attempted: {summary['total_fixes_attempted']}")
            logger.info(f"  Successful fixes: {summary['total_fixes_successful']}")
            logger.info(f"  Failed fixes: {summary['total_fixes_failed']}")
            
            if self.backup_dir:
                logger.info(f"  Backup created: {self.backup_dir}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during comprehensive fix: {e}")
            results["error"] = str(e)
            return results
    
    # Helper methods
    def _get_content_directories(self) -> List[str]:
        """Get content directories for site type"""
        return self.content_dirs.get(self.site_type, ["content"])
    
    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped"""
        for pattern in self.skip_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def _parse_front_matter(self, file_path: str) -> Tuple[Dict, str]:
        """Parse YAML front matter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    try:
                        front_matter = yaml.safe_load(parts[1]) or {}
                        body = parts[2]
                        return front_matter, body
                    except yaml.YAMLError as e:
                        logger.warning(f"YAML error in {file_path}: {e}")
                        return {}, content
            
            return {}, content
            
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
            return {}, ""
    
    def _save_front_matter(self, file_path: str, front_matter: Dict, content: str) -> bool:
        """Save front matter and content"""
        try:
            if not front_matter:
                new_content = content
            else:
                yaml_content = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
                new_content = f"---\n{yaml_content}---\n{content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def _get_url_from_file_path(self, file_path: str) -> str:
        """Convert file path to URL"""
        try:
            if self.site_type == "jekyll":
                if "_posts" in file_path:
                    filename = os.path.basename(file_path)
                    if re.match(r'\d{4}-\d{2}-\d{2}-.+\.md$', filename):
                        date_part = filename[:10]
                        title_part = filename[11:-3]
                        year, month, day = date_part.split('-')
                        return f"/{year}/{month}/{day}/{title_part}/"
                
                if "_pages" in file_path:
                    rel_path = os.path.relpath(file_path, "_pages")
                    return "/" + rel_path.replace('.md', '/')
            
            else:  # Hugo
                if "content" in file_path:
                    rel_path = os.path.relpath(file_path, "content")
                    if rel_path.endswith('/index.md'):
                        return "/" + os.path.dirname(rel_path) + "/"
                    else:
                        return "/" + rel_path.replace('.md', '/')
            
            # Fallback
            return "/" + os.path.basename(file_path).replace('.md', '/')
            
        except Exception as e:
            logger.warning(f"Error converting path to URL {file_path}: {e}")
            return "/" + os.path.basename(file_path).replace('.md', '/')
    
    def _find_problematic_robots_rules(self, robots_content: str) -> List[str]:
        """Find problematic disallow rules in robots.txt"""
        problematic_rules = []
        lines = robots_content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('Disallow:') and (current_user_agent in ['*', 'Googlebot'] or current_user_agent is None):
                rule = line.split(':', 1)[1].strip()
                
                # Rules that are likely problematic
                if rule in ['/', '/blog/', '/posts/', '/content/']:
                    problematic_rules.append(rule)
                elif rule.endswith('*') and len(rule) < 10:  # Very broad wildcards
                    problematic_rules.append(rule)
        
        return problematic_rules
    
    def _fix_robots_content(self, content: str, rules_to_remove: List[str]) -> str:
        """Remove problematic rules from robots.txt content"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('Disallow:'):
                rule = line.split(':', 1)[1].strip()
                if rule not in rules_to_remove:
                    new_lines.append(line)
                # Skip lines with problematic rules
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _extract_internal_links(self) -> Dict[str, Dict]:
        """Extract all internal links from content files"""
        link_map = {}
        
        for content_dir in self._get_content_directories():
            if not os.path.exists(content_dir):
                continue
            
            for file_path in Path(content_dir).rglob("*.md"):
                if self._should_skip_file(str(file_path)):
                    continue
                
                try:
                    _, content = self._parse_front_matter(str(file_path))
                    
                    # Find markdown links
                    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
                    matches = re.findall(link_pattern, content)
                    
                    for link_text, link_url in matches:
                        # Skip external links
                        if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                            continue
                        
                        # Normalize internal URLs
                        if not link_url.startswith('/'):
                            link_url = '/' + link_url
                        
                        if link_url not in link_map:
                            link_map[link_url] = {
                                "referring_files": [],
                                "link_texts": set()
                            }
                        
                        link_map[link_url]["referring_files"].append(str(file_path))
                        link_map[link_url]["link_texts"].add(link_text)
                
                except Exception as e:
                    logger.warning(f"Error extracting links from {file_path}: {e}")
                    continue
        
        return link_map
    
    def _find_broken_links(self, link_map: Dict[str, Dict]) -> Dict[str, Dict]:
        """Find broken internal links by testing URLs"""
        broken_links = {}
        
        for url, info in link_map.items():
            try:
                full_url = urljoin(self.site_url, url)
                
                # Quick check if file exists locally first
                local_exists = self._check_local_file_exists(url)
                if local_exists:
                    continue
                
                # Test URL if site is accessible
                if self.site_url.startswith('http'):
                    try:
                        response = requests.head(full_url, timeout=5, allow_redirects=True)
                        if response.status_code == 404:
                            broken_links[url] = info
                    except requests.RequestException:
                        # If we can't test, assume it might be broken for local analysis
                        broken_links[url] = info
                else:
                    # For local analysis without HTTP, just check file existence
                    broken_links[url] = info
            
            except Exception as e:
                logger.warning(f"Error checking link {url}: {e}")
                continue
        
        return broken_links
    
    def _check_local_file_exists(self, url: str) -> bool:
        """Check if a local file exists for the given URL"""
        try:
            # Convert URL back to potential file paths
            url_clean = url.strip('/')
            
            for content_dir in self._get_content_directories():
                if not os.path.exists(content_dir):
                    continue
                
                # Try different path combinations
                potential_paths = [
                    os.path.join(content_dir, f"{url_clean}.md"),
                    os.path.join(content_dir, url_clean, "index.md"),
                    os.path.join(content_dir, f"{url_clean}/index.md"),
                ]
                
                # For Jekyll posts, check date-prefixed format
                if self.site_type == "jekyll":
                    # Try to find posts with date prefix
                    posts_dir = "_posts"
                    if os.path.exists(posts_dir):
                        for post_file in Path(posts_dir).glob("*.md"):
                            post_name = post_file.name
                            if post_name.endswith(f"-{url_clean}.md"):
                                return True
                
                for path in potential_paths:
                    if os.path.exists(path):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking local file for {url}: {e}")
            return False
    
    def _find_replacement_url(self, broken_url: str) -> Optional[str]:
        """Find a suitable replacement URL for a broken link"""
        try:
            # Extract keywords from broken URL
            url_parts = broken_url.strip('/').split('/')
            keywords = []
            
            for part in url_parts:
                words = re.split(r'[-_\s]+', part)
                keywords.extend([w.lower() for w in words if len(w) > 2])
            
            if not keywords:
                return None
            
            # Search for similar content
            best_match = None
            best_score = 0
            
            for content_dir in self._get_content_directories():
                if not os.path.exists(content_dir):
                    continue
                
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        # Calculate similarity score
                        score = 0
                        title = str(front_matter.get('title', '')).lower()
                        file_name = os.path.basename(str(file_path)).lower()
                        content_snippet = content[:500].lower()
                        
                        for keyword in keywords:
                            if keyword in title:
                                score += 3
                            if keyword in file_name:
                                score += 2
                            if keyword in content_snippet:
                                score += 1
                        
                        if score > best_score and score >= 2:
                            best_score = score
                            best_match = self._get_url_from_file_path(str(file_path))
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing replacement candidate {file_path}: {e}")
                        continue
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding replacement for {broken_url}: {e}")
            return None
    
    def _update_links_in_file(self, file_path: str, old_url: str, new_url: str) -> Optional[FixResult]:
        """Update links in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace markdown links
            old_pattern = f"]({old_url})"
            new_pattern = f"]({new_url})"
            
            if old_pattern in content:
                new_content = content.replace(old_pattern, new_pattern)
                
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                self._log_change({
                    "type": "link_updated",
                    "file": file_path,
                    "old_url": old_url,
                    "new_url": new_url
                })
                
                return FixResult(
                    success=True,
                    fix_type="link_update",
                    file_path=file_path,
                    details={
                        "old_url": old_url,
                        "new_url": new_url
                    }
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="link_update",
                file_path=file_path,
                details={"old_url": old_url, "new_url": new_url},
                error=str(e)
            )
    
    def _create_redirect(self, from_url: str, to_url: str) -> Optional[FixResult]:
        """Create a redirect from old URL to new URL"""
        try:
            if self.site_type == "jekyll":
                success = self._create_jekyll_redirect(from_url, to_url)
            else:  # Hugo
                success = self._create_hugo_redirect(from_url, to_url)
            
            if success:
                self._log_change({
                    "type": "redirect_created",
                    "from_url": from_url,
                    "to_url": to_url
                })
                
                return FixResult(
                    success=True,
                    fix_type="redirect_creation",
                    file_path=f"redirect_{from_url.replace('/', '_')}",
                    details={
                        "from_url": from_url,
                        "to_url": to_url,
                        "site_type": self.site_type
                    }
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="redirect_creation",
                file_path=f"redirect_{from_url.replace('/', '_')}",
                details={"from_url": from_url, "to_url": to_url},
                error=str(e)
            )
    
    def _create_jekyll_redirect(self, from_url: str, to_url: str) -> bool:
        """Create Jekyll redirect page"""
        try:
            redirect_dir = "_redirects"
            
            if not self.dry_run:
                os.makedirs(redirect_dir, exist_ok=True)
            
            # Clean filename
            filename = from_url.strip('/').replace('/', '-').replace(' ', '-') + '.md'
            redirect_file = os.path.join(redirect_dir, filename)
            
            redirect_content = f"""---
layout: redirect
redirect_to: {to_url}
permalink: {from_url}
sitemap: false
---

This page has moved to [{to_url}]({to_url}).
"""
            
            if not self.dry_run:
                with open(redirect_file, 'w', encoding='utf-8') as f:
                    f.write(redirect_content)
            
            logger.info(f"Created Jekyll redirect: {from_url} → {to_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Jekyll redirect: {e}")
            return False
    
    def _create_hugo_redirect(self, from_url: str, to_url: str) -> bool:
        """Create Hugo redirect page"""
        try:
            redirect_dir = "content/redirects"
            
            if not self.dry_run:
                os.makedirs(redirect_dir, exist_ok=True)
            
            # Clean filename
            filename = from_url.strip('/').replace('/', '-').replace(' ', '-') + '.md'
            redirect_file = os.path.join(redirect_dir, filename)
            
            redirect_content = f"""---
title: "Redirected"
aliases:
  - {from_url}
url: {to_url}
sitemap: false
---

<script>
window.location.replace("{to_url}");
</script>

<meta http-equiv="refresh" content="0; url={to_url}">

This page has moved to [{to_url}]({to_url}).
"""
            
            if not self.dry_run:
                with open(redirect_file, 'w', encoding='utf-8') as f:
                    f.write(redirect_content)
            
            logger.info(f"Created Hugo redirect: {from_url} → {to_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Hugo redirect: {e}")
            return False
    
    def _add_canonical_url(self, file_path: str, canonical_url: str) -> Optional[FixResult]:
        """Add canonical URL to front matter"""
        try:
            front_matter, content = self._parse_front_matter(file_path)
            
            if front_matter.get('canonical_url'):
                return None  # Already has canonical URL
            
            front_matter['canonical_url'] = canonical_url
            
            if not self.dry_run:
                success = self._save_front_matter(file_path, front_matter, content)
            else:
                success = True
            
            if success:
                self._log_change({
                    "type": "canonical_added",
                    "file": file_path,
                    "canonical_url": canonical_url
                })
                
                return FixResult(
                    success=True,
                    fix_type="canonical_addition",
                    file_path=file_path,
                    details={"canonical_url": canonical_url}
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="canonical_addition",
                file_path=file_path,
                details={"canonical_url": canonical_url},
                error=str(e)
            )
    
    def _generate_title(self, file_path: str, content: str) -> Optional[str]:
        """Generate title from content or filename"""
        try:
            # Look for first H1 heading
            h1_match = re.search(r'^#\s+(.+), content, re.MULTILINE)
            if h1_match:
                return h1_match.group(1).strip()
            
            # Look for first H2 heading
            h2_match = re.search(r'^##\s+(.+), content, re.MULTILINE)
            if h2_match:
                return h2_match.group(1).strip()
            
            # Generate from filename
            filename = os.path.basename(file_path)
            if filename.endswith('.md'):
                filename = filename[:-3]
            
            # Remove date prefix for Jekyll posts
            filename = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
            
            # Convert to title case
            title = filename.replace('-', ' ').replace('_', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            
            return title if len(title) > 3 else None
            
        except Exception as e:
            logger.warning(f"Error generating title for {file_path}: {e}")
            return None
    
    def _generate_description(self, content: str) -> Optional[str]:
        """Generate meta description from content"""
        try:
            # Find first substantial paragraph
            paragraphs = content.split('\n\n')
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                
                # Skip headings, code blocks, and short paragraphs
                if (paragraph.startswith('#') or 
                    paragraph.startswith('```') or 
                    len(paragraph) < 50):
                    continue
                
                # Clean markdown formatting
                clean_text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', paragraph)  # Links
                clean_text = re.sub(r'\*\*([^*]*)\*\*', r'\1', clean_text)  # Bold
                clean_text = re.sub(r'\*([^*]*)\*', r'\1', clean_text)  # Italic
                clean_text = re.sub(r'`([^`]*)`', r'\1', clean_text)  # Code
                clean_text = re.sub(r'\n+', ' ', clean_text)  # Line breaks
                clean_text = clean_text.strip()
                
                # Truncate to appropriate meta description length
                if len(clean_text) > 160:
                    clean_text = clean_text[:157] + '...'
                
                return clean_text
            
            return None
            
        except Exception as e:
            logger.warning(f"Error generating description: {e}")
            return None
    
    def _extract_date_from_filename(self, file_path: str) -> Optional[str]:
        """Extract date from Jekyll post filename"""
        try:
            filename = os.path.basename(file_path)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-.+\.md, filename)
            if date_match:
                return date_match.group(1)
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting date from {file_path}: {e}")
            return None
    
    def _log_change(self, change: Dict):
        """Log a change for tracking"""
        change["timestamp"] = datetime.now().isoformat()
        self.changes_log.append(change)
    
    def export_results(self, results: Dict, output_file: Optional[str] = None) -> str:
        """Export fix results to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_file or f"indexation_fixes_{timestamp}.json"
            
            export_data = {
                **results,
                "changes_log": self.changes_log,
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return ""

    def apply_fixes(self, analysis_results: Dict, fix_types: Optional[List[str]] = None) -> Dict:
        """Apply fixes from analysis results - GitHub Actions compatible interface"""
        if not analysis_results or "indexation_issues" not in analysis_results:
            return {
                "error": "No analysis results provided",
                "fixes_applied": 0,
                "fixes_failed": 0,
                "fixes_skipped": 0
            }
        
        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "fixes_applied": 0,
            "fixes_failed": 0,
            "fixes_skipped": 0,
            "details": []
        }
        
        try:
            # Create backup if not dry run
            if not self.dry_run and not self.create_backup():
                return {
                    "error": "Failed to create backup",
                    "fixes_applied": 0,
                    "fixes_failed": 0,
                    "fixes_skipped": 0
                }
            
            # Process each issue type
            for issue_type, issue_data in analysis_results.get("indexation_issues", {}).items():
                if fix_types and issue_type not in fix_types:
                    fix_results["fixes_skipped"] += len(issue_data.get("pages", []))
                    continue
                
                # Apply fixes based on issue type
                if issue_type == "noindex_tag":
                    results = self._apply_noindex_fixes_from_analysis(issue_data)
                elif issue_type == "blocked_robots_txt":
                    results = self._apply_robots_fixes_from_analysis(issue_data)
                elif issue_type == "canonical_issues":
                    results = self._apply_canonical_fixes_from_analysis(issue_data)
                elif issue_type == "crawled_not_indexed":
                    results = self._apply_content_quality_fixes_from_analysis(issue_data)
                else:
                    logger.warning(f"Unsupported fix type: {issue_type}")
                    fix_results["fixes_skipped"] += len(issue_data.get("pages", []))
                    continue
                
                # Aggregate results
                for result in results:
                    if result.success:
                        fix_results["fixes_applied"] += 1
                    else:
                        fix_results["fixes_failed"] += 1
                    
                    fix_results["details"].append({
                        "issue_type": issue_type,
                        "fix_type": result.fix_type,
                        "file_path": result.file_path,
                        "success": result.success,
                        "details": result.details,
                        "error": result.error
                    })
            
            return fix_results
            
        except Exception as e:
            logger.error(f"Error applying fixes: {e}")
            return {
                "error": str(e),
                "fixes_applied": fix_results.get("fixes_applied", 0),
                "fixes_failed": fix_results.get("fixes_failed", 0),
                "fixes_skipped": fix_results.get("fixes_skipped", 0)
            }
    
    def save_changes_log(self, output_file: Optional[str] = None) -> str:
        """Save changes log for GitHub Actions"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_file or f"indexation_changes_{timestamp}.json"
            
            changes_data = {
                "timestamp": datetime.now().isoformat(),
                "total_changes": len(self.changes_log),
                "changes": self.changes_log
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(changes_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Changes log saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving changes log: {e}")
            return ""
    
    # Helper methods for applying fixes from analysis results
    def _apply_noindex_fixes_from_analysis(self, issue_data: Dict) -> List[FixResult]:
        """Apply noindex fixes from analysis results"""
        results = []
        fixes = issue_data.get("fixes", [])
        
        for fix in fixes:
            if fix.get("type") == "fix_noindex" and fix.get("automated", False):
                file_path = fix["file_path"]
                changes = fix.get("changes", [])
                
                try:
                    front_matter, content = self._parse_front_matter(file_path)
                    modified = False
                    changes_made = []
                    
                    for change in changes:
                        field = change["field"]
                        action = change["action"]
                        
                        if action == "remove" and field in front_matter:
                            del front_matter[field]
                            modified = True
                            changes_made.append(f"Removed {field}")
                        
                        elif action == "set_value":
                            front_matter[field] = change["new_value"]
                            modified = True
                            changes_made.append(f"Set {field} to {change['new_value']}")
                    
                    if modified:
                        if not self.dry_run:
                            success = self._save_front_matter(file_path, front_matter, content)
                        else:
                            success = True
                        
                        if success:
                            self._log_change({
                                "type": "noindex_fixed",
                                "file": file_path,
                                "changes": changes_made
                            })
                        
                        results.append(FixResult(
                            success=success,
                            fix_type="noindex",
                            file_path=file_path,
                            details={"changes": changes_made}
                        ))
                
                except Exception as e:
                    results.append(FixResult(
                        success=False,
                        fix_type="noindex",
                        file_path=file_path,
                        details={},
                        error=str(e)
                    ))
        
        return results
    
    def _apply_robots_fixes_from_analysis(self, issue_data: Dict) -> List[FixResult]:
        """Apply robots.txt fixes from analysis results"""
        results = []
        fixes = issue_data.get("fixes", [])
        
        for fix in fixes:
            if fix.get("type") == "fix_robots_rule" and fix.get("automated", False):
                robots_file = fix["robots_file"]
                rule_to_remove = fix["rule_to_remove"]
                
                result = self._apply_single_robots_fix(robots_file, rule_to_remove)
                if result:
                    results.append(result)
        
        return results
    
    def _apply_canonical_fixes_from_analysis(self, issue_data: Dict) -> List[FixResult]:
        """Apply canonical fixes from analysis results"""
        results = []
        fixes = issue_data.get("fixes", [])
        
        for fix in fixes:
            if fix.get("type") == "add_canonical_tag" and fix.get("automated", False):
                file_path = fix["file_path"]
                canonical_url = fix["canonical_url"]
                
                result = self._add_canonical_url(file_path, canonical_url)
                if result:
                    results.append(result)
        
        return results
    
    def _apply_content_quality_fixes_from_analysis(self, issue_data: Dict) -> List[FixResult]:
        """Apply content quality fixes from analysis results"""
        results = []
        fixes = issue_data.get("fixes", [])
        
        for fix in fixes:
            if fix.get("type") == "improve_content_quality" and fix.get("automated", False):
                file_path = fix["file_path"]
                improvements = fix.get("improvements", [])
                
                result = self._apply_content_improvements(file_path, improvements)
                if result:
                    results.append(result)
        
        return results
    
    def _apply_single_robots_fix(self, robots_file: str, rule_to_remove: str) -> Optional[FixResult]:
        """Apply single robots.txt fix"""
        try:
            if not os.path.exists(robots_file):
                return FixResult(
                    success=False,
                    fix_type="robots_txt",
                    file_path=robots_file,
                    details={},
                    error="Robots file not found"
                )
            
            with open(robots_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the problematic rule
            lines = content.split('\n')
            new_lines = []
            rule_removed = False
            
            for line in lines:
                if line.strip().startswith('Disallow:'):
                    rule = line.split(':', 1)[1].strip()
                    if rule != rule_to_remove:
                        new_lines.append(line)
                    else:
                        rule_removed = True
                else:
                    new_lines.append(line)
            
            if rule_removed:
                new_content = '\n'.join(new_lines)
                
                if not self.dry_run:
                    # Create backup
                    backup_path = f"{robots_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(robots_file, backup_path)
                    
                    with open(robots_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                self._log_change({
                    "type": "robots_rule_removed",
                    "file": robots_file,
                    "rule": rule_to_remove
                })
                
                return FixResult(
                    success=True,
                    fix_type="robots_txt",
                    file_path=robots_file,
                    details={"rule_removed": rule_to_remove}
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="robots_txt",
                file_path=robots_file,
                details={"rule_to_remove": rule_to_remove},
                error=str(e)
            )
    
    def _apply_content_improvements(self, file_path: str, improvements: List[Dict]) -> Optional[FixResult]:
        """Apply content quality improvements"""
        try:
            front_matter, content = self._parse_front_matter(file_path)
            modified = False
            applied_improvements = []
            
            for improvement in improvements:
                imp_type = improvement["type"]
                value = improvement["value"]
                
                if imp_type == "add_title" and not front_matter.get("title"):
                    front_matter["title"] = value
                    modified = True
                    applied_improvements.append(f"Added title: {value}")
                
                elif imp_type == "add_description" and not front_matter.get("description"):
                    front_matter["description"] = value
                    modified = True
                    applied_improvements.append("Added description")
            
            if modified:
                if not self.dry_run:
                    success = self._save_front_matter(file_path, front_matter, content)
                else:
                    success = True
                
                if success:
                    self._log_change({
                        "type": "content_improved",
                        "file": file_path,
                        "improvements": applied_improvements
                    })
                
                return FixResult(
                    success=success,
                    fix_type="content_quality",
                    file_path=file_path,
                    details={"improvements": applied_improvements}
                )
            
            return None
            
        except Exception as e:
            return FixResult(
                success=False,
                fix_type="content_quality",
                file_path=file_path,
                details={},
                error=str(e)
            )


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Indexation Fixer - Fix SEO indexation issues")
    parser.add_argument("--site-url", required=True, help="Site URL (e.g., https://example.com)")
    parser.add_argument("--site-type", default="jekyll", choices=["jekyll", "hugo"], 
                       help="Site type (default: jekyll)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)")
    
    # Fix type options
    parser.add_argument("--fix-noindex", action="store_true", help="Fix noindex issues")
    parser.add_argument("--fix-robots", action="store_true", help="Fix robots.txt issues")
    parser.add_argument("--fix-links", action="store_true", help="Fix broken internal links")
    parser.add_argument("--fix-canonical", action="store_true", help="Fix canonical issues")
    parser.add_argument("--improve-content", action="store_true", help="Improve content quality")
    parser.add_argument("--all", action="store_true", help="Run all fixes")
    
    # Options
    parser.add_argument("--create-redirects", action="store_true", default=True,
                       help="Create redirects for broken links (default: True)")
    parser.add_argument("--no-redirects", action="store_true", 
                       help="Don't create redirects for broken links")
    parser.add_argument("--limit-noindex", type=int, help="Limit number of noindex fixes")
    parser.add_argument("--limit-content", type=int, help="Limit number of content improvements")
    
    # Output options
    parser.add_argument("--output-file", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    # Backup and restore
    parser.add_argument("--restore-backup", help="Restore from backup directory")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle backup restoration
    if args.restore_backup:
        fixer = IndexationFixer(args.site_url, args.site_type)
        success = fixer.restore_backup(args.restore_backup)
        return 0 if success else 1
    
    # Determine what fixes to run
    if args.all:
        fix_noindex = fix_robots = fix_links = fix_canonical = improve_content = True
    else:
        fix_noindex = args.fix_noindex
        fix_robots = args.fix_robots
        fix_links = args.fix_links
        fix_canonical = args.fix_canonical
        improve_content = args.improve_content
        
        # If no specific fixes specified, run all
        if not any([fix_noindex, fix_robots, fix_links, fix_canonical, improve_content]):
            fix_noindex = fix_robots = fix_links = fix_canonical = improve_content = True
    
    create_redirects = not args.no_redirects if args.no_redirects else args.create_redirects
    
    # Set up limits
    limits = {}
    if args.limit_noindex:
        limits['noindex'] = args.limit_noindex
    if args.limit_content:
        limits['content_quality'] = args.limit_content
    
    # Initialize fixer
    fixer = IndexationFixer(
        site_url=args.site_url,
        site_type=args.site_type,
        dry_run=args.dry_run
    )
    
    try:
        print(f"🔧 Starting indexation fixes...")
        print(f"   Site: {args.site_url}")
        print(f"   Type: {args.site_type}")
        print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        print()
        
        # Run comprehensive fix
        results = fixer.run_comprehensive_fix(
            fix_noindex=fix_noindex,
            fix_robots=fix_robots,
            fix_broken_links=fix_links,
            fix_canonical=fix_canonical,
            improve_content=improve_content,
            create_redirects=create_redirects,
            limits=limits
        )
        
        if "error" in results:
            print(f"❌ Fix operation failed: {results['error']}")
            return 1
        
        # Print summary
        summary = results["summary"]
        print(f"📊 FIX SUMMARY")
        print(f"   Total fixes attempted: {summary['total_fixes_attempted']}")
        print(f"   ✅ Successful: {summary['total_fixes_successful']}")
        print(f"   ❌ Failed: {summary['total_fixes_failed']}")
        
        if results.get("backup_dir"):
            print(f"   💾 Backup: {results['backup_dir']}")
        
        # Show details by fix type
        print(f"\n📋 FIXES BY TYPE:")
        for fix_type, fix_results in results.get("fixes", {}).items():
            successful = len([r for r in fix_results if r.get("success", False)])
            total = len(fix_results)
            print(f"   {fix_type}: {successful}/{total} successful")
        
        # Export results
        output_path = fixer.export_results(results, args.output_file)
        if output_path:
            print(f"   📄 Results: {output_path}")
        
        print()
        
        # Return appropriate exit code
        if summary["total_fixes_failed"] > 0:
            print("⚠️  Some fixes failed - check the detailed results")
            return 1
        elif summary["total_fixes_successful"] > 0:
            print("🎉 All fixes completed successfully!")
            return 0
        else:
            print("ℹ️  No issues found to fix")
            return 0
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())