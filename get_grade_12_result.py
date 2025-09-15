import requests
import time
import random
from typing import Optional

# API endpoint
url = "https://api.eaes.et/api/v1/results/web"

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_user_input() -> tuple[str, str]:
    """Get admission number and first name from user input."""
    print("Ethiopian Grade 12 Results Checker")
    print("=" * 40)
    
    while True:
        admission_no = input("Enter admission number: ").strip()
        if admission_no:
            break
        print("Admission number cannot be empty. Please try again.")
    
    while True:
        first_name = input("Enter first name: ").strip()
        if first_name:
            break
        print("First name cannot be empty. Please try again.")
    
    return admission_no, first_name

def make_request_with_retry(admission_no: str, first_name: str, max_retries: int = 5) -> Optional[dict]:
    """Make API request with retry mechanism and traffic handling."""
    
    for attempt in range(max_retries):
        try:
            # Random delay to avoid overwhelming the server
            if attempt > 0:
                delay = min(2 ** attempt + random.uniform(0, 1), 30)  # Exponential backoff with jitter
                print(f"Attempt {attempt + 1}/{max_retries}. Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)
            
            # Rotate user agent
            user_agent = random.choice(USER_AGENTS)
            
            # Request payload
            payload = {
                "admissionNo": admission_no,
                "firstName": first_name,
                "turnstileToken": ""
            }
            
            # Headers with rotating user agent
            headers = {
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://eaes.et/",
                "Origin": "https://eaes.et"
            }
            
            print(f"Making request (attempt {attempt + 1}/{max_retries})...")
            
            # Send POST request with timeout
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                timeout=30,
                allow_redirects=True
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Too Many Requests
                print(f"Rate limited (429). Server is busy. Waiting longer...")
                time.sleep(10 + random.uniform(0, 5))
            elif response.status_code == 503:  # Service Unavailable
                print(f"Service temporarily unavailable (503). Retrying...")
                time.sleep(5 + random.uniform(0, 3))
            else:
                print(f"Request failed with status code: {response.status_code}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                else:
                    print("Response text:", response.text)
                    
        except requests.exceptions.Timeout:
            print(f"Request timed out (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.ConnectionError:
            print(f"Connection error (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e} (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"Unexpected error: {e} (attempt {attempt + 1}/{max_retries})")
    
    return None

def display_results(data: dict) -> None:
    """Display the student information and results in a formatted way."""
    # Format and print student info
    student = data.get('studentInfo', {})
    print("\n" + "="*50)
    print("STUDENT INFORMATION")
    print("="*50)
    print(f"Full Name    : {student.get('FullName', 'N/A')}")
    print(f"Admission No.: {student.get('Admission_No', 'N/A')}")
    print(f"Sex          : {student.get('Sex', 'N/A')}")
    print(f"School       : {student.get('School', 'N/A')}")
    print(f"Stream       : {student.get('Stream', 'N/A')}")
    print(f"Photo URL    : {student.get('Photo', 'N/A')}")
    print(f"Print URL    : {student.get('print', 'N/A')}")
    
    # Format and print results
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    results = data.get('results', [])
    if results:
        for r in results:
            subject = r.get('Subject', 'N/A')
            result = r.get('Result', 'N/A')
            print(f"{subject:30}: {result}")
    else:
        print("No results found.")

def main():
    """Main function to run the grade 12 results checker."""
    try:
        # Get user input
        admission_no, first_name = get_user_input()
        
        print(f"\nChecking results for: {first_name} (Admission: {admission_no})")
        print("Please wait while we fetch your results...\n")
        
        # Make request with retry mechanism
        data = make_request_with_retry(admission_no, first_name)
        
        if data:
            display_results(data)
            print("\n" + "="*50)
            print("Results retrieved!")
        else:
            print("\n" + "="*50)
            print("Failed to retrieve results after multiple attempts.")
            print("The server might be experiencing high traffic.")
            print("Please try again later.")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
