param(
    [string]$PythonCommand = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
$VenvDir = Join-Path $ProjectRoot ".venv"
$KernelName = "clean-air-agent"
$KernelDisplayName = "Clean Air Agent (.venv)"

Set-Location $ProjectRoot

if ([string]::IsNullOrWhiteSpace($PythonCommand)) {
    $candidates = @("py -3.14", "py -3", "python")
} else {
    $candidates = @($PythonCommand)
}

$PythonBin = $null
foreach ($candidate in $candidates) {
    try {
        $version = Invoke-Expression "$candidate -c `"import platform; print(platform.python_version())`""
        if (-not [string]::IsNullOrWhiteSpace($version)) {
            $PythonBin = $candidate
            break
        }
    } catch {
        continue
    }
}

if ([string]::IsNullOrWhiteSpace($PythonBin)) {
    Write-Error "Could not find Python on PATH. Install Python 3.10+ and try again."
}

$PythonExe = Invoke-Expression "$PythonBin -c `"import sys; print(sys.executable)`""
$TargetVersion = Invoke-Expression "$PythonBin -c `"import platform; print(platform.python_version())`""
Write-Host "Using Python: $PythonExe"

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at $VenvDir"
    Invoke-Expression "$PythonBin -m venv `"$VenvDir`""
} else {
    $CurrentVersion = ""
    if (Test-Path $VenvPython) {
        try {
            $CurrentVersion = & $VenvPython -c "import platform; print(platform.python_version())"
        } catch {
            $CurrentVersion = ""
        }
    }

    if ($CurrentVersion -ne $TargetVersion) {
        Write-Host "Recreating virtual environment at $VenvDir ($CurrentVersion -> $TargetVersion)"
        Invoke-Expression "$PythonBin -m venv --clear `"$VenvDir`""
    } else {
        Write-Host "Using existing virtual environment at $VenvDir"
    }
}

Write-Host "Ensuring pip is available in the virtual environment"
& $VenvPython -m ensurepip --upgrade

Write-Host "Upgrading packaging tools"
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Host "Installing project dependencies"
& $VenvPython -m pip install -r requirements.txt

Write-Host "Registering Jupyter kernel: $KernelDisplayName"
& $VenvPython -m ipykernel install --user --name $KernelName --display-name $KernelDisplayName

Write-Host ""
Write-Host "Setup complete."
Write-Host ""
Write-Host "Use this interpreter:"
Write-Host "  $VenvPython"
Write-Host ""
Write-Host "In VS Code / Jupyter, select this kernel:"
Write-Host "  $KernelDisplayName"
Write-Host ""
Write-Host "Run tests with:"
Write-Host "  $VenvPython -m pytest -q"
