$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}
$LogFile = Join-Path $LogDir "run.log"

$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#=][^=]*)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

Add-Content -Path $LogFile -Value "`n===== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$cmdLine = "`"$python`" -m src.main >> `"$LogFile`" 2>&1"
cmd.exe /c $cmdLine
