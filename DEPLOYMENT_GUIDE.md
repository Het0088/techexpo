# ISL Recognition - Production Deployment Guide

## 🚀 Quick Deploy to Render.com (FREE)

### Step 1: Prepare Code

1. **Create `.env` file:**
```bash
DEBUG=False
PORT=

5000
```

2. **Create `Procfile`:**
```
web: gunicorn app_production:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

3. **Push to GitHub:**
```bash
git init
git add .
git commit -m "ISL Recognition System"
git push origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign up (free)
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Configure:
   - **Name:** isl-recognition
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app_production:app --bind 0.0.0.0:$PORT`
6. Click "Create Web Service"

**Done!** Your site will be live at: `https://isl-recognition.onrender.com`

---

## 🔧 Alternative: Deploy to Railway.app

1. Go to [railway.app](https://railway.app)
2. Connect GitHub
3. Deploy from repo
4. Railway auto-detects Python
5. Live in 2 minutes!

---

## 💻 Deploy to Your Own Server (VPS)

### Ubuntu/Debian Server

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# 2. Clone your repo
git clone https://github.com/YOUR_USERNAME/isl-recognition.git
cd isl-recognition

# 3. Install Python packages
pip3 install -r requirements.txt

# 4. Run with Gunicorn
gunicorn app_production:app --bind 0.0.0.0:5000 --workers 2
```

### Configure Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Add SSL certificate (Render provides free)
- [ ] Set up monitoring
- [ ] Configure CORS properly
- [ ] Optimize model loading
- [ ] Add rate limiting
- [ ] Set up logging
- [ ] Database for analytics (optional)
- [ ] CDN for static files (optional)

---

## 📊 Hosting Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| **Render.com** | FREE | Easy, SSL included | Cold starts on free tier |
| **Railway.app** | $5/month | Fast, good DX | Paid only |
| **Heroku** | $7/month | Reliable | No free tier |
| **DigitalOcean** | $5/month | Full control | Manual setup |
| **AWS/Azure** | $10+/month | Scalable | Complex |

---

## 🎯 Recommended for Your Project

**For Tech Expo:** Render.com (FREE)
- Good performance
- Free SSL
- Easy setup
- Professional URL

**For Long-term:** Railway.app ($5/month)
- Better performance
- No cold starts
- Great support

---

## 🚨 Important Notes

1. **Model Size:** Your models (~200 MB) work fine on all platforms
2. **RAM:** Need ~1 GB minimum (all platforms provide this)
3. **Cold Starts:** Free tiers sleep after 15 mins of inactivity
4. **Custom Domain:** All platforms support custom domains
5. **GitHub Required:** Easiest to deploy from GitHub

---

## ⚡ Quick Start Commands

**Test production mode locally:**
```bash
pip install gunicorn
gunicorn app_production:app --bind 0.0.0.0:5000
```

**Then visit:** http://localhost:5000

---

**Ready to deploy?** I recommend Render.com for the easiest free deployment!
