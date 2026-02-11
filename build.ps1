$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$iconPath = Join-Path $projectRoot "assets\\images\\logo_corfo_azul.ico"
$dataArg = "assets\\images;assets\\images"

$argsList = @(
    "--onefile",
    "--windowed",
    "--name", "PDF_a_Word",
    "--add-data", $dataArg
)

if (Test-Path $iconPath) {
    $argsList += @("--icon", $iconPath)
}

pyinstaller @argsList gui.py
