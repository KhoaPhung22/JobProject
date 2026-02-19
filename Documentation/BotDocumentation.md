How the LinkedIn Scraper Bot Works - Detailed Guide
This document provides a step-by-step technical explanation of the 
Linkedin_scaped_bot.py
 script, covering its architecture, data flow, and features.

1. Overview of Technology Stack
Language: Python
API Provider: JSearch API (via RapidAPI) to fetch job listings from LinkedIn, Indeed, and other platforms.
Database: SQLite (local 
jobs.db
) for persistent storage.
Configuration: 
.env
 file for secure API key management.
2. Step-by-Step Data Flow
Step 1: Initialization & Configuration
When you run the script, it first loads environment variables (like your RAPIDAPI_KEY) using python-dotenv. It then initializes the SQLite database by calling 
init_db()
 from 
database.py
, ensuring the 
jobs
 table exists.

Step 2: The 
LinkedInScraper
 Class
The core logic is encapsulated in the 
LinkedInScraper
 class:

init
: Sets up the API URL and headers, including your RapidAPI key.
fetch_jobs(query, pages)
: This is where the magic happens.
It sends an HTTP GET request to the JSearch API.
Parameters include the search query (e.g., "Software Engineer in Canada"), the page number, and filters like date_posted: week.
It receives a JSON response containing a list of job postings.
process_and_save_jobs(jobs)
:
It iterates through each job in the JSON list.
It maps the API's fields (like job_title, employer_name, job_id) to the specific format expected by your database.
It calls 
upsert_job()
 for each record. "Upsert" means it will Insert the job if it's new, or Update it if the job_id already exists, ensuring you never have duplicates.
Step 3: Command-Line Interface (CLI)
The bot uses the argparse library to handle different ways of running:

Standard Run: Fetches jobs for the predefined queries and exits.
--loop: Enters a while True loop, running the scraping cycle and then sleeping for the specified interval.
--pages: Allows you to control how deep historical data you want to fetch.
Step 4: Scraping Cycle execution
The 
run_scraping_cycle
 function coordinates the queries:

It loops through a list of job titles (queries).
For each title, it fetches the specified number of pages.
It prints progress updates to the terminal (with timestamps).
After all queries are done, it displays the total number of jobs processed.
3. Automation Logic
Built-in Loop
When --loop is active, the script uses time.sleep(interval * 3600). This puts the script into a "hibernation" state for the number of hours you chose (e.g., 12 hours), then automatically wakes up and starts the next cycle.

PowerShell Runner
The 
run_scraper.ps1
 script is a simple "trigger":

It navigates to your project folder.
It activates the Python virtual environment (venv).
It runs the scraper for a single cycle and logs the result to scraping_log.txt.
This script is intended to be triggered by the Windows Task Scheduler.
4. Summary of Key Files
Linkedin_scaped_bot.py
: Main bot logic.
database.py
: SQLite database interaction layer.
run_scraper.ps1
: Helper for Windows automation.
.env
: Stores your secret API key.
jobs.db
: Where all your job data lives.