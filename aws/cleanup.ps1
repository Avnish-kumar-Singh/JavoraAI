$ErrorActionPreference = "Stop"

$TerraformDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "terraform"
Set-Location $TerraformDir

Write-Host "==> Destroying AWS deployment"
terraform destroy -auto-approve

Write-Host "==> Cleanup complete"
