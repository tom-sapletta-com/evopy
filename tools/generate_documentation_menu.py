#!/usr/bin/env python3
"""
Menu Generator for Documentation

This script generates a consistent navigation menu for all documentation files in the Evopy project.
It ensures that all documentation files have the same navigation menu, making it easier to navigate
between different sections of the documentation.

Usage:
    python generate_documentation_menu.py [--dir=<directory>] [--apply]

Options:
    --dir=<directory>  Directory containing documentation files (default: docs)
    --apply            Apply changes to files (default: dry run)
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("evopy-menu-generator")

# Constants
MARKDOWN_EXTENSIONS = ['.md', '.markdown']
JEKYLL_FRONT_MATTER_PATTERN = r'^---\s*\n.*?\n---\s*\n'
MENU_START_MARKER = "<!-- MENU_START -->"
MENU_END_MARKER = "<!-- MENU_END -->"
MENU_PATTERN = f"{MENU_START_MARKER}.*?{MENU_END_MARKER}"

# Menu structure
MENU_STRUCTURE = [
    {"title": "Główna dokumentacja", "url": "../index.md", "icon": "📚"},
    {"title": "Raporty testów", "url": "../reports/index.md", "icon": "📊"},
    {"title": "Instrukcja testowania", "url": "../TESTING.md", "icon": "🧪"},
    {"title": "Architektura piaskownic", "url": "../sandbox_architecture.md", "icon": "🏗️"},
    {"title": "Umiejętności programistyczne", "url": "../junior_programmer_skills.md", "icon": "💻"},
    {"title": "Wytyczne projektu", "url": "../project_guidelines.md", "icon": "📝"},
    {"title": "Wsparcie cross-platform", "url": "../cross_platform.md", "icon": "🖥️"},
    {"title": "Testy diagramów Mermaid", "url": "../mermaid_test.md", "icon": "📊"}
]

class MenuGenerator:
    """Class for generating navigation menus for documentation files."""
    
    def __init__(self, base_dir: str, apply_changes: bool = False):
        """
        Initialize the menu generator.
        
        Args:
            base_dir: Base directory containing documentation files
            apply_changes: Whether to apply changes to files
        """
        self.base_dir = os.path.abspath(base_dir)
        self.apply_changes = apply_changes
        self.modified_files = []
        
    def find_markdown_files(self) -> List[str]:
        """
        Find all Markdown files in the documentation directory.
        
        Returns:
            List of paths to Markdown files
        """
        markdown_files = []
        
        for root, _, files in os.walk(self.base_dir):
            # Skip vendor and other non-documentation directories
            if any(ignored in root for ignored in ['vendor', 'node_modules', '.git']):
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in MARKDOWN_EXTENSIONS):
                    markdown_files.append(os.path.join(root, file))
                    
        return markdown_files
    
    def generate_menu_html(self, current_file: str) -> str:
        """
        Generate HTML for the navigation menu.
        
        Args:
            current_file: Path to the current file
            
        Returns:
            HTML for the navigation menu
        """
        menu_html = f"{MENU_START_MARKER}\n"
        menu_html += '<div class="navigation-menu">\n'
        menu_html += '  <ul>\n'
        
        # Determine the relative path prefix based on the current file's depth
        rel_path = os.path.relpath(current_file, self.base_dir)
        depth = len(rel_path.split(os.sep)) - 1
        prefix = "" if depth == 0 else "../" * (depth - 1)
        
        # Special case for files in reports directory
        if "reports" in rel_path:
            prefix = "../" if depth == 1 else "../../"
        
        for item in MENU_STRUCTURE:
            # Determine if this is the current page
            is_current = False
            item_path = item["url"].replace("../", "")
            
            if rel_path.endswith(item_path) or (item_path == "index.md" and rel_path == "index.md"):
                is_current = True
            
            # Adjust the URL based on the current file's depth
            adjusted_url = prefix + item["url"].replace("../", "")
            
            # Generate HTML for the menu item
            current_class = ' class="current"' if is_current else ''
            menu_html += f'    <li{current_class}><a href="{adjusted_url}">{item["icon"]} {item["title"]}</a></li>\n'
            
        menu_html += '  </ul>\n'
        menu_html += '</div>\n'
        menu_html += f"{MENU_END_MARKER}"
        
        return menu_html
    
    def add_menu_to_file(self, file_path: str) -> bool:
        """
        Add navigation menu to a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            True if the file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file has Jekyll front matter
            has_front_matter = bool(re.match(JEKYLL_FRONT_MATTER_PATTERN, content, re.DOTALL))
            
            if not has_front_matter:
                logger.warning(f"File {file_path} does not have Jekyll front matter, skipping")
                return False
                
            # Generate menu HTML
            menu_html = self.generate_menu_html(file_path)
            
            # Check if the file already has a menu
            if re.search(MENU_PATTERN, content, re.DOTALL):
                # Replace existing menu
                new_content = re.sub(MENU_PATTERN, menu_html, content, flags=re.DOTALL)
            else:
                # Add menu after front matter
                front_matter_end = re.search(JEKYLL_FRONT_MATTER_PATTERN, content, re.DOTALL).end()
                new_content = content[:front_matter_end] + "\n" + menu_html + "\n" + content[front_matter_end:]
                
            # Check if the content has changed
            if content == new_content:
                logger.info(f"No changes needed for {file_path}")
                return False
                
            # Apply changes if requested
            if self.apply_changes:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                logger.info(f"Updated menu in {file_path}")
                return True
            else:
                logger.info(f"Would update menu in {file_path} (dry run)")
                return True
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def generate_menus(self) -> None:
        """Generate navigation menus for all Markdown files."""
        markdown_files = self.find_markdown_files()
        
        logger.info(f"Found {len(markdown_files)} Markdown files")
        
        for file_path in markdown_files:
            rel_path = os.path.relpath(file_path, os.path.dirname(self.base_dir))
            logger.info(f"Processing {rel_path}")
            
            if self.add_menu_to_file(file_path):
                self.modified_files.append(rel_path)
                
        # Print summary
        logger.info(f"Modified {len(self.modified_files)} files")
        
        if not self.apply_changes and self.modified_files:
            logger.info("To apply changes, run with --apply")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate navigation menus for documentation files")
    parser.add_argument("--dir", default="docs", help="Directory containing documentation files")
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    args = parser.parse_args()
    
    generator = MenuGenerator(args.dir, args.apply)
    generator.generate_menus()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
