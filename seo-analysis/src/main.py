#!/usr/bin/env python3
"""
SEO Analysis Script - GitHub Actions Ready
Compatible with pandas 2.0+ and production environments
"""

import pandas as pd
import numpy as np
import requests
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from seo_analysis_fixer import SEOIssueFixer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('seo_analysis.log')
    ]
)
logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """Production-ready SEO analyzer with structured output"""
    
    def __init__(self, sitemap_url: str, site_url: str, output_dir: str = "_seo/seo-analysis/output"):
        self.sitemap_url = sitemap_url
        self.site_url = site_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {
            "metadata": {
                "site_url": site_url,
                "sitemap_url": sitemap_url,
                "analysis_timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "scraped_pages": [],
            "seo_issues": [],
            "statistics": {}
        }
    
    def fetch_sitemap(self) -> List[str]:
        """Fetch and parse sitemap URLs"""
        try:
            logger.info(f"Fetching sitemap: {self.sitemap_url}")
            response = requests.get(self.sitemap_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (SEO Analyzer Bot)'
            })
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            
            if not urls:
                # Try without namespace
                urls = [loc.text for loc in root.findall('.//loc')]
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
            
        except requests.RequestException as e:
            logger.error(f"Error fetching sitemap: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap XML: {e}")
            return []
    
    def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single page for SEO data"""
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (SEO Analyzer Bot)'
            })
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract SEO elements
            page_data = {
                "url": url,
                "status_code": response.status_code,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "h1s": self._extract_headings(soup, 'h1'),
                "h2s": self._extract_headings(soup, 'h2'),
                "h3s": self._extract_headings(soup, 'h3'),
                "h4s": self._extract_headings(soup, 'h4'),
                "h5s": self._extract_headings(soup, 'h5'),
                "h6s": self._extract_headings(soup, 'h6'),
                "canonical": self._extract_canonical(soup),
                "robots": self._extract_robots(soup),
                "hreflang": self._extract_hreflang(soup),
                "word_count": len(soup.get_text().split()),
                "image_count": len(soup.find_all('img')),
                "internal_links": len([a for a in soup.find_all('a', href=True) 
                                      if self._is_internal_link(url, a['href'])]),
                "external_links": len([a for a in soup.find_all('a', href=True) 
                                      if not self._is_internal_link(url, a['href'])]),
                "images_without_alt": len([img for img in soup.find_all('img') 
                                          if not img.get('alt')]),
                "content_length": len(response.content)
            }
            
            return page_data
            
        except requests.RequestException as e:
            logger.warning(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "status_code": 0,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_description(self, soup) -> str:
        """Extract meta description"""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if not desc_tag:
            desc_tag = soup.find('meta', attrs={'property': 'og:description'})
        return desc_tag.get('content', '').strip() if desc_tag else ""
    
    def _extract_headings(self, soup, tag: str) -> str:
        """Extract headings and join with pipe separator"""
        headings = soup.find_all(tag)
        return " | ".join([h.get_text().strip() for h in headings if h.get_text().strip()])
    
    def _extract_canonical(self, soup) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href', '') if canonical else ""
    
    def _extract_robots(self, soup) -> str:
        """Extract robots meta tag"""
        robots = soup.find('meta', attrs={'name': 'robots'})
        return robots.get('content', '') if robots else ""
    
    def _extract_hreflang(self, soup) -> str:
        """Extract hreflang tags"""
        hreflang_tags = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
        return " | ".join([f"{tag.get('hreflang')}:{tag.get('href')}" 
                          for tag in hreflang_tags])
    
    def _is_internal_link(self, base_url: str, link_url: str) -> bool:
        """Check if link is internal"""
        if link_url.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            return False
        
        try:
            base_domain = urlparse(base_url).netloc
            full_url = urljoin(base_url, link_url)
            link_domain = urlparse(full_url).netloc
            return base_domain == link_domain
        except:
            return False
    
    def analyze_seo_issues(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze SEO issues for a page"""
        issues = []
        url = page_data.get("url", "")
        
        # Skip if page had errors
        if page_data.get("error"):
            return issues
        
        # Missing title
        if not page_data.get("title"):
            issues.append({
                "url": url,
                "issue_type": "missing_title",
                "severity": "critical",
                "message": "Page is missing title tag",
                "recommendation": "Add a descriptive title tag (50-60 characters)"
            })
        elif len(page_data.get("title", "")) < 10:
            issues.append({
                "url": url,
                "issue_type": "short_title",
                "severity": "high",
                "message": f"Title is too short: {len(page_data.get('title', ''))} characters",
                "recommendation": "Expand title to 50-60 characters with relevant keywords"
            })
        elif len(page_data.get("title", "")) > 70:
            issues.append({
                "url": url,
                "issue_type": "long_title",
                "severity": "medium",
                "message": f"Title is too long: {len(page_data.get('title', ''))} characters",
                "recommendation": "Shorten title to 50-60 characters to avoid truncation in search results"
            })
        
        # Missing description
        if not page_data.get("description"):
            issues.append({
                "url": url,
                "issue_type": "missing_description",
                "severity": "critical",
                "message": "Page is missing meta description",
                "recommendation": "Add meta description (150-160 characters)"
            })
        elif len(page_data.get("description", "")) < 50:
            issues.append({
                "url": url,
                "issue_type": "short_description",
                "severity": "high",
                "message": f"Description is too short: {len(page_data.get('description', ''))} characters",
                "recommendation": "Expand description to 150-160 characters"
            })
        elif len(page_data.get("description", "")) > 170:
            issues.append({
                "url": url,
                "issue_type": "long_description",
                "severity": "medium",
                "message": f"Description is too long: {len(page_data.get('description', ''))} characters",
                "recommendation": "Shorten description to 150-160 characters"
            })
        
        # Missing H1
        h1s = page_data.get("h1s", "")
        if not h1s:
            issues.append({
                "url": url,
                "issue_type": "missing_h1",
                "severity": "critical",
                "message": "Page is missing H1 heading",
                "recommendation": "Add a single H1 heading that describes the page content"
            })
        else:
            # Multiple H1s
            h1_count = len([h for h in h1s.split(" | ") if h.strip()])
            if h1_count > 1:
                issues.append({
                    "url": url,
                    "issue_type": "multiple_h1",
                    "severity": "high",
                    "message": f"Page has {h1_count} H1 headings (should have 1)",
                    "recommendation": "Use only one H1 tag per page"
                })
        
        # Low word count
        word_count = page_data.get("word_count", 0)
        if word_count < 300:
            issues.append({
                "url": url,
                "issue_type": "low_word_count",
                "severity": "high",
                "message": f"Low word count: {word_count} words",
                "recommendation": "Add more content (aim for 500+ words for better rankings)"
            })
        
        # No canonical
        if not page_data.get("canonical"):
            issues.append({
                "url": url,
                "issue_type": "missing_canonical",
                "severity": "medium",
                "message": "Page is missing canonical tag",
                "recommendation": "Add canonical tag to prevent duplicate content issues"
            })
        
        # Robots noindex
        robots = page_data.get("robots", "").lower()
        if "noindex" in robots:
            issues.append({
                "url": url,
                "issue_type": "noindex",
                "severity": "critical",
                "message": "Page has noindex directive - it won't be indexed by search engines",
                "recommendation": "Remove noindex if you want this page indexed"
            })
        
        # Images without alt text
        images_without_alt = page_data.get("images_without_alt", 0)
        if images_without_alt > 0:
            issues.append({
                "url": url,
                "issue_type": "missing_alt_text",
                "severity": "medium",
                "message": f"{images_without_alt} images missing alt text",
                "recommendation": "Add descriptive alt text to all images for accessibility and SEO"
            })
        
        # No H2 headings
        if not page_data.get("h2s"):
            issues.append({
                "url": url,
                "issue_type": "missing_h2",
                "severity": "low",
                "message": "Page has no H2 headings",
                "recommendation": "Add H2 headings to structure your content"
            })
        
        return issues
    
    def run_analysis(self, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """Run complete SEO analysis"""
        try:
            # Install beautifulsoup4 if not available
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logger.info("Installing beautifulsoup4...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "beautifulsoup4", "lxml"])
                from bs4 import BeautifulSoup
            
            # Fetch sitemap URLs
            urls = self.fetch_sitemap()
            
            if not urls:
                logger.error("No URLs found in sitemap")
                self.results["statistics"]["error"] = "No URLs found in sitemap"
                self._save_empty_results()
                return self.results
            
            # Limit pages if specified
            if max_pages:
                urls = urls[:max_pages]
                logger.info(f"Limited to first {max_pages} pages")
            
            # Scrape pages
            logger.info(f"Scraping {len(urls)} pages...")
            scraped_pages = []
            all_issues = []
            
            for i, url in enumerate(urls, 1):
                logger.info(f"Scraping {i}/{len(urls)}: {url}")
                
                page_data = self.scrape_page(url)
                if page_data:
                    scraped_pages.append(page_data)
                    
                    # Analyze issues
                    issues = self.analyze_seo_issues(page_data)
                    all_issues.extend(issues)
                
                # Rate limiting - be respectful
                if i % 5 == 0:
                    import time
                    time.sleep(1)
            
            # Update results
            self.results["scraped_pages"] = scraped_pages
            self.results["seo_issues"] = all_issues
            
            # Calculate statistics
            self.results["statistics"] = self._calculate_statistics(scraped_pages, all_issues)
            
            # Save results
            self._save_results()
            
            logger.info("Analysis complete")
            return self.results
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
            self.results["statistics"]["error"] = str(e)
            self._save_empty_results()
            return self.results
    
    def _calculate_statistics(self, pages: List[Dict], issues: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from analysis"""
        stats = {
            "total_pages": len(pages),
            "total_issues": len(issues),
            "pages_with_issues": len(set(issue["url"] for issue in issues)),
            "pages_without_issues": 0,
            "issues_by_severity": {
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"]),
                "low": len([i for i in issues if i["severity"] == "low"])
            },
            "issues_by_type": {}
        }
        
        stats["pages_without_issues"] = stats["total_pages"] - stats["pages_with_issues"]
        
        # Count issues by type
        for issue in issues:
            issue_type = issue["issue_type"]
            stats["issues_by_type"][issue_type] = stats["issues_by_type"].get(issue_type, 0) + 1
        
        # Average metrics
        if pages:
            valid_pages = [p for p in pages if not p.get("error")]
            if valid_pages:
                stats["average_word_count"] = sum(p.get("word_count", 0) for p in valid_pages) / len(valid_pages)
                stats["average_title_length"] = sum(len(p.get("title", "")) for p in valid_pages) / len(valid_pages)
                stats["average_description_length"] = sum(len(p.get("description", "")) for p in valid_pages) / len(valid_pages)
                stats["pages_with_errors"] = len([p for p in pages if p.get("error")])
        
        return stats
    
    def _save_results(self):
        """Save results to multiple formats"""
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp = datetime.now().strftime("%A")
        
        # Save JSON (for processing by other scripts)
        json_file = self.output_dir / f"seo_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON results: {json_file}")
        
        # Also save as latest.json for easy access
        latest_json = self.output_dir / "seo_analysis_latest.json"
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved latest results: {latest_json}")
        
        # Save CSV for pages
        if self.results["scraped_pages"]:
            df_pages = pd.DataFrame(self.results["scraped_pages"])
            csv_file = self.output_dir / f"scraped_pages_{timestamp}.csv"
            df_pages.to_csv(csv_file, index=False)
            logger.info(f"Saved pages CSV: {csv_file}")
        
        # Save CSV for issues (prioritized)
        if self.results["seo_issues"]:
            df_issues = pd.DataFrame(self.results["seo_issues"])
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            df_issues['severity_rank'] = df_issues['severity'].map(severity_order)
            df_issues = df_issues.sort_values('severity_rank')
            df_issues = df_issues.drop('severity_rank', axis=1)
            
            issues_file = self.output_dir / f"seo_issues_{timestamp}.csv"
            df_issues.to_csv(issues_file, index=False)
            logger.info(f"Saved issues CSV: {issues_file}")
            
            # Save priority issues (critical and high only)
            priority_issues = df_issues[df_issues['severity'].isin(['critical', 'high'])]
            if not priority_issues.empty:
                priority_file = self.output_dir / f"priority_issues_{timestamp}.csv"
                priority_issues.to_csv(priority_file, index=False)
                logger.info(f"Saved priority issues CSV: {priority_file}")
        
        # Save summary report
        self._save_summary_report(timestamp)
    
    def _save_empty_results(self):
        """Save empty results when analysis fails"""
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp = datetime.now().strftime("%A")
        
        # Save minimal JSON
        json_file = self.output_dir / f"seo_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Create empty CSVs
        pd.DataFrame().to_csv(self.output_dir / f"scraped_pages_{timestamp}.csv", index=False)
        pd.DataFrame().to_csv(self.output_dir / f"seo_issues_{timestamp}.csv", index=False)
        
        logger.warning("Saved empty results due to analysis failure")
    
    def _save_summary_report(self, timestamp: str):
        """Save human-readable summary report"""
        report_file = self.output_dir / f"summary_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SEO ANALYSIS SUMMARY REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Site URL: {self.site_url}\n")
            f.write(f"Sitemap: {self.sitemap_url}\n")
            f.write(f"Analysis Date: {self.results['metadata']['analysis_timestamp']}\n")
            f.write(f"Version: {self.results['metadata']['version']}\n\n")
            
            stats = self.results["statistics"]
            
            f.write("-" * 70 + "\n")
            f.write("OVERVIEW\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Pages Analyzed: {stats.get('total_pages', 0)}\n")
            f.write(f"Pages Without Issues: {stats.get('pages_without_issues', 0)}\n")
            f.write(f"Pages With Issues: {stats.get('pages_with_issues', 0)}\n")
            f.write(f"Total Issues Found: {stats.get('total_issues', 0)}\n\n")
            
            if stats.get('total_pages', 0) > 0:
                issue_rate = (stats.get('pages_with_issues', 0) / stats.get('total_pages', 1)) * 100
                f.write(f"Issue Rate: {issue_rate:.1f}%\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("ISSUES BY SEVERITY\n")
            f.write("-" * 70 + "\n")
            for severity in ["critical", "high", "medium", "low"]:
                count = stats.get('issues_by_severity', {}).get(severity, 0)
                f.write(f"{severity.upper():12} {count:5} issues\n")
            f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("TOP ISSUES (by frequency)\n")
            f.write("-" * 70 + "\n")
            issue_types = sorted(stats.get('issues_by_type', {}).items(), 
                               key=lambda x: x[1], reverse=True)
            for i, (issue_type, count) in enumerate(issue_types[:15], 1):
                f.write(f"{i:2}. {issue_type:30} {count:5} occurrences\n")
            f.write("\n")
            
            if 'average_word_count' in stats:
                f.write("-" * 70 + "\n")
                f.write("AVERAGE METRICS\n")
                f.write("-" * 70 + "\n")
                f.write(f"Average Word Count: {stats['average_word_count']:.0f} words\n")
                f.write(f"Average Title Length: {stats['average_title_length']:.0f} characters\n")
                f.write(f"Average Description Length: {stats['average_description_length']:.0f} characters\n\n")
            
            # Priority recommendations
            f.write("-" * 70 + "\n")
            f.write("PRIORITY RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            
            critical_count = stats.get('issues_by_severity', {}).get('critical', 0)
            high_count = stats.get('issues_by_severity', {}).get('high', 0)
            
            if critical_count > 0:
                f.write(f"⚠️  URGENT: Fix {critical_count} critical issues immediately\n")
                f.write("   These issues prevent pages from being indexed or ranking well.\n\n")
            
            if high_count > 0:
                f.write(f"⚡ HIGH PRIORITY: Address {high_count} high-severity issues\n")
                f.write("   These issues significantly impact SEO performance.\n\n")
            
            if critical_count == 0 and high_count == 0:
                f.write("✅ No critical or high-priority issues found!\n")
                f.write("   Focus on optimizing medium and low-priority items.\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("NEXT STEPS\n")
            f.write("-" * 70 + "\n")
            f.write("1. Review priority_issues CSV for pages needing immediate attention\n")
            f.write("2. Fix critical issues (noindex, missing titles/descriptions)\n")
            f.write("3. Address high-priority issues (short titles, missing H1s)\n")
            f.write("4. Optimize content length and structure\n")
            f.write("5. Re-run analysis after fixes to verify improvements\n\n")
            
            f.write("=" * 70 + "\n")
        
        logger.info(f"Saved summary report: {report_file}")


def main():
    """Main execution function for GitHub Actions"""
    
    # Get environment variables
    site_url = os.getenv("INPUT_SITE_URL")
    sitemap_url = os.getenv("INPUT_SITEMAP_URL")
    dry_run = os.getenv("INPUT_DRY_RUN", "true").lower() == "true"
    should_fix_issues = os.getenv("INPUT_FIX_ISSUES", "false").lower() == "true"
    fix_severity = os.getenv("INPUT_FIX_SEVERITY", "critical,high").split(',')
    content_dirs = os.getenv("INPUT_CONTENT_DIRS", "content,_posts,_pages").split(',')
    no_backup = os.getenv("INPUT_NO_BACKUP", "false").lower() == "true"
    max_pages = os.getenv("INPUT_MAX_PAGES")
    output_dir = os.getenv("INPUT_OUTPUT_DIR", "_seo/seo-analysis/output")
    
    # Validate required inputs
    if not site_url:
        logger.error("INPUT_SITE_URL is required")
        sys.exit(1)
    
    # Default sitemap URL if not provided
    if not sitemap_url:
        sitemap_url = f"{site_url.rstrip('/')}/sitemap.xml"
        logger.info(f"Using default sitemap URL: {sitemap_url}")
    
    # Log configuration
    logger.info("=" * 70)
    logger.info("SEO ANALYSIS CONFIGURATION")
    logger.info("=" * 70)
    logger.info(f"Site URL: {site_url}")
    logger.info(f"Sitemap URL: {sitemap_url}")
    logger.info(f"Dry Run: {dry_run}")
    logger.info(f"Max Pages: {max_pages or 'unlimited'}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("=" * 70)
    
    if dry_run:
        logger.info("DRY RUN MODE: Analysis will be performed but no changes will be made")
    
    try:
        # Convert max_pages to int if provided
        max_pages_int = int(max_pages) if max_pages else None
        
        # Initialize analyzer
        analyzer = SEOAnalyzer(sitemap_url, site_url, output_dir)
        
        # Run analysis
        results = analyzer.run_analysis(max_pages_int)
        
        # Print summary to console
        stats = results.get("statistics", {})
        print("\n" + "=" * 70)
        print("SEO ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Total Pages Analyzed: {stats.get('total_pages', 0)}")
        print(f"Total Issues Found: {stats.get('total_issues', 0)}")
        print(f"Pages Without Issues: {stats.get('pages_without_issues', 0)}")
        print(f"Pages With Issues: {stats.get('pages_with_issues', 0)}")
        print("\nIssues by Severity:")
        print(f"  Critical: {stats.get('issues_by_severity', {}).get('critical', 0)}")
        print(f"  High:     {stats.get('issues_by_severity', {}).get('high', 0)}")
        print(f"  Medium:   {stats.get('issues_by_severity', {}).get('medium', 0)}")
        print(f"  Low:      {stats.get('issues_by_severity', {}).get('low', 0)}")
        print("=" * 70)
        
        # Set GitHub Actions output
        output_file = Path(output_dir) / "seo_analysis_latest.json"
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            # print(f'{name}={value}', file=fh)
            print(f"analysis_file={output_file}", file=fh)
            print(f"total_issues={stats.get('total_issues', 0)}", file=fh)
            print(f"critical_issues={stats.get('issues_by_severity', {}).get('critical', 0)}", file=fh)
            
            # print(f"::set-output name=analysis_file::{output_file}")
            # print(f"::set-output name=total_issues::{stats.get('total_issues', 0)}")
            # print(f"::set-output name=critical_issues::{stats.get('issues_by_severity', {}).get('critical', 0)}")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

    analysis_file = f"{output_dir}/seo_analysis_latest.json"

    logger.info("=" * 70)
    logger.info("SEO ISSUE FIXER")
    logger.info("=" * 70)
    logger.info(f"Analysis file: {analysis_file}")
    logger.info(f"Content directories: {content_dirs}")
    logger.info(f"Dry run: {dry_run}")
    logger.info(f"Backup: {not no_backup}")
    logger.info(f"Severity filter: {fix_severity}")
    logger.info("=" * 70)

    if should_fix_issues:
        logger.info("FIXING MODE: Running the script to fix the issues automatically")
        try:
            fixer = SEOIssueFixer(
                analysis_file=analysis_file,
                content_dirs=content_dirs,
                dry_run=dry_run,
                backup=not no_backup
            )
            
            report = fixer.process_issues(severity_filter=fix_severity)
            
            # Print summary
            summary = report['summary']
            print("\n" + "=" * 70)
            print("FIX SUMMARY")
            print("=" * 70)
            print(f"Total fixes attempted: {summary['total_fixes_attempted']}")
            print(f"Fixes successful: {summary['fixes_successful']}")
            print(f"Fixes failed: {summary['fixes_failed']}")
            
            if dry_run:
                print("\nDRY RUN: No actual changes were made")
            else:
                print(f"\nBackup location: {report.get('backup_location', 'N/A')}")
            
            print("=" * 70)
            
            # Exit code based on results
                
            # Return appropriate exit code
            if stats.get('issues_by_severity', {}).get('critical', 0) > 0:
                logger.warning("Critical issues found - immediate attention required")
                return 2
            elif stats.get('total_issues', 0) > 0:
                logger.info("Issues found - review and optimize")
                return 0  # Don't fail the build for non-critical issues
            elif summary['fixes_failed'] > summary['fixes_successful']:
                logger.error("Issue fixing failed. Look at what is happening!")
                return 1
            else:
                logger.info("No issues found - site is well optimized!")
                return 0
            
            # if summary['fixes_failed'] > summary['fixes_successful']:
            #     return 1
            # return 0
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return 1
    else:
        logger.info("NO FIXING MODE: No fixing will be performed")

if __name__ == "__main__":
    sys.exit(main())
