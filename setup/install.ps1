# FS-X-CLAUDE installer (Windows PowerShell). Installs every plugin, or only the ones you name.
#   powershell -ExecutionPolicy Bypass -File setup\install.ps1                  -> all plugins
#   powershell -ExecutionPolicy Bypass -File setup\install.ps1 cinematic-sound  -> just that one
$ErrorActionPreference = "Stop"
$Repo = "NK-EMPIRE/FS-X-CLAUDE"; $Market = "fs-x-claude"
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) { Write-Host "Install Claude Code first: https://claude.com/claude-code" -ForegroundColor Red; exit 1 }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host "Install Git and sign in to GitHub first." -ForegroundColor Red; exit 1 }
$env:GIT_TERMINAL_PROMPT = "0"
git ls-remote "https://github.com/$Repo.git" *> $null
if ($LASTEXITCODE -ne 0) { Write-Host "No access to $Repo. Ask NK-EMPIRE for access, then sign in to Git." -ForegroundColor Red; exit 1 }
$known = (claude plugin marketplace list 2>&1) -join "`n"
if ($known -match $Market) { claude plugin marketplace update $Market } else { claude plugin marketplace add $Repo }
$Plugins = $args
if ($Plugins.Count -eq 0) {
  $mk = Get-Content (Join-Path $PSScriptRoot "..\.claude-plugin\marketplace.json") -Raw | ConvertFrom-Json
  $Plugins = $mk.plugins | ForEach-Object { $_.name }
}
foreach ($p in $Plugins) { claude plugin install "$p@$Market" }
Write-Host "`nInstalled: $($Plugins -join ', '). Restart Claude Code." -ForegroundColor Green
