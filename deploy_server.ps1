# PowerShell Deployment Script for Capital Flow & Credit Risk Dashboard
# Run this on your Windows Hyper-V Server 2019

Write-Host "==========================================="
Write-Host "CAPITAL FLOW & CREDIT RISK DASHBOARD DEPLOYMENT"
Write-Host "==========================================="
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✓ Python found: $pythonVersion"
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ from:"
    Write-Host "  https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Installation steps:"
    Write-Host "1. Download Python 3.11+ installer"
    Write-Host "2. Run installer with 'Add to PATH' option"
    Write-Host "3. Restart PowerShell"
    Write-Host "4. Run this script again"
    exit 1
}

# Check if we're in the right directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir"

if (!(Test-Path "requirements.txt")) {
    Write-Host "✗ requirements.txt not found in current directory"
    Write-Host "Please navigate to the project directory or copy files there"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Installing Python dependencies..."
Write-Host "=========================================="

# Install requirements
try {
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed successfully"
} catch {
    Write-Host "✗ Failed to install dependencies"
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Configuring Windows Firewall..."
Write-Host "======================================"

# Check if rule already exists
$existingRule = Get-NetFirewallRule -DisplayName "Streamlit Dashboard" -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "✓ Firewall rule already exists"
} else {
    # Add firewall rule for port 8501
    try {
        New-NetFirewallRule -DisplayName "Streamlit Dashboard" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
        Write-Host "✓ Firewall rule added for port 8501"
    } catch {
        Write-Host "✗ Failed to add firewall rule"
        Write-Host "Error: $($_.Exception.Message)"
        Write-Host ""
        Write-Host "Alternative: Run manually in PowerShell:"
        Write-Host "New-NetFirewallRule -DisplayName 'Streamlit Dashboard' -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow"
    }
}

Write-Host ""
Write-Host "Step 3: Testing dashboard..."
Write-Host "==========================="

# Test if dashboard can start (don't run in background for testing)
try {
    $testProcess = Start-Process python -ArgumentList " -c 'import streamlit; print(\"Streamlit import successful\")' " -NoNewWindow -Wait -PassThru
    if ($testProcess.ExitCode -eq 0) {
        Write-Host "✓ Streamlit can be imported"
    } else {
        Write-Host "✗ Streamlit import failed"
        exit 1
    }
} catch {
    Write-Host "✗ Streamlit test failed"
    exit 1
}

Write-Host ""
Write-Host "==========================================="
Write-Host "DEPLOYMENT COMPLETE!"
Write-Host "==========================================="
Write-Host ""
Write-Host "To start the dashboard:"
Write-Host ""
Write-Host "Option 1 - Run in current session:"
Write-Host "  streamlit run dashboards/streamlit_app.py"
Write-Host ""
Write-Host "Option 2 - Run in background:"
Write-Host "  Start-Process python -ArgumentList 'src/modeling/core.py' -NoNewWindow"
Write-Host ""
Write-Host "Dashboard URLs:"
Write-Host "  Local:      http://localhost:8501"
Write-Host "  Network:    http://your-server-ip:8501"
Write-Host "  External:   http://37.187.250.eu:8501"
Write-Host ""
Write-Host "Features available:"
Write-Host "  ✓ Australia & US credit risk modeling"
Write-Host "  ✓ Interactive scenarios & stress testing"
Write-Host "  ✓ Professional risk report narratives"
Write-Host "  ✓ Portfolio analytics & capital calculations"
Write-Host ""
Write-Host "For troubleshooting, see: docs/deployment_guide.md"
Write-Host ""
Write-Host "Happy risk modeling! 🚀📊"

