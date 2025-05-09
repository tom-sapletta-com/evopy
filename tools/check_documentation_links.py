#!/usr/bin/env python3
"""
Link Checker for Documentation

This script checks the validity of links in Markdown documentation files.
It verifies both internal links (to other files in the repository) and external URLs.

Features:
- Checks if internal file references exist
- Verifies if Markdown files have proper Jekyll front matter
- Tests external URLs for accessibility
- Generates a report of broken links
- Supports GitHub Pages specific path resolution

Usage:
    python check_documentation_links.py [--dir=<directory>] [--fix]

Options:
    --dir=<directory>  Directory to scan for Markdown files (default: project root)
    --fix              Automatically fix missing Jekyll front matter
"""

import os
import re
import sys
import argparse
import logging
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Set, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("evopy-link-checker")

# Constants
GITHUB_PAGES_BASE_URL = "https://tom-sapletta-com.github.io/evopy/"
REPO_BASE_URL = "https://github.com/tom-sapletta-com/evopy/"
MARKDOWN_EXTENSIONS = ['.md', '.markdown']
JEKYLL_FRONT_MATTER_PATTERN = r'^---\s*\n.*?\n---\s*\n'
LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'
IMAGE_LINK_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'
HTML_LINK_PATTERN = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"'
IGNORED_URLS = [
    "http://localhost",
    "https://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1"
]
IGNORED_DIRS = [
    "vendor",
    "node_modules",
    ".venv",
    "venv",
    ".git"
]

class LinkChecker:
    """Class for checking links in Markdown documentation."""
    
    def __init__(self, base_dir: str, fix_issues: bool = False):
        """
        Initialize the link checker.
        
        Args:
            base_dir: Base directory to scan for Markdown files
            fix_issues: Whether to automatically fix issues
        """
        self.base_dir = os.path.abspath(base_dir)
        self.fix_issues = fix_issues
        self.docs_dir = os.path.join(self.base_dir, 'docs')
        self.broken_links: Dict[str, List[Tuple[str, str]]] = {}
        self.missing_front_matter: List[str] = []
        self.checked_urls: Dict[str, bool] = {}
        
    def find_markdown_files(self) -> List[str]:
        """
        Find all Markdown files in the repository.
        
        Returns:
            List of paths to Markdown files
        """
        markdown_files = []
        
        # Check the README.md in the root directory
        readme_path = os.path.join(self.base_dir, 'README.md')
        if os.path.exists(readme_path):
            markdown_files.append(readme_path)
        
        # Check all Markdown files in the docs directory
        if os.path.exists(self.docs_dir):
            for root, dirs, files in os.walk(self.docs_dir):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not any(ignored in os.path.join(root, d) for ignored in IGNORED_DIRS)]
                
                for file in files:
                    if any(file.endswith(ext) for ext in MARKDOWN_EXTENSIONS):
                        markdown_files.append(os.path.join(root, file))
        
        return markdown_files
    
    def check_jekyll_front_matter(self, file_path: str) -> bool:
        """
        Check if a Markdown file has Jekyll front matter.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            True if the file has front matter, False otherwise
        """
        # Skip README.md in the root directory
        if file_path == os.path.join(self.base_dir, 'README.md'):
            return True
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_front_matter = bool(re.match(JEKYLL_FRONT_MATTER_PATTERN, content, re.DOTALL))
        
        if not has_front_matter:
            self.missing_front_matter.append(file_path)
            
            if self.fix_issues:
                self.add_front_matter(file_path, content)
                
        return has_front_matter
    
    def add_front_matter(self, file_path: str, content: str) -> None:
        """
        Add Jekyll front matter to a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            content: Current content of the file
        """
        # Extract the title from the first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(file_path).replace('.md', '')
        
        # Create front matter
        front_matter = f"""---
layout: default
title: {title}
---

"""
        
        # Add front matter to the beginning of the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(front_matter + content)
            
        logger.info(f"Added Jekyll front matter to {os.path.relpath(file_path, self.base_dir)}")
    
    def extract_links(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Extract all links from a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            List of tuples (link_text, link_url)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        links = []
        
        # Extract Markdown links [text](url)
        for text, url in re.findall(LINK_PATTERN, content):
            links.append((text, url))
            
        # Extract image links ![alt](url)
        for alt, url in re.findall(IMAGE_LINK_PATTERN, content):
            links.append((alt, url))
            
        # Extract HTML links <a href="url">
        for url in re.findall(HTML_LINK_PATTERN, content):
            links.append(("HTML link", url))
            
        return links
    
    def check_internal_link(self, link_url: str, file_path: str) -> bool:
        """
        Check if an internal link points to an existing file.
        
        Args:
            link_url: URL of the link
            file_path: Path to the file containing the link
            
        Returns:
            True if the link is valid, False otherwise
        """
        # Handle fragment identifiers
        if '#' in link_url:
            link_url = link_url.split('#')[0]
            
        # Skip empty links (fragment-only links)
        if not link_url:
            return True
            
        # Handle relative paths
        if not link_url.startswith(('http://', 'https://', '/')):
            # Get the directory of the current file
            base_dir = os.path.dirname(file_path)
            
            # Resolve the path
            target_path = os.path.normpath(os.path.join(base_dir, link_url))
            
            # Check if the file exists
            return os.path.exists(target_path)
        
        # Handle absolute paths within the repository
        if link_url.startswith('/'):
            target_path = os.path.normpath(os.path.join(self.base_dir, link_url.lstrip('/')))
            return os.path.exists(target_path)
            
        return True
    
    def check_external_link(self, link_url: str) -> bool:
        """
        Check if an external link is accessible.
        
        Args:
            link_url: URL of the link
            
        Returns:
            True if the link is accessible, False otherwise
        """
        # Skip checking URLs that are already checked
        if link_url in self.checked_urls:
            return self.checked_urls[link_url]
            
        # Skip ignored URLs
        if any(link_url.startswith(ignored) for ignored in IGNORED_URLS):
            return True
            
        # Special handling for GitHub Pages links
        if link_url.startswith(GITHUB_PAGES_BASE_URL):
            # For GitHub Pages links, we'll check if the corresponding file exists in the docs directory
            # Extract the path from the URL
            path = link_url.replace(GITHUB_PAGES_BASE_URL, '')
            
            # Handle special cases
            if path.endswith('/'):
                path += 'index.html'
                
            # Check if it's a .md file or should be an HTML file
            if not path.endswith(('.html', '.md')):
                # Try both .md and .html extensions
                md_path = os.path.join(self.docs_dir, path + '.md')
                html_path = os.path.join(self.docs_dir, path + '.html')
                index_path = os.path.join(self.docs_dir, path, 'index.html')
                md_index_path = os.path.join(self.docs_dir, path, 'index.md')
                
                exists = any(os.path.exists(p) for p in [md_path, html_path, index_path, md_index_path])
                self.checked_urls[link_url] = exists
                return exists
            else:
                # Direct file reference
                file_path = os.path.join(self.docs_dir, path)
                exists = os.path.exists(file_path)
                self.checked_urls[link_url] = exists
                return exists
        
        try:
            # For other external links, send a HEAD request with a timeout
            response = requests.head(link_url, timeout=5, allow_redirects=True)
            
            # If the server doesn't support HEAD, try GET
            if response.status_code >= 400:
                response = requests.get(link_url, timeout=5, stream=True)
                response.close()  # Close the connection immediately
                
            is_valid = response.status_code < 400
            self.checked_urls[link_url] = is_valid
            return is_valid
            
        except requests.RequestException:
            self.checked_urls[link_url] = False
            return False
    
    def check_link(self, link: Tuple[str, str], file_path: str) -> bool:
        """
        Check if a link is valid.
        
        Args:
            link: Tuple (link_text, link_url)
            file_path: Path to the file containing the link
            
        Returns:
            True if the link is valid, False otherwise
        """
        link_text, link_url = link
        
        # Skip anchor links
        if link_url.startswith('#'):
            return True
            
        # Check if it's an external link
        if link_url.startswith(('http://', 'https://')):
            return self.check_external_link(link_url)
            
        # Check internal link
        return self.check_internal_link(link_url, file_path)
    
    def check_file_links(self, file_path: str) -> None:
        """
        Check all links in a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
        """
        # Check if the file has Jekyll front matter
        self.check_jekyll_front_matter(file_path)
        
        # Extract links
        links = self.extract_links(file_path)
        
        # Check each link
        broken_links = []
        for link in links:
            if not self.check_link(link, file_path):
                broken_links.append(link)
                
        # Record broken links
        if broken_links:
            rel_path = os.path.relpath(file_path, self.base_dir)
            self.broken_links[rel_path] = broken_links
    
    def check_all_links(self) -> None:
        """Check links in all Markdown files."""
        markdown_files = self.find_markdown_files()
        
        logger.info(f"Found {len(markdown_files)} Markdown files")
        
        # Check each file
        for file_path in markdown_files:
            rel_path = os.path.relpath(file_path, self.base_dir)
            logger.info(f"Checking links in {rel_path}")
            self.check_file_links(file_path)
    
    def fix_github_pages_links(self) -> None:
        """Fix GitHub Pages links in README.md"""
        if not self.fix_issues:
            return
            
        readme_path = os.path.join(self.base_dir, 'README.md')
        if not os.path.exists(readme_path):
            return
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all links to GitHub Pages
        links = re.findall(LINK_PATTERN, content)
        modified = False
        
        for link_text, link_url in links:
            # Check if it's a link to a documentation file
            if link_url.startswith(GITHUB_PAGES_BASE_URL):
                path = link_url.replace(GITHUB_PAGES_BASE_URL, '')
                
                # Check if the file exists in the docs directory
                if not path.endswith(('.html', '.md')):
                    md_path = os.path.join(self.docs_dir, path + '.md')
                    if os.path.exists(md_path):
                        # Fix the link to point to the .md file
                        new_link_url = f"{GITHUB_PAGES_BASE_URL}{path}.md"
                        content = content.replace(f"[{link_text}]({link_url})", f"[{link_text}]({new_link_url})")
                        modified = True
                        logger.info(f"Fixed link in README.md: {link_url} -> {new_link_url}")
        
        if modified:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Updated README.md with fixed GitHub Pages links")
    
    def generate_report(self) -> None:
        """Generate a report of broken links and missing front matter."""
        # Fix GitHub Pages links if requested
        self.fix_github_pages_links()
        
        print("\n=== Link Checker Report ===\n")
        
        # Report broken links
        if self.broken_links:
            print("Broken Links:")
            for file_path, links in self.broken_links.items():
                print(f"\n  {file_path}:")
                for link_text, link_url in links:
                    print(f"    - [{link_text}]({link_url})")
        else:
            print("No broken links found!")
            
        # Report missing front matter
        if self.missing_front_matter and not self.fix_issues:
            print("\nFiles missing Jekyll front matter:")
            for file_path in self.missing_front_matter:
                rel_path = os.path.relpath(file_path, self.base_dir)
                print(f"  - {rel_path}")
                
        # Summary
        print("\nSummary:")
        print(f"  - {len(self.broken_links)} files with broken links")
        print(f"  - {sum(len(links) for links in self.broken_links.values())} total broken links")
        print(f"  - {len(self.missing_front_matter)} files missing Jekyll front matter")
        
        # Provide fix command
        if self.missing_front_matter and not self.fix_issues:
            print("\nTo automatically fix missing front matter, run:")
            print(f"  python {os.path.basename(__file__)} --fix")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check links in Markdown documentation")
    parser.add_argument("--dir", default=os.getcwd(), help="Directory to scan for Markdown files")
    parser.add_argument("--fix", action="store_true", help="Automatically fix missing Jekyll front matter")
    args = parser.parse_args()
    
    checker = LinkChecker(args.dir, args.fix)
    checker.check_all_links()
    checker.generate_report()
    
    # Return non-zero exit code if there are broken links
    return 1 if checker.broken_links else 0

if __name__ == "__main__":
    sys.exit(main())
