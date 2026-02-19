import sys
import os
import requests
import json
from dotenv import load_dotenv
from database import init_db, upsert_job
from datetime import datetime

# Load environment variables
load_dotenv()

def main():
    print("Starting job search script...")
    
    # Initialize Database
    init_db()
    
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("Error: RAPIDAPI_KEY not found in environment variables.")
        return

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": "Computer Science Data jobs in Canada",
        "page": "1",
        "num_pages": "1",
        "country": "CA",
        "date_posted": "year",
        "employment_types": "FULLTIME, CONTRACTOR, PARTTIME, INTERN"
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        print("Data received successfully. Parsing JSON...")
        data = response.json()
        
        jobs = data.get('data', [])
        print(f"Found {len(jobs)} jobs. Saving to database...")
        
        for job in jobs:
            # Extract relevant fields
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
            
            upsert_job(job_record)
            
        print(f"Success! Saved {len(jobs)} jobs to the database.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response content: {response.text[:200]}...") # Print first 200 chars of response
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()