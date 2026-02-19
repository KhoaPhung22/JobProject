# Run the LinkedIn Job Scraper Bot
# This script is designed to be called by Windows Task Scheduler

# Get the script's directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Run the script using the virtual environment's python execution
./venv/Scripts/python.exe Linkedin_scaped_bot.py --pages 2

# Log the completion
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] Scraping cycle completed via Task Scheduler" | Out-File -FilePath scraping_log.txt -Append
