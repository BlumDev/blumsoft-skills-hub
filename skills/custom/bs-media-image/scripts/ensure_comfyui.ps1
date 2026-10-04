# Ensure the ComfyUI API is reachable; start it headless if not.
# Used by the bs-media-image skill so an agent can run fully autonomously
# (no Stability Matrix GUI needed). Prints status; exit 0 = ready.
param([string]$Url = "http://127.0.0.1:8188")
if (Test-Path (Join-Path $PSScriptRoot "..\WARTUNG")) { Write-Output "bs-media-image ist in Wartung: die Bildablage zieht um, ComfyUI wird nicht gestartet"; exit 1 }

$comfy = "D:\Apps\Stability Matrix\Data\Packages\ComfyUI"
$py = Join-Path $comfy "venv\Scripts\python.exe"

function Test-Up {
    try { Invoke-WebRequest "$Url/system_stats" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

if (Test-Up) { Write-Output "ComfyUI laeuft bereits: $Url"; exit 0 }
if (-not (Test-Path $py)) { Write-Output "venv-Python fehlt: $py"; exit 1 }

Write-Output "Starte ComfyUI headless ..."
# Output MUSS in Dateien umgeleitet werden, sonst haelt der laufende Server die
# stdout-Pipe offen und das aufrufende Shell/der Background-Task haengt ewig.
# One pair of files per run. The fixed names could still belong to an earlier server that
# holds them open, and Start-Process fails outright on a locked redirect target.
$stamp = "{0}_{1}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $PID
$srvLog = Join-Path $env:TEMP "comfyui_server_$stamp.log"
$srvErr = Join-Path $env:TEMP "comfyui_server_$stamp.err"
# Startparameter wie in Stability Matrix (settings.json, LaunchArgs des Pakets ComfyUI), dazu Port und kein Browser:
# UI- und Skript-Läufe rechnen so mit demselben Attention-Backend, die Oberfläche zeigt die Live-Vorschau.
try {
    $proc = Start-Process -FilePath $py `
        -ArgumentList @("`"$comfy\main.py`"", "--port", "8188", "--disable-auto-launch", "--preview-method", "auto",
                        "--use-pytorch-cross-attention", "--enable-manager") `
        -WorkingDirectory $comfy -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $srvLog -RedirectStandardError $srvErr
} catch {
    Write-Output "Start fehlgeschlagen: $($_.Exception.Message)"; exit 1
}
Write-Output "Log: $srvLog"

# Warten nach Wanduhr, nicht nach Schleifendurchläufen: jede fehlgeschlagene
# Probe kostet zusätzlich bis zu 3 s Timeout, gezählte Durchläufe ergeben
# deshalb eine unvorhersehbare Wartezeit.
# Warum so lange: --enable-manager zieht beim Start die ComfyRegistry und
# blockiert dabei die HTTP-API. Gemessen am 27.08.2026: 3 min 14 s bzw. 4 min 25 s
# vom Prozessstart bis zum Ende des Fetches, danach laufen noch Startup-Tasks.
# Ein abgestürzter Server wird sofort gemeldet statt nach Ablauf der Frist: ohne -PassThru
# könnte die Schleife "bootet noch" nicht von "schon abgestürzt" unterscheiden.
$deadline = (Get-Date).AddSeconds(900)
$t0 = Get-Date
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 3
    if (Test-Up) {
        $s = [int]((Get-Date) - $t0).TotalSeconds
        Write-Output "ComfyUI bereit nach ~${s}s: $Url"; exit 0
    }
    if ($proc.HasExited) {
        Write-Output "ComfyUI-Prozess beendet mit Exitcode $($proc.ExitCode), siehe $srvErr"
        exit 1
    }
}
Write-Output "TIMEOUT: ComfyUI nicht erreichbar nach 900s, siehe $srvErr"; exit 1
