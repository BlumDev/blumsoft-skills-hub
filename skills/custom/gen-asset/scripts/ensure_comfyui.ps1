# Ensure the ComfyUI API is reachable; start it headless if not.
# Used by the gen-asset skill so an agent can run fully autonomously
# (no Stability Matrix GUI needed). Prints status; exit 0 = ready.
param([string]$Url = "http://127.0.0.1:8188")

$comfy = "D:\Apps\Stability Matrix\Data\Packages\ComfyUI"
$py = Join-Path $comfy "venv\Scripts\python.exe"

function Test-Up {
    try { Invoke-WebRequest "$Url/system_stats" -TimeoutSec 3 -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

if (Test-Up) { Write-Output "ComfyUI laeuft bereits: $Url"; exit 0 }
if (-not (Test-Path $py)) { Write-Output "venv-Python fehlt: $py"; exit 1 }

Write-Output "Starte ComfyUI headless ..."
# Output MUSS in Dateien umgeleitet werden, sonst haelt der laufende Server die
# stdout-Pipe offen und das aufrufende Shell/der Background-Task haengt ewig.
$srvLog = Join-Path $env:TEMP "comfyui_server.log"
$srvErr = Join-Path $env:TEMP "comfyui_server.err"
Start-Process -FilePath $py `
    -ArgumentList @("`"$comfy\main.py`"", "--port", "8188", "--disable-auto-launch") `
    -WorkingDirectory $comfy -WindowStyle Hidden `
    -RedirectStandardOutput $srvLog -RedirectStandardError $srvErr

for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Up) { Write-Output "ComfyUI bereit nach ~$($i*2)s: $Url"; exit 0 }
}
Write-Output "TIMEOUT: ComfyUI nicht erreichbar nach 240s"; exit 1
