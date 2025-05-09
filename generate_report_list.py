#!/usr/bin/env python3
"""
Evopy Report List Generator
===========================
This script generates a dynamic list of all available reports in the reports directory.
It creates an HTML page with links to all reports, organized by date and type.

Usage:
    python generate_report_list.py
"""

import os
import re
import glob
import datetime
import logging
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('evopy-report-list-generator')

# Default paths
SCRIPT_DIR = Path(__file__).parent.absolute()
REPORTS_DIR = SCRIPT_DIR / "reports"
OUTPUT_FILE = REPORTS_DIR / "report_list.html"

def parse_report_filename(filename):
    """Parse a report filename to extract type, date, and time."""
    basename = os.path.basename(filename)
    
    # Extract report type, date and time
    match = re.match(r'(comparison|performance|report_simplified)_(\d{8})_(\d{6})\.(\w+)', basename)
    if match:
        report_type, date_str, time_str, extension = match.groups()
        
        # Convert date and time strings to datetime object
        try:
            date_obj = datetime.datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            base_name = f"{report_type}_{date_str}_{time_str}"
            return {
                'type': report_type,
                'date': date_obj,
                'extension': extension,
                'filename': basename,
                'path': filename,
                'base_name': base_name
            }
        except ValueError:
            pass
    
    # Handle special cases like 'latest' reports
    if 'latest' in basename:
        return {
            'type': 'latest',
            'date': datetime.datetime.now(),  # Use current time for sorting
            'extension': basename.split('.')[-1],
            'filename': basename,
            'path': filename,
            'base_name': os.path.splitext(basename)[0]
        }
    
    return None

def get_all_reports():
    """Get all report files and organize them by type and date."""
    report_files = []
    
    # Find all report files (md, html, pdf)
    for ext in ['md', 'html', 'pdf']:
        pattern = os.path.join(REPORTS_DIR, f"*.{ext}")
        report_files.extend(glob.glob(pattern))
    
    # Parse report filenames
    reports = []
    for file_path in report_files:
        report_info = parse_report_filename(file_path)
        if report_info:
            reports.append(report_info)
    
    # Sort reports by date (newest first)
    reports.sort(key=lambda x: x['date'], reverse=True)
    
    # Group reports by type and date
    grouped_reports = defaultdict(list)
    for report in reports:
        # Use date as string key for grouping
        date_key = report['date'].strftime("%Y-%m-%d")
        grouped_reports[date_key].append(report)
    
    return grouped_reports

def generate_html_report_list(grouped_reports):
    """Generate HTML content for the report list."""
    html_content = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evopy - Lista raportów</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        .report-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }
        .report-card h3 {
            margin-top: 0;
            color: #3498db;
        }
        .report-links {
            display: flex;
            gap: 10px;
        }
        .report-link {
            display: inline-block;
            padding: 5px 10px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            font-size: 14px;
        }
        .report-link.md {
            background-color: #2ecc71;
        }
        .report-link.pdf {
            background-color: #e74c3c;
        }
        .report-link:hover {
            opacity: 0.9;
        }
        .report-date {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .report-type {
            display: inline-block;
            padding: 3px 8px;
            background-color: #f1c40f;
            color: #333;
            border-radius: 3px;
            font-size: 12px;
            margin-right: 10px;
        }
        .report-type.comparison {
            background-color: #3498db;
            color: white;
        }
        .report-type.performance {
            background-color: #2ecc71;
            color: white;
        }
        .report-type.simplified {
            background-color: #e67e22;
            color: white;
        }
        .report-type.latest {
            background-color: #9b59b6;
            color: white;
        }
        .no-reports {
            color: #7f8c8d;
            font-style: italic;
        }
        .last-updated {
            margin-top: 50px;
            color: #7f8c8d;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Evopy - Lista raportów</h1>
    
    <p>Ta strona zawiera listę wszystkich wygenerowanych raportów dla systemu Evopy, posortowanych według daty.</p>
"""

    # Add latest reports section if available
    latest_reports = []
    for date_key in grouped_reports:
        for report in grouped_reports[date_key]:
            if 'latest' in report['filename']:
                latest_reports.append(report)
    
    if latest_reports:
        html_content += """
    <h2>Najnowsze raporty</h2>
    <div class="report-card">
        <h3>Aktualne raporty porównawcze</h3>
        <div class="report-links">
"""
        # Group latest reports by base name
        latest_by_base = {}
        for report in latest_reports:
            base_name = report['base_name']
            if base_name not in latest_by_base:
                latest_by_base[base_name] = {}
            latest_by_base[base_name][report['extension']] = report
        
        # Standard formats to check for
        formats_to_check = ['md', 'html', 'pdf']
        
        # Add links for each base name and format
        for base_name, formats in latest_by_base.items():
            for ext in formats_to_check:
                if ext in formats:
                    report = formats[ext]
                    html_content += f'            <a href="{os.path.basename(report["path"])}" class="report-link {ext}">{ext.upper()}</a>\n'
        
        html_content += """
        </div>
    </div>
"""

    # Add reports by date
    html_content += """
    <h2>Raporty według daty</h2>
"""

    if not grouped_reports:
        html_content += """
    <p class="no-reports">Nie znaleziono żadnych raportów.</p>
"""
    else:
        for date_key in sorted(grouped_reports.keys(), reverse=True):
            date_obj = datetime.datetime.strptime(date_key, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%d.%m.%Y")
            
            html_content += f"""
    <h2>{date_formatted}</h2>
"""
            
            # Group by report type and time
            reports_by_time = defaultdict(list)
            for report in grouped_reports[date_key]:
                if 'latest' in report['filename']:
                    continue  # Skip latest reports as they're shown in the top section
                
                time_key = report['date'].strftime("%H:%M:%S")
                reports_by_time[time_key].append(report)
            
            for time_key in sorted(reports_by_time.keys(), reverse=True):
                # Get all reports for this time
                time_reports = reports_by_time[time_key]
                
                # Group by base filename (without extension)
                base_reports = defaultdict(list)
                for report in time_reports:
                    base_name = os.path.splitext(report['filename'])[0]
                    base_reports[base_name].append(report)
                
                for base_name, reports in base_reports.items():
                    # Get report type for display
                    report_type = reports[0]['type']
                    report_type_display = {
                        'comparison': 'Raport porównawczy',
                        'performance': 'Raport wydajności',
                        'report_simplified': 'Raport uproszczony'
                    }.get(report_type, 'Inny raport')
                    
                    report_type_class = report_type
                    if report_type == 'report_simplified':
                        report_type_class = 'simplified'
                    
                    time_formatted = time_key
                    
                    html_content += f"""
    <div class="report-card">
        <span class="report-type {report_type_class}">{report_type_display}</span>
        <span class="report-date">{time_formatted}</span>
        <div class="report-links">
"""
                    
                    # Check which formats are available for this report
                    available_formats = {}
                    for report in reports:
                        available_formats[report['extension']] = report
                    
                    # Standard formats to check for
                    formats_to_check = ['md', 'html', 'pdf']
                    
                    # Add links only for formats that exist
                    for ext in formats_to_check:
                        if ext in available_formats:
                            report = available_formats[ext]
                            html_content += f'            <a href="{os.path.basename(report["path"])}" class="report-link {ext}">{ext.upper()}</a>\n'
                    
                    html_content += """
        </div>
    </div>
"""

    # Add footer
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
    <div class="last-updated">
        Ostatnia aktualizacja: {current_time}
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    """Main function to generate the report list."""
    logger.info("Generating report list...")
    
    # Get all reports
    grouped_reports = get_all_reports()
    
    # Generate HTML content
    html_content = generate_html_report_list(grouped_reports)
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Report list generated: {OUTPUT_FILE}")
    
    # Create a symlink to the latest report list
    latest_link = REPORTS_DIR / "index.html"
    if os.path.exists(latest_link):
        os.remove(latest_link)
    
    try:
        os.symlink(os.path.basename(OUTPUT_FILE), latest_link)
        logger.info(f"Created symlink: {latest_link} -> {os.path.basename(OUTPUT_FILE)}")
    except OSError as e:
        logger.warning(f"Failed to create symlink: {e}")
        # If symlink fails, just copy the file
        import shutil
        shutil.copy2(OUTPUT_FILE, latest_link)
        logger.info(f"Copied file instead: {OUTPUT_FILE} -> {latest_link}")

if __name__ == "__main__":
    main()
