#!/bin/bash

# Automated 13F Filing Update - Cron Job Setup
# This script checks for new 13F filings and updates the live portfolio data

# Navigate to project directory
cd /home/wobbler/alpha-research

# Activate virtual environment
source venv/bin/activate

# Run the quarterly scheduler
echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking for 13F filing updates..."
python3 -m market.fetchers.quarterly_scheduler >> logs/13f_updates.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 13F check completed successfully" >> logs/13f_updates.log
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 13F check failed!" >> logs/13f_updates.log
fi

# Optional: Restart backend if updates were made
# Uncomment the following line to auto-restart backend after updates
# pm2 restart alpha-backend
