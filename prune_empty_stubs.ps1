# Finds and removes empty Sphinx autodoc .rst stub items from the Cloudflare
# AI Search "c4dynamics-docs" instance -- items whose entire content is a bare
# directive like ".. automethod:: ekf.predict" and nothing else. These were
# uploaded as raw .rst SOURCE files; the real content only exists after a
# Sphinx build (which pulls the live docstring in), so the raw source for an
# autodoc-only page is just that one pointer line, not actual documentation.
# They were found to actively win retrieval over the real, rich content in
# docs/source/tutorials/api_generated/ (see generate_api_reference.py) for
# some queries, purely because their filename matches the class+method name
# exactly -- so they're worth removing rather than just out-competing.
#
# SAFE BY DEFAULT: this only LISTS candidates and shows their content. It
# does not delete anything unless you pass -Confirm.
#
# Usage (run in the SAME PowerShell window/session where you set the token):
#   $env:CF_API_TOKEN = "your-token-here"   # needs AI Search:Edit + AI Search:Run
#   .\prune_empty_stubs.ps1                 # dry run: lists what WOULD be deleted
#   .\prune_empty_stubs.ps1 -Confirm        # actually deletes the listed items
#
# NOTE: the delete endpoint pattern below ($BaseUrl/$id, DELETE) matches the
# documented REST convention (https://developers.cloudflare.com/ai-search/api/items/rest-api/)
# but has not been exercised by a successful call before -- watch the first
# real run's output carefully.

param(
    [switch]$Confirm
)

$ErrorActionPreference = "Stop"

if (-not $env:CF_API_TOKEN) {
    Write-Error "CF_API_TOKEN is not set in this session. Run: `$env:CF_API_TOKEN = '...'` first, in this same window."
    exit 1
}

$AccountId = "30155f861b9eb7f24cd03ddbd914802c"
$Instance  = "c4dynamics-docs"
$BaseUrl   = "https://api.cloudflare.com/client/v4/accounts/$AccountId/ai-search/namespaces/default/instances/$Instance/items"
$Headers   = @{ Authorization = "Bearer $env:CF_API_TOKEN" }

Write-Host "Fetching item list (paginated -- the API defaults to 20 per page)..."
$items = @()
$page = 1
$perPage = 20   # per_page=100 was rejected with 400 Bad Request; 20 (the API's
                # own default) is confirmed to work, so loop pages instead.

do {
    $response = Invoke-RestMethod -Uri "$BaseUrl`?page=$page&per_page=$perPage" -Headers $Headers -Method Get
    $items += $response.result
    $totalCount = $response.result_info.total_count
    Write-Host "  page $page`: $($response.result.Count) items (have $($items.Count) of $totalCount so far)"
    $page++
} while ($items.Count -lt $totalCount -and $response.result.Count -gt 0)

if (-not $items) {
    Write-Host "No items returned -- check the response shape hasn't changed:"
    $response | ConvertTo-Json -Depth 6
    exit 1
}

Write-Host "Total items in index: $($items.Count)"

# Autodoc per-member stub pages follow a distinctive, deeply-dotted Python
# path naming convention, e.g. "c4dynamics.filters.ekf.ekf.predict.rst" --
# unlike genuine conceptual pages (index.rst, installation.rst, filters.rst,
# tsipor.rst, ...), which are short, undotted names.
$candidates = $items | Where-Object { $_.key -match '^c4dynamics(\.[A-Za-z0-9_]+){3,}\.rst$' }

Write-Host "`n$($candidates.Count) candidate(s) matching the autodoc-stub naming pattern.`n"

$confirmedEmpty = @()

foreach ($item in $candidates) {
    Write-Host "Checking $($item.key) (id: $($item.id), file_size: $($item.file_size)) ..."

    try {
        $content = Invoke-RestMethod -Uri "$BaseUrl/$($item.id)/download" -Headers $Headers -Method Get -ErrorAction Stop
    } catch {
        Write-Warning "  Could not download content for $($item.key): $($_.Exception.Message) -- skipping, not deleting."
        continue
    }

    $text = if ($content -is [string]) { $content } else { $content | Out-String }

    # Real shape (confirmed 2026-09-22 by downloading an actual item):
    #   c4dynamics.filters.ekf.ekf.predict
    #   ==================================
    #
    #   .. currentmodule:: c4dynamics.filters.ekf
    #
    #   .. automethod:: ekf.predict
    # i.e. a title line + underline, an optional ".. currentmodule::" line,
    # and exactly one ".. auto*::" directive -- strip all of that off and
    # check whether anything of substance is left over.
    $lines = $text -split "`r?`n"
    $remaining = New-Object System.Collections.Generic.List[string]

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $isTitleUnderline = ($i -gt 0) -and ($line -match '^[=\-~]{3,}\s*$') -and ($lines[$i - 1].Trim().Length -gt 0)
        $isDirective = $line.TrimStart() -match '^\.\. (currentmodule|automethod|autoclass|autofunction|autoattribute|automodule)::'
        if ($isTitleUnderline -or $isDirective -or $line.Trim().Length -eq 0) {
            continue
        }
        # The line right before a title-underline is the title itself -- skip it too.
        if (($i -lt $lines.Count - 1) -and ($lines[$i + 1] -match '^[=\-~]{3,}\s*$')) {
            continue
        }
        $remaining.Add($line)
    }

    $leftover = ($remaining -join "`n").Trim()

    if ($leftover.Length -eq 0) {
        Write-Host "  -> EMPTY STUB (nothing left after stripping title/directives)" -ForegroundColor Yellow
        $confirmedEmpty += $item
    } else {
        Write-Host "  -> has real content ($($leftover.Length) chars beyond title/directives) -- NOT a candidate, leaving alone."
    }
}

Write-Host "`n$($confirmedEmpty.Count) confirmed empty stub(s) out of $($candidates.Count) candidate(s) checked.`n"

if ($confirmedEmpty.Count -eq 0) {
    Write-Host "Nothing to delete."
    exit 0
}

$confirmedEmpty | ForEach-Object { Write-Host "  $($_.key)  (id: $($_.id))" }

if (-not $Confirm) {
    Write-Host "`nDry run only -- nothing was deleted. Re-run with -Confirm to actually delete these $($confirmedEmpty.Count) item(s)."
    exit 0
}

Write-Host "`nDeleting $($confirmedEmpty.Count) item(s)..."

$deleted = 0
$failed = @()

foreach ($item in $confirmedEmpty) {
    Write-Host "Deleting $($item.key) (id: $($item.id)) ..."
    try {
        Invoke-RestMethod -Uri "$BaseUrl/$($item.id)" -Headers $Headers -Method Delete -ErrorAction Stop | Out-Null
        $deleted++
    } catch {
        Write-Warning "  Failed to delete $($item.key): $($_.Exception.Message) -- continuing with the rest."
        $failed += $item
    }
}

Write-Host "`nDeleted $deleted of $($confirmedEmpty.Count)."
if ($failed.Count -gt 0) {
    Write-Host "$($failed.Count) failed (likely transient -- just re-run the script, it will re-detect only what's left):"
    $failed | ForEach-Object { Write-Host "  $($_.key)" }
}

Write-Host "`nDone."
