# 🔒 HTTPS Setup Guide for Voice Detection API

This guide will help you run the Voice Detection API with HTTPS (SSL/TLS) on localhost.

## 📋 Table of Contents
1. [Why HTTPS?](#why-https)
2. [Quick Start](#quick-start)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Troubleshooting](#troubleshooting)
5. [Browser Certificate Warnings](#browser-certificate-warnings)

---

## Why HTTPS?

Running on HTTPS provides:
- **Secure connections** with encrypted data
- **Better browser compatibility** for modern web features
- **Professional setup** similar to production environments
- **Required for some APIs** (like microphone access in some browsers)

---

## 🚀 Quick Start

### Option 1: Python Script (Recommended - Works Everywhere)

```bash
# Step 1: Generate SSL certificates
python generate_ssl_cert.py

# Step 2: Start HTTPS server
python main_https.py

# Step 3: Open in browser
# Visit: https://localhost:8443
```

### Option 2: Linux/Mac

```bash
# Step 1: Make script executable
chmod +x generate_ssl_cert.sh

# Step 2: Generate SSL certificates
./generate_ssl_cert.sh

# Step 3: Start HTTPS server
python main_https.py

# Step 4: Open in browser
# Visit: https://localhost:8443
```

### Option 3: Windows

```batch
REM Step 1: Generate SSL certificates
generate_ssl_cert.bat

REM Step 2: Start HTTPS server
python main_https.py

REM Step 3: Open in browser
REM Visit: https://localhost:8443
```

---

## 📝 Step-by-Step Setup

### Prerequisites

1. **Python 3.8+** installed
2. **OpenSSL** installed

**Check if OpenSSL is installed:**
```bash
openssl version
```

**If not installed:**
- **Windows**: Download from https://slproweb.com/products/Win32OpenSSL.html
- **Mac**: `brew install openssl`
- **Linux**: `sudo apt-get install openssl`

### Step 1: Generate SSL Certificates

The certificates allow your browser to establish an HTTPS connection.

**Choose your method:**

#### Python (Cross-platform, Recommended)
```bash
python generate_ssl_cert.py
```

#### Linux/Mac (Shell script)
```bash
chmod +x generate_ssl_cert.sh
./generate_ssl_cert.sh
```

#### Windows (Batch file)
```batch
generate_ssl_cert.bat
```

#### Manual (OpenSSL command)
```bash
# Create certs directory
mkdir certs

# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes \
    -out certs/cert.pem \
    -keyout certs/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"
```

**What this creates:**
- `certs/cert.pem` - SSL certificate (public)
- `certs/key.pem` - Private key (keep secret)
- Valid for 365 days

### Step 2: Start the HTTPS Server

```bash
python main_https.py
```

You should see:
```
============================================================
🔒 Starting Voice Detection API with HTTPS
============================================================

Server will be available at:
  ➜ https://localhost:8443
  ➜ https://127.0.0.1:8443

Interactive API docs:
  ➜ https://localhost:8443/docs

⚠️  Note: You'll need to accept the browser security
    warning for self-signed certificates

============================================================
```

### Step 3: Access the API

Open your browser and visit:
- **Main interface**: https://localhost:8443
- **API docs**: https://localhost:8443/docs
- **Health check**: https://localhost:8443/health

### Step 4: Accept Browser Warning

Since we're using a self-signed certificate, you'll see a security warning.

**This is normal and expected!** Follow these steps:

#### Chrome
1. Click "Advanced"
2. Click "Proceed to localhost (unsafe)"

#### Firefox
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

#### Safari
1. Click "Show Details"
2. Click "visit this website"
3. Enter your Mac password if prompted

#### Edge
1. Click "Advanced"
2. Click "Continue to localhost (unsafe)"

**Why this warning?**
- Self-signed certificates aren't verified by a Certificate Authority
- Perfect for local development
- In production, use a proper SSL certificate from Let's Encrypt or similar

---

## 📁 File Structure

After setup, you'll have:

```
voice_detection_api/
├── certs/                    # SSL certificates (generated)
│   ├── cert.pem             # SSL certificate
│   └── key.pem              # Private key
├── generate_ssl_cert.py     # Certificate generator (Python)
├── generate_ssl_cert.sh     # Certificate generator (Linux/Mac)
├── generate_ssl_cert.bat    # Certificate generator (Windows)
├── main_https.py            # HTTPS server
├── index_https.html         # HTTPS web interface
└── ... (other files)
```

---

## 🔧 Configuration

### Change HTTPS Port

Edit `main_https.py`:
```python
uvicorn.run(
    "main_https:app",
    host="0.0.0.0",
    port=8443,  # Change this port
    ssl_keyfile="certs/key.pem",
    ssl_certfile="certs/cert.pem",
    reload=True
)
```

Then update `index_https.html`:
```javascript
const API_URL = 'https://localhost:8443';  // Update port here
```

### Certificate Expiration

Certificates are valid for 365 days. To regenerate:
```bash
# Delete old certificates
rm -rf certs/

# Generate new ones
python generate_ssl_cert.py
```

---

## 🐛 Troubleshooting

### Problem: "SSL certificates not found"

**Solution:**
```bash
# Make sure you're in the project directory
cd voice_detection_api

# Generate certificates
python generate_ssl_cert.py

# Verify files exist
ls -la certs/
# Should show: cert.pem and key.pem
```

### Problem: "OpenSSL not found"

**Solution - Install OpenSSL:**

**Windows:**
1. Download from: https://slproweb.com/products/Win32OpenSSL.html
2. Install "Win64 OpenSSL v3.x.x"
3. Add to PATH: `C:\Program Files\OpenSSL-Win64\bin`

**Mac:**
```bash
brew install openssl
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install openssl
```

### Problem: "Port 8443 already in use"

**Solution:**
```bash
# Find what's using the port (Linux/Mac)
lsof -i :8443

# Find what's using the port (Windows)
netstat -ano | findstr :8443

# Kill the process or change port in main_https.py
```

### Problem: "Connection refused"

**Solutions:**
1. Make sure server is running: `python main_https.py`
2. Check the port: Visit https://localhost:8443
3. Check firewall isn't blocking port 8443
4. Try https://127.0.0.1:8443 instead

### Problem: "Module not found" errors

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt
```

### Problem: Browser keeps showing warning

**This is normal for self-signed certificates!**

Options:
1. **Accept it every time** (safest for development)
2. **Add to trusted certificates** (advanced):
   - Chrome: Settings → Privacy & Security → Security → Manage Certificates
   - Firefox: Settings → Privacy & Security → View Certificates
3. **Use mkcert** for automatically trusted certificates:
   ```bash
   # Install mkcert
   brew install mkcert  # Mac
   
   # Generate trusted certificates
   mkcert -install
   mkcert localhost 127.0.0.1
   ```

---

## 🔒 Security Notes

### For Development (Current Setup)
- ✅ Self-signed certificates are **perfect** for local development
- ✅ No external access needed
- ✅ Data encrypted between browser and server

### For Production
If deploying to a real server:
1. **Get a real domain name**
2. **Use Let's Encrypt** for free SSL certificates
3. **Never commit** `key.pem` to version control
4. **Use environment variables** for sensitive config
5. **Enable rate limiting** and authentication

---

## 🆚 HTTP vs HTTPS Comparison

| Feature | HTTP (main.py) | HTTPS (main_https.py) |
|---------|----------------|------------------------|
| Port | 8000 | 8443 |
| Encryption | ❌ No | ✅ Yes |
| Browser warning | ❌ No | ⚠️ Yes (self-signed) |
| Setup complexity | Easy | Medium |
| Production ready | ❌ No | ✅ Yes (with real cert) |
| Secure data transfer | ❌ No | ✅ Yes |

---

## 📖 Additional Resources

- **OpenSSL Documentation**: https://www.openssl.org/docs/
- **Let's Encrypt** (Production SSL): https://letsencrypt.org/
- **mkcert** (Local trusted certs): https://github.com/FiloSottile/mkcert
- **FastAPI SSL Docs**: https://fastapi.tiangolo.com/deployment/manually/

---

## ✅ Quick Test Checklist

- [ ] OpenSSL installed (`openssl version`)
- [ ] Certificates generated (`ls certs/`)
- [ ] Server running (`python main_https.py`)
- [ ] Browser can access https://localhost:8443
- [ ] Health endpoint works: https://localhost:8443/health
- [ ] Can upload and analyze audio file
- [ ] API docs accessible: https://localhost:8443/docs

---

## 🎉 Success!

If you can:
1. ✅ Visit https://localhost:8443
2. ✅ See the web interface
3. ✅ Upload and analyze audio

**You're all set!** Your Voice Detection API is running securely with HTTPS! 🔒

---

For more help, check:
- **README.md** - General documentation
- **USAGE_GUIDE.md** - Usage examples
- **PROJECT_OVERVIEW.md** - Architecture details

**Need help?** Check the troubleshooting section above or review the error messages carefully.
