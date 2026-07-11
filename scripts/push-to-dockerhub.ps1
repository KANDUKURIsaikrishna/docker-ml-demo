<#
.SYNOPSIS
    Builds and pushes all 5 images to Docker Hub, then rewrites the k8s
    manifests to reference them. Windows equivalent of
    scripts/push-to-dockerhub.sh — same steps as docs/03-push-dockerhub.md,
    automated. Read that doc first if you want to understand each step
    before running this.

.USAGE
    powershell -ExecutionPolicy Bypass -File scripts\push-to-dockerhub.ps1 -Username YOUR_DOCKERHUB_USERNAME
    powershell -ExecutionPolicy Bypass -File scripts\push-to-dockerhub.ps1 -Username YOUR_DOCKERHUB_USERNAME -Tag v2
#>
param(
    [Parameter(Mandatory = $true)][string]$Username,
    [string]$Tag = "v1"
)

$ErrorActionPreference = "Stop"

Write-Host "Logging in to Docker Hub..." -ForegroundColor Cyan
docker login

$services = @("smile-service", "glasses-service", "eyes-service", "gateway", "frontend")

foreach ($svc in $services) {
    $context = if (Test-Path "models\$svc") { "models\$svc" } else { $svc }
    $image = "${Username}/${svc}:${Tag}"
    Write-Host "Building and pushing $image ..." -ForegroundColor Cyan
    docker build -t $image $context
    docker push $image
}

Write-Host ""
Write-Host "Updating k8s manifests to reference ${Username}/*:${Tag} ..." -ForegroundColor Cyan
Get-ChildItem k8s\*.yaml | ForEach-Object {
    (Get-Content $_.FullName) -replace `
        "REPLACE_WITH_YOUR_DOCKERHUB_USERNAME/([a-z-]+):v1", "${Username}/`$1:${Tag}" |
        Set-Content $_.FullName
}

Write-Host ""
Write-Host "Done. Pushed images:" -ForegroundColor Green
foreach ($svc in $services) {
    Write-Host "  ${Username}/${svc}:${Tag}"
}
Write-Host ""
Write-Host "k8s\*.yaml now point at your images. Continue at docs\04-local-k8s-setup.md." -ForegroundColor Green
