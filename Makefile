# Certphisher - Makefile for Docker operations
# Makes common Docker commands easier

.PHONY: help setup start stop restart logs logs-backend logs-frontend logs-mongo status clean rebuild backup

# Default target
help:
	@echo "Certphisher Docker Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup (copy config, build images)"
	@echo ""
	@echo "Running:"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Logs:"
	@echo "  make logs           - View all logs"
	@echo "  make logs-backend   - View backend logs only"
	@echo "  make logs-frontend  - View frontend logs only"
	@echo "  make logs-mongo     - View MongoDB logs"
	@echo ""
	@echo "Status:"
	@echo "  make status         - Show running containers"
	@echo "  make ps             - Show container status"
	@echo ""
	@echo "Maintenance:"
	@echo "  make rebuild        - Rebuild and restart"
	@echo "  make clean          - Stop and remove containers"
	@echo "  make clean-all      - Remove containers AND data"
	@echo "  make backup         - Backup MongoDB data"
	@echo ""
	@echo "MongoDB:"
	@echo "  make mongo-shell    - Access MongoDB shell"
	@echo "  make mongo-stats    - Show database statistics"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup"
	@echo "  2. Edit config.ini with your API keys"
	@echo "  3. make start"
	@echo "  4. Open http://localhost:5000"

# Initial setup
setup:
	@echo "Setting up Certphisher..."
	@if [ ! -f config.ini ]; then \
		cp config.docker.ini config.ini; \
		echo "✓ Created config.ini from template"; \
		echo "⚠️  IMPORTANT: Edit config.ini and add your API keys!"; \
	else \
		echo "✓ config.ini already exists"; \
	fi
	@echo "Building Docker images..."
	docker-compose build
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit config.ini and add your VirusTotal and urlscan.io API keys"
	@echo "  2. Run: make start"
	@echo "  3. Open http://localhost:5000"

# Start services
start:
	@echo "Starting Certphisher services..."
	docker-compose up -d
	@echo "✓ Services started!"
	@echo ""
	@echo "Dashboard: http://localhost:5000"
	@echo "Settings:  http://localhost:5000/settings"
	@echo ""
	@echo "View logs: make logs"

# Stop services
stop:
	@echo "Stopping Certphisher services..."
	docker-compose stop
	@echo "✓ Services stopped"

# Restart services
restart:
	@echo "Restarting Certphisher services..."
	docker-compose restart
	@echo "✓ Services restarted"

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f certphisher-backend

logs-frontend:
	docker-compose logs -f certphisher-frontend

logs-mongo:
	docker-compose logs -f mongodb

# Container status
status:
	@echo "Certphisher Service Status:"
	@echo "==========================="
	@docker-compose ps
	@echo ""
	@echo "Resource Usage:"
	@docker stats --no-stream

ps:
	docker-compose ps

# Rebuild
rebuild:
	@echo "Rebuilding Certphisher..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✓ Rebuild complete!"

# Clean up
clean:
	@echo "Stopping and removing containers..."
	docker-compose down
	@echo "✓ Cleanup complete (data preserved)"

clean-all:
	@echo "⚠️  WARNING: This will delete ALL data including detections!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker-compose down -v
	@echo "✓ Full cleanup complete (all data removed)"

# Backup
backup:
	@echo "Backing up MongoDB data..."
	@mkdir -p backups
	docker-compose exec -T mongodb mongodump --out=/tmp/backup
	docker cp certphisher-mongodb:/tmp/backup ./backups/backup_$$(date +%Y%m%d_%H%M%S)
	@echo "✓ Backup complete: backups/backup_$$(date +%Y%m%d_%H%M%S)"

# MongoDB operations
mongo-shell:
	docker-compose exec mongodb mongosh certphisher

mongo-stats:
	@echo "Database Statistics:"
	@echo "==================="
	@docker-compose exec mongodb mongosh certphisher --quiet --eval "db.stats()" | grep -E "db|collections|dataSize|indexSize"
	@echo ""
	@echo "Sites Collection:"
	@docker-compose exec mongodb mongosh certphisher --quiet --eval "db.sites.countDocuments({})" | tail -1 | xargs echo "  Total sites:"
	@docker-compose exec mongodb mongosh certphisher --quiet --eval "db.sites.countDocuments({certphisher_score: {\$$gt: 100}})" | tail -1 | xargs echo "  Suspicious (>100):"
	@echo ""
	@echo "Brands Collection:"
	@docker-compose exec mongodb mongosh certphisher --quiet --eval "db.brands.countDocuments({})" | tail -1 | xargs echo "  Total brands:"

# Development helpers
dev-backend:
	docker-compose up certphisher-backend

dev-frontend:
	docker-compose up certphisher-frontend

shell-backend:
	docker-compose exec certphisher-backend bash

shell-frontend:
	docker-compose exec certphisher-frontend bash

# Update
update:
	@echo "Pulling latest changes..."
	git pull
	@echo "Rebuilding..."
	$(MAKE) rebuild
	@echo "✓ Update complete!"
