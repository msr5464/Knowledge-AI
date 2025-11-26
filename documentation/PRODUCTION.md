# Production Deployment Guide

Complete guide for deploying InHouse Knowledge AI in production environments.

## Table of Contents

- [Understanding the Development Server Warning](#understanding-the-development-server-warning)
- [Why Use a Production WSGI Server?](#why-use-a-production-wsgi-server)
- [Production Deployment Options](#production-deployment-options)
- [Gunicorn Setup](#gunicorn-setup)
- [Systemd Service (Linux)](#systemd-service-linux)
- [Production Checklist](#production-checklist)
- [Security Considerations](#security-considerations)
- [Monitoring and Logging](#monitoring-and-logging)
- [Performance Tuning](#performance-tuning)

---

## Understanding the Development Server Warning

When you run the application using `python backend/app.py` or `scripts/run.sh`, you'll see this warning:

```
WARNING: This is a development server. Do not use it in a production deployment.
Use a production WSGI server instead.
```

### What This Means

Flask's built-in development server (`app.run()`) is:
- **Single-threaded**: Can only handle one request at a time
- **Not optimized**: Designed for development, not performance
- **Insecure**: Not hardened for production use
- **Unstable**: May crash under load or with multiple concurrent requests

### Why It's Not Production-Ready

1. **Performance**: Can't handle concurrent requests efficiently
2. **Reliability**: Not designed for 24/7 operation
3. **Security**: Missing production security features
4. **Scalability**: Can't scale to handle multiple users

---

## Why Use a Production WSGI Server?

A production WSGI server like **Gunicorn** provides:

✅ **Multi-worker architecture**: Handle multiple requests simultaneously  
✅ **Process management**: Automatic worker restart on crashes  
✅ **Production-grade**: Designed for reliability and performance  
✅ **Security**: Hardened for production environments  
✅ **Scalability**: Can handle high traffic loads  

---

## Production Deployment Options

### Option 1: Gunicorn (Recommended)

**Best for**: Most production deployments (Linux, macOS, cloud servers)

**Advantages**:
- Easy to set up and configure
- Excellent performance
- Great for Python applications
- Well-documented and widely used

### Option 2: uWSGI

**Best for**: Advanced deployments requiring fine-grained control

**Advantages**:
- Highly configurable
- Supports multiple protocols
- Advanced features

**Disadvantages**:
- More complex setup
- Steeper learning curve

### Option 3: Docker + Gunicorn

**Best for**: Containerized deployments, cloud platforms

**Advantages**:
- Consistent environment
- Easy scaling
- Isolation

---

## Gunicorn Setup

### Quick Start

1. **Install Gunicorn** (already in requirements.txt):
   ```bash
   pip install gunicorn
   ```

2. **Run with production script**:
   ```bash
   ./scripts/run-production.sh
   ```

3. **Or run manually**:
   ```bash
   gunicorn -c gunicorn_config.py "backend.app:create_app()"
   ```

### Configuration

The `gunicorn_config.py` file is pre-configured with production settings:

```python
# Workers: Automatically set to (CPU cores * 2) + 1
workers = 4  # Adjust based on your server

# Bind address
bind = "0.0.0.0:5001"

# Timeouts
timeout = 120  # For long-running LLM queries

# Logging
accesslog = '-'  # stdout
errorlog = '-'   # stderr
loglevel = 'info'
```

### Environment Variables

You can override settings via environment variables:

```bash
export PORT=5001
export GUNICORN_WORKERS=4
export GUNICORN_LOG_LEVEL=info
gunicorn -c gunicorn_config.py "backend.app:create_app()"
```

### Worker Count Guidelines

- **CPU-bound tasks** (LLM processing): `workers = CPU cores + 1`
- **I/O-bound tasks** (API calls): `workers = (CPU cores * 2) + 1`
- **Mixed workload** (this app): `workers = (CPU cores * 2) + 1`

**Example**:
- 2 CPU cores → 5 workers
- 4 CPU cores → 9 workers
- 8 CPU cores → 17 workers

---

## Systemd Service (Linux)

Create a systemd service for automatic startup and management.

### Create Service File

Create `/etc/systemd/system/rag-system.service`:

```ini
[Unit]
Description=InHouse Knowledge AI RAG System
After=network.target

[Service]
Type=notify
User=your-username
Group=your-group
WorkingDirectory=/path/to/my-rag
Environment="PATH=/path/to/my-rag/venv/bin"
ExecStart=/path/to/my-rag/venv/bin/gunicorn -c /path/to/my-rag/gunicorn_config.py "backend.app:create_app()"
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable rag-system

# Start service
sudo systemctl start rag-system

# Check status
sudo systemctl status rag-system

# View logs
sudo journalctl -u rag-system -f
```

---

## Production Checklist

### Before Deployment

- [ ] **Change SECRET_KEY**: Update in `config/.env`
- [ ] **Disable DEBUG**: Set `FLASK_DEBUG=False` in `config/.env`
- [ ] **Set strong passwords**: Change default admin password
- [ ] **Configure HTTPS**: Use reverse proxy (Nginx/Apache) with SSL
- [ ] **Set up firewall**: Only allow necessary ports
- [ ] **Configure logging**: Set up log rotation
- [ ] **Set resource limits**: Configure worker count appropriately
- [ ] **Test backup/restore**: Ensure data can be recovered

### Security Checklist

- [ ] **SECRET_KEY**: Changed from default
- [ ] **HTTPS enabled**: SSL/TLS certificates configured
- [ ] **Firewall configured**: Only necessary ports open
- [ ] **Strong passwords**: All user accounts have secure passwords
- [ ] **Regular updates**: System and dependencies updated
- [ ] **Backup strategy**: Automated backups configured
- [ ] **Monitoring**: Health checks and alerts set up

### Performance Checklist

- [ ] **Worker count**: Optimized for your server
- [ ] **Database**: ChromaDB storage optimized
- [ ] **Caching**: Query and embedding caches enabled
- [ ] **Resource limits**: Memory and CPU limits set
- [ ] **Monitoring**: Performance metrics tracked

---

## Security Considerations

### 1. HTTPS/SSL

**Always use HTTPS in production!**

Set up a reverse proxy (Nginx or Apache) with SSL:

```nginx
# Nginx example
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Firewall Configuration

Only allow necessary ports:

```bash
# Allow SSH (22) and HTTPS (443)
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Environment Variables

Never commit `.env` file. Use secure secret management:
- Environment variables
- Secret management services (AWS Secrets Manager, HashiCorp Vault)
- Configuration files with restricted permissions

### 4. Regular Updates

Keep dependencies updated:

```bash
pip list --outdated
pip install --upgrade package-name
```

---

## Monitoring and Logging

### Health Check Endpoint

The application provides a health check:

```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "status": "healthy",
  "service": "rag-system"
}
```

### Logging

Gunicorn logs to stdout/stderr by default. For production:

1. **Redirect to files**:
   ```python
   # In gunicorn_config.py
   accesslog = '/var/log/rag-system/access.log'
   errorlog = '/var/log/rag-system/error.log'
   ```

2. **Set up log rotation**:
   ```bash
   # /etc/logrotate.d/rag-system
   /var/log/rag-system/*.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 your-user your-group
   }
   ```

### Monitoring Tools

Consider using:
- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **New Relic / Datadog**: Application performance monitoring

---

## Performance Tuning

### 1. Worker Configuration

Adjust based on your workload:

```python
# CPU-bound (LLM processing)
workers = CPU_cores + 1

# I/O-bound (API calls)
workers = (CPU_cores * 2) + 1
```

### 2. Timeout Settings

For long-running LLM queries:

```python
timeout = 120  # 2 minutes
keepalive = 5
```

### 3. Resource Limits

Set appropriate limits in systemd or Docker:

```ini
# systemd
LimitNOFILE=65536
MemoryMax=4G
CPUQuota=200%
```

### 4. Database Optimization

- Enable ChromaDB persistence
- Configure appropriate chunk sizes
- Use embedding cache
- Enable query cache

---

## Quick Reference

### Start Production Server

```bash
# Using script
./scripts/run-production.sh

# Manual
gunicorn -c gunicorn_config.py "backend.app:create_app()"
```

### Check Status

```bash
# Health check
curl http://localhost:5001/health

# Process status
ps aux | grep gunicorn
```

### View Logs

```bash
# If using systemd
sudo journalctl -u rag-system -f

# If logging to files
tail -f /var/log/rag-system/access.log
tail -f /var/log/rag-system/error.log
```

### Stop Server

```bash
# If using systemd
sudo systemctl stop rag-system

# If running manually
pkill -f gunicorn
```

---

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [Nginx Reverse Proxy Guide](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Systemd Service Guide](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Remember**: Always test your production setup in a staging environment before deploying to production!

