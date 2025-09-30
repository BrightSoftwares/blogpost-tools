#!/usr/bin/env python3
"""
SEO Issue Fixer - Automated SEO Problem Resolution
Processes analysis results and applies fixes to content files
"""

import json
import os
import sys
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml
from bs4 import BeautifulSoup
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('seo_fixer.log')
    ]
)
logger = logging.getLogger(__name__)


class SEOIssueFixer:
    """Automated SEO issue fixer with safety checks"""
    
    def __init__(self, analysis_file: str, content_dirs: List[str], 
                 dry_run: bool = True, backup: bool = True):
        self.analysis_file = analysis_file
        self.content_dirs = content_dirs
        self.dry_run = dry_run
        self.backup = backup
        self.fixes_applied = []
        self.fixes_failed = []
        self.backup_dir = None
        
        # Load analysis results
        self.analysis_data = self._load_analysis()
        
        # URL to file path cache
        self.url_to_file_cache = {}
    
    def _load_analysis(self) -> Dict[str, Any]:
        """Load SEO analysis results"""
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded analysis from {self.analysis_file}")
            return data
        except FileNotFoundError:
            logger.error(f"Analysis file not found: {self.analysis_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in analysis file: {e}")
            sys.exit(1)
    
    def create_backup(self) -> bool:
        """Create backup of content directories"""
        if not self.backup:
            return True
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = Path(f"_seo/backups/backup_{timestamp}")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for content_dir in self.content_dirs:
                if os.path.exists(content_dir):
                    import shutil
                    dest = self.backup_dir / Path(content_dir).name
                    shutil.copytree(content_dir, dest)
                    logger.info(f"Backed up {content_dir} to {dest}")
            
            logger.info(f"Backup created at {self.backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def build_url_to_file_map(self):
        """Build mapping from URLs to file paths"""
        logger.info("Building URL to file path mapping...")
        
        for content_dir in self.content_dirs:
            if not os.path.exists(content_dir):
                continue
            
            for file_path in Path(content_dir).rglob("*.md"):
                try:
                    # Read front matter to get URL/permalink
                    front_matter, _ = self._parse_front_matter(str(file_path))
                    
                    # Try multiple URL patterns
                    possible_urls = self._extract_possible_urls(str(file_path), front_matter)
                    
                    for url in possible_urls:
                        self.url_to_file_cache[url] = str(file_path)
                    
                except Exception as e:
                    logger.warning(f"Error processing {file_path}: {e}")
        
        logger.info(f"Mapped {len(self.url_to_file_cache)} URLs to files")
    
    def _extract_possible_urls(self, file_path: str, front_matter: Dict) -> List[str]:
        """Extract all possible URL patterns for a file"""
        urls = []
        
        # From front matter
        if 'permalink' in front_matter:
            urls.append(front_matter['permalink'])
        if 'url' in front_matter:
            urls.append(front_matter['url'])
        if 'slug' in front_matter:
            urls.append('/' + front_matter['slug'])
        
        # From filename (Jekyll post pattern)
        filename = os.path.basename(file_path)
        if re.match(r'\d{4}-\d{2}-\d{2}-.+\.md$', filename):
            date_part = filename[:10]
            title_part = filename[11:-3]
            year, month, day = date_part.split('-')
            urls.append(f"/{year}/{month}/{day}/{title_part}/")
            urls.append(f"/{year}/{month}/{day}/{title_part}")
        
        # From relative path
        for content_dir in self.content_dirs:
            if content_dir in file_path:
                rel_path = os.path.relpath(file_path, content_dir)
                url_path = '/' + rel_path.replace('.md', '/').replace('\\', '/')
                urls.append(url_path)
                urls.append(url_path.rstrip('/'))
        
        return urls
    
    def _parse_front_matter(self, file_path: str) -> tuple:
        """Parse YAML front matter from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                    return front_matter, body
            
            return {}, content
        except Exception as e:
            logger.warning(f"Error parsing front matter in {file_path}: {e}")
            return {}, ""
    
    def _save_file(self, file_path: str, front_matter: Dict, content: str) -> bool:
        """Save front matter and content to file"""
        try:
            if front_matter:
                yaml_content = yaml.dump(front_matter, default_flow_style=False, 
                                        allow_unicode=True, sort_keys=False)
                full_content = f"---\n{yaml_content}---\n{content}"
            else:
                full_content = content
            
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                logger.debug(f"Saved changes to {file_path}")
            else:
                logger.info(f"DRY RUN: Would save changes to {file_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    def find_file_for_url(self, url: str) -> Optional[str]:
        """Find file path for a given URL"""
        # Normalize URL
        url_normalized = url.rstrip('/')
        
        # Check cache
        if url_normalized in self.url_to_file_cache:
            return self.url_to_file_cache[url_normalized]
        
        # Try with trailing slash
        if url_normalized + '/' in self.url_to_file_cache:
            return self.url_to_file_cache[url_normalized + '/']
        
        # Try to match by partial URL
        for cached_url, file_path in self.url_to_file_cache.items():
            if url_normalized in cached_url or cached_url in url_normalized:
                return file_path
        
        logger.warning(f"Could not find file for URL: {url}")
        return None
    
    def fix_missing_title(self, issue: Dict) -> bool:
        """Fix missing title issue"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            if front_matter.get('title'):
                logger.info(f"Title already exists in {file_path}")
                return True
            
            # Generate title from filename or first heading
            new_title = self._generate_title(file_path, content)
            
            if new_title:
                front_matter['title'] = new_title
                success = self._save_file(file_path, front_matter, content)
                
                if success:
                    logger.info(f"Added title '{new_title}' to {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing missing title: {e}")
            return False
    
    def fix_missing_description(self, issue: Dict) -> bool:
        """Fix missing meta description"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            if front_matter.get('description'):
                logger.info(f"Description already exists in {file_path}")
                return True
            
            # Generate description from first paragraph
            new_description = self._generate_description(content)
            
            if new_description:
                front_matter['description'] = new_description
                success = self._save_file(file_path, front_matter, content)
                
                if success:
                    logger.info(f"Added description to {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing missing description: {e}")
            return False
    
    def fix_short_title(self, issue: Dict) -> bool:
        """Fix short title by expanding it"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            current_title = front_matter.get('title', '')
            
            if len(current_title) >= 30:
                return True
            
            # Try to expand title using first H1 or context
            expanded_title = self._expand_title(current_title, content)
            
            if expanded_title and len(expanded_title) >= 30 and expanded_title != current_title:
                front_matter['title'] = expanded_title
                success = self._save_file(file_path, front_matter, content)
                
                if success:
                    logger.info(f"Expanded title in {file_path}: '{current_title}' -> '{expanded_title}'")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing short title: {e}")
            return False
    
    def fix_missing_h1(self, issue: Dict) -> bool:
        """Fix missing H1 by adding one based on title"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            # Check if H1 already exists
            if re.search(r'^#\s+.+$', content, re.MULTILINE):
                logger.info(f"H1 already exists in {file_path}")
                return True
            
            # Use title as H1
            title = front_matter.get('title', '')
            if not title:
                title = self._generate_title(file_path, content)
            
            if title:
                # Add H1 at the beginning of content
                new_content = f"# {title}\n\n{content}"
                success = self._save_file(file_path, front_matter, new_content)
                
                if success:
                    logger.info(f"Added H1 to {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing missing H1: {e}")
            return False
    
    def fix_multiple_h1(self, issue: Dict) -> bool:
        """Fix multiple H1s by converting extras to H2"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            # Find all H1s
            h1_pattern = r'^#\s+(.+)$'
            h1_matches = list(re.finditer(h1_pattern, content, re.MULTILINE))
            
            if len(h1_matches) <= 1:
                return True
            
            # Keep first H1, convert rest to H2
            new_content = content
            for i, match in enumerate(h1_matches):
                if i > 0:  # Skip first H1
                    old_h1 = match.group(0)
                    new_h2 = '##' + old_h1[1:]  # Change # to ##
                    new_content = new_content.replace(old_h1, new_h2, 1)
            
            success = self._save_file(file_path, front_matter, new_content)
            
            if success:
                logger.info(f"Fixed multiple H1s in {file_path} (converted {len(h1_matches)-1} to H2)")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing multiple H1s: {e}")
            return False
    
    def fix_missing_canonical(self, issue: Dict) -> bool:
        """Fix missing canonical tag"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            if front_matter.get('canonical') or front_matter.get('canonical_url'):
                return True
            
            # Set canonical to the page's own URL
            url = issue['url']
            front_matter['canonical_url'] = url
            
            success = self._save_file(file_path, front_matter, content)
            
            if success:
                logger.info(f"Added canonical URL to {file_path}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing missing canonical: {e}")
            return False
    
    def fix_noindex(self, issue: Dict) -> bool:
        """Fix noindex directive"""
        try:
            file_path = self.find_file_for_url(issue['url'])
            if not file_path:
                return False
            
            front_matter, content = self._parse_front_matter(file_path)
            
            modified = False
            
            # Remove noindex from robots
            if 'robots' in front_matter:
                robots = str(front_matter['robots']).lower()
                if 'noindex' in robots:
                    # Change to index,follow
                    front_matter['robots'] = 'index, follow'
                    modified = True
            
            # Remove noindex field if exists
            if 'noindex' in front_matter:
                del front_matter['noindex']
                modified = True
            
            # Set published to true if false
            if front_matter.get('published') == False:
                front_matter['published'] = True
                modified = True
            
            if modified:
                success = self._save_file(file_path, front_matter, content)
                if success:
                    logger.info(f"Removed noindex directive from {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error fixing noindex: {e}")
            return False
    
    def _generate_title(self, file_path: str, content: str) -> str:
        """Generate title from content or filename"""
        # Try first H1
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Try first H2
        h2_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
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
        
        return title if len(title) > 5 else "Untitled Page"
    
    def _generate_description(self, content: str) -> str:
        """Generate meta description from first paragraph"""
        # Remove markdown formatting
        clean_content = re.sub(r'^#+\s+.+$', '', content, flags=re.MULTILINE)  # Remove headings
        clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_content)  # Remove links
        clean_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_content)  # Remove bold
        clean_content = re.sub(r'\*([^*]+)\*', r'\1', clean_content)  # Remove italic
        clean_content = re.sub(r'`([^`]+)`', r'\1', clean_content)  # Remove code
        
        # Find first substantial paragraph
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            if len(paragraph) >= 100 and not paragraph.startswith(('---', '```', '|')):
                # Truncate to 155 characters
                if len(paragraph) > 155:
                    description = paragraph[:152] + '...'
                else:
                    description = paragraph
                return description
        
        return ""
    
    def _expand_title(self, current_title: str, content: str) -> str:
        """Expand short title using content context"""
        if not current_title:
            return self._generate_title("", content)
        
        # Try to find context in first paragraph
        first_para = content.split('\n\n')[0].strip() if content else ""
        
        # Remove markdown
        first_para = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', first_para)
        first_para = re.sub(r'\*\*?([^*]+)\*\*?', r'\1', first_para)
        
        # Extract key phrases
        sentences = first_para.split('.')
        if sentences and len(sentences[0]) > len(current_title):
            # Use first sentence as expanded title
            expanded = sentences[0].strip()
            if len(expanded) <= 70:
                return expanded
        
        # Fallback: add generic context
        return f"{current_title} - Complete Guide"
    
    def process_issues(self, severity_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Process and fix SEO issues"""
        logger.info("Starting SEO issue fixing process...")
        
        if self.dry_run:
            logger.info("DRY RUN MODE: No actual changes will be made")
        
        # Create backup
        if not self.dry_run and self.backup:
            if not self.create_backup():
                logger.error("Backup failed, aborting fixes")
                return self._generate_report()
        
        # Build URL mapping
        self.build_url_to_file_map()
        
        # Get issues to fix
        issues = self.analysis_data.get('seo_issues', [])
        
        # Filter by severity if specified
        if severity_filter:
            issues = [i for i in issues if i.get('severity') in severity_filter]
        
        logger.info(f"Processing {len(issues)} issues...")
        
        # Fix handlers
        fix_handlers = {
            'missing_title': self.fix_missing_title,
            'missing_description': self.fix_missing_description,
            'short_title': self.fix_short_title,
            'missing_h1': self.fix_missing_h1,
            'multiple_h1': self.fix_multiple_h1,
            'missing_canonical': self.fix_missing_canonical,
            'noindex': self.fix_noindex,
        }
        
        # Process each issue
        for i, issue in enumerate(issues, 1):
            issue_type = issue.get('issue_type')
            url = issue.get('url')
            
            logger.info(f"[{i}/{len(issues)}] Processing {issue_type} for {url}")
            
            if issue_type not in fix_handlers:
                logger.warning(f"No handler for issue type: {issue_type}")
                self.fixes_failed.append({
                    'issue': issue,
                    'reason': 'No handler available'
                })
                continue
            
            try:
                success = fix_handlers[issue_type](issue)
                
                if success:
                    self.fixes_applied.append({
                        'issue_type': issue_type,
                        'url': url,
                        'severity': issue.get('severity')
                    })
                else:
                    self.fixes_failed.append({
                        'issue': issue,
                        'reason': 'Fix handler returned False'
                    })
            except Exception as e:
                logger.error(f"Error processing {issue_type} for {url}: {e}")
                self.fixes_failed.append({
                    'issue': issue,
                    'reason': str(e)
                })
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate fix report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'backup_location': str(self.backup_dir) if self.backup_dir else None,
            'summary': {
                'total_fixes_attempted': len(self.fixes_applied) + len(self.fixes_failed),
                'fixes_successful': len(self.fixes_applied),
                'fixes_failed': len(self.fixes_failed)
            },
            'fixes_applied': self.fixes_applied,
            'fixes_failed': self.fixes_failed
        }
        
        # Save report
        report_file = Path("_seo/seo-analysis/output/fix_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Fix report saved to {report_file}")
        
        return report


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Issue Fixer")
    parser.add_argument("--analysis-file", 
                       default=os.getenv("INPUT_ANALYSIS_FILE", 
                                        "_seo/seo-analysis/output/seo_analysis_latest.json"),
                       help="Path to analysis JSON file")
    parser.add_argument("--content-dirs", nargs='+',
                       default=os.getenv("INPUT_CONTENT_DIRS", "content,_posts,_pages").split(','),
                       help="Content directories to search")
    parser.add_argument("--dry-run", action="store_true",
                       default=os.getenv("INPUT_DRY_RUN", "true").lower() == "true",
                       help="Run without making changes")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup creation")
    parser.add_argument("--severity", nargs='+',
                       choices=['critical', 'high', 'medium', 'low'],
                       default=os.getenv("INPUT_FIX_SEVERITY", "critical,high").split(','),
                       help="Issue severities to fix")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("SEO ISSUE FIXER")
    logger.info("=" * 70)
    logger.info(f"Analysis file: {args.analysis_file}")
    logger.info(f"Content directories: {args.content_dirs}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Backup: {not args.no_backup}")
    logger.info(f"Severity filter: {args.severity}")
    logger.info("=" * 70)
    
    try:
        fixer = SEOIssueFixer(
            analysis_file=args.analysis_file,
            content_dirs=args.content_dirs,
            dry_run=args.dry_run,
            backup=not args.no_backup
        )
        
        report = fixer.process_issues(severity_filter=args.severity)
        
        # Print summary
        summary = report['summary']
        print("\n" + "=" * 70)
        print("FIX SUMMARY")
        print("=" * 70)
        print(f"Total fixes attempted: {summary['total_fixes_attempted']}")
        print(f"Fixes successful: {summary['fixes_successful']}")
        print(f"Fixes failed: {summary['fixes_failed']}")
        
        if args.dry_run:
            print("\nDRY RUN: No actual changes were made")
        else:
            print(f"\nBackup location: {report.get('backup_location', 'N/A')}")
        
        print("=" * 70)
        
        # Exit code based on results
        if summary['fixes_failed'] > summary['fixes_successful']:
            return 1
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())