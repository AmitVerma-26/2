"""
generate_ssl_cert.py - Generate self-signed SSL certificate for localhost
Cross-platform Python solution
"""

import os
import subprocess
import sys
from pathlib import Path


def generate_certificate():
    """Generate self-signed SSL certificate for localhost"""
    
    print("=" * 60)
    print("Generating Self-Signed SSL Certificate")
    print("=" * 60)
    print()
    
    # Create certs directory
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"
    
    # Check if OpenSSL is available
    try:
        subprocess.run(["openssl", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: OpenSSL is not installed or not in PATH")
        print()
        print("Please install OpenSSL:")
        print("  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("  - Mac: brew install openssl")
        print("  - Linux: sudo apt-get install openssl")
        sys.exit(1)
    
    print("Generating private key and certificate...")
    print()
    
    # Generate certificate
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
        "-out", str(cert_file),
        "-keyout", str(key_file),
        "-days", "365",
        "-subj", "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost",
        "-addext", "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ SSL Certificate generated successfully!")
            print()
            print("Files created:")
            print(f"  - {cert_file} (Certificate)")
            print(f"  - {key_file} (Private Key)")
            print()
            print("These certificates are valid for 365 days")
            print()
            print("Next steps:")
            print("1. Run: python main_https.py")
            print("2. Access: https://localhost:8443")
            print("3. Accept the browser security warning (self-signed cert)")
            print()
        else:
            print("❌ Error generating certificate:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    generate_certificate()
