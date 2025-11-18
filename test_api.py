"""
Simple test script for the GitHub PR Analysis API
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def test_analyze_pr(repo_url: str, pr_number: int):
    """Test the complete PR analysis workflow"""
    
    print("=" * 60)
    print("GitHub PR Analysis API Test")
    print("=" * 60)
    
    # Step 1: Start PR Analysis
    print(f"\n[1/3] Starting PR analysis...")
    print(f"      Repository: {repo_url}")
    print(f"      PR Number: {pr_number}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-pr",
            params={
                "repo_url": repo_url,
                "pr_number": pr_number
            },
            timeout=10
        )
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"      ✓ Task created: {task_id}")
    except requests.exceptions.RequestException as e:
        print(f"      ✗ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Response: {e.response.text}")
        return None
    
    # Step 2: Poll for status
    print(f"\n[2/3] Waiting for analysis to complete...")
    max_wait = 300  # 5 minutes max
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"      ✗ Timeout after {max_wait} seconds")
            return None
        
        try:
            status_response = requests.get(f"{BASE_URL}/status/{task_id}", timeout=5)
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data["status"]
            
            print(f"      Status: {status} (elapsed: {int(elapsed)}s)", end='\r')
            
            if status == "completed":
                print(f"\n      ✓ Analysis completed!")
                break
            elif status == "failed":
                print(f"\n      ✗ Analysis failed!")
                # Try to get error details
                try:
                    results_response = requests.get(f"{BASE_URL}/results/{task_id}", timeout=5)
                    results = results_response.json()
                    if "results" in results:
                        print(f"      Error: {results['results']}")
                except:
                    pass
                return None
            
            time.sleep(2)  # Wait 2 seconds before checking again
            
        except requests.exceptions.RequestException as e:
            print(f"\n      ✗ Error checking status: {e}")
            return None
    
    # Step 3: Get results
    print(f"\n[3/3] Retrieving results...")
    try:
        results_response = requests.get(f"{BASE_URL}/results/{task_id}", timeout=10)
        results_response.raise_for_status()
        results = results_response.json()
        
        print(f"      ✓ Results retrieved")
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        if "results" in results and results["results"]:
            for idx, item in enumerate(results["results"], 1):
                # Check if this is a commit analysis (has commit_sha) or file analysis
                if "commit_sha" in item:
                    # Commit analysis
                    print(f"\n{'='*60}")
                    print(f"COMMIT {idx}: {item.get('commit_sha', 'Unknown')}")
                    print(f"{'='*60}")
                    print(f"Message: {item.get('commit_message', 'N/A')}")
                    print(f"Author: {item.get('author', 'N/A')}")
                    print(f"Date: {item.get('date', 'N/A')}")
                    print(f"\nFiles Analyzed: {len(item.get('files_analyzed', []))}")
                    print("-" * 60)
                    
                    for file_item in item.get('files_analyzed', []):
                        print(f"\n📄 File: {file_item.get('filename', 'Unknown')}")
                        print(f"   Status: {file_item.get('status', 'N/A')} | "
                              f"+{file_item.get('additions', 0)}/-{file_item.get('deletions', 0)}")
                        analysis = file_item.get('analysis', 'No analysis available')
                        # Print first 800 characters
                        if len(analysis) > 800:
                            print(f"   Analysis: {analysis[:800]}...")
                        else:
                            print(f"   Analysis: {analysis}")
                else:
                    # File analysis (fallback)
                    print(f"\n📄 File: {item.get('file_name', 'Unknown')}")
                    print("-" * 60)
                    analysis = item.get('analysis', 'No analysis available')
                    # Print first 500 characters
                    if len(analysis) > 500:
                        print(analysis[:500] + "...")
                    else:
                        print(analysis)
        else:
            print("No results found")
        
        print("\n" + "=" * 60)
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"      ✗ Error retrieving results: {e}")
        return None


if __name__ == "__main__":
    # Default test case
    repo_url = "https://github.com/octocat/Hello-World"
    pr_number = 1
    
    # Allow command line arguments
    if len(sys.argv) >= 2:
        repo_url = sys.argv[1]
    if len(sys.argv) >= 3:
        pr_number = int(sys.argv[2])
    
    print(f"\nTesting with:")
    print(f"  Repository: {repo_url}")
    print(f"  PR Number: {pr_number}")
    print(f"\n(You can override with: python test_api.py <repo_url> <pr_number>)\n")
    
    result = test_analyze_pr(repo_url, pr_number)
    
    if result:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

