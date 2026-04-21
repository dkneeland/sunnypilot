$ErrorActionPreference = "Stop"

param(
  [string]$Branch = "tesla-combined"
)

function Invoke-Git {
  param(
    [string]$Command,
    [string]$RepoPath = "."
  )

  git -C $RepoPath $Command
  if ($LASTEXITCODE -ne 0) {
    throw "git command failed in '$RepoPath': git $Command"
  }
}

Write-Host "Pushing Tesla branches for '$Branch'..."

# Push submodule first so the superproject pointer is resolvable.
Invoke-Git -RepoPath "opendbc_repo" -Command "push origin $Branch"

# Push superproject branch second.
Invoke-Git -Command "push origin $Branch"

$spSha = (git rev-parse --short HEAD).Trim()
$odSha = (git -C "opendbc_repo" rev-parse --short HEAD).Trim()

Write-Host "Push complete."
Write-Host "- superproject ($Branch): $spSha"
Write-Host "- opendbc ($Branch): $odSha"
