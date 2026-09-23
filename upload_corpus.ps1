# Syncs the changed/new c4dynamics documentation corpus files to the
# Cloudflare AI Search "c4dynamics-docs" instance (Built-in Storage, Items API).
#
# Usage (run both lines in the SAME PowerShell window/session):
#   $env:CF_API_TOKEN = "your-token-here"   # needs AI Search:Edit + AI Search:Run
#   .\upload_corpus.ps1
#
# Confirmed behavior (2026-09-22 run): the Items API keys an upload by the
# uploaded file's basename (curl's multipart filename, not the full path --
# folder always comes back "" for us). Re-uploading a file with the same
# basename as an existing item updates it in place (same id/created_at,
# status goes back to "queued" for re-indexing) rather than creating a
# duplicate. So a plain upload is enough; no separate list/delete step
# is needed.
#
# Source: https://developers.cloudflare.com/ai-search/api/items/rest-api/

$ErrorActionPreference = "Stop"

if (-not $env:CF_API_TOKEN) {
    Write-Error "CF_API_TOKEN is not set in this session. Run: `$env:CF_API_TOKEN = '...'` first, in this same window."
    exit 1
}

$AccountId = "30155f861b9eb7f24cd03ddbd914802c"
$Instance  = "c4dynamics-docs"
$BaseUrl   = "https://api.cloudflare.com/client/v4/accounts/$AccountId/ai-search/namespaces/default/instances/$Instance/items"
$RepoRoot  = "C:\Users\zivme\Dropbox\c4dynamics"

# The corpus files that changed or were added while calibrating the chatbot.
# Update this list on future runs to whatever docs/source/**.md changed.
$Files = @(
    "docs\source\tutorials\use_cases_overview.md",
    "docs\source\tutorials\syntax_reference.md",
    "docs\source\programs\car_tracker_yolo11\car_tracker_yolo11.md",
    "docs\source\programs\ballistic_ekf\ballistic_coefficient.md",
    "docs\source\programs\car_tracker\car_tracker.md",
    "docs\source\programs\pn_guidance\dof6sim.md"
)

# Rich, source-generated per-class API reference (see generate_api_reference.py)
# -- pulled directly from the real docstrings, not hand-summarized. Re-run that
# script after any docstring change in c4dynamics/**/*.py, then re-run this.
$Files += Get-ChildItem -Path (Join-Path $RepoRoot "docs\source\tutorials\api_generated") -Filter "*.md" |
    ForEach-Object { $_.FullName.Substring($RepoRoot.Length + 1) }

foreach ($relPath in $Files) {
    $fullPath = Join-Path $RepoRoot $relPath

    if (-not (Test-Path $fullPath)) {
        Write-Warning "Skipping missing file: $fullPath"
        continue
    }

    Write-Host "Uploading $relPath ..."
    # curl.exe explicitly -- plain `curl` in PowerShell is aliased to
    # Invoke-WebRequest, which does not support -F multipart uploads the
    # same way.
    curl.exe -X POST $BaseUrl `
        -H "Authorization: Bearer $env:CF_API_TOKEN" `
        -F "file=@$fullPath"
    Write-Host ""
}

Write-Host "`nDone. Re-run a GET on $BaseUrl to confirm, and give the index a minute to finish indexing before testing the chatbot."
