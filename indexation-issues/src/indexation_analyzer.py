#!/usr/bin/env python3
"""
Complete Indexation Analyzer - Fixed and Enhanced
Handles all Google Search Console indexation issues with proper error handling
"""

import pandas as pd
import numpy as np
import requests
import os
import json
import yaml
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import hashlib
import shutil
import subprocess

# Google Search Console imports
try:
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logging.warning("Google API client not available. Install with: pip install google-api-python-client google-auth")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndexationAnalyzer:
    """Complete indexation issues analyzer for Google Search Console"""
    
    def __init__(self, service_account_path: str, site_url: str, site_type: str = "jekyll", dry_run: bool = False):
        self.service_account_path = service_account_path
        self.site_url = site_url.rstrip('/')
        self.site_type = site_type.lower()
        self.dry_run = dry_run
        self.service = None
        self.changes_log = []
        
        if GOOGLE_AVAILABLE and os.path.exists(service_account_path):
            self.service = self._build_service()
        
        # Content directories by site type
        self.content_dirs = {
            "jekyll": ["_posts", "_pages", "content", "_drafts"],
            "hugo": ["content/posts", "content/pages", "content", "content/blog"]
        }
        
        # Issue type mappings
        self.issue_types = {
            'noindex_tag': {'severity': 'high', 'automated': True},
            'blocked_robots_txt': {'severity': 'high', 'automated': True},
            'server_error': {'severity': 'critical', 'automated': False},
            'not_found_404': {'severity': 'high', 'automated': True},
            'redirect_page': {'severity': 'medium', 'automated': False},
            'canonical_issues': {'severity': 'high', 'automated': True},
            'crawled_not_indexed': {'severity': 'medium', 'automated': True},
            'discovered_not_indexed': {'severity': 'low', 'automated': True}
        }
    
    def _build_service(self):
        """Build Google Search Console service"""
        if not GOOGLE_AVAILABLE:
            logger.error("Google API libraries not available")
            return None
            
        try:
            if not os.path.exists(self.service_account_path):
                logger.error(f"Service account file not found: {self.service_account_path}")
                return None
                
            credentials = Credentials.from_service_account_file(
                self.service_account_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            
            service = build('searchconsole', 'v1', credentials=credentials)
            
            # Test the connection
            try:
                sites = service.sites().list().execute()
                logger.info(f"Successfully connected to Google Search Console")
                logger.info(f"Available sites: {len(sites.get('siteEntry', []))}")
                return service
            except HttpError as e:
                logger.error(f"Google Search Console API error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to build Google Search Console service: {e}")
            return None
    
    def analyze_all_indexation_issues(self) -> Dict:
        """Analyze all types of indexation issues"""
        logger.info("Starting comprehensive indexation analysis...")
        
        analysis_results = {
            "site_url": self.site_url,
            "site_type": self.site_type,
            "analysis_timestamp": datetime.now().isoformat(),
            "indexation_issues": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_priority_issues": 0,
                "automated_fixes_available": 0,
                "manual_fixes_required": 0
            }
        }
        
        try:
            # 1. Analyze noindex issues
            logger.info("Analyzing noindex issues...")
            noindex_results = self._analyze_noindex_issues()
            if noindex_results:
                analysis_results["indexation_issues"]["noindex_tag"] = noindex_results
            
            # 2. Analyze robots.txt issues
            logger.info("Analyzing robots.txt blocking...")
            robots_results = self._analyze_robots_issues()
            if robots_results:
                analysis_results["indexation_issues"]["blocked_robots_txt"] = robots_results
            
            # 3. Analyze 404 errors
            logger.info("Analyzing 404 errors...")
            error_404_results = self._analyze_404_errors()
            if error_404_results:
                analysis_results["indexation_issues"]["not_found_404"] = error_404_results
            
            # 4. Analyze server errors
            logger.info("Analyzing server errors...")
            server_error_results = self._analyze_server_errors()
            if server_error_results:
                analysis_results["indexation_issues"]["server_error"] = server_error_results
            
            # 5. Analyze canonical issues
            logger.info("Analyzing canonical issues...")
            canonical_results = self._analyze_canonical_issues()
            if canonical_results:
                analysis_results["indexation_issues"]["canonical_issues"] = canonical_results
            
            # 6. Analyze content quality issues
            logger.info("Analyzing content quality issues...")
            content_quality_results = self._analyze_content_quality_issues()
            if content_quality_results:
                analysis_results["indexation_issues"]["crawled_not_indexed"] = content_quality_results
            
            # 7. Generate summary
            analysis_results["summary"] = self._generate_summary(analysis_results["indexation_issues"])
            
            logger.info(f"Analysis complete. Found {analysis_results['summary']['total_issues']} total issues")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error during indexation analysis: {e}")
            return {"error": str(e), "partial_results": analysis_results}
    
    def _analyze_noindex_issues(self) -> Optional[Dict]:
        """Analyze pages with noindex issues"""
        issues = {
            "type": "noindex_tag",
            "description": "Pages excluded by noindex tag",
            "severity": "high",
            "pages": [],
            "fixes": []
        }
        
        try:
            content_dirs = self._get_content_directories()
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        has_noindex_issue = False
                        issue_details = []
                        
                        # Check various noindex conditions
                        if front_matter.get('published') == False:
                            has_noindex_issue = True
                            issue_details.append("published: false")
                        
                        if front_matter.get('noindex') == True:
                            has_noindex_issue = True
                            issue_details.append("noindex: true")
                        
                        if 'robots' in front_matter:
                            robots_value = str(front_matter['robots']).lower()
                            if 'noindex' in robots_value:
                                has_noindex_issue = True
                                issue_details.append(f"robots: {front_matter['robots']}")
                        
                        if front_matter.get('draft') == True:
                            has_noindex_issue = True
                            issue_details.append("draft: true")
                        
                        if has_noindex_issue:
                            url = self._get_url_from_file_path(str(file_path))
                            
                            page_issue = {
                                "url": url,
                                "file_path": str(file_path),
                                "issue_details": issue_details,
                                "content_length": len(content),
                                "has_title": bool(front_matter.get('title')),
                                "has_description": bool(front_matter.get('description')),
                                "priority": self._calculate_page_priority(content, front_matter),
                                "recommended_action": self._get_noindex_recommendation(front_matter, content)
                            }
                            
                            issues["pages"].append(page_issue)
                            
                    except Exception as e:
                        logger.warning(f"Error analyzing file {file_path}: {e}")
                        continue
            
            # Generate automated fixes
            issues["fixes"] = self._generate_noindex_fixes(issues["pages"])
            
            logger.info(f"Found {len(issues['pages'])} noindex issues")
            return issues if issues["pages"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing noindex issues: {e}")
            return None
    
    def _analyze_robots_issues(self) -> Optional[Dict]:
        """Analyze robots.txt blocking issues"""
        issues = {
            "type": "blocked_robots_txt",
            "description": "Pages blocked by robots.txt",
            "severity": "high", 
            "pages": [],
            "fixes": []
        }
        
        try:
            # Find robots.txt file
            robots_paths = ["robots.txt", "_site/robots.txt", "public/robots.txt", "static/robots.txt"]
            robots_path = None
            robots_content = ""
            
            for path in robots_paths:
                if os.path.exists(path):
                    robots_path = path
                    with open(path, 'r', encoding='utf-8') as f:
                        robots_content = f.read()
                    break
            
            if not robots_path:
                logger.info("No robots.txt file found")
                return None
            
            # Parse disallow rules
            disallow_rules = self._parse_robots_disallow(robots_content)
            
            if not disallow_rules:
                logger.info("No disallow rules found in robots.txt")
                return None
            
            # Check which pages are affected
            content_dirs = self._get_content_directories()
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        url = self._get_url_from_file_path(str(file_path))
                        url_path = urlparse(url).path
                        
                        blocking_rule = self._find_blocking_rule(url_path, disallow_rules)
                        
                        if blocking_rule:
                            front_matter, content = self._parse_front_matter(str(file_path))
                            
                            page_issue = {
                                "url": url,
                                "file_path": str(file_path),
                                "blocking_rule": blocking_rule,
                                "robots_file": robots_path,
                                "priority": self._calculate_page_priority(content, front_matter),
                                "recommended_action": f"Remove or modify rule: {blocking_rule}"
                            }
                            
                            issues["pages"].append(page_issue)
                            
                    except Exception as e:
                        logger.warning(f"Error analyzing robots blocking for {file_path}: {e}")
                        continue
            
            # Generate fixes
            issues["fixes"] = self._generate_robots_fixes(issues["pages"], robots_path)
            
            logger.info(f"Found {len(issues['pages'])} robots.txt blocking issues")
            return issues if issues["pages"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing robots.txt issues: {e}")
            return None
    
    def _analyze_404_errors(self) -> Optional[Dict]:
        """Analyze 404 error issues"""
        issues = {
            "type": "not_found_404",
            "description": "Broken internal links (404 errors)",
            "severity": "high",
            "pages": [],
            "fixes": []
        }
        
        try:
            # Extract all internal links
            internal_links = self._extract_all_internal_links()
            
            # Test links for 404 errors
            for link_info in internal_links:
                try:
                    full_url = urljoin(self.site_url, link_info["url"])
                    
                    # Skip external links
                    if not full_url.startswith(self.site_url):
                        continue
                    
                    response = requests.head(full_url, timeout=10, allow_redirects=True)
                    
                    if response.status_code == 404:
                        # Try to find a replacement page
                        suggested_replacement = self._find_replacement_page(link_info["url"])
                        
                        page_issue = {
                            "broken_url": link_info["url"],
                            "full_url": full_url,
                            "referring_pages": link_info["referring_pages"],
                            "suggested_replacement": suggested_replacement,
                            "priority": "high" if len(link_info["referring_pages"]) > 2 else "medium",
                            "recommended_action": self._get_404_recommendation(link_info["url"], suggested_replacement)
                        }
                        
                        issues["pages"].append(page_issue)
                        
                except requests.RequestException as e:
                    logger.debug(f"Network error testing {link_info['url']}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error testing link {link_info['url']}: {e}")
                    continue
            
            # Generate fixes
            issues["fixes"] = self._generate_404_fixes(issues["pages"])
            
            logger.info(f"Found {len(issues['pages'])} 404 errors")
            return issues if issues["pages"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing 404 errors: {e}")
            return None
    
    def _analyze_server_errors(self) -> Optional[Dict]:
        """Analyze server error issues (5xx)"""
        issues = {
            "type": "server_error",
            "description": "Pages returning server errors (5xx)",
            "severity": "critical",
            "pages": [],
            "fixes": []
        }
        
        try:
            # Get list of important pages to test
            important_pages = self._get_important_pages_list()
            
            for page_info in important_pages:
                try:
                    full_url = urljoin(self.site_url, page_info["url"])
                    
                    response = requests.get(full_url, timeout=15, allow_redirects=True)
                    
                    if response.status_code >= 500:
                        page_issue = {
                            "url": page_info["url"],
                            "full_url": full_url,
                            "file_path": page_info["file_path"],
                            "status_code": response.status_code,
                            "error_type": self._get_server_error_type(response.status_code),
                            "priority": "critical",
                            "recommended_action": self._get_server_error_recommendation(response.status_code)
                        }
                        
                        issues["pages"].append(page_issue)
                        
                except requests.RequestException as e:
                    # Network errors might indicate server issues too
                    page_issue = {
                        "url": page_info["url"],
                        "full_url": urljoin(self.site_url, page_info["url"]),
                        "file_path": page_info["file_path"],
                        "status_code": "connection_error",
                        "error_type": "Connection failed",
                        "error_details": str(e),
                        "priority": "critical",
                        "recommended_action": "Check server configuration and connectivity"
                    }
                    
                    issues["pages"].append(page_issue)
                    
                except Exception as e:
                    logger.warning(f"Error testing server response for {page_info['url']}: {e}")
                    continue
            
            # Generate fixes (mostly manual recommendations)
            issues["fixes"] = self._generate_server_error_fixes(issues["pages"])
            
            logger.info(f"Found {len(issues['pages'])} server error issues")
            return issues if issues["pages"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing server errors: {e}")
            return None
    
    def _analyze_canonical_issues(self) -> Optional[Dict]:
        """Analyze canonical tag issues"""
        issues = {
            "type": "canonical_issues",
            "description": "Canonical tag problems and duplicate content",
            "severity": "high",
            "pages": [],
            "fixes": []
        }
        
        try:
            content_dirs = self._get_content_directories()
            content_hashes = {}
            canonical_issues_found = []
            
            # First pass: collect content and check for duplicates
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        # Generate content hash for duplicate detection
                        content_clean = re.sub(r'\s+', ' ', content[:1000]).strip().lower()
                        content_hash = hashlib.md5(content_clean.encode()).hexdigest()
                        
                        url = self._get_url_from_file_path(str(file_path))
                        canonical_url = front_matter.get('canonical_url')
                        
                        page_info = {
                            "url": url,
                            "file_path": str(file_path),
                            "canonical_url": canonical_url,
                            "content_hash": content_hash,
                            "content_length": len(content),
                            "title": front_matter.get('title', ''),
                            "front_matter": front_matter
                        }
                        
                        # Check for duplicate content
                        if content_hash in content_hashes:
                            # Found duplicate content
                            original = content_hashes[content_hash]
                            
                            if not canonical_url:
                                canonical_issues_found.append({
                                    "issue_type": "duplicate_no_canonical",
                                    "page": page_info,
                                    "duplicate_of": original,
                                    "priority": "high",
                                    "recommended_action": f"Add canonical_url pointing to {original['url']}"
                                })
                        else:
                            content_hashes[content_hash] = page_info
                        
                        # Check canonical URL validity
                        if canonical_url:
                            if not self._validate_canonical_url(canonical_url):
                                canonical_issues_found.append({
                                    "issue_type": "invalid_canonical",
                                    "page": page_info,
                                    "priority": "medium",
                                    "recommended_action": f"Fix or remove invalid canonical URL: {canonical_url}"
                                })
                        
                    except Exception as e:
                        logger.warning(f"Error analyzing canonical for {file_path}: {e}")
                        continue
            
            issues["pages"] = canonical_issues_found
            issues["fixes"] = self._generate_canonical_fixes(canonical_issues_found)
            
            logger.info(f"Found {len(canonical_issues_found)} canonical issues")
            return issues if canonical_issues_found else None
            
        except Exception as e:
            logger.error(f"Error analyzing canonical issues: {e}")
            return None
    
    def _analyze_content_quality_issues(self) -> Optional[Dict]:
        """Analyze content quality issues that prevent indexation"""
        issues = {
            "type": "crawled_not_indexed",
            "description": "Content quality issues preventing indexation",
            "severity": "medium",
            "pages": [],
            "fixes": []
        }
        
        try:
            content_dirs = self._get_content_directories()
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        quality_issues = self._assess_content_quality(content, front_matter)
                        
                        if quality_issues:
                            url = self._get_url_from_file_path(str(file_path))
                            
                            page_issue = {
                                "url": url,
                                "file_path": str(file_path),
                                "quality_issues": quality_issues,
                                "content_length": len(content),
                                "word_count": len(content.split()),
                                "has_title": bool(front_matter.get('title')),
                                "has_description": bool(front_matter.get('description')),
                                "priority": self._calculate_content_quality_priority(quality_issues),
                                "recommended_action": self._get_content_quality_recommendations(quality_issues)
                            }
                            
                            issues["pages"].append(page_issue)
                            
                    except Exception as e:
                        logger.warning(f"Error analyzing content quality for {file_path}: {e}")
                        continue
            
            issues["fixes"] = self._generate_content_quality_fixes(issues["pages"])
            
            logger.info(f"Found {len(issues['pages'])} content quality issues")
            return issues if issues["pages"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing content quality: {e}")
            return None
    
    # Helper methods
    def _get_content_directories(self) -> List[str]:
        """Get content directories for the site type"""
        return self.content_dirs.get(self.site_type, ["content"])
    
    def _parse_front_matter(self, file_path: str) -> Tuple[Dict, str]:
        """Parse YAML front matter from markdown file"""
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
            logger.warning(f"Error parsing front matter in {file_path}: {e}")
            return {}, ""
    
    def _get_url_from_file_path(self, file_path: str) -> str:
        """Convert file path to URL"""
        try:
            if self.site_type == "jekyll":
                # Handle Jekyll post format: YYYY-MM-DD-title.md
                if "_posts" in file_path:
                    filename = os.path.basename(file_path)
                    if re.match(r'\d{4}-\d{2}-\d{2}-.+\.md$', filename):
                        date_part = filename[:10]
                        title_part = filename[11:-3]
                        year, month, day = date_part.split('-')
                        return f"/{year}/{month}/{day}/{title_part}/"
                
                # Handle pages
                if "_pages" in file_path:
                    rel_path = os.path.relpath(file_path, "_pages")
                    return "/" + rel_path.replace('.md', '/')
                
                # Default handling
                rel_path = os.path.relpath(file_path)
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
            logger.warning(f"Error converting file path to URL: {file_path} - {e}")
            return "/" + os.path.basename(file_path).replace('.md', '/')
    
    def _calculate_page_priority(self, content: str, front_matter: Dict) -> str:
        """Calculate priority level for a page"""
        score = 0
        
        # Content length
        if len(content) > 2000:
            score += 3
        elif len(content) > 1000:
            score += 2
        elif len(content) > 500:
            score += 1
        
        # Has proper metadata
        if front_matter.get('title'):
            score += 1
        if front_matter.get('description'):
            score += 1
        
        # Important keywords
        important_keywords = ['guide', 'tutorial', 'how to', 'complete', 'ultimate', 'beginner']
        content_lower = content.lower()
        title_lower = str(front_matter.get('title', '')).lower()
        
        if any(keyword in content_lower or keyword in title_lower for keyword in important_keywords):
            score += 2
        
        if score >= 6:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def _get_noindex_recommendation(self, front_matter: Dict, content: str) -> str:
        """Get recommendation for fixing noindex issues"""
        recommendations = []
        
        if front_matter.get('published') == False:
            if len(content.strip()) > 200:
                recommendations.append("Change 'published: false' to 'published: true'")
            else:
                recommendations.append("Complete content then set 'published: true'")
        
        if front_matter.get('noindex') == True:
            recommendations.append("Remove 'noindex: true' from front matter")
        
        if front_matter.get('draft') == True:
            recommendations.append("Remove 'draft: true' or set 'draft: false'")
        
        if 'robots' in front_matter and 'noindex' in str(front_matter['robots']).lower():
            recommendations.append("Update robots directive to allow indexing")
        
        return "; ".join(recommendations) if recommendations else "Allow page to be indexed"
    
    def _generate_noindex_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate automated fixes for noindex issues"""
        fixes = []
        
        for page in pages:
            file_path = page["file_path"]
            
            fix = {
                "type": "fix_noindex",
                "file_path": file_path,
                "automated": True,
                "changes": []
            }
            
            # Determine what changes are needed based on issue details
            for issue_detail in page["issue_details"]:
                if "published: false" in issue_detail and page["content_length"] > 200:
                    fix["changes"].append({
                        "field": "published",
                        "action": "set_value",
                        "new_value": True
                    })
                
                if "noindex: true" in issue_detail:
                    fix["changes"].append({
                        "field": "noindex", 
                        "action": "remove"
                    })
                
                if "draft: true" in issue_detail:
                    fix["changes"].append({
                        "field": "draft",
                        "action": "set_value", 
                        "new_value": False
                    })
                
                if "robots:" in issue_detail and "noindex" in issue_detail:
                    fix["changes"].append({
                        "field": "robots",
                        "action": "set_value",
                        "new_value": "index, follow"
                    })
            
            if fix["changes"]:
                fixes.append(fix)
        
        return fixes
    
    def _parse_robots_disallow(self, robots_content: str) -> List[str]:
        """Parse Disallow rules from robots.txt"""
        disallow_rules = []
        lines = robots_content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('Disallow:') and (current_user_agent in ['*', 'Googlebot'] or current_user_agent is None):
                rule = line.split(':', 1)[1].strip()
                if rule:
                    disallow_rules.append(rule)
        
        return disallow_rules
    
    def _find_blocking_rule(self, url_path: str, disallow_rules: List[str]) -> Optional[str]:
        """Find which disallow rule blocks a URL"""
        for rule in disallow_rules:
            if rule == '/':
                return rule  # Blocks everything
            elif rule.endswith('*'):
                if url_path.startswith(rule[:-1]):
                    return rule
            elif url_path.startswith(rule):
                return rule
        
        return None
    
    def _generate_robots_fixes(self, pages: List[Dict], robots_path: str) -> List[Dict]:
        """Generate fixes for robots.txt issues"""
        fixes = []
        
        # Group pages by blocking rule
        rules_to_fix = {}
        for page in pages:
            rule = page["blocking_rule"]
            if rule not in rules_to_fix:
                rules_to_fix[rule] = []
            rules_to_fix[rule].append(page)
        
        # Create fix for each problematic rule
        for rule, affected_pages in rules_to_fix.items():
            fix = {
                "type": "fix_robots_rule",
                "robots_file": robots_path,
                "rule_to_remove": rule,
                "affected_pages": len(affected_pages),
                "automated": True,
                "backup_created": True
            }
            fixes.append(fix)
        
        return fixes
    
    def _extract_all_internal_links(self) -> List[Dict]:
        """Extract all internal links from markdown files"""
        internal_links = {}
        
        try:
            content_dirs = self._get_content_directories()
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        _, content = self._parse_front_matter(str(file_path))
                        
                        # Extract markdown links
                        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
                        matches = re.findall(link_pattern, content)
                        
                        for link_text, link_url in matches:
                            # Skip external links
                            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                                continue
                            
                            # Normalize URL
                            if not link_url.startswith('/'):
                                link_url = '/' + link_url
                            
                            if link_url not in internal_links:
                                internal_links[link_url] = {
                                    "url": link_url,
                                    "referring_pages": []
                                }
                            
                            internal_links[link_url]["referring_pages"].append({
                                "file_path": str(file_path),
                                "link_text": link_text
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error extracting links from {file_path}: {e}")
                        continue
            
            return list(internal_links.values())
            
        except Exception as e:
            logger.error(f"Error extracting internal links: {e}")
            return []
    
    def _find_replacement_page(self, broken_url: str) -> Optional[str]:
        """Find a replacement page for a broken URL"""
        try:
            # Extract keywords from broken URL
            url_parts = broken_url.strip('/').split('/')
            keywords = []
            
            for part in url_parts:
                # Split on common separators
                words = re.split(r'[-_\s]+', part)
                keywords.extend([w.lower() for w in words if len(w) > 2])
            
            if not keywords:
                return None
            
            # Search through existing pages
            content_dirs = self._get_content_directories()
            best_match = None
            best_score = 0
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        # Calculate match score
                        score = 0
                        title = str(front_matter.get('title', '')).lower()
                        file_name = os.path.basename(str(file_path)).lower()
                        content_text = content[:500].lower()
                        
                        for keyword in keywords:
                            if keyword in title:
                                score += 3
                            if keyword in file_name:
                                score += 2
                            if keyword in content_text:
                                score += 1
                        
                        if score > best_score and score > 2:
                            best_score = score
                            best_match = self._get_url_from_file_path(str(file_path))
                            
                    except Exception as e:
                        logger.warning(f"Error searching replacement in {file_path}: {e}")
                        continue
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding replacement page: {e}")
            return None
    
    def _get_404_recommendation(self, broken_url: str, suggested_replacement: Optional[str]) -> str:
        """Get recommendation for fixing 404 errors"""
        if suggested_replacement:
            return f"Update internal links to point to {suggested_replacement}, or create redirect"
        else:
            return "Create missing content or remove broken links"
    
    def _generate_404_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for 404 errors"""
        fixes = []
        
        for page in pages:
            if page.get("suggested_replacement"):
                # Create redirect fix
                fix = {
                    "type": "create_redirect",
                    "from_url": page["broken_url"],
                    "to_url": page["suggested_replacement"],
                    "automated": True
                }
                fixes.append(fix)
                
                # Update internal links fix
                for referring_page in page["referring_pages"]:
                    fix = {
                        "type": "update_internal_link",
                        "file_path": referring_page["file_path"],
                        "old_url": page["broken_url"],
                        "new_url": page["suggested_replacement"],
                        "automated": True
                    }
                    fixes.append(fix)
            else:
                # Remove broken links
                for referring_page in page["referring_pages"]:
                    fix = {
                        "type": "remove_broken_link",
                        "file_path": referring_page["file_path"],
                        "broken_url": page["broken_url"],
                        "automated": False,
                        "manual_review_required": True
                    }
                    fixes.append(fix)
        
        return fixes
    
    def _get_important_pages_list(self) -> List[Dict]:
        """Get list of important pages to test for server errors"""
        important_pages = []
        
        try:
            content_dirs = self._get_content_directories()
            
            for content_dir in content_dirs:
                if not os.path.exists(content_dir):
                    continue
                    
                for file_path in Path(content_dir).rglob("*.md"):
                    try:
                        front_matter, content = self._parse_front_matter(str(file_path))
                        
                        # Prioritize important pages
                        priority = self._calculate_page_priority(content, front_matter)
                        
                        if priority in ["high", "medium"]:
                            url = self._get_url_from_file_path(str(file_path))
                            important_pages.append({
                                "url": url,
                                "file_path": str(file_path),
                                "priority": priority
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error evaluating page importance {file_path}: {e}")
                        continue
            
            # Limit to reasonable number for testing
            important_pages = sorted(important_pages, key=lambda x: x["priority"], reverse=True)[:50]
            
            return important_pages
            
        except Exception as e:
            logger.error(f"Error getting important pages list: {e}")
            return []
    
    def _get_server_error_type(self, status_code: int) -> str:
        """Get server error type description"""
        error_types = {
            500: "Internal Server Error",
            501: "Not Implemented", 
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported"
        }
        return error_types.get(status_code, f"Server Error {status_code}")
    
    def _get_server_error_recommendation(self, status_code: int) -> str:
        """Get recommendation for server errors"""
        recommendations = {
            500: "Check server logs for application errors, review recent code changes",
            501: "Check if requested functionality is implemented on server",
            502: "Check reverse proxy configuration and upstream servers",
            503: "Check server resources and capacity, review maintenance mode",
            504: "Check upstream server response times and timeout configurations",
            505: "Update HTTP version configuration"
        }
        return recommendations.get(status_code, "Check server configuration and logs")
    
    def _generate_server_error_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for server errors (mostly manual)"""
        fixes = []
        
        # Group by error type
        error_groups = {}
        for page in pages:
            error_type = page.get("status_code", "unknown")
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(page)
        
        for error_type, pages_with_error in error_groups.items():
            fix = {
                "type": "server_error_investigation",
                "error_type": error_type,
                "affected_pages": len(pages_with_error),
                "automated": False,
                "recommended_actions": [
                    "Check server logs",
                    "Review server configuration", 
                    "Monitor server resources",
                    "Test pages individually"
                ]
            }
            fixes.append(fix)
        
        return fixes
    
    def _validate_canonical_url(self, canonical_url: str) -> bool:
        """Validate canonical URL format"""
        try:
            parsed = urlparse(canonical_url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _generate_canonical_fixes(self, canonical_issues: List[Dict]) -> List[Dict]:
        """Generate fixes for canonical issues"""
        fixes = []
        
        for issue in canonical_issues:
            page = issue["page"]
            
            if issue["issue_type"] == "duplicate_no_canonical":
                fix = {
                    "type": "add_canonical_tag",
                    "file_path": page["file_path"],
                    "canonical_url": issue["duplicate_of"]["url"],
                    "automated": True
                }
                fixes.append(fix)
            
            elif issue["issue_type"] == "invalid_canonical":
                fix = {
                    "type": "fix_canonical_url",
                    "file_path": page["file_path"],
                    "current_canonical": page["canonical_url"],
                    "automated": False,
                    "recommended_action": "Review and fix canonical URL format"
                }
                fixes.append(fix)
        
        return fixes
    
    def _assess_content_quality(self, content: str, front_matter: Dict) -> List[str]:
        """Assess content quality issues"""
        issues = []
        
        # Content length
        if len(content.strip()) < 300:
            issues.append("Content too short (less than 300 characters)")
        
        # Word count
        word_count = len(content.split())
        if word_count < 50:
            issues.append(f"Low word count ({word_count} words)")
        
        # Missing title
        if not front_matter.get('title'):
            issues.append("Missing title")
        
        # Missing description
        if not front_matter.get('description'):
            issues.append("Missing meta description")
        
        # Empty or placeholder content
        placeholder_indicators = ['lorem ipsum', 'placeholder', 'todo', 'coming soon']
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in placeholder_indicators):
            issues.append("Contains placeholder content")
        
        # No headings
        if not re.search(r'^#+\s', content, re.MULTILINE):
            issues.append("No headings found")
        
        # Title too short or generic
        title = front_matter.get('title', '')
        if title and len(title) < 10:
            issues.append("Title too short")
        
        generic_titles = ['untitled', 'new post', 'draft', 'test']
        if any(generic in title.lower() for generic in generic_titles):
            issues.append("Generic or placeholder title")
        
        return issues
    
    def _calculate_content_quality_priority(self, quality_issues: List[str]) -> str:
        """Calculate priority for content quality issues"""
        critical_issues = ['Content too short', 'Missing title', 'Contains placeholder content']
        
        if any(critical in issue for critical in critical_issues for issue in quality_issues):
            return "high"
        elif len(quality_issues) > 3:
            return "medium"
        else:
            return "low"
    
    def _get_content_quality_recommendations(self, quality_issues: List[str]) -> str:
        """Get recommendations for content quality issues"""
        recommendations = []
        
        for issue in quality_issues:
            if "Content too short" in issue:
                recommendations.append("Expand content with more detailed information")
            elif "Low word count" in issue:
                recommendations.append("Add more comprehensive content")
            elif "Missing title" in issue:
                recommendations.append("Add descriptive title")
            elif "Missing meta description" in issue:
                recommendations.append("Add SEO meta description")
            elif "placeholder content" in issue:
                recommendations.append("Replace placeholder content with real content")
            elif "No headings" in issue:
                recommendations.append("Add proper heading structure")
            elif "Title too short" in issue:
                recommendations.append("Create more descriptive title")
            elif "Generic" in issue:
                recommendations.append("Use specific, descriptive title")
        
        return "; ".join(set(recommendations)) if recommendations else "Improve content quality"
    
    def _generate_content_quality_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for content quality issues"""
        fixes = []
        
        for page in pages:
            fix = {
                "type": "improve_content_quality",
                "file_path": page["file_path"],
                "automated": True,
                "improvements": []
            }
            
            # Generate specific improvements based on issues
            for issue in page["quality_issues"]:
                if "Missing title" in issue:
                    # Generate title from filename or first heading
                    suggested_title = self._generate_title_from_content(page["file_path"])
                    if suggested_title:
                        fix["improvements"].append({
                            "type": "add_title",
                            "value": suggested_title
                        })
                
                if "Missing meta description" in issue:
                    # Generate description from first paragraph
                    suggested_description = self._generate_description_from_content(page["file_path"])
                    if suggested_description:
                        fix["improvements"].append({
                            "type": "add_description", 
                            "value": suggested_description
                        })
            
            if fix["improvements"]:
                fixes.append(fix)
        
        return fixes
    
    def _generate_title_from_content(self, file_path: str) -> Optional[str]:
        """Generate title from content or filename"""
        try:
            _, content = self._parse_front_matter(file_path)
            
            # Look for first H1 heading
            h1_match = re.search(r'^#\s+(.+)
    , content, re.MULTILINE)
            if h1_match:
                return h1_match.group(1).strip()
            
            # Look for first H2 heading
            h2_match = re.search(r'^##\s+(.+)
    , content, re.MULTILINE)
            if h2_match:
                return h2_match.group(1).strip()
            
            # Generate from filename
            filename = os.path.basename(file_path)
            if filename.endswith('.md'):
                filename = filename[:-3]
            
            # Remove date prefix from Jekyll posts
            filename = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
            
            # Convert to title case
            title = filename.replace('-', ' ').replace('_', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            
            return title if len(title) > 5 else None
            
        except Exception as e:
            logger.warning(f"Error generating title for {file_path}: {e}")
            return None
    
    def _generate_description_from_content(self, file_path: str) -> Optional[str]:
        """Generate meta description from content"""
        try:
            _, content = self._parse_front_matter(file_path)
            
            # Find first paragraph that's substantial
            paragraphs = content.split('\n\n')
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                # Skip headings and short paragraphs
                if paragraph.startswith('#') or len(paragraph) < 50:
                    continue
                
                # Clean up markdown formatting
                paragraph = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', paragraph)  # Links
                paragraph = re.sub(r'\*\*([^*]*)\*\*', r'\1', paragraph)  # Bold
                paragraph = re.sub(r'\*([^*]*)\*', r'\1', paragraph)  # Italic
                paragraph = re.sub(r'`([^`]*)`', r'\1', paragraph)  # Code
                
                # Truncate to appropriate length
                if len(paragraph) > 160:
                    paragraph = paragraph[:157] + '...'
                
                return paragraph
            
            return None
            
        except Exception as e:
            logger.warning(f"Error generating description for {file_path}: {e}")
            return None
    
    def _generate_summary(self, indexation_issues: Dict) -> Dict:
        """Generate summary of all indexation issues"""
        summary = {
            "total_issues": 0,
            "critical_issues": 0,
            "high_priority_issues": 0,
            "automated_fixes_available": 0,
            "manual_fixes_required": 0,
            "issues_by_type": {}
        }
        
        for issue_type, issue_data in indexation_issues.items():
            pages = issue_data.get("pages", [])
            fixes = issue_data.get("fixes", [])
            severity = issue_data.get("severity", "low")
            
            count = len(pages)
            summary["total_issues"] += count
            summary["issues_by_type"][issue_type] = {
                "count": count,
                "severity": severity,
                "automated_fixes": len([f for f in fixes if f.get("automated", False)]),
                "manual_fixes": len([f for f in fixes if not f.get("automated", False)])
            }
            
            if severity == "critical":
                summary["critical_issues"] += count
            elif severity == "high":
                summary["high_priority_issues"] += count
            
            summary["automated_fixes_available"] += len([f for f in fixes if f.get("automated", False)])
            summary["manual_fixes_required"] += len([f for f in fixes if not f.get("automated", False)])
        
        return summary
    
    # Fix implementation methods
    def apply_fixes(self, analysis_results: Dict, fix_types: Optional[List[str]] = None) -> Dict:
        """Apply automated fixes for indexation issues"""
        if not analysis_results or "indexation_issues" not in analysis_results:
            return {"error": "No analysis results to apply fixes to"}
        
        if self.dry_run:
            logger.info("DRY RUN MODE: No actual changes will be made")
        
        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": [],
            "fixes_failed": [],
            "summary": {
                "total_fixes_attempted": 0,
                "successful_fixes": 0,
                "failed_fixes": 0
            }
        }
        
        # Create backup if not dry run
        if not self.dry_run:
            self._create_backup()
        
        # Apply fixes for each issue type
        for issue_type, issue_data in analysis_results["indexation_issues"].items():
            if fix_types and issue_type not in fix_types:
                continue
            
            fixes = issue_data.get("fixes", [])
            
            for fix in fixes:
                fix_results["summary"]["total_fixes_attempted"] += 1
                
                try:
                    success = self._apply_single_fix(fix)
                    
                    if success:
                        fix_results["fixes_applied"].append({
                            "fix_type": fix["type"],
                            "issue_type": issue_type,
                            "details": fix
                        })
                        fix_results["summary"]["successful_fixes"] += 1
                    else:
                        fix_results["fixes_failed"].append({
                            "fix_type": fix["type"],
                            "issue_type": issue_type,
                            "error": "Fix application failed",
                            "details": fix
                        })
                        fix_results["summary"]["failed_fixes"] += 1
                        
                except Exception as e:
                    logger.error(f"Error applying fix {fix.get('type', 'unknown')}: {e}")
                    fix_results["fixes_failed"].append({
                        "fix_type": fix.get("type", "unknown"),
                        "issue_type": issue_type,
                        "error": str(e),
                        "details": fix
                    })
                    fix_results["summary"]["failed_fixes"] += 1
        
        logger.info(f"Fix application complete. {fix_results['summary']['successful_fixes']} successful, {fix_results['summary']['failed_fixes']} failed")
        
        return fix_results
    
    def _create_backup(self) -> bool:
        """Create backup of important files before making changes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"indexation_backup_{timestamp}"
            
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            os.makedirs(backup_dir)
            
            # Backup content directories
            for content_dir in self._get_content_directories():
                if os.path.exists(content_dir):
                    dest_dir = os.path.join(backup_dir, content_dir)
                    shutil.copytree(content_dir, dest_dir)
                    logger.info(f"Backed up {content_dir} to {dest_dir}")
            
            # Backup robots.txt if exists
            robots_paths = ["robots.txt", "_site/robots.txt", "public/robots.txt"]
            for robots_path in robots_paths:
                if os.path.exists(robots_path):
                    shutil.copy2(robots_path, backup_dir)
                    logger.info(f"Backed up {robots_path}")
                    break
            
            self._log_change({
                "type": "backup_created",
                "backup_dir": backup_dir,
                "timestamp": timestamp
            })
            
            logger.info(f"Backup created in {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def _apply_single_fix(self, fix: Dict) -> bool:
        """Apply a single fix"""
        fix_type = fix.get("type")
        
        if fix_type == "fix_noindex":
            return self._apply_noindex_fix(fix)
        elif fix_type == "fix_robots_rule":
            return self._apply_robots_fix(fix)
        elif fix_type == "create_redirect":
            return self._apply_redirect_fix(fix)
        elif fix_type == "update_internal_link":
            return self._apply_link_update_fix(fix)
        elif fix_type == "add_canonical_tag":
            return self._apply_canonical_fix(fix)
        elif fix_type == "improve_content_quality":
            return self._apply_content_quality_fix(fix)
        else:
            logger.warning(f"Unknown fix type: {fix_type}")
            return False
    
    def _apply_noindex_fix(self, fix: Dict) -> bool:
        """Apply noindex fix to front matter"""
        try:
            file_path = fix["file_path"]
            changes = fix.get("changes", [])
            
            if not os.path.exists(file_path):
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            modified = False
            
            for change in changes:
                field = change["field"]
                action = change["action"]
                
                if action == "remove" and field in front_matter:
                    del front_matter[field]
                    modified = True
                    logger.info(f"Removed {field} from {file_path}")
                
                elif action == "set_value":
                    front_matter[field] = change["new_value"]
                    modified = True
                    logger.info(f"Set {field} to {change['new_value']} in {file_path}")
            
            if modified:
                success = self._save_front_matter(file_path, front_matter, content)
                if success:
                    self._log_change({
                        "type": "noindex_fixed",
                        "file": file_path,
                        "changes": changes
                    })
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying noindex fix: {e}")
            return False
    
    def _apply_robots_fix(self, fix: Dict) -> bool:
        """Apply robots.txt fix"""
        try:
            robots_file = fix["robots_file"]
            rule_to_remove = fix["rule_to_remove"]
            
            if not os.path.exists(robots_file):
                return False
            
            with open(robots_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the problematic disallow rule
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if line.strip().startswith('Disallow:'):
                    rule = line.split(':', 1)[1].strip()
                    if rule != rule_to_remove:
                        new_lines.append(line)
                    else:
                        logger.info(f"Removed robots rule: {rule_to_remove}")
                else:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
            
            if not self.dry_run:
                with open(robots_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            self._log_change({
                "type": "robots_rule_removed",
                "file": robots_file,
                "rule": rule_to_remove
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying robots fix: {e}")
            return False
    
    def _apply_redirect_fix(self, fix: Dict) -> bool:
        """Apply redirect creation fix"""
        try:
            from_url = fix["from_url"]
            to_url = fix["to_url"]
            
            if self.site_type == "jekyll":
                success = self._create_jekyll_redirect(from_url, to_url)
            else:  # Hugo
                success = self._create_hugo_redirect(from_url, to_url)
            
            if success:
                self._log_change({
                    "type": "redirect_created",
                    "from_url": from_url,
                    "to_url": to_url,
                    "site_type": self.site_type
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating redirect: {e}")
            return False
    
    def _create_jekyll_redirect(self, from_url: str, to_url: str) -> bool:
        """Create Jekyll redirect"""
        try:
            redirect_dir = "_redirects"
            
            if not self.dry_run:
                os.makedirs(redirect_dir, exist_ok=True)
            
            filename = from_url.strip('/').replace('/', '-') + '.md'
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
                logger.info(f"Created Jekyll redirect: {redirect_file}")
            else:
                logger.info(f"DRY RUN: Would create Jekyll redirect {from_url} → {to_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating Jekyll redirect: {e}")
            return False
    
    def _create_hugo_redirect(self, from_url: str, to_url: str) -> bool:
        """Create Hugo redirect"""
        try:
            redirect_dir = "content/redirects"
            
            if not self.dry_run:
                os.makedirs(redirect_dir, exist_ok=True)
            
            filename = from_url.strip('/').replace('/', '-') + '.md'
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
                logger.info(f"Created Hugo redirect: {redirect_file}")
            else:
                logger.info(f"DRY RUN: Would create Hugo redirect {from_url} → {to_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating Hugo redirect: {e}")
            return False
    
    def _apply_link_update_fix(self, fix: Dict) -> bool:
        """Apply internal link update fix"""
        try:
            file_path = fix["file_path"]
            old_url = fix["old_url"]
            new_url = fix["new_url"]
            
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the link
            old_link_pattern = f"]({old_url})"
            new_link_pattern = f"]({new_url})" if new_url != "#removed" else "]"
            
            if old_link_pattern in content:
                new_content = content.replace(old_link_pattern, new_link_pattern)
                
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self._log_change({
                        "type": "link_updated",
                        "file": file_path,
                        "old_url": old_url,
                        "new_url": new_url
                    })
                    
                    logger.info(f"Updated link in {file_path}: {old_url} → {new_url}")
                else:
                    logger.info(f"DRY RUN: Would update link in {file_path}: {old_url} → {new_url}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating internal link: {e}")
            return False
    
    def _apply_canonical_fix(self, fix: Dict) -> bool:
        """Apply canonical tag fix"""
        try:
            file_path = fix["file_path"]
            canonical_url = fix["canonical_url"]
            
            front_matter, content = self._parse_front_matter(file_path)
            front_matter["canonical_url"] = canonical_url
            
            success = self._save_front_matter(file_path, front_matter, content)
            
            if success:
                self._log_change({
                    "type": "canonical_added",
                    "file": file_path,
                    "canonical_url": canonical_url
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding canonical tag: {e}")
            return False
    
    def _apply_content_quality_fix(self, fix: Dict) -> bool:
        """Apply content quality improvements"""
        try:
            file_path = fix["file_path"]
            improvements = fix.get("improvements", [])
            
            if not improvements:
                return True
            
            front_matter, content = self._parse_front_matter(file_path)
            modified = False
            
            for improvement in improvements:
                imp_type = improvement["type"]
                value = improvement["value"]
                
                if imp_type == "add_title" and not front_matter.get("title"):
                    front_matter["title"] = value
                    modified = True
                    logger.info(f"Added title '{value}' to {file_path}")
                
                elif imp_type == "add_description" and not front_matter.get("description"):
                    front_matter["description"] = value
                    modified = True
                    logger.info(f"Added description to {file_path}")
            
            if modified:
                success = self._save_front_matter(file_path, front_matter, content)
                if success:
                    self._log_change({
                        "type": "content_quality_improved",
                        "file": file_path,
                        "improvements": improvements
                    })
                return success
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying content quality fix: {e}")
            return False
    
    def _save_front_matter(self, file_path: str, front_matter: Dict, content: str) -> bool:
        """Save front matter and content to file"""
        try:
            if not front_matter:
                new_content = content
            else:
                yaml_content = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
                new_content = f"---\n{yaml_content}---\n{content}"
            
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.debug(f"Saved front matter changes to {file_path}")
            else:
                logger.info(f"DRY RUN: Would save changes to {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving front matter to {file_path}: {e}")
            return False
    
    def _log_change(self, change: Dict):
        """Log a change for tracking purposes"""
        change["timestamp"] = datetime.now().isoformat()
        self.changes_log.append(change)
    
    def export_results(self, analysis_results: Dict, fix_results: Optional[Dict] = None, 
                      output_format: str = "json", output_file: Optional[str] = None) -> str:
        """Export analysis and fix results"""
        try:
            export_data = {
                "analysis": analysis_results,
                "fixes": fix_results,
                "export_timestamp": datetime.now().isoformat(),
                "changes_log": self.changes_log
            }
            
            if output_format == "json":
                output_content = json.dumps(export_data, indent=2, ensure_ascii=False)
                default_filename = f"indexation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif output_format == "yaml":
                output_content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
                default_filename = f"indexation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            output_path = output_file or default_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            logger.info(f"Results exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return ""


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete Indexation Issues Analyzer")
    parser.add_argument("--service-account", required=True, help="Path to Google service account JSON file")
    parser.add_argument("--site-url", required=True, help="Site URL (e.g., https://example.com)")
    parser.add_argument("--site-type", default="jekyll", choices=["jekyll", "hugo"], help="Site type")
    parser.add_argument("--dry-run", action="store_true", help="Run analysis without making changes")
    parser.add_argument("--apply-fixes", action="store_true", help="Apply automated fixes")
    parser.add_argument("--fix-types", nargs="*", help="Specific fix types to apply")
    parser.add_argument("--output-format", default="json", choices=["json", "yaml"], help="Output format")
    parser.add_argument("--output-file", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize analyzer
    analyzer = IndexationAnalyzer(
        service_account_path=args.service_account,
        site_url=args.site_url,
        site_type=args.site_type,
        dry_run=args.dry_run
    )
    
    try:
        # Run analysis
        logger.info("Starting indexation analysis...")
        analysis_results = analyzer.analyze_all_indexation_issues()
        
        if "error" in analysis_results:
            logger.error(f"Analysis failed: {analysis_results['error']}")
            return 1
        
        # Print summary
        summary = analysis_results.get("summary", {})
        print(f"\n=== INDEXATION ANALYSIS SUMMARY ===")
        print(f"Total issues found: {summary.get('total_issues', 0)}")
        print(f"Critical issues: {summary.get('critical_issues', 0)}")
        print(f"High priority issues: {summary.get('high_priority_issues', 0)}")
        print(f"Automated fixes available: {summary.get('automated_fixes_available', 0)}")
        print(f"Manual fixes required: {summary.get('manual_fixes_required', 0)}")
        
        # Show issues by type
        if "issues_by_type" in summary:
            print(f"\n=== ISSUES BY TYPE ===")
            for issue_type, info in summary["issues_by_type"].items():
                print(f"{issue_type}: {info['count']} issues (severity: {info['severity']})")
                print(f"  - Automated fixes: {info['automated_fixes']}")
                print(f"  - Manual fixes: {info['manual_fixes']}")
        
        fix_results = None
        
        # Apply fixes if requested
        if args.apply_fixes:
            logger.info("Applying automated fixes...")
            fix_results = analyzer.apply_fixes(analysis_results, args.fix_types)
            
            if "error" in fix_results:
                logger.error(f"Fix application failed: {fix_results['error']}")
            else:
                fix_summary = fix_results.get("summary", {})
                print(f"\n=== FIX APPLICATION SUMMARY ===")
                print(f"Total fixes attempted: {fix_summary.get('total_fixes_attempted', 0)}")
                print(f"Successful fixes: {fix_summary.get('successful_fixes', 0)}")
                print(f"Failed fixes: {fix_summary.get('failed_fixes', 0)}")
        
        # Export results
        output_path = analyzer.export_results(
            analysis_results, fix_results, 
            args.output_format, args.output_file
        )
        
        if output_path:
            print(f"\nResults exported to: {output_path}")
        
        # Return appropriate exit code
        if summary.get("critical_issues", 0) > 0:
            logger.warning("Critical issues found - recommend immediate attention")
            return 2
        elif summary.get("total_issues", 0) > 0:
            logger.info("Issues found but not critical")
            return 1
        else:
            logger.info("No indexation issues found")
            return 0
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())