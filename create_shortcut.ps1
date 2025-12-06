$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "CHRONON.lnk"
$CurrentDir = $PSScriptRoot
$Target = Join-Path $CurrentDir "run_gui.bat"
$Icon = Join-Path $CurrentDir "logo_zenodo_v2.ico"

Write-Host "Creating shortcut at: $ShortcutPath"
Write-Host "Target: $Target"
Write-Host "Icon: $Icon"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = $CurrentDir
$Shortcut.IconLocation = $Icon
$Shortcut.Description = "CHRONON Application"
$Shortcut.Save()

Write-Host "Done."
