"""
Test script for file comparison API
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def test_compare_files(repo_a_url: str, repo_b_url: str, ref_a: str = "HEAD", ref_b: str = "HEAD"):
    """Test the file comparison API"""
    
    print("=" * 60)
    print("File Comparison API Test")
    print("=" * 60)
    
    # Step 1: Start comparison
    print(f"\n[1/3] Starting file comparison...")
    print(f"      File A: {repo_a_url}")
    print(f"      File B: {repo_b_url}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/compare-files",
            params={
                "repo_a_raw_url": repo_a_url,
                "repo_b_raw_url": repo_b_url,
                "ref_a": ref_a,
                "ref_b": ref_b
            },
            timeout=30
        )
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"      [OK] Task created: {task_id}")
    except requests.exceptions.RequestException as e:
        print(f"      [ERROR] Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Response: {e.response.text}")
        return None
    
    # Step 2: Poll for status with checkpoint info
    print(f"\n[2/3] Waiting for comparison to complete...")
    max_wait = 600  # 10 minutes max
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"      [ERROR] Timeout after {max_wait} seconds")
            return None
        
        try:
            status_response = requests.get(f"{BASE_URL}/status/{task_id}", timeout=5)
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data["status"]
            checkpoint = status_data.get("checkpoint", "")
            
            checkpoint_display = f" [{checkpoint}]" if checkpoint else ""
            print(f"      Status: {status}{checkpoint_display} (elapsed: {int(elapsed)}s)", end='\r')
            
            if status == "completed":
                print(f"\n      [OK] Comparison completed!")
                break
            elif status == "failed":
                print(f"\n      [ERROR] Comparison failed!")
                # Try to get error details
                try:
                    results_response = requests.get(f"{BASE_URL}/results/{task_id}", timeout=5)
                    results = results_response.json()
                    if "results" in results and "meta" in results["results"]:
                        errors = results["results"]["meta"].get("errors", [])
                        if errors:
                            print(f"      Error: {errors[0]}")
                except:
                    pass
                return None
            
            time.sleep(2)  # Wait 2 seconds before checking again
            
        except requests.exceptions.RequestException as e:
            print(f"\n      [ERROR] Error checking status: {e}")
            return None
    
    # Step 3: Get results
    print(f"\n[3/3] Retrieving results...")
    try:
        results_response = requests.get(f"{BASE_URL}/results/{task_id}", timeout=10)
        results_response.raise_for_status()
        results = results_response.json()
        
        print(f"      [OK] Results retrieved")
        print("\n" + "=" * 60)
        print("COMPARISON RESULTS")
        print("=" * 60)
        
        if "results" in results:
            result_data = results["results"]
            
            # Show file info
            print(f"\n[File A] {result_data.get('repo_a', {}).get('raw_url', 'N/A')}")
            repo_a = result_data.get('repo_a', {})
            if repo_a.get('fetched'):
                meta_a = repo_a.get('meta', {})
                print(f"   Size: {meta_a.get('size', 0)} bytes | SHA: {meta_a.get('sha', 'N/A')[:7] if meta_a.get('sha') else 'N/A'}")
            
            print(f"\n[File B] {result_data.get('repo_b', {}).get('raw_url', 'N/A')}")
            repo_b = result_data.get('repo_b', {})
            if repo_b.get('fetched'):
                meta_b = repo_b.get('meta', {})
                print(f"   Size: {meta_b.get('size', 0)} bytes | SHA: {meta_b.get('sha', 'N/A')[:7] if meta_b.get('sha') else 'N/A'}")
            
            # Show diff summary
            diff = result_data.get('diff', {})
            if diff:
                changes = diff.get('summary_lines_changed', {})
                print(f"\n[Diff Summary]")
                print(f"   Added: {changes.get('added', 0)} lines")
                print(f"   Removed: {changes.get('removed', 0)} lines")
                print(f"   Modified: {changes.get('modified', 0)} lines")
            
            # Show analysis
            analysis = result_data.get('analysis', [])
            summary = result_data.get('summary', {})
            
            print(f"\n[Analysis Summary]")
            print(f"   Total Issues: {summary.get('total_issues', 0)}")
            print(f"   Critical: {summary.get('critical', 0)}")
            print(f"   Major: {summary.get('major', 0)}")
            print(f"   Minor: {summary.get('minor', 0)}")
            print(f"   Info: {summary.get('info', 0)}")
            
            if summary.get('recommendation'):
                print(f"\n[Recommendation]")
                print(f"   {summary['recommendation']}")
            
            # Show top issues
            if analysis:
                print(f"\n[Top Issues]")
                for idx, issue in enumerate(analysis[:10], 1):  # Show top 10
                    severity_marker = {
                        "critical": "[CRITICAL]",
                        "major": "[MAJOR]",
                        "minor": "[MINOR]",
                        "info": "[INFO]"
                    }.get(issue.get('severity', 'info'), "[UNKNOWN]")
                    
                    print(f"\n   {idx}. {severity_marker} [{issue.get('type', 'unknown')}]")
                    print(f"      Section: {issue.get('file_section', 'N/A')}")
                    print(f"      Description: {issue.get('description', 'N/A')}")
                    if issue.get('suggestion'):
                        print(f"      Suggestion: {issue.get('suggestion')}")
                    if issue.get('lines', {}).get('start'):
                        print(f"      Lines: {issue['lines']['start']}-{issue['lines'].get('end', 'N/A')}")
            
            # Show metadata
            meta = result_data.get('meta', {})
            if meta:
                print(f"\n[Duration] {meta.get('duration_seconds', 0)}s")
                if meta.get('errors'):
                    print(f"   Errors: {', '.join(meta['errors'])}")
        
        print("\n" + "=" * 60)
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"      [ERROR] Error retrieving results: {e}")
        return None


if __name__ == "__main__":
    # Default test files
    repo_a = "https://raw.githubusercontent.com/psf/requests/main/requests/api.py"
    repo_b = "https://raw.githubusercontent.com/encode/httpx/main/httpx/_client.py"
    
    # Allow command line arguments
    if len(sys.argv) >= 3:
        repo_a = sys.argv[1]
        repo_b = sys.argv[2]
    
    print(f"\nTesting with:")
    print(f"  File A: {repo_a}")
    print(f"  File B: {repo_b}")
    print(f"\n(You can override with: python test_compare_files.py <url_a> <url_b>)\n")
    
    result = test_compare_files(repo_a, repo_b)
    
    if result:
        print("\n[SUCCESS] Test completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILED] Test failed!")
        sys.exit(1)

