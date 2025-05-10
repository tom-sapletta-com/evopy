#!/bin/bash

# Script to ensure comparison_report_latest.md exists for Jekyll build
# This prevents the "No such file or directory" error in GitHub Actions

REPORTS_DIR="reports"
LATEST_REPORT="${REPORTS_DIR}/comparison_report_latest.md"

# Create reports directory if it doesn't exist
mkdir -p "${REPORTS_DIR}"

# Check if the latest report exists
if [ ! -f "${LATEST_REPORT}" ]; then
    echo "Creating empty comparison_report_latest.md file..."
    
    # Find the most recent comparison report
    LATEST_TIMESTAMP_REPORT=$(ls -t ${REPORTS_DIR}/comparison_report_*.md 2>/dev/null | head -n 1)
    
    if [ -n "${LATEST_TIMESTAMP_REPORT}" ]; then
        echo "Copying most recent report to comparison_report_latest.md..."
        cp "${LATEST_TIMESTAMP_REPORT}" "${LATEST_REPORT}"
    else
        # Create a placeholder report if no reports exist
        echo "# Evopy Comparison Report" > "${LATEST_REPORT}"
        echo "No comparison data available yet." >> "${LATEST_REPORT}"
    fi
fi

echo "Latest report file is ready for Jekyll build."
