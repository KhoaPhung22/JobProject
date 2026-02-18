# Script to check if the backend is running
import requests
import sys

def test_api():
    try:
        response = requests.get("http://127.0.0.1:8000/jobs")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Status Code: {response.status_code}")
            print(f"Job Count: {data.get('count')}")
            if data.get('jobs'):
                print(f"First Job Title: {data['jobs'][0]['title']}")
            else:
                print("No jobs found in response.")
        else:
            print(f"Failed. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_api()
