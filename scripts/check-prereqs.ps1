<#
.SYNOPSIS
    Checks required tools for this project on Windows, and optionally
    installs missing ones via winget (built into Windows 10 21H2+ / 11).

.USAGE
    powershell -ExecutionPolicy Bypass -File scripts\check-prereqs.ps1
    powershell -ExecutionPolicy Bypass -File scripts\check-prereqs.ps1 -Install
#>
param(
    [switch]$Install
)

$ErrorActionPreference = "SilentlyContinue"

$tools = @(
    @{ Name = "git";     Command = "git";     Winget = "Git.Git" },
    @{ Name = "python";  Command = "python";  Winget = "Python.Python.3.12" },
    @{ Name = "docker";  Command = "docker";  Winget = "Docker.DockerDesktop" },
    @{ Name = "kubectl"; Command = "kubectl"; Winget = "Kubernetes.kubectl" },
    @{ Name = "kind";    Command = "kind";    Winget = "Kubernetes.kind" }
)

$missing = @()

Write-Host "Checking required tools..." -ForegroundColor Cyan
foreach ($tool in $tools) {
    $cmd = Get-Command $tool.Command -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  OK       $($tool.Name)" -ForegroundColor Green
    } else {
        Write-Host "  MISSING  $($tool.Name)  ->  winget install --id $($tool.Winget) -e" -ForegroundColor Yellow
        $missing += $tool
    }
}

Write-Host ""
Write-Host "Checking Docker daemon..." -ForegroundColor Cyan
docker info *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK       docker daemon running" -ForegroundColor Green
} else {
    Write-Host "  NOT RUNNING  docker daemon  ->  open Docker Desktop from the Start menu, wait for it to say 'Engine running'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking docker compose (bundled with Docker Desktop)..." -ForegroundColor Cyan
docker compose version *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK       docker compose" -ForegroundColor Green
} else {
    Write-Host "  MISSING  docker compose  ->  update Docker Desktop to a recent version, it ships this bundled" -ForegroundColor Yellow
}

if ($missing.Count -eq 0) {
    Write-Host ""
    Write-Host "All required CLI tools found. Start Docker Desktop if it isn't running, then see docs\01-train-models.md." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "$($missing.Count) tool(s) missing." -ForegroundColor Yellow

if ($Install) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "winget not found. Install 'App Installer' from the Microsoft Store, then re-run this script with -Install." -ForegroundColor Red
        exit 1
    }
    foreach ($tool in $missing) {
        Write-Host "Installing $($tool.Name) via winget..." -ForegroundColor Cyan
        winget install --id $tool.Winget -e --accept-package-agreements --accept-source-agreements
    }
    Write-Host ""
    Write-Host "Install commands finished. Close and reopen PowerShell (so PATH refreshes), then re-run this script to confirm everything's found." -ForegroundColor Green
    Write-Host "Docker Desktop specifically needs a manual first launch + WSL2 setup — see docs\windows-setup.md if 'docker' still isn't found after reopening PowerShell." -ForegroundColor Yellow
} else {
    Write-Host "Re-run with -Install to install missing tools automatically via winget:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\check-prereqs.ps1 -Install" -ForegroundColor Yellow
    Write-Host "Or install manually using the winget IDs listed above. See docs\windows-setup.md for full instructions." -ForegroundColor Yellow
}
