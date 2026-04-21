$ErrorActionPreference = "Stop"

param(
  [string]$DeviceIp = "192.168.86.212",
  [string]$SshUser = "comma",
  [string]$SshKeyPath = "C:\Users\dave\.ssh\comma",
  [string]$RepoOwner = "dkneeland",
  [string]$Branch = "t-combo",
  [switch]$Reboot
)

$remoteCmd = @"
set -e
cd /data/openpilot
git remote add $RepoOwner https://github.com/$RepoOwner/sunnypilot.git 2>/dev/null || true
git fetch $RepoOwner
git checkout -B $Branch $RepoOwner/$Branch
git reset --hard $RepoOwner/$Branch
rm -rf msgq_repo opendbc_repo panda rednose_repo teleoprtc_repo tinygrad_repo sunnypilot/neural_network_data
rm -rf .git/modules/msgq_repo .git/modules/opendbc_repo .git/modules/panda .git/modules/rednose_repo .git/modules/teleoprtc_repo .git/modules/tinygrad_repo .git/modules/sunnypilot/neural_network_data
git submodule sync --recursive
git submodule update --init --recursive
git rev-parse --short HEAD
git -C opendbc_repo rev-parse --short HEAD
"@

Write-Host "Updating device $SshUser@$DeviceIp to $RepoOwner/$Branch..."
ssh -o StrictHostKeyChecking=accept-new -i $SshKeyPath "$SshUser@$DeviceIp" $remoteCmd

if ($LASTEXITCODE -ne 0) {
  throw "Device update failed."
}

if ($Reboot) {
  Write-Host "Rebooting device..."
  ssh -o StrictHostKeyChecking=accept-new -i $SshKeyPath "$SshUser@$DeviceIp" "sudo reboot"
  if ($LASTEXITCODE -ne 0) {
    throw "Device reboot command failed."
  }
}

Write-Host "Device update complete."
