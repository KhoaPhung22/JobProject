import os
import json
import requests
import time
import argparse
from dotenv import load_dotenv
from database import init_db, upsert_job
from datetime import datetime

# Load environment variables
load_dotenv()

class LinkedInScraper:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY not found in environment variables.")
        
        self.url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        
    def fetch_jobs(self, query, country="CA", pages=1):
        """
        Fetches job listings from JSearch API for a given query with retry logic.
        """
        all_jobs = []
        
        for page in range(1, pages + 1):
            max_retries = 3
            retry_count = 0
            backoff_time = 2
            
            while retry_count <= max_retries:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching page {page} for query: '{query}'...")
                
                querystring = {
                    "query": query,
                    "page": str(page),
                    "num_pages": "1",
                    "country": country,
                    "date_posted": "week",
                    "employment_types": "FULLTIME, CONTRACTOR, PARTTIME, INTERN"
                }
                
                try:
                    response = requests.get(self.url, headers=self.headers, params=querystring)
                    
                    if response.status_code == 429:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"Rate limit hit (429). Retrying in {backoff_time}s... (Attempt {retry_count}/{max_retries})")
                            time.sleep(backoff_time)
                            backoff_time *= 2
                            continue
                        else:
                            print("Max retries reached for 429 error. Skipping this query.")
                            return all_jobs

                    response.raise_for_status()
                    data = response.json()
                    
                    jobs = data.get('data', [])
                    if not jobs:
                        print(f"No more jobs found for query: '{query}' on page {page}.")
                        return all_jobs
                        
                    print(f"Found {len(jobs)} jobs on page {page}.")
                    all_jobs.extend(jobs)
                    
                    # Sleep between pages
                    if page < pages:
                        time.sleep(2)
                    break # Success, move to next page
                        
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data on page {page}: {e}")
                    return all_jobs # Exit for other errors
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return all_jobs
                    
        return all_jobs

    def process_and_save_jobs(self, jobs):
        """
        Processes raw job data and saves to the database.
        """
        saved_count = 0
        for job in jobs:
            try:
                job_record = {
                    'id': job.get('job_id'),
                    'title': job.get('job_title'),
                    'employer': job.get('employer_name'),
                    'logo': job.get('employer_logo'),
                    'city': job.get('job_city'),
                    'state': job.get('job_state'),
                    'country': job.get('job_country'),
                    'description': job.get('job_description'),
                    'apply_link': job.get('job_apply_link'),
                    'is_remote': job.get('job_is_remote', False),
                    'employment_type': job.get('job_employment_type'),
                    'posted_at': job.get('job_posted_at_datetime_utc'),
                    'raw_data': json.dumps(job)
                }
                
                if job_record['id']:
                    upsert_job(job_record)
                    saved_count += 1
            except Exception as e:
                print(f"Error processing job {job.get('job_id')}: {e}")
                
        return saved_count

def run_scraping_cycle(scraper, queries, pages):
    total_new_jobs = 0
    print(f"\n--- Starting Scraping Cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    for query in queries:
        jobs = scraper.fetch_jobs(query, pages=pages)
        saved_count = scraper.process_and_save_jobs(jobs)
        print(f"Successfully processed {saved_count} jobs for query: '{query}'.")
        total_new_jobs += saved_count
        # Add delay between different queries to avoid hitting rate limits
        print("Waiting 3 seconds before next query...")
        time.sleep(3)
        
    print(f"Cycle complete! Total jobs processed/updated: {total_new_jobs}")
    return total_new_jobs

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper Bot")
    parser.add_argument("--loop", action="store_true", help="Run the scraper in a continuous loop")
    parser.add_argument("--interval", type=float, default=24.0, help="Interval between loops in hours (default: 24)")
    parser.add_argument("--pages", type=int, default=2, help="Number of pages to scrape per query (default: 2)")
    args = parser.parse_args()

    print("--- LinkedIn Job Scraper Bot ---")
    
    # Initialize Database
    init_db()
    
    scraper = LinkedInScraper()
    
    queries = [
        "Software Engineer jobs in Canada",
        "Data Scientist jobs in Canada",
        "Frontend Developer jobs in Canada",
        "Backend Developer jobs in Canada",
        "Data Analyst jobs in Canada",
        "Machine Learning Engineer jobs in Canada",
        "Data Engineer jobs in Canada",
        "Business Analyst jobs in Canada",
        "Project Manager jobs in Canada",
        "Product Manager jobs in Canada",
        "QA Engineer jobs in Canada",
        "DevOps Engineer jobs in Canada",
        "Cloud Engineer jobs in Canada",
        "AI Engineer jobs in Canada",
        "MLOps Engineer jobs in Canada",
        "Data Visualization Engineer jobs in Canada",
        "Data Architect jobs in Canada",
        "Data Governance Engineer jobs in Canada",
        "Data Quality Engineer jobs in Canada",
        "Data Integration Engineer jobs in Canada",
        "Data Migration Engineer jobs in Canada",
        "Data Warehouse Engineer jobs in Canada",
        "Data Lake Engineer jobs in Canada",
        "Data Mesh Engineer jobs in Canada",
        "Data Fabric Engineer jobs in Canada",
        "DataOps Engineer jobs in Canada",
    ]
    
    if args.loop:
        while True:
            run_scraping_cycle(scraper, queries, args.pages)
            print(f"Next run in {args.interval} hours. Press Ctrl+C to stop.")
            time.sleep(args.interval * 3600)
    else:
        run_scraping_cycle(scraper, queries, args.pages)

if __name__ == "__main__":
    main()
