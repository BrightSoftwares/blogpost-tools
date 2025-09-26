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
    
    def __init__(self, service_account_path: str, site_url: str, site_type: str = "jekyll"):
        self.service_account_path = service_account_path
        self.site_url = site_url.rstrip('/')
        self.site_type = site_type.lower()
        self.service = None
        
        if GOOGLE_AVAILABLE:
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
        
        if not self.service:
            logger.error("Google Search Console service not available")
            return {"error": "Google Search Console connection failed"}
        
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
                rules_to_fix, filename):
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
            
            return "/" + os.path.basename(file_path).replace('.md', '/')
        
        except Exception as e:
            logger.warning(f"Error converting path to URL: {e}")
            return "/" + os.path.basename(file_path).replace('.md', '/')
    
    def _get_server_error_type(self, status_code: int) -> str:
        """Get server error type description"""
        error_types = {
            500: "Internal Server Error",
            502: "Bad Gateway", 
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        return error_types.get(status_code, f"Server Error {status_code}")
    
    def _get_server_error_recommendation(self, status_code: int) -> str:
        """Get recommendation for server errors"""
        recommendations = {
            500: "Check server logs for internal errors; verify site generation process",
            502: "Check proxy/load balancer configuration",
            503: "Check server resources and hosting limits",
            504: "Check server response times and optimize slow pages"
        }
        return recommendations.get(status_code, "Contact hosting provider to investigate server issues")
    
    def _generate_server_error_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for server errors (mostly manual)"""
        fixes = []
        
        # Group by error type
        errors_by_type = {}
        for page in pages:
            error_type = page.get("status_code", "unknown")
            if error_type not in errors_by_type:
                errors_by_type[error_type] = []
            errors_by_type[error_type].append(page)
        
        for error_type, affected_pages in errors_by_type.items():
            fix = {
                "type": "server_error_investigation",
                "error_type": error_type,
                "affected_pages": len(affected_pages),
                "automated": False,
                "recommended_actions": [
                    "Check server logs for detailed error information",
                    "Verify site build process completes successfully",
                    "Test individual page generation",
                    "Contact hosting provider if issues persist",
                    "Check server resources and limits"
                ]
            }
            fixes.append(fix)
        
        return fixes
    
    def _validate_canonical_url(self, canonical_url: str) -> bool:
        """Validate if canonical URL is accessible"""
        try:
            if canonical_url.startswith('/'):
                canonical_url = urljoin(self.site_url, canonical_url)
            
            response = requests.head(canonical_url, timeout=10, allow_redirects=True)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _generate_canonical_fixes(self, canonical_issues: List[Dict]) -> List[Dict]:
        """Generate fixes for canonical issues"""
        fixes = []
        
        for issue in canonical_issues:
            issue_type = issue["issue_type"]
            
            if issue_type == "duplicate_no_canonical":
                fix = {
                    "type": "add_canonical_tag",
                    "file_path": issue["page"]["file_path"],
                    "canonical_url": issue["duplicate_of"]["url"],
                    "automated": True
                }
                fixes.append(fix)
            
            elif issue_type == "invalid_canonical":
                fix = {
                    "type": "fix_invalid_canonical", 
                    "file_path": issue["page"]["file_path"],
                    "current_canonical": issue["page"]["canonical_url"],
                    "automated": False,
                    "recommended_action": "Review and correct canonical URL or remove if not needed"
                }
                fixes.append(fix)
        
        return fixes
    
    def _assess_content_quality(self, content: str, front_matter: Dict) -> List[str]:
        """Assess content quality and return list of issues"""
        issues = []
        content_clean = content.strip()
        
        # Check content length
        if len(content_clean) < 300:
            issues.append("content_too_short")
        
        # Check word count
        word_count = len(content_clean.split())
        if word_count < 50:
            issues.append("very_low_word_count")
        
        # Check for missing metadata
        if not front_matter.get('title'):
            issues.append("missing_title")
        
        if not front_matter.get('description'):
            issues.append("missing_description")
        
        # Check content structure
        paragraphs = [p.strip() for p in content_clean.split('\n\n') if len(p.strip()) > 20]
        if len(paragraphs) < 2:
            issues.append("poor_paragraph_structure")
        
        # Check for mostly list content
        lines = content_clean.split('\n')
        list_lines = sum(1 for line in lines if line.strip().startswith(('- ', '* ', '1. ', '2. ', '3.')))
        if lines and list_lines / len(lines) > 0.7:
            issues.append("mostly_list_content")
        
        # Check for duplicate/template content
        if "lorem ipsum" in content_clean.lower() or "placeholder" in content_clean.lower():
            issues.append("template_content")
        
        return issues
    
    def _calculate_content_quality_priority(self, quality_issues: List[str]) -> str:
        """Calculate priority for content quality issues"""
        critical_issues = ["missing_title", "template_content", "very_low_word_count"]
        high_issues = ["content_too_short", "missing_description"]
        
        if any(issue in critical_issues for issue in quality_issues):
            return "high"
        elif any(issue in high_issues for issue in quality_issues):
            return "medium"
        else:
            return "low"
    
    def _get_content_quality_recommendations(self, quality_issues: List[str]) -> str:
        """Get recommendations for content quality issues"""
        recommendations = []
        
        issue_recommendations = {
            "content_too_short": "Expand content to at least 500 words with detailed information",
            "very_low_word_count": "Add substantial content with proper explanations",
            "missing_title": "Add descriptive title to front matter",
            "missing_description": "Add meta description for better SEO",
            "poor_paragraph_structure": "Reorganize into well-structured paragraphs",
            "mostly_list_content": "Add explanatory paragraphs between lists",
            "template_content": "Replace placeholder content with original material"
        }
        
        for issue in quality_issues:
            if issue in issue_recommendations:
                recommendations.append(issue_recommendations[issue])
        
        return "; ".join(recommendations)
    
    def _generate_content_quality_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for content quality issues"""
        fixes = []
        
        for page in pages:
            automated_fixes = []
            manual_fixes = []
            
            for issue in page["quality_issues"]:
                if issue == "missing_title":
                    automated_fixes.append({
                        "field": "title",
                        "action": "generate_from_content"
                    })
                elif issue == "missing_description":
                    automated_fixes.append({
                        "field": "description", 
                        "action": "generate_from_content"
                    })
                else:
                    manual_fixes.append(issue)
            
            if automated_fixes:
                fix = {
                    "type": "automated_content_improvement",
                    "file_path": page["file_path"],
                    "automated_fixes": automated_fixes,
                    "automated": True
                }
                fixes.append(fix)
            
            if manual_fixes:
                fix = {
                    "type": "manual_content_improvement",
                    "file_path": page["file_path"],
                    "issues": manual_fixes,
                    "automated": False,
                    "recommendations": self._get_content_quality_recommendations(manual_fixes)
                }
                fixes.append(fix)
        
        return fixes
    
    def _generate_summary(self, indexation_issues: Dict) -> Dict:
        """Generate summary of all indexation issues"""
        summary = {
            "total_issues": 0,
            "critical_issues": 0,
            "high_priority_issues": 0,
            "medium_priority_issues": 0,
            "low_priority_issues": 0,
            "automated_fixes_available": 0,
            "manual_fixes_required": 0,
            "issues_by_type": {}
        }
        
        for issue_type, issue_data in indexation_issues.items():
            if not issue_data or "pages" not in issue_data:
                continue
                
            page_count = len(issue_data["pages"])
            summary["total_issues"] += page_count
            
            severity = issue_data.get("severity", "medium")
            if severity == "critical":
                summary["critical_issues"] += page_count
            elif severity == "high":
                summary["high_priority_issues"] += page_count
            elif severity == "medium":
                summary["medium_priority_issues"] += page_count
            else:
                summary["low_priority_issues"] += page_count
            
            # Count automated vs manual fixes
            for fix in issue_data.get("fixes", []):
                if fix.get("automated", False):
                    summary["automated_fixes_available"] += 1
                else:
                    summary["manual_fixes_required"] += 1
            
            summary["issues_by_type"][issue_type] = {
                "count": page_count,
                "severity": severity,
                "description": issue_data.get("description", "")
            }
        
        return summary
    
    def save_analysis_report(self, analysis_results: Dict, output_file: str = None) -> str:
        """Save analysis results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"indexation_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Analysis report saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving analysis report: {e}")
            return ""


class IndexationFixer:
    """Applies fixes for indexation issues"""
    
    def __init__(self, site_type: str = "jekyll", dry_run: bool = True):
        self.site_type = site_type.lower()
        self.dry_run = dry_run
        self.changes_log = []
    
    def apply_fixes(self, analysis_results: Dict, fix_types: List[str] = None) -> Dict:
        """Apply indexation fixes based on analysis results"""
        logger.info(f"Applying indexation fixes (dry_run: {self.dry_run})")
        
        if not analysis_results or "indexation_issues" not in analysis_results:
            return {"error": "No analysis results provided"}
        
        results = {
            "fixes_applied": 0,
            "fixes_failed": 0,
            "fixes_skipped": 0,
            "fixes_by_type": {},
            "changes_log": []
        }
        
        # Default to all automated fix types
        if fix_types is None:
            fix_types = ["noindex_tag", "blocked_robots_txt", "not_found_404", "canonical_issues", "crawled_not_indexed"]
        
        try:
            indexation_issues = analysis_results["indexation_issues"]
            
            for issue_type in fix_types:
                if issue_type not in indexation_issues:
                    continue
                
                issue_data = indexation_issues[issue_type]
                fix_results = self._apply_issue_type_fixes(issue_type, issue_data)
                
                results["fixes_by_type"][issue_type] = fix_results
                results["fixes_applied"] += fix_results.get("applied", 0)
                results["fixes_failed"] += fix_results.get("failed", 0)
                results["fixes_skipped"] += fix_results.get("skipped", 0)
            
            results["changes_log"] = self.changes_log
            
            logger.info(f"Indexation fixes complete: {results['fixes_applied']} applied, {results['fixes_failed']} failed")
            
        except Exception as e:
            logger.error(f"Error applying indexation fixes: {e}")
            results["error"] = str(e)
        
        return results
    
    def _apply_issue_type_fixes(self, issue_type: str, issue_data: Dict) -> Dict:
        """Apply fixes for a specific issue type"""
        results = {"applied": 0, "failed": 0, "skipped": 0, "details": []}
        
        try:
            fixes = issue_data.get("fixes", [])
            
            for fix in fixes:
                if not fix.get("automated", False):
                    results["skipped"] += 1
                    continue
                
                try:
                    success = self._apply_single_fix(fix)
                    
                    if success:
                        results["applied"] += 1
                        results["details"].append({
                            "fix_type": fix["type"],
                            "file_path": fix.get("file_path", "N/A"),
                            "status": "applied" if not self.dry_run else "dry_run"
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "fix_type": fix["type"],
                            "file_path": fix.get("file_path", "N/A"),
                            "status": "failed"
                        })
                
                except Exception as e:
                    logger.error(f"Error applying fix {fix.get('type', 'unknown')}: {e}")
                    results["failed"] += 1
        
        except Exception as e:
            logger.error(f"Error processing fixes for {issue_type}: {e}")
            results["failed"] += 1
        
        return results
    
    def _apply_single_fix(self, fix: Dict) -> bool:
        """Apply a single fix"""
        fix_type = fix["type"]
        
        try:
            if fix_type == "fix_noindex":
                return self._fix_noindex(fix)
            elif fix_type == "update_robots_txt":
                return self._fix_robots_txt(fix)
            elif fix_type == "create_redirect":
                return self._create_redirect(fix)
            elif fix_type == "update_internal_link":
                return self._update_internal_link(fix)
            elif fix_type == "add_canonical_tag":
                return self._add_canonical_tag(fix)
            elif fix_type == "automated_content_improvement":
                return self._improve_content_automatically(fix)
            else:
                logger.warning(f"Unknown fix type: {fix_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying {fix_type} fix: {e}")
            return False
    
    def _fix_noindex(self, fix: Dict) -> bool:
        """Fix noindex issues"""
        try:
            file_path = fix["file_path"]
            
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Parse front matter
            front_matter, content = self._parse_front_matter(file_path)
            original_front_matter = front_matter.copy()
            
            # Apply changes
            changes_made = []
            for change in fix.get("changes", []):
                field = change["field"]
                action = change["action"]
                
                if action == "set_value":
                    front_matter[field] = change["new_value"]
                    changes_made.append(f"Set {field} = {change['new_value']}")
                elif action == "remove":
                    if field in front_matter:
                        del front_matter[field]
                        changes_made.append(f"Removed {field}")
            
            if changes_made:
                if not self.dry_run:
                    success = self._save_front_matter(file_path, front_matter, content)
                    if success:
                        self._log_change({
                            "type": "noindex_fix",
                            "file": file_path,
                            "changes": changes_made,
                            "original": original_front_matter,
                            "updated": front_matter
                        })
                        return True
                else:
                    logger.info(f"DRY RUN: Would fix noindex in {file_path}: {'; '.join(changes_made)}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error fixing noindex in {fix['file_path']}: {e}")
            return False
    
    def _fix_robots_txt(self, fix: Dict) -> bool:
        """Fix robots.txt issues"""
        try:
            robots_path = fix["file_path"]
            rule_to_remove = fix["rule_to_remove"]
            
            if not os.path.exists(robots_path):
                logger.error(f"Robots.txt not found: {robots_path}")
                return False
            
            with open(robots_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_path = f"{robots_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if not self.dry_run:
                shutil.copy2(robots_path, backup_path)
            
            # Remove the problematic rule
            lines = content.split('\n')
            new_lines = []
            removed_lines = []
            
            for line in lines:
                if line.strip().startswith('Disallow:') and rule_to_remove in line:
                    removed_lines.append(line.strip())
                    new_lines.append(f"# Removed by indexation fixer: {line}")
                else:
                    new_lines.append(line)
            
            if removed_lines:
                new_content = '\n'.join(new_lines)
                
                if not self.dry_run:
                    with open(robots_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self._log_change({
                        "type": "robots_fix",
                        "file": robots_path,
                        "rule_removed": rule_to_remove,
                        "lines_removed": removed_lines,
                        "backup_file": backup_path
                    })
                    
                    logger.info(f"Fixed robots.txt: removed rule '{rule_to_remove}'")
                else:
                    logger.info(f"DRY RUN: Would remove robots.txt rule: {rule_to_remove}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error fixing robots.txt: {e}")
            return False
    
    def _create_redirect(self, fix: Dict) -> bool:
        """Create redirect for 404 fix"""
        try:
            from_url = fix["from_url"]
            to_url = fix["to_url"]
            
            if self.site_type == "jekyll":
                success = self._create_jekyll_redirect(from_url, to_url)
            else:
                success = self._create_hugo_redirect(from_url, to_url)
            
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
    
    def _improve_content_automatically(self, fix: Dict) -> bool:
        """Apply automated content improvements"""
        try:
            file_path = fix["file_path"]
            front_matter, content = self._parse_front_matter(file_path)
            changes_made = []
            
            for auto_fix in fix.get("automated_fixes", []):
                field = auto_fix["field"]
                action = auto_fix["action"]
                
                if action == "generate_from_content":
                    if field == "title" and not front_matter.get('title'):
                        title = self._generate_title_from_content(content)
                        if title:
                            front_matter['title'] = title
                            changes_made.append(f"Generated title: {title}")
                    
                    elif field == "description" and not front_matter.get('description'):
                        description = self._generate_description_from_content(content)
                        if description:
                            front_matter['description'] = description
                            changes_made.append(f"Generated description")
            
            if changes_made:
                success = self._save_front_matter(file_path, front_matter, content)
                if success:
                    self._log_change({
                        "type": "content_improvement",
                        "file": file_path,
                        "changes": changes_made
                    })
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error improving content automatically: {e}")
            return False
    
    def _generate_title_from_content(self, content: str) -> Optional[str]:
        """Generate title from content"""
        try:
            # Look for first H1 heading
            h1_match = re.search(r'^#\s+(.+)redirect_created',
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
    
    def _update_internal_link(self, fix: Dict) -> bool:
        """Update internal link in markdown file"""
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
    
    def _add_canonical_tag(self, fix: Dict) -> bool:
        """Add canonical tag"""
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
            logger.error(f"Error adding canonical: {e}")
            return False
    
    def _improve_content_automatically(self, fix: Dict) -> bool:
        """Apply automated content improvements"""
        try:
            file_path = fix["file_path"]
            front_matter, content = self._parse_front_matter(file_path)
            changes = []
            
            for auto_fix in fix.get("automated_fixes", []):
                field = auto_fix["field"]
                action = auto_fix["action"]
                
                if action == "generate_from_content":
                    if field == "title" and not front_matter.get('title'):
                        title = self._generate_title_from_content(content)
                        if title:
                            front_matter['title'] = title
                            changes.append(f"Generated title: {title}")
                    
                    elif field == "description" and not front_matter.get('description'):
                        description = self._generate_description_from_content(content)
                        if description:
                            front_matter['description'] = description
                            changes.append("Generated description")
            
            if changes:
                success = self._save_front_matter(file_path, front_matter, content)
                if success:
                    self._log_change({
                        "type": "content_improvement",
                        "file": file_path,
                        "changes": changes
                    })
                return success
            
            return False
        
        except Exception as e:
            logger.error(f"Error improving content: {e}")
            return False
    
    def _generate_title_from_content(self, content: str) -> Optional[str]:
        """Generate title from content"""
        try:
            # Look for headings
            h1_match = re.search(r'^#\s+(.+)
                        'home' in str(file_path).lower() or
                        'about' in str(file_path).lower() or
                        any(keyword in content.lower() for keyword in ['guide', 'tutorial', 'complete'])
                    )
                    
                    if is_important:
                        important_pages.append({
                            "url": self._get_url_from_file_path(str(file_path)),
                            "file_path": str(file_path),
                            "title": front_matter.get('title', ''),
                            "content_length": len(content)
                        })
                
                except Exception as e:
                    continue
        
        return important_pages[:20]  # Limit to top 20 to avoid too many requests
    
    def _get_server_error_type(self, status_code: int) -> str:
        """Get server error type description"""
        error_types = {
            500: "Internal Server Error",
            502: "Bad Gateway", 
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        return error_types.get(status_code, f"Server Error {status_code}")
    
    def _get_server_error_recommendation(self, status_code: int) -> str:
        """Get recommendation for server errors"""
        recommendations = {
            500: "Check server logs for internal errors; verify site generation process",
            502: "Check proxy/load balancer configuration",
            503: "Check server resources and hosting limits",
            504: "Check server response times and optimize slow pages"
        }
        return recommendations.get(status_code, "Contact hosting provider to investigate server issues")
    
    def _generate_server_error_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for server errors (mostly manual)"""
        fixes = []
        
        # Group by error type
        errors_by_type = {}
        for page in pages:
            error_type = page.get("status_code", "unknown")
            if error_type not in errors_by_type:
                errors_by_type[error_type] = []
            errors_by_type[error_type].append(page)
        
        for error_type, affected_pages in errors_by_type.items():
            fix = {
                "type": "server_error_investigation",
                "error_type": error_type,
                "affected_pages": len(affected_pages),
                "automated": False,
                "recommended_actions": [
                    "Check server logs for detailed error information",
                    "Verify site build process completes successfully",
                    "Test individual page generation",
                    "Contact hosting provider if issues persist",
                    "Check server resources and limits"
                ]
            }
            fixes.append(fix)
        
        return fixes
    
    def _validate_canonical_url(self, canonical_url: str) -> bool:
        """Validate if canonical URL is accessible"""
        try:
            if canonical_url.startswith('/'):
                canonical_url = urljoin(self.site_url, canonical_url)
            
            response = requests.head(canonical_url, timeout=10, allow_redirects=True)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _generate_canonical_fixes(self, canonical_issues: List[Dict]) -> List[Dict]:
        """Generate fixes for canonical issues"""
        fixes = []
        
        for issue in canonical_issues:
            issue_type = issue["issue_type"]
            
            if issue_type == "duplicate_no_canonical":
                fix = {
                    "type": "add_canonical_tag",
                    "file_path": issue["page"]["file_path"],
                    "canonical_url": issue["duplicate_of"]["url"],
                    "automated": True
                }
                fixes.append(fix)
            
            elif issue_type == "invalid_canonical":
                fix = {
                    "type": "fix_invalid_canonical", 
                    "file_path": issue["page"]["file_path"],
                    "current_canonical": issue["page"]["canonical_url"],
                    "automated": False,
                    "recommended_action": "Review and correct canonical URL or remove if not needed"
                }
                fixes.append(fix)
        
        return fixes
    
    def _assess_content_quality(self, content: str, front_matter: Dict) -> List[str]:
        """Assess content quality and return list of issues"""
        issues = []
        content_clean = content.strip()
        
        # Check content length
        if len(content_clean) < 300:
            issues.append("content_too_short")
        
        # Check word count
        word_count = len(content_clean.split())
        if word_count < 50:
            issues.append("very_low_word_count")
        
        # Check for missing metadata
        if not front_matter.get('title'):
            issues.append("missing_title")
        
        if not front_matter.get('description'):
            issues.append("missing_description")
        
        # Check content structure
        paragraphs = [p.strip() for p in content_clean.split('\n\n') if len(p.strip()) > 20]
        if len(paragraphs) < 2:
            issues.append("poor_paragraph_structure")
        
        # Check for mostly list content
        lines = content_clean.split('\n')
        list_lines = sum(1 for line in lines if line.strip().startswith(('- ', '* ', '1. ', '2. ', '3.')))
        if lines and list_lines / len(lines) > 0.7:
            issues.append("mostly_list_content")
        
        # Check for duplicate/template content
        if "lorem ipsum" in content_clean.lower() or "placeholder" in content_clean.lower():
            issues.append("template_content")
        
        return issues
    
    def _calculate_content_quality_priority(self, quality_issues: List[str]) -> str:
        """Calculate priority for content quality issues"""
        critical_issues = ["missing_title", "template_content", "very_low_word_count"]
        high_issues = ["content_too_short", "missing_description"]
        
        if any(issue in critical_issues for issue in quality_issues):
            return "high"
        elif any(issue in high_issues for issue in quality_issues):
            return "medium"
        else:
            return "low"
    
    def _get_content_quality_recommendations(self, quality_issues: List[str]) -> str:
        """Get recommendations for content quality issues"""
        recommendations = []
        
        issue_recommendations = {
            "content_too_short": "Expand content to at least 500 words with detailed information",
            "very_low_word_count": "Add substantial content with proper explanations",
            "missing_title": "Add descriptive title to front matter",
            "missing_description": "Add meta description for better SEO",
            "poor_paragraph_structure": "Reorganize into well-structured paragraphs",
            "mostly_list_content": "Add explanatory paragraphs between lists",
            "template_content": "Replace placeholder content with original material"
        }
        
        for issue in quality_issues:
            if issue in issue_recommendations:
                recommendations.append(issue_recommendations[issue])
        
        return "; ".join(recommendations)
    
    def _generate_content_quality_fixes(self, pages: List[Dict]) -> List[Dict]:
        """Generate fixes for content quality issues"""
        fixes = []
        
        for page in pages:
            automated_fixes = []
            manual_fixes = []
            
            for issue in page["quality_issues"]:
                if issue == "missing_title":
                    automated_fixes.append({
                        "field": "title",
                        "action": "generate_from_content"
                    })
                elif issue == "missing_description":
                    automated_fixes.append({
                        "field": "description", 
                        "action": "generate_from_content"
                    })
                else:
                    manual_fixes.append(issue)
            
            if automated_fixes:
                fix = {
                    "type": "automated_content_improvement",
                    "file_path": page["file_path"],
                    "automated_fixes": automated_fixes,
                    "automated": True
                }
                fixes.append(fix)
            
            if manual_fixes:
                fix = {
                    "type": "manual_content_improvement",
                    "file_path": page["file_path"],
                    "issues": manual_fixes,
                    "automated": False,
                    "recommendations": self._get_content_quality_recommendations(manual_fixes)
                }
                fixes.append(fix)
        
        return fixes
    
    def _generate_summary(self, indexation_issues: Dict) -> Dict:
        """Generate summary of all indexation issues"""
        summary = {
            "total_issues": 0,
            "critical_issues": 0,
            "high_priority_issues": 0,
            "medium_priority_issues": 0,
            "low_priority_issues": 0,
            "automated_fixes_available": 0,
            "manual_fixes_required": 0,
            "issues_by_type": {}
        }
        
        for issue_type, issue_data in indexation_issues.items():
            if not issue_data or "pages" not in issue_data:
                continue
                
            page_count = len(issue_data["pages"])
            summary["total_issues"] += page_count
            
            severity = issue_data.get("severity", "medium")
            if severity == "critical":
                summary["critical_issues"] += page_count
            elif severity == "high":
                summary["high_priority_issues"] += page_count
            elif severity == "medium":
                summary["medium_priority_issues"] += page_count
            else:
                summary["low_priority_issues"] += page_count
            
            # Count automated vs manual fixes
            for fix in issue_data.get("fixes", []):
                if fix.get("automated", False):
                    summary["automated_fixes_available"] += 1
                else:
                    summary["manual_fixes_required"] += 1
            
            summary["issues_by_type"][issue_type] = {
                "count": page_count,
                "severity": severity,
                "description": issue_data.get("description", "")
            }
        
        return summary
    
    def save_analysis_report(self, analysis_results: Dict, output_file: str = None) -> str:
        """Save analysis results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"indexation_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Analysis report saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving analysis report: {e}")
            return ""

