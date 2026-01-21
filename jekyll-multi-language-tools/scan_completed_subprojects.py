#!/usr/bin/env python3
"""
Scan Vault for Completed Sub-Projects

Identifies completed sub-projects suitable for blog post generation.

Scoring criteria:
- Money potential (High=3, Medium=2, Low=1)
- Publishing interest (storytelling + recruiter appeal)
- Priority (P0=4, P1=3, P2=2, P3=1)
- Task count (≥8 = series candidate)
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import glob


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract frontmatter from markdown file."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"')

    return frontmatter


def extract_subprojects(content: str, filename: str) -> List[Dict]:
    """Extract all sub-projects from a project file."""
    subprojects = []

    # Find all sub-project headers (### SP or #### SP)
    sp_pattern = r'(#{3,4})\s+(SP\d+(?:\.\d+)?):?\s+(.+?)(?:\n|$)'
    matches = re.finditer(sp_pattern, content, re.MULTILINE)

    for match in matches:
        level = len(match.group(1))
        sp_number = match.group(2)
        sp_title = match.group(3).strip()

        # Extract the sub-project section (until next heading of same or higher level)
        start_pos = match.end()
        next_heading_pattern = f'^#{{{1,{level}}}}\\s+'
        next_match = re.search(next_heading_pattern, content[start_pos:], re.MULTILINE)

        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            end_pos = len(content)

        sp_content = content[start_pos:end_pos]

        # Parse inline dataview fields
        status = 'unknown'
        completion = 0
        identifier = ''

        status_match = re.search(r'Status::\s*(.+?)(?:\n|$)', sp_content)
        if status_match:
            status = status_match.group(1).strip()

        completion_match = re.search(r'Completion::\s*(\d+)%', sp_content)
        if completion_match:
            completion = int(completion_match.group(1))

        identifier_match = re.search(r'Identifier::\s*(\S+)', sp_content)
        if identifier_match:
            identifier = identifier_match.group(1)

        # Count tasks
        tasks = re.findall(r'^- \[[ x-]\]', sp_content, re.MULTILINE)
        task_count = len(tasks)

        # Count completed tasks
        completed_tasks = re.findall(r'^- \[x\]', sp_content, re.MULTILINE)
        completed_count = len(completed_tasks)

        subprojects.append({
            'project_file': filename,
            'sp_number': sp_number,
            'title': sp_title,
            'status': status,
            'completion': completion,
            'identifier': identifier,
            'task_count': task_count,
            'completed_count': completed_count,
            'content_length': len(sp_content)
        })

    return subprojects


def calculate_publishing_interest(sp: Dict, project_meta: Dict) -> Tuple[float, str]:
    """Calculate publishing interest score (0-10)."""
    storytelling = 0
    recruiter_appeal = 0

    # Storytelling potential (0-5)
    if sp['task_count'] >= 8:
        storytelling += 2  # Complex project = good narrative
    if sp['task_count'] >= 5:
        storytelling += 1
    if sp['content_length'] > 2000:
        storytelling += 2  # Detailed documentation = good story

    # Recruiter appeal (0-5)
    project_type = project_meta.get('project_type', 'unknown')
    if 'ftj' in project_type.lower():
        recruiter_appeal += 3  # Work projects show professional skills
    if 'solo' in project_type.lower():
        recruiter_appeal += 2  # Solo projects show initiative

    # Technical keywords boost recruiter appeal
    tech_keywords = ['python', 'automation', 'architecture', 'jekyll', 'github', 'api', 'database']
    title_lower = sp['title'].lower()
    for keyword in tech_keywords:
        if keyword in title_lower:
            recruiter_appeal += 0.5
            break

    recruiter_appeal = min(5, recruiter_appeal)  # Cap at 5

    score = (storytelling + recruiter_appeal) / 2

    # Generate reasoning
    reasoning = f"Storytelling: {storytelling}/5, Recruiter: {recruiter_appeal}/5"

    return score, reasoning


def determine_post_type(task_count: int) -> str:
    """Determine if single post or series."""
    if task_count < 8:
        return 'single'
    else:
        return 'series'


def scan_vault(vault_path: Path) -> List[Dict]:
    """Scan vault for all project files and extract sub-projects."""
    results = []

    # Find all project files
    project_files = []
    for pattern in ['**/21.active_projects/*.PRJ.*.md', '**/31.active_projects/*.PRJ.*.md', '**/23.finished_projects/*.PRJ.*.md', '**/33.finished_projects/*.PRJ.*.md']:
        project_files.extend(glob.glob(str(vault_path / pattern), recursive=True))

    print(f"Found {len(project_files)} project files to scan...\n")

    for file_path in project_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = parse_frontmatter(content)

            # Extract sub-projects
            subprojects = extract_subprojects(content, Path(file_path).name)

            # Add project metadata to each sub-project
            for sp in subprojects:
                sp['priority'] = frontmatter.get('Priority', 'P3')
                sp['money_potential'] = frontmatter.get('money_potential', 'Low')
                sp['project_status'] = frontmatter.get('Status', 'Unknown')

                # Determine project type from path
                if '/31.active_projects/' in file_path or '/33.finished_projects/' in file_path:
                    sp['project_type'] = 'ftj'
                elif '/21.active_projects/' in file_path or '/23.finished_projects/' in file_path:
                    sp['project_type'] = 'solo'
                else:
                    sp['project_type'] = 'other'

                # Calculate publishing interest
                pub_score, pub_reasoning = calculate_publishing_interest(sp, frontmatter)
                sp['publishing_interest'] = pub_score
                sp['pub_reasoning'] = pub_reasoning

                # Determine post type
                sp['post_type'] = determine_post_type(sp['task_count'])

                # Filter: only completed sub-projects
                if 'COMPLETED' in sp['status'].upper() or sp['completion'] == 100:
                    results.append(sp)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    return results


def generate_report(subprojects: List[Dict]) -> str:
    """Generate eligibility report sorted by scoring criteria."""
    # Scoring: money_potential DESC, publishing_interest DESC, priority ASC
    money_scores = {'High': 3, 'Medium': 2, 'Low': 1, 'Unknown': 0}
    priority_scores = {'P0': 4, 'P1': 3, 'P2': 2, 'P3': 1, 'Unknown': 0}

    def sort_key(sp):
        return (
            -money_scores.get(sp['money_potential'], 0),
            -sp['publishing_interest'],
            -priority_scores.get(sp['priority'], 0)
        )

    sorted_sps = sorted(subprojects, key=sort_key)

    # Generate markdown report
    report = "# Completed Sub-Projects - Blog Post Eligibility Report\n\n"
    report += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
    report += f"**Total Completed Sub-Projects:** {len(sorted_sps)}\n\n"
    report += "---\n\n"
    report += "## Top Candidates for Blog Posts\n\n"
    report += "| Rank | Sub-Project | Tasks | Type | Money | Pub Score | Priority | Project |\n"
    report += "|------|-------------|-------|------|-------|-----------|----------|----------|\n"

    for i, sp in enumerate(sorted_sps[:20], 1):  # Top 20
        report += f"| {i} | [[{sp['project_file']}#{sp['sp_number']}]] {sp['title'][:40]} | {sp['task_count']} | {sp['post_type']} | {sp['money_potential']} | {sp['publishing_interest']:.1f}/10 | {sp['priority']} | {sp['project_type']} |\n"

    report += "\n---\n\n"
    report += "## Detailed Top 10\n\n"

    for i, sp in enumerate(sorted_sps[:10], 1):
        report += f"### {i}. {sp['sp_number']}: {sp['title']}\n\n"
        report += f"**Project:** [[{sp['project_file']}]]\n"
        report += f"**Status:** {sp['status']} ({sp['completion']}%)\n"
        report += f"**Tasks:** {sp['completed_count']}/{sp['task_count']} completed\n"
        report += f"**Post Type:** {sp['post_type'].upper()} (<8 tasks = single, ≥8 = series)\n"
        report += f"**Money Potential:** {sp['money_potential']}\n"
        report += f"**Publishing Interest:** {sp['publishing_interest']:.1f}/10 ({sp['pub_reasoning']})\n"
        report += f"**Priority:** {sp['priority']}\n"
        report += f"**Project Type:** {sp['project_type']}\n"
        report += f"**Identifier:** {sp['identifier']}\n\n"

        # Recommended blog target
        if sp['project_type'] == 'ftj':
            blog_target = "kekeli.afanou.com (anonymize work content)"
        elif sp['project_type'] == 'solo':
            blog_target = "beaconharbor.afanou.com or bright-softwares.com"
        else:
            blog_target = "beaconharbor.afanou.com (personal/family)"

        report += f"**Recommended Blog:** {blog_target}\n"
        report += f"**Blog Readiness:** needs_anonymization (default - requires review)\n\n"
        report += "---\n\n"

    return report


def main():
    vault_path = Path('/home/user/my-obsidian')

    print("=" * 60)
    print("Scanning Vault for Completed Sub-Projects")
    print("=" * 60)
    print()

    # Scan vault
    subprojects = scan_vault(vault_path)

    print(f"\n✅ Found {len(subprojects)} completed sub-projects\n")

    # Generate report
    report = generate_report(subprojects)

    # Save report
    report_path = vault_path / 'task_executor/docs/completed-subprojects-blog-eligibility.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"📄 Report saved to: {report_path}")
    print()
    print("=" * 60)
    print("Top 5 Candidates:")
    print("=" * 60)

    # Print top 5
    sorted_sps = sorted(subprojects, key=lambda sp: (
        -{'High': 3, 'Medium': 2, 'Low': 1}.get(sp['money_potential'], 0),
        -sp['publishing_interest'],
        -{'P0': 4, 'P1': 3, 'P2': 2, 'P3': 1}.get(sp['priority'], 0)
    ))

    for i, sp in enumerate(sorted_sps[:5], 1):
        print(f"{i}. {sp['sp_number']}: {sp['title']}")
        print(f"   Tasks: {sp['task_count']}, Money: {sp['money_potential']}, Pub: {sp['publishing_interest']:.1f}/10")
        print()


if __name__ == '__main__':
    main()
