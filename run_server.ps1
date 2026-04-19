#!/usr/bin/env powershell
# Start the Business Agent 2.0 production server

Write-Host "="*70 -ForegroundColor Green
Write-Host "🚀 STARTING BUSINESS AGENT 2.0 PRODUCTION SERVER" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green
Write-Host ""

# Navigate to project
cd "C:\Users\silen\Desktop\Business-Agent-2.0"

# Show startup info
Write-Host "📋 Server Configuration:" -ForegroundColor Cyan
Write-Host "  • Host: 0.0.0.0"
Write-Host "  • Port: 8000"
Write-Host "  • Workers: 1 (use Gunicorn for multiple workers)"
Write-Host "  • API Docs: http://localhost:8000/docs"
Write-Host ""

# Start the server
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app_production:app --host 0.0.0.0 --port 8000 --reload
