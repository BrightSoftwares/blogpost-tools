#!/usr/bin/env python3
"""
GitHub Action main script for Indexation Issues Analyzer
Handles input parameters and sets GitHub Action outputs
"""

import os
import sys
import json
import logging
from pathlib import Path

# Import our indexation analyzer
from indexation_analyzer import IndexationAnalyzer
from indexation_fixer import IndexationFixer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_github_output(name: str, value: str):
    """Set GitHub Action output"""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"::set-output name={name}::{value}")

def set_github_summary(content: str):
    """Set GitHub Action step summary"""
    github_step_summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if github_step_summary:
        with open(github_step_summary, 'a') as f:
            f.write(content + '\n')

def main():
    """Main function for GitHub Action"""
    
    # Get input parameters
    site_url = os.getenv('INPUT_SITE_URL', '').strip()
    site_type = os.getenv('INPUT_SITE_TYPE', 'jekyll').strip().lower()
    service_account_path = os.getenv('INPUT_SERVICE_ACCOUNT_JSON_FILE_PATH', '').strip()
    apply_fixes = os.getenv('INPUT_APPLY_FIXES', 'false').strip().lower() == 'true'
    dry_run = os.getenv('INPUT_DRY_RUN', 'true').strip().lower() == 'true'
    fix_types_input = os.getenv('INPUT_FIX_TYPES', 'noindex_tag,blocked_robots_txt,canonical_issues,crawled_not_indexed').strip()
    max_issues_per_type = int(os.getenv('INPUT_MAX_ISSUES_PER_TYPE', '20'))
    
    # Parse fix types
    fix_types = [ft.strip() for ft in fix_types_input.split(',') if ft.strip()] if fix_types_input else None
    
    # Validate required inputs
    if not site_url:
        logger.error("site_url is required")
        set_github_output('success', 'false')
        sys.exit(1)
    
    if not service_account_path or not os.path.exists(service_account_path):
        logger.error(f"Service account file not found: {service_account_path}")
        set_github_output('success', 'false')
        sys.exit(1)
    
    if site_type not in ['jekyll', 'hugo']:
        logger.error(f"Invalid site_type: {site_type}. Must be 'jekyll' or 'hugo'")
        set_github_output('success', 'false')
        sys.exit(1)
    
    try:
        print("🚀 Starting Indexation Issues Analysis...")
        print(f"📊 Site: {site_url}")
        print(f"🏗️ Type: {site_type}")
        print(f"🔧 Apply fixes: {apply_fixes}")
        print(f"🧪 Dry run: {dry_run}")
        
        # Initialize analyzer
        analyzer = IndexationAnalyzer(
            service_account_path=service_account_path,
            site_url=site_url,
            site_type=site_type
        )
        
        # Run analysis
        print("\n🔍 Analyzing indexation issues...")
        analysis_results = analyzer.analyze_all_indexation_issues()
        
        if "error" in analysis_results:
            logger.error(f"Analysis failed: {analysis_results['error']}")
            set_github_output('success', 'false')
            sys.exit(1)
        
        # Save analysis report
        report_file = analyzer.save_analysis_report(analysis_results)
        
        # Extract summary data
        summary = analysis_results.get("summary", {})
        total_issues = summary.get('total_issues', 0)
        critical_issues = summary.get('critical_issues', 0)
        high_priority = summary.get('high_priority_issues', 0)
        automated_fixes_available = summary.get('automated_fixes_available', 0)
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   • Total issues: {total_issues}")
        print(f"   • Critical issues: {critical_issues}")
        print(f"   • High priority: {high_priority}")
        print(f"   • Automated fixes available: {automated_fixes_available}")
        
        # Set outputs for analysis
        set_github_output('analysis_report', report_file)
        set_github_output('total_issues_found', str(total_issues))
        set_github_output('critical_issues', str(critical_issues))
        
        # Apply fixes if requested
        fixes_applied = 0
        fixes_failed = 0
        changes_log_file = ""
        
        if apply_fixes and total_issues > 0:
            print(f"\n🔧 Applying fixes (dry_run: {dry_run})...")
            
            fixer = IndexationFixer(
                site_type=site_type,
                dry_run=dry_run
            )
            
            fix_results = fixer.apply_fixes(analysis_results, fix_types)
            
            if "error" in fix_results:
                logger.error(f"Fix application failed: {fix_results['error']}")
                set_github_output('success', 'false')
                sys.exit(1)
            
            fixes_applied = fix_results.get('fixes_applied', 0)
            fixes_failed = fix_results.get('fixes_failed', 0)
            fixes_skipped = fix_results.get('fixes_skipped', 0)
            
            print(f"   • Fixes applied: {fixes_applied}")
            print(f"   • Fixes failed: {fixes_failed}")
            print(f"   • Fixes skipped: {fixes_skipped}")
            
            # Save changes log
            if fixes_applied > 0 or fixes_failed > 0:
                changes_log_file = fixer.save_changes_log()
                print(f"   • Changes log: {changes_log_file}")
        
        # Set all outputs
        set_github_output('changes_log', changes_log_file)
        set_github_output('fixes_applied', str(fixes_applied))
        set_github_output('fixes_failed', str(fixes_failed))
        set_github_output('success', 'true')
        
        # Create GitHub step summary
        create_github_summary(analysis_results, fixes_applied, fixes_failed, report_file)
        
        print(f"\n✅ Indexation analysis completed successfully!")
        
        # Exit with error if there are critical issues
        if critical_issues > 0:
            print(f"⚠️ Found {critical_issues} critical issues that need attention")
            sys.exit(1)  # This will fail the action to draw attention
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.error("Process interrupted")
        set_github_output('success', 'false')
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        set_github_output('success', 'false')
        sys.exit(1)

def create_github_summary(analysis_results: dict, fixes_applied: int, fixes_failed: int, report_file: str):
    """Create GitHub Action step summary"""
    
    summary = analysis_results.get("summary", {})
    total_issues = summary.get('total_issues', 0)
    critical_issues = summary.get('critical_issues', 0)
    high_priority = summary.get('high_priority_issues', 0)
    medium_priority = summary.get('medium_priority_issues', 0)
    low_priority = summary.get('low_priority_issues', 0)
    
    # Create summary markdown
    summary_content = f"""# 🔍 Indexation Issues Analysis Report

## 📊 Summary
- **Total Issues Found:** {total_issues}
- **Critical Issues:** {critical_issues} 🔴
- **High Priority:** {high_priority} 🟡
- **Medium Priority:** {medium_priority} 🔵
- **Low Priority:** {low_priority} ⚪

## 🔧 Fix Results
- **Fixes Applied:** {fixes_applied}
- **Fixes Failed:** {fixes_failed}

## 📋 Issues by Type
"""
    
    # Add issues breakdown
    issues_by_type = summary.get('issues_by_type', {})
    for issue_type, details in issues_by_type.items():
        count = details.get('count', 0)
        severity = details.get('severity', 'medium')
        description = details.get('description', '')
        
        severity_icon = {
            'critical': '🔴',
            'high': '🟡', 
            'medium': '🔵',
            'low': '⚪'
        }.get(severity, '🔵')
        
        summary_content += f"- **{issue_type.replace('_', ' ').title()}:** {count} issues {severity_icon}\n"
        if description:
            summary_content += f"  - _{description}_\n"
    
    # Add recommendations
    summary_content += f"""
## 💡 Next Steps
"""
    
    if critical_issues > 0:
        summary_content += f"- ⚠️ **{critical_issues} critical issues need immediate attention**\n"
    
    if fixes_applied > 0:
        summary_content += f"- ✅ {fixes_applied} fixes have been applied\n"
        summary_content += f"- 🧪 Test your site build to ensure no issues\n"
        summary_content += f"- 📤 Submit updated sitemap to Google Search Console\n"
    
    if total_issues - fixes_applied > 0:
        remaining_issues = total_issues - fixes_applied
        summary_content += f"- 🔍 {remaining_issues} issues require manual review\n"
    
    summary_content += f"""
## 📁 Generated Files
- **Analysis Report:** `{report_file}`
- **Site URL:** {analysis_results.get('site_url', 'N/A')}
- **Site Type:** {analysis_results.get('site_type', 'N/A')}
- **Analysis Date:** {analysis_results.get('analysis_timestamp', 'N/A')}

---
*Generated by Indexation Issues Analyzer*
"""
    
    set_github_summary(summary_content)

if __name__ == "__main__":
    main()