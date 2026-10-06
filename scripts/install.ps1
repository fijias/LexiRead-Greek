# Bootstrap only. Remaining setup runs with the project's .venv Python.
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$settingsPath = Join-Path $projectRoot ".local\settings.json"
$uiLanguage = (Get-UICulture).TwoLetterISOLanguageName
if (Test-Path -LiteralPath $settingsPath) {
    try { $saved = (Get-Content -LiteralPath $settingsPath -Raw | ConvertFrom-Json).ui_language; if ($saved) { $uiLanguage = $saved } } catch {}
}
$env:LEXIREAD_UI_LANG = $(if ($uiLanguage -eq "ru") { "ru" } else { "en" })
function L([string]$En, [string]$Ru) { if ($env:LEXIREAD_UI_LANG -eq "ru") { return $Ru } return $En }

function Test-Python([string]$Exe) {
    if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) { return $null }
    try {
        $answer = & $Exe -c "import sys,struct,platform; import tkinter,venv,ensurepip; assert (3,11)<=sys.version_info<(3,14) and struct.calcsize('P')==8 and platform.machine().lower() in ('amd64','x86_64'); print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0) { return ($answer | Select-Object -Last 1) }
    } catch {}
    return $null
}

function Find-Python {
    $existing = Test-Python (Join-Path $projectRoot ".venv\Scripts\python.exe")
    if ($existing) { return $existing }
    foreach ($name in @("python.exe", "python3.exe")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notlike "*WindowsApps*") {
            $candidate = Test-Python $command.Source
            if ($candidate) { return $candidate }
        }
    }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($version in @("-3.12", "-3.13", "-3.11")) {
            try {
                $candidate = & $launcher.Source $version -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $found = Test-Python ($candidate | Select-Object -Last 1)
                    if ($found) { return $found }
                }
            } catch {}
        }
    }
    foreach ($base in @("$env:LOCALAPPDATA\Programs\Python", "$env:ProgramFiles\Python")) {
        foreach ($path in @(Get-ChildItem -LiteralPath $base -Filter "Python3*" -Directory -ErrorAction SilentlyContinue)) {
            $found = Test-Python (Join-Path $path.FullName "python.exe")
            if ($found) { return $found }
        }
    }
    return $null
}

try {
    Write-Host "LexiRead Greek Setup"
    Write-Host (L "[1/7] Checking Python..." "[1/7] Проверка Python...")
    if (-not [Environment]::Is64BitOperatingSystem) { throw (L "64-bit Windows is required." "Нужна 64-разрядная Windows.") }
    $pythonExe = Find-Python
    if (-not $pythonExe) {
        Write-Host (L "No compatible Python found. Installing the official Python 3.13.15 (x64) for the current user." "Совместимый Python не найден. Устанавливается официальный Python 3.13.15 (x64) для текущего пользователя.")
        $downloadDir = Join-Path $projectRoot ".local\downloads"
        New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
        $installer = Join-Path $downloadDir "python-3.13.15-amd64.exe"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.13.15/python-3.13.15-amd64.exe" -OutFile $installer -TimeoutSec 300
        $expected = "edec09c4853aeae9ac36efb8c9f95b6b8e2fee65eee56d9767a8b7c69c574403"
        if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
            throw (L "The Python installer checksum does not match. Run INSTALL.bat again." "Контрольная сумма установщика Python не совпала. Повторите INSTALL.bat.")
        }
        $signature = Get-AuthenticodeSignature -LiteralPath $installer
        if ($signature.Status -ne "Valid") { throw (L "Could not verify the Python installer signature." "Не удалось проверить подпись установщика Python.") }
        $installProcess = Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0 Include_tcltk=1 Include_pip=1" -WindowStyle Hidden -Wait -PassThru
        if ($installProcess.ExitCode -notin @(0, 3010)) { throw ((L "Python: installer exit code " "Python: код установки ") + "$($installProcess.ExitCode).") }
        $pythonExe = Find-Python
        if (-not $pythonExe) { throw (L "Python not found after installation. Install x64 Python 3.11-3.13 from python.org (with Tcl/Tk), then run INSTALL.bat again." "Python не найден после установки. Установите x64 Python 3.11–3.13 с python.org (с Tcl/Tk), затем повторите INSTALL.bat.") }
    }
    Write-Host "Python: $pythonExe"
    Write-Host (L "[2/7] Checking the virtual environment..." "[2/7] Проверка виртуального окружения...")
    $venvDir = Join-Path $projectRoot ".venv"
    $venvPython = Join-Path $venvDir "Scripts\python.exe"
    $valid = Test-Python $venvPython
    if ($valid) {
        & $venvPython -c "import sys,pip; from pathlib import Path; assert sys.prefix != sys.base_prefix; assert Path(sys.prefix).resolve() == Path('.venv').resolve(); assert Path(sys.executable).with_name('pythonw.exe').is_file()" 2>$null
        $valid = $LASTEXITCODE -eq 0
    }
    if (-not $valid) {
        if (Test-Path -LiteralPath $venvDir) {
            # Preserve damaged environments. Verify containment before moving.
            $resolved = (Resolve-Path -LiteralPath $venvDir).Path
            if ((Split-Path -Parent $resolved) -ne $projectRoot) { throw (L "Unsafe .venv path." "Небезопасный путь .venv.") }
            if ((Get-Item -LiteralPath $venvDir).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw (L ".venv is a link. Use a regular local folder." ".venv является ссылкой. Используйте обычный локальный каталог.") }
            # Choose a base interpreter outside .venv before moving its files.
            $baseExe = & $pythonExe -c "import sys; print(sys._base_executable)"
            $pythonExe = Test-Python ($baseExe | Select-Object -Last 1)
            if (-not $pythonExe) { throw (L "Base Python not found. Install Python and run INSTALL.bat again." "Не найден базовый Python. Установите Python и повторите INSTALL.bat.") }
            $backup = Join-Path $projectRoot (".venv.broken-" + [guid]::NewGuid().ToString("N"))
            if ((Split-Path -Parent $backup) -ne $projectRoot) { throw (L "Unsafe backup path." "Небезопасный путь резервной копии.") }
            Move-Item -LiteralPath $resolved -Destination $backup
            Write-Host ((L "The old environment is saved in " "Старое окружение сохранено в ") + $backup)
        }
        & $pythonExe -m venv $venvDir
        if ($LASTEXITCODE -ne 0) { throw (L "Could not create .venv." "Не удалось создать .venv.") }
    }
    & $venvPython -m scripts.setup --language el
    if ($LASTEXITCODE -ne 0) { throw (L "Setup did not finish. See the message above and logs\setup.log; run INSTALL.bat again." "Установка не завершена. Проверьте сообщение выше и logs\setup.log; повторите INSTALL.bat.") }
    Write-Host (L "Setup complete. Start the app with LexiRead.bat" "Установка завершена. Для запуска используйте LexiRead.bat")
    exit 0
} catch {
    Write-Host ((L "Setup error: " "Ошибка установки: ") + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
