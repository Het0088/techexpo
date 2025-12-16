# Complete Production Deployment Guide
# Deploy ISL Recognition to Your Own Domain

## 🎯 **Overview**

You'll need:
1. **VPS Server** (DigitalOcean, Linode, AWS) - ~$5/month
2. **Your Domain** (you already have this!)
3. **Server Setup** (Linux, Nginx, SSL)
4. **Process Manager** (Keep Python running 24/7)
5. **Logging & Monitoring**

---

## 📋 **Part 1: Choose a VPS Provider**

### **Recommended: DigitalOcean**
- **Cost:** $6/month (2GB RAM)
- **Setup Time:** 10 minutes
- **Location:** Choose nearest to your users

**Alternatives:**
- Linode: $5/month
- AWS Lightsail: $5/month
- Vultr: $6/month

---

## 🖥️ **Part 2: Server Setup (Ubuntu 22.04)**

### **Step 1: Initial Setup**

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx supervisor git
```

### **Step 2: Create Application User**

```bash
# Don't run as root - create app user
sudo adduser islapp
sudo usermod -aG sudo islapp

# Switch to app user
su - islapp
```

### **Step 3: Deploy Your Code**

```bash
# Clone from GitHub (recommended)
cd /home/islapp
git clone https://github.com/YOUR_USERNAME/isl-recognition.git
cd isl-recognition

# OR upload files via SCP
# scp -r d:/Ideas/techexpo/* islapp@your-server-ip:/home/islapp/isl-recognition/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ **Part 3: Keep Python Running 24/7 (Supervisor)**

### **Create Supervisor Config**

```bash
sudo nano /etc/supervisor/conf.d/isl-recognition.conf
```

**Add this:**

```ini
[program:isl-recognition]
directory=/home/islapp/isl-recognition
command=/home/islapp/isl-recognition/venv/bin/gunicorn app_production:app --bind 127.0.0.1:8000 --workers 2 --timeout 120
user=islapp
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/isl-recognition/err.log
stdout_logfile=/var/log/isl-recognition/out.log
```

**Create log directory:**

```bash
sudo mkdir -p /var/log/isl-recognition
sudo chown islapp:islapp /var/log/isl-recognition
```

**Start service:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start isl-recognition

# Check status
sudo supervisorctl status
```

**You should see:**
```
isl-recognition    RUNNING   pid 12345, uptime 0:00:10
```

---

## 🌐 **Part 4: Configure Nginx (Web Server)**

### **Create Nginx Config**

```bash
sudo nano /etc/nginx/sites-available/isl-recognition
```

**Add this:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Increase upload size for images
    client_max_body_size 10M;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Static files (optional - serve directly)
    location /css {
        alias /home/islapp/isl-recognition/css;
        expires 30d;
    }

    location /js {
        alias /home/islapp/isl-recognition/js;
        expires 30d;
    }

    # Logging
    access_log /var/log/nginx/isl-access.log;
    error_log /var/log/nginx/isl-error.log;
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/isl-recognition /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl restart nginx
```

---

## 🔒 **Part 5: Add SSL Certificate (HTTPS)**

### **Free SSL with Let's Encrypt**

```bash
# Point your domain to server IP first!
# Then run:

sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)
```

**Auto-renewal (already configured):**
```bash
# Test renewal
sudo certbot renew --dry-run

# Certificate auto-renews every 90 days
```

**Now your site is LIVE at:** `https://yourdomain.com` ✅

---

## 📊 **Part 6: Logging & Monitoring**

### **Application Logs**

**View real-time logs:**
```bash
# Application logs
tail -f /var/log/isl-recognition/out.log
tail -f /var/log/isl-recognition/err.log

# Nginx logs
tail -f /var/log/nginx/isl-access.log
tail -f /var/log/nginx/isl-error.log
```

### **Enhanced Application Logging**

**Update `app_production.py`:**

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
if not DEBUG:
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler - rotates at 10MB
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ISL Recognition startup')

# Log predictions
@app.route('/api/predict/alphabet', methods=['POST'])
def predict_alphabet():
    try:
        # ... existing code ...
        app.logger.info(f'Alphabet prediction: {result["letter"]} ({result["confidence"]:.2f})')
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Prediction error: {str(e)}')
        return jsonify({'error': str(e)}), 500
```

### **System Monitoring**

**Install monitoring tools:**
```bash
# Resource monitoring
sudo apt install htop

# Check server health
htop  # CPU, RAM usage

# Check Python process
ps aux | grep gunicorn

# Check disk space
df -h
```

### **Simple Uptime Monitor (Free)**

Use **UptimeRobot.com**:
1. Sign up (free)
2. Add monitor: https://yourdomain.com/health
3. Get email alerts if site goes down

---

## 🔄 **Part 7: Deployment Workflow**

### **Initial Deployment**
```bash
# On server
cd /home/islapp/isl-recognition
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart isl-recognition
```

### **Auto-Deploy Script**

Create `deploy.sh`:

```bash
#!/bin/bash
cd /home/islapp/isl-recognition

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart application
sudo supervisorctl restart isl-recognition

# Check status
sleep 2
sudo supervisorctl status isl-recognition

echo "✅ Deployment complete!"
```

**Make executable:**
```bash
chmod +x deploy.sh
```

**Deploy with one command:**
```bash
./deploy.sh
```

---

## 🚨 **Part 8: Production Checklist**

### **Security**

- [ ] Enable firewall
  ```bash
  sudo ufw allow 22      # SSH
  sudo ufw allow 80      # HTTP
  sudo ufw allow 443     # HTTPS
  sudo ufw enable
  ```

- [ ] Change SSH port (optional but recommended)
- [ ] Disable root SSH login
- [ ] Set up SSH keys (no password login)
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`

### **Performance**

- [ ] **No spaCy** ✅ (you removed it - good!)
- [ ] Use Gunicorn with 2-4 workers
- [ ] Enable Nginx caching for static files
- [ ] Compress responses (gzip)
- [ ] Use smaller model files if possible

### **Reliability**

- [ ] Supervisor auto-restart ✅
- [ ] SSL certificate auto-renewal ✅
- [ ] Database backups (if you add one)
- [ ] Model files backed up
- [ ] Log rotation configured

### **Monitoring**

- [ ] Uptime monitoring (UptimeRobot)
- [ ] Log monitoring
- [ ] Disk space alerts
- [ ] SSL expiry reminders

---

## 📱 **Part 9: DNS Configuration**

**Point your domain to server:**

In your domain registrar (GoDaddy, Namecheap, etc.):

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

**Wait 10-60 minutes for DNS to propagate.**

---

## 🎯 **Quick Commands Reference**

```bash
# Restart app
sudo supervisorctl restart isl-recognition

# View logs
tail -f /var/log/isl-recognition/out.log

# Check if running
sudo supervisorctl status

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx config
sudo nginx -t

# View Nginx logs
tail -f /var/log/nginx/isl-access.log
```

---

## 💰 **Cost Breakdown**

- **VPS:** $5-6/month (DigitalOcean, Linode)
- **Domain:** $10-15/year (if you already have it: $0)
- **SSL:** FREE (Let's Encrypt)
- **Total:** **~$6/month + domain**

---

## ✅ **What You DON'T Need to Worry About**

❌ **spaCy** - You removed it! Good decision.  
❌ **GPU** - CPU is fine for your models  
❌ **Databases** - Not needed for your app  
❌ **Redis/Celery** - Not needed for simple requests  
❌ **Docker** - Optional, not required  

---

## 🚀 **Your Complete Setup Summary**

1. **Get VPS** ($5/month)
2. **Point domain** to VPS IP
3. **SSH into server** and run setup commands
4. **Deploy code** (git clone or SCP)
5. **Configure Supervisor** (keeps Python running)
6. **Configure Nginx** (web server + reverse proxy)
7. **Add SSL** (certbot - free HTTPS)
8. **Done!** Your site is live at https://yourdomain.com

**Logs:** `/var/log/isl-recognition/out.log`  
**Restart:** `sudo supervisorctl restart isl-recognition`  
**Monitor:** https://uptimerobot.com

---

**Need help with any specific step?** Let me know which part you want to dive deeper into! 🎯
