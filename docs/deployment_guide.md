# Deployment Guide: Capital Flow & Credit Risk Dashboard

## Server Details
- **Server Name**: ns339474.ip-37-187-250.eu
- **IP**: 37.187.250.eu (resolve to full IP)
- **OS**: Windows Hyper-V Server 2019
- **Location**: France (Roubaix) - eu-west-rbx

## 🚀 Deployment Options

### Option 1: Direct Server Deployment (Recommended)

Deploy directly on your Windows server.

#### Step 1: Install Python on Server

```powershell
# Download Python 3.11+ (64-bit)
# https://www.python.org/downloads/

# Verify installation
python --version
# Should show: Python 3.11.x or higher
```

#### Step 2: Install Dependencies

```powershell
# Navigate to project directory (copy files first)
cd C:\path\to\your\project

# Install requirements
pip install -r requirements.txt

# Verify Streamlit
streamlit --version
```

#### Step 3: Run the Dashboard

```powershell
# Start the dashboard
streamlit run dashboards/streamlit_app.py

# Dashboard will be available at:
# http://localhost:8501
# http://your-server-ip:8501
```

#### Step 4: Configure Firewall

```powershell
# Open port 8501 in Windows Firewall
netsh advfirewall firewall add rule name="Streamlit Dashboard" dir=in action=allow protocol=TCP localport=8501

# Or via Windows Defender Firewall GUI:
# Control Panel > System and Security > Windows Defender Firewall > Advanced Settings
# Inbound Rules > New Rule > Port > TCP 8501 > Allow
```

#### Step 5: Access the Dashboard

- **Internal**: http://localhost:8501
- **External**: http://37.187.250.eu:8501 (or your full IP)
- **Domain**: http://yourdomain.com:8501 (if you have a domain)

### Option 2: Docker Deployment (Alternative)

For easier deployment and isolation:

```dockerfile
# Create Dockerfile in project root
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "dashboards/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t credit-risk-dashboard .
docker run -p 8501:8501 credit-risk-dashboard
```

## 🌐 Network Configuration

### Firewall Rules
```powershell
# Check current firewall status
netsh advfirewall firewall show rule name=all | findstr 8501

# Add inbound rule for Streamlit
netsh advfirewall firewall add rule name="Streamlit Dashboard" dir=in action=allow protocol=TCP localport=8501

# For external access, also allow on public profile
netsh advfirewall firewall set rule name="Streamlit Dashboard" new profile=public
```

### Port Forwarding (if behind NAT)
If your server is behind a router/firewall:
```powershell
# Check if port 8501 is accessible externally
# From external machine: telnet your-server-ip 8501

# If not accessible, configure port forwarding in router
# Router admin panel > Port Forwarding > Add rule:
# External Port: 8501
# Internal IP: your-server-ip
# Internal Port: 8501
# Protocol: TCP
```

## 🔒 Security Considerations

### Basic Security
```powershell
# Run as non-admin user
runas /user:limited-user "streamlit run dashboards/streamlit_app.py"

# Enable Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
```

### HTTPS (Recommended for Production)
```bash
# Install certbot for Let's Encrypt (if you have a domain)
# https://certbot.eff.org/

# Or use self-signed certificate
# Generate self-signed cert (PowerShell):
New-SelfSignedCertificate -DnsName "your-server-ip" -CertStoreLocation "cert:\LocalMachine\My"

# Configure Streamlit for HTTPS (requires custom server)
# Alternative: Use nginx as reverse proxy with SSL
```

### Authentication (Optional)
```python
# Add to streamlit_app.py for basic auth
import streamlit_authenticator as stauth

# Configure authentication (requires streamlit-authenticator package)
```

## 📊 Monitoring & Maintenance

### Check Status
```powershell
# Check if Streamlit is running
Get-Process -Name python | Where-Object {$_.CommandLine -like "*streamlit*"}

# Check port usage
netstat -ano | findstr 8501

# View logs (if logging configured)
Get-Content -Path "streamlit.log" -Wait -Tail 10
```

### Automatic Startup
```powershell
# Create scheduled task for auto-start
schtasks /create /tn "CreditRiskDashboard" /tr "powershell -ExecutionPolicy Bypass -File C:\path\to\start_dashboard.ps1" /sc onstart /ru System

# start_dashboard.ps1 content:
# cd C:\path\to\project
# streamlit run dashboards/streamlit_app.py
```

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use**
```powershell
# Find what's using port 8501
netstat -ano | findstr 8501

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
streamlit run dashboards/streamlit_app.py --server.port 8502
```

**2. Python Not Found**
```powershell
# Add Python to PATH
$env:Path += ";C:\Python311"

# Or use full path
C:\Python311\python.exe -m streamlit run dashboards/streamlit_app.py
```

**3. Dependencies Missing**
```powershell
# Install missing packages
pip install missing-package-name

# Check what's installed
pip list | findstr streamlit
```

**4. External Access Blocked**
```powershell
# Test from external machine
curl http://your-server-ip:8501

# Check firewall
netsh advfirewall firewall show rule name="Streamlit Dashboard"
```

**5. Memory/CPU Issues**
```powershell
# Monitor resource usage
Get-Process python | Select-Object CPU, WorkingSet

# Optimize for server (add to streamlit_app.py)
# st.set_page_config(initial_sidebar_state="collapsed")
```

## 📋 Pre-Deployment Checklist

- [ ] Python 3.11+ installed on server
- [ ] Project files copied to server (`capital_flow_risk/` folder)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Port 8501 opened in Windows Firewall
- [ ] External IP/domain accessible (test with curl)
- [ ] Dashboard tested locally first (`streamlit run dashboards/streamlit_app.py`)
- [ ] Server has internet access (for data APIs)
- [ ] Consider HTTPS setup (certbot/nginx)
- [ ] Backup strategy for data/logs

## 🚀 Quick Start Script

Create `deploy.ps1` on your server:

```powershell
# deploy.ps1
Write-Host "Deploying Capital Flow & Credit Risk Dashboard..."

# Install Python if needed
# winget install Python.Python.3.11

# Navigate to project
cd "C:\path\to\capital_flow_risk"

# Install dependencies
pip install -r requirements.txt

# Configure firewall
netsh advfirewall firewall add rule name="Streamlit Dashboard" dir=in action=allow protocol=TCP localport=8501

# Start dashboard
Write-Host "Starting dashboard on port 8501..."
streamlit run dashboards/streamlit_app.py --server.address 0.0.0.0 --server.port 8501

Write-Host "Dashboard available at:"
Write-Host "  Local: http://localhost:8501"
Write-Host "  External: http://37.187.250.eu:8501"
```

## 🌍 Production Considerations

### Scalability
- **Load Balancing**: For multiple users, use nginx reverse proxy
- **Database**: Replace synthetic data with real database connections
- **Caching**: Add Redis for data caching
- **Monitoring**: Add logging and metrics (Prometheus + Grafana)

### High Availability
- **Backup Server**: Deploy to second server for redundancy
- **Auto-restart**: Use process managers (PM2 equivalent for Python)
- **Health Checks**: Monitor dashboard availability

### Data Sources
- **Real APIs**: Set up FRED API key for live US data
- **Database**: Connect to SQL Server/PostgreSQL for portfolio data
- **Scheduled Updates**: Use Windows Task Scheduler for data refresh

## 📞 Support

If you encounter issues:

1. **Check logs**: Look for error messages in PowerShell/terminal
2. **Test locally**: Verify dashboard works on your local machine first
3. **Port access**: Use `telnet your-server-ip 8501` to test connectivity
4. **Dependencies**: Run `pip check` to verify all packages installed correctly

---

## 🎯 Expected URLs

After deployment:

- **Dashboard**: http://37.187.250.eu:8501
- **API Health**: http://37.187.250.eu:8501/_stcore/health (if enabled)
- **Streamlit Info**: http://37.187.250.eu:8501 (footer shows version)

The dashboard will show all the same features as local deployment but accessible from anywhere in the world! 🌍📊

---

**Ready to deploy?** Copy your project files to the server and run the quick start script above!

