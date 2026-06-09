# GlassesCat - Windows Task Scheduler Kurulum Scripti
# Yonetici olarak calistir (Run as Administrator)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoPath = Split-Path -Parent $scriptPath
$syncBat = Join-Path $scriptPath "sync.bat"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GlassesCat - Windows Otomasyon Kurulumu" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Task Scheduler - Her saat basi pull
$taskNameSync = "GlassesCat Hourly Sync"
$actionSync = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$syncBat`""
$triggerSync = New-ScheduledTaskTrigger -Daily -At 00:00 -RepetitionInterval (New-TimeSpan -Minutes 60) -RepetitionDuration (New-TimeSpan -Days 365)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskNameSync -Action $actionSync -Trigger $triggerSync -Principal $principal -Force -ErrorAction Stop
    Write-Host "[OK] Task '$taskNameSync' kuruldu (her saat basi)" -ForegroundColor Green
} catch {
    Write-Host "[HATA] Task kurulamadi: $_" -ForegroundColor Red
    Write-Host "Yonetici olarak calistirdigindan emin ol." -ForegroundColor Yellow
}

# 2. Task Scheduler - Bilgisayar baslangicinda pull
$taskNameStartup = "GlassesCat Startup Sync"
$actionStartup = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$syncBat`""
$triggerStartup = New-ScheduledTaskTrigger -AtStartup

try {
    Register-ScheduledTask -TaskName $taskNameStartup -Action $actionStartup -Trigger $triggerStartup -Principal $principal -Force -ErrorAction Stop
    Write-Host "[OK] Task '$taskNameStartup' kuruldu (baslangicta)" -ForegroundColor Green
} catch {
    Write-Host "[HATA] Task kurulamadi: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  KULLANIM:"
Write-Host "  push.bat    -> Tek tusla commit+push+ollama"
Write-Host "  sync.bat    -> Elle pull (gerektiginde)"
Write-Host "========================================" -ForegroundColor Cyan

pause
