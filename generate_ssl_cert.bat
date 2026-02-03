@echo off
REM generate_ssl_cert.bat - Generate self-signed SSL certificate for localhost (Windows)

echo ================================================
echo Generating Self-Signed SSL Certificate
echo ================================================
echo.

REM Create certs directory if it doesn't exist
if not exist certs mkdir certs

echo Generating private key and certificate...
echo.

REM Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -nodes ^
    -out certs\cert.pem ^
    -keyout certs\key.pem ^
    -days 365 ^
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost" ^
    -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"

echo.
echo ✓ SSL Certificate generated successfully!
echo.
echo Files created:
echo   - certs\cert.pem (Certificate)
echo   - certs\key.pem (Private Key)
echo.
echo These certificates are valid for 365 days
echo.
echo Next steps:
echo 1. Run: python main_https.py
echo 2. Access: https://localhost:8443
echo 3. Accept the browser security warning (self-signed cert)
echo.
echo ================================================
pause
