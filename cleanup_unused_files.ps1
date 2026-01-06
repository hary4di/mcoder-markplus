# Clean Up Script - Remove Unused Files
# Run this in PowerShell

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "CLEANING UP UNUSED FILES" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding"

# Files to delete
$filesToDelete = @(
    # Old backups
    "PROJECT_OVERVIEW_OLD_BACKUP.md",
    "PROFILE_PHOTO_FEATURE.md",
    
    # Test files
    "test_category_generation.py",
    "test_distribution.py",
    "test_favicon.py",
    "test_improved_prompt.py",
    "test_local_classification.py",
    "test_multilabel.py",
    "test_parallel_admin.py",
    "test_semi_open.py",
    
    # Check/Analysis files
    "check_a6.py",
    "check_categories_in_result.py",
    "check_code13.py",
    "check_kobo_categories.py",
    "check_result.py",
    "analyze_bad_classification.py",
    "analyze_results.py",
    "quick_a6_analysis.py",
    "quick_check.py",
    
    # One-time migration scripts
    "add_profile_photo.py",
    "deploy_profile_photo.bat",
    
    # Redundant deployment scripts
    "deploy.bat",
    "deploy.sh",
    "check-logs.bat",
    "git-push.bat",
    "git-setup.bat",
    "setup-git.ps1",
    
    # Setup scripts (already done)
    "cleanup-old-files.sh",
    "restructure_for_multitenant.sh",
    "quick-setup.sh",
    "setup-vps.sh",
    
    # Favicon scripts (not needed)
    "generate_favicon.py",
    
    # Redundant documentation
    "ADMIN_GUIDE_PARALLEL.md",
    "PARALLEL_PROCESSING.md",
    "TEST_RESULTS_PARALLEL.md",
    "SEMI_OPEN_GUIDE.md",
    "SEMI_OPEN_WEB_GUIDE.md",
    "MOBILE_RESPONSIVE.md",
    "MULTI_TENANT_STRUCTURE.md",
    "NEXT_STEPS_RECOMMENDATIONS.md",
    "DEPLOYMENT_GUIDE.md",
    "VPS_DEPLOYMENT_QUICKSTART.md",
    "DEVELOPMENT_WORKFLOW.md",
    "TECHNOLOGY_SUMMARY.md",
    "FAVICON_GUIDE.md",
    "FAVICON_IMPLEMENTATION.md",
    "HOW_TO_TEST_FIX.txt",
    "INSTALL_PYTHON.md"
)

$deletedCount = 0
$notFoundCount = 0

foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $baseDir $file
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "[DELETED] $file" -ForegroundColor Green
        $deletedCount++
    } else {
        Write-Host "[NOT FOUND] $file" -ForegroundColor Yellow
        $notFoundCount++
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Deleted: $deletedCount files" -ForegroundColor Green
Write-Host "Not Found: $notFoundCount files" -ForegroundColor Yellow
Write-Host ""
Write-Host "Cleanup completed!" -ForegroundColor Green
Write-Host ""
