param(
  [string]$FrontendDir = "frontend"
)

$ErrorActionPreference = "Stop"

$dockerExe = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
if (Test-Path $dockerExe) {
  $env:PATH = "C:\Program Files\Docker\Docker\resources\bin;$env:PATH"
  & $dockerExe compose up -d
} else {
  Write-Host "Docker CLI not found at default path. Trying 'docker' from PATH..."
  docker compose up -d
}

if (-not (Test-Path $FrontendDir)) {
  throw "Frontend directory '$FrontendDir' not found."
}

Push-Location $FrontendDir
try {
  if (-not (Test-Path "node_modules")) {
    npm install
  }
  Write-Host "Starting Next.js dev server..."
  npm run dev
} finally {
  Pop-Location
}
