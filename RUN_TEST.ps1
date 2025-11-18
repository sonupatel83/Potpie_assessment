# PowerShell script to test the API with a real GitHub PR

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GitHub PR Analysis API Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Test with FastAPI repository PR #1
$repoUrl = "https://github.com/tiangolo/fastapi"
$prNumber = 1

Write-Host "Testing with:" -ForegroundColor Yellow
Write-Host "  Repository: $repoUrl" -ForegroundColor White
Write-Host "  PR Number: $prNumber" -ForegroundColor White
Write-Host ""

# Run the Python test script
python test_api.py $repoUrl $prNumber

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

