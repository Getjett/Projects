# Strategy Builder - Startup Script (PowerShell)
# This script starts both backend and frontend servers

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Strategy Builder - Starting Services" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

# Check if backend port is in use
if (Test-Port -Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use. Backend may already be running." -ForegroundColor Yellow
    Write-Host "   Skipping backend startup..." -ForegroundColor Yellow
} else {
    Write-Host "🚀 Starting Backend Server (Port 8000)..." -ForegroundColor Green
    
    # Start backend in a new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\backend'; Write-Host 'Starting FastAPI Backend...' -ForegroundColor Green; python app.py"
    
    Write-Host "   Waiting for backend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# Check if frontend port is in use
if (Test-Port -Port 3000) {
    Write-Host "⚠️  Port 3000 is already in use. Frontend may already be running." -ForegroundColor Yellow
    Write-Host "   Skipping frontend startup..." -ForegroundColor Yellow
} else {
    Write-Host "`n🚀 Starting Frontend Server (Port 3000)..." -ForegroundColor Green
    
    # Start frontend in a new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; Write-Host 'Starting React Frontend...' -ForegroundColor Green; npm start"
    
    Write-Host "   Waiting for frontend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services Started!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📍 Access Points:" -ForegroundColor White
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:    http://localhost:8000/api/docs" -ForegroundColor Cyan

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Both services are running in separate windows" -ForegroundColor Gray
Write-Host "   - Close those windows to stop the services" -ForegroundColor Gray
Write-Host "   - Check logs in each window for errors" -ForegroundColor Gray

Write-Host "`n🎯 Navigate to Strategy Builder:" -ForegroundColor White
Write-Host "   http://localhost:3000 → Click 'Strategy Builder' in the menu" -ForegroundColor Cyan

Write-Host "`nPress any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
