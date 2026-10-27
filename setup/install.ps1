# FS-X-VFX one-shot installer (Windows PowerShell). Adds the marketplace and installs every plugin.
# Usage:  powershell -ExecutionPolicy Bypass -File setup\install.ps1
$ErrorActionPreference = "Stop"
$Repo = "NK-EMPIRE/FS-X-VFX"
$Market = "fs-x-vfx"
$Plugins = @("vfx-intro")

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) { Write-Host "Claude Code CLI not found. Install it first: https://claude.com/claude-code" -ForegroundColor Red; exit 1 }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host "Git not found. Install Git and sign in to GitHub first." -ForegroundColor Red; exit 1 }

Write-Host "Checking access to $Repo ..."
$env:GIT_TERMINAL_PROMPT = "0"
git ls-remote "https://github.com/$Repo.git" *> $null
if ($LASTEXITCODE -ne 0) { Write-Host "No access to the private repo. Ask NK-EMPIRE to add your GitHub account, then sign in to Git (git credential manager)." -ForegroundColor Red; exit 1 }

$known = (claude plugin marketplace list 2>&1) -join "`n"
if ($known -match $Market) { claude plugin marketplace update $Market } else { claude plugin marketplace add $Repo }
foreach ($p in $Plugins) { claude plugin install "$p@$Market" }

Write-Host "`nDone. Restart Claude Code, then run /vfx-setup to check Blender, After Effects, ffmpeg, Python and GPU." -ForegroundColor Green
