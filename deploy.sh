#!/bin/bash
# Auto-deployment script for ISL Recognition

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Navigate to project
cd /home/islapp/isl-recognition

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtualenv..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Restart application
echo "♻️  Restarting application..."
sudo supervisorctl restart isl-recognition

# Wait for startup
sleep 3

# Check status
echo "✅ Checking status..."
sudo supervisorctl status isl-recognition

# Check if running
if sudo supervisorctl status isl-recognition | grep -q "RUNNING"; then
    echo "✅ Deployment successful!"
    echo "🌐 Live at: https://yourdomain.com"
else
    echo "❌ Deployment failed - check logs:"
    echo "   tail -f /var/log/isl-recognition/err.log"
    exit 1
fi
