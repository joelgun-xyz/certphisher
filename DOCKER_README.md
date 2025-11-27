# Certphisher - Docker Setup 🐳

Quick and easy way to run Certphisher on macOS, Linux, or Windows using Docker.

## 🚀 Quick Start (3 Steps)

### 1. Install Docker Desktop

**macOS:**
```bash
brew install --cask docker
# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
```

**Windows:**
Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### 2. Configure API Keys

Copy the Docker config template and add your API keys:

```bash
cp config.docker.ini config.ini
nano config.ini  # or use your favorite editor
```

**Required:** Add your API keys:
- `vt_key` - Get from [VirusTotal](https://developers.virustotal.com/reference)
- `urlscan_key` - Get from [urlscan.io](https://urlscan.io/about-api/)

**Optional:** Configure Slack notifications (or set `integration = 0` to disable)

### 3. Start Everything

```bash
docker-compose up -d
```

That's it! 🎉

**Access the dashboard:** http://localhost:5000

**Access settings:** http://localhost:5000/settings

## 📦 What Gets Installed

The Docker setup includes:

- **MongoDB 7.0** - Database for storing detections
- **Certphisher Backend** - Certificate stream monitor (main.py)
- **Flask Frontend** - Web dashboard (app.py)
- **Chrome/Chromium** - For screenshot capture
- **All Python dependencies** - Automatically installed

## 🎮 Usage

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Start and see logs
docker-compose up

# Start specific service
docker-compose up certphisher-backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only (certificate monitoring)
docker-compose logs -f certphisher-backend

# Frontend only (web dashboard)
docker-compose logs -f certphisher-frontend

# MongoDB
docker-compose logs -f mongodb

# Last 100 lines
docker-compose logs --tail=100 -f certphisher-backend
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart certphisher-backend

# Restart after config change
docker-compose restart certphisher-backend certphisher-frontend
```

### Check Status

```bash
# See running containers
docker-compose ps

# See resource usage
docker stats
```

## 🔧 Configuration

### Update Configuration

After editing `config.ini`:

```bash
docker-compose restart certphisher-backend certphisher-frontend
```

### Add Brands via Web UI

1. Open http://localhost:5000/settings
2. Add brand keyword (e.g., "bankxyz")
3. Upload logo
4. Add official website URL
5. Capture screenshot

No restart needed - changes are immediate!

### Environment Variables

You can also configure via environment variables in `docker-compose.yml`:

```yaml
environment:
  - MONGODB_HOST=mongodb
  - MONGODB_PORT=27017
  - SLACK_INTEGRATION=0
```

## 📊 Accessing Data

### MongoDB Shell

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh certphisher

# Example queries
db.sites.find().limit(5)
db.sites.countDocuments({"certphisher_score": {$gt: 100}})
db.brands.find()
```

### View Uploaded Logos/Screenshots

Files are stored in `./app/uploads/` on your host machine:

```bash
ls -lh app/uploads/
```

### Export Data

```bash
# Export all detections to JSON
docker-compose exec mongodb mongoexport \
  --db=certphisher \
  --collection=sites \
  --out=/tmp/detections.json

# Copy to host
docker cp certphisher-mongodb:/tmp/detections.json ./detections.json
```

## 🛠️ Troubleshooting

### Backend Not Starting

**Check logs:**
```bash
docker-compose logs certphisher-backend
```

**Common issues:**
- Missing API keys in config.ini
- MongoDB not ready (wait 10 seconds and check again)
- Config file syntax error

**Solution:**
```bash
# Check config
cat config.ini

# Restart with fresh logs
docker-compose restart certphisher-backend
docker-compose logs -f certphisher-backend
```

### Frontend Not Accessible

**Check if running:**
```bash
docker-compose ps certphisher-frontend
```

**Try accessing:**
```bash
curl http://localhost:5000
```

**Restart frontend:**
```bash
docker-compose restart certphisher-frontend
```

### Screenshot Capture Fails

**Error:** "Chrome/Chromium not found"

**Solution:** Already included in Docker image, but verify:
```bash
docker-compose exec certphisher-frontend which chromium
docker-compose exec certphisher-frontend chromium --version
```

### Port Already in Use

**Error:** "port 5000 is already allocated"

**Solution:** Change port in `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Use port 5001 instead
```

Then access at http://localhost:5001

### MongoDB Connection Issues

**Check MongoDB health:**
```bash
docker-compose exec mongodb mongosh --eval "db.runCommand({ping: 1})"
```

**View MongoDB logs:**
```bash
docker-compose logs mongodb
```

**Reset MongoDB:**
```bash
docker-compose down
docker volume rm certphisher_mongodb_data
docker-compose up -d
```

### Out of Disk Space

**Check Docker space:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (CAUTION: removes data)
docker volume prune

# Remove everything unused
docker system prune -a
```

## 🔄 Updating

### Pull Latest Code

```bash
# Stop services
docker-compose down

# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### Update Dependencies Only

```bash
# Rebuild just the app image
docker-compose build certphisher-backend certphisher-frontend

# Restart services
docker-compose up -d
```

## 💾 Data Persistence

Data is persisted in Docker volumes:

- **mongodb_data** - All detections, brands, configurations
- **uploads** - Mounted from `./app/uploads/` (logos, screenshots)
- **logs** - Application logs

To backup:

```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out=/backup
docker cp certphisher-mongodb:/backup ./mongodb_backup

# Backup uploads
tar -czf uploads_backup.tar.gz app/uploads/
```

To restore:

```bash
# Restore MongoDB
docker cp ./mongodb_backup certphisher-mongodb:/backup
docker-compose exec mongodb mongorestore /backup

# Restore uploads
tar -xzf uploads_backup.tar.gz
```

## 🔒 Security Notes

### Production Deployment

For production use:

1. **Change MongoDB credentials:**
   ```yaml
   mongodb:
     environment:
       - MONGO_INITDB_ROOT_USERNAME=admin
       - MONGO_INITDB_ROOT_PASSWORD=strongpassword
   ```

2. **Use secrets for API keys:**
   ```bash
   echo "your_api_key" | docker secret create vt_key -
   ```

3. **Enable SSL/TLS:**
   - Use nginx reverse proxy
   - Configure SSL certificates
   - Update docker-compose with nginx service

4. **Restrict network access:**
   ```yaml
   ports:
     - "127.0.0.1:5000:5000"  # Only localhost
   ```

5. **Update Flask secret key:**
   Edit `app/app.py` and change `SECRET_KEY`

## 📈 Performance Tuning

### Increase Resources

Edit `docker-compose.yml`:

```yaml
certphisher-backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

### Scale Services

Run multiple backend instances:

```bash
docker-compose up -d --scale certphisher-backend=3
```

### Optimize MongoDB

```bash
# Create indexes for faster queries
docker-compose exec mongodb mongosh certphisher --eval '
  db.sites.createIndex({"certphisher_score": -1});
  db.sites.createIndex({"checked_vt": 1});
  db.brands.createIndex({"keyword": 1});
'
```

## 🧪 Development

### Hot Reload

For development with code changes:

```yaml
certphisher-backend:
  volumes:
    - .:/app  # Mount entire directory
  command: watchmedo auto-restart -d . -p '*.py' -- python3 main.py
```

### Debug Mode

```yaml
certphisher-frontend:
  environment:
    - FLASK_ENV=development
    - FLASK_DEBUG=1
```

### Access Container Shell

```bash
# Backend
docker-compose exec certphisher-backend bash

# Frontend
docker-compose exec certphisher-frontend bash

# MongoDB
docker-compose exec mongodb bash
```

## 📋 Common Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart after config change
docker-compose restart

# Rebuild after code change
docker-compose up -d --build

# View running containers
docker-compose ps

# Access MongoDB shell
docker-compose exec mongodb mongosh certphisher

# View backend logs only
docker-compose logs -f certphisher-backend

# Check resource usage
docker stats

# Clean up
docker-compose down -v  # CAUTION: Removes data
```

## 🆘 Getting Help

1. **Check logs first:**
   ```bash
   docker-compose logs -f
   ```

2. **Verify configuration:**
   ```bash
   cat config.ini
   ```

3. **Test MongoDB connection:**
   ```bash
   docker-compose exec mongodb mongosh certphisher --eval "db.runCommand({ping: 1})"
   ```

4. **Check if all services are running:**
   ```bash
   docker-compose ps
   ```

5. **View resource usage:**
   ```bash
   docker stats
   ```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB in Docker](https://hub.docker.com/_/mongo)
- [Certphisher Documentation](./README_ENHANCED.md)
- [Settings Guide](./SETTINGS_GUIDE.md)

## ⚡ Quick Testing

Just want to test it quickly?

```bash
# 1. Clone repo
git clone https://github.com/your-username/certphisher.git
cd certphisher

# 2. Create minimal config
cat > config.ini << EOF
[apikeys]
vt_key = your_vt_key_here
urlscan_key = your_urlscan_key_here

[mongodb]
my_instance = mongodb://mongodb:27017/
my_db = certphisher
my_col = sites

[slack]
integration = 0

[ca_filtering]
legitimate_cas = DigiCert, Sectigo

[logo_detection]
enabled = true
brand_keywords = paypal, amazon
EOF

# 3. Start
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Open browser
open http://localhost:5000
```

Enjoy! 🚀
